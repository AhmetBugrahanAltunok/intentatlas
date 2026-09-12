from __future__ import annotations

from io import StringIO
from pathlib import Path

import pytest

from intentatlas.change_analysis import ChangeAnalysis, ChangeAnalysisFile
from intentatlas.change_report import build_change_report, render_change_report
from intentatlas.change_set import ChangeFile, ChangeSet
from intentatlas.cli import build_parser
from intentatlas.config import ProjectConfig
from intentatlas.graph import AtlasGraph
from intentatlas.models import Edge, Node
from intentatlas.onboarding import GuideSnapshot, TerminalIO, _render_summary
from intentatlas.recommendations import recommend_tests
from intentatlas.scanner import scan_repository
from intentatlas.test_eligibility import classify_python_test, load_python_test_policy


def _write(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _analysis(target: str) -> ChangeAnalysis:
    change_set = ChangeSet(
        "worktree",
        "a" * 40,
        None,
        (ChangeFile("modified", "src/pkg/core.py"),),
    )
    return ChangeAnalysis(
        change_set,
        "analyzed",
        (
            ChangeAnalysisFile(
                "src/pkg/core.py",
                "modified",
                "analyzed",
                "aligned",
                "high",
                (target,),
                ("validated-symbol-span",),
            ),
        ),
    )


def _linked_reason_graph() -> tuple[AtlasGraph, str]:
    target = "symbol:src/pkg/core.py::target"
    graph = AtlasGraph()
    graph.extend(
        [
            Node("file:src/pkg/core.py", "file", "core.py", path="src/pkg/core.py"),
            Node(target, "symbol", "target", path="src/pkg/core.py"),
            Node(
                "file:src/pkg/__init__.py",
                "file",
                "__init__.py",
                path="src/pkg/__init__.py",
            ),
            Node(
                "file:tests/test_core.py",
                "test",
                "test_core.py",
                path="tests/test_core.py",
                metadata={"size_bytes": 100},
            ),
        ],
        [
            Edge("file:src/pkg/core.py", target, "defines", "python-ast"),
            Edge("file:src/pkg/__init__.py", target, "imports", "python-symbol-reference"),
            Edge("file:tests/test_core.py", target, "tests", "python-symbol-reference"),
            Edge(
                "file:tests/test_core.py",
                "file:src/pkg/__init__.py",
                "tests",
                "python-ast",
            ),
        ],
    )
    return graph, target


def test_change_report_preserves_primary_reason_path_and_evidence() -> None:
    graph, target = _linked_reason_graph()

    recommendation = recommend_tests(graph, target).recommendations[0]
    report = build_change_report(graph, _analysis(target))
    item = report.tests[0]
    payload = report.to_dict()["tests"][0]

    assert item.score == 80
    assert item.primary_reason.signal == "symbol-structural-test"
    assert item.primary_reason.score == item.score
    assert item.primary_reason.path.nodes == (target, "file:tests/test_core.py")
    assert "python-symbol-reference" in item.primary_reason.evidence
    assert item.reason_details[1].signal == "direct-symbol-dependent-package-fallback"
    assert item.reason_details[1].score == 45
    assert payload["primary_reason"] == payload["reason_details"][0]
    assert payload["primary_reason"] == recommendation.reasons[0].to_dict()
    assert {reason["signal"] for reason in payload["reason_details"]} == {
        "symbol-structural-test",
        "direct-symbol-dependent-package-fallback",
    }
    assert payload["reasons"] and payload["paths"] and payload["evidence"]
    text = render_change_report(report, explain=True)
    assert "Why: The test directly references an exactly modified symbol." in text
    assert "(symbol-structural-test, 80/100)" in text
    assert f"Path: {target} -[tested-by]-> file:tests/test_core.py" in text
    assert "Evidence: python-ast, python-symbol-reference" in text
    assert "Additional signals: 1" in text
    assert "tests[].reason_details" in text


def test_omission_counts_and_ranking_reason_remain_separate_on_all_human_surfaces() -> None:
    target = "symbol:src/pkg/core.py::target"
    graph = AtlasGraph()
    nodes = [
        Node("file:src/pkg/core.py", "file", "core.py", path="src/pkg/core.py"),
        Node(target, "symbol", "target", path="src/pkg/core.py"),
    ]
    edges = [Edge("file:src/pkg/core.py", target, "defines", "python-ast")]
    for index in range(25):
        requirement_id = f"REQ-OMIT-{index:02d}"
        test_id = f"file:tests/test_weak_{index:02d}.py"
        nodes.extend(
            [
                Node(requirement_id, "requirement", requirement_id),
                Node(
                    test_id,
                    "test",
                    test_id.removeprefix("file:"),
                    path=test_id.removeprefix("file:"),
                    metadata={"size_bytes": 50},
                ),
            ]
        )
        edges.extend(
            [
                Edge(requirement_id, target, "defines", "wikilink"),
                Edge(test_id, "file:src/pkg/core.py", "tests", "filename-convention"),
            ]
        )
    graph.extend(nodes, edges)

    report = build_change_report(graph, _analysis(target), minimum_confidence="medium")
    payload = report.to_dict()

    for key in ("requirement_selection", "test_selection"):
        assert payload[key] == {
            "selected_count": 0,
            "total_candidate_count": 25,
            "filtered_count": 25,
            "limit_omitted_count": 0,
            "omitted_shown_count": 20,
        }
    omitted = payload["omitted_tests"][0]
    assert omitted["selection_reason"] == "below-minimum-confidence"
    assert omitted["reason"] == omitted["selection_reason"]
    assert omitted["primary_reason"]["score"] == omitted["score"]
    assert omitted["primary_reason"] == omitted["reason_details"][0]

    text = render_change_report(report, explain=True)
    assert text.count("20/25 omission details shown") == 2

    output = StringIO()
    snapshot = GuideSnapshot(
        Path("."),
        None,  # type: ignore[arg-type]
        report.analysis.change_set,
        graph,
        report,
        b"",
        b"",
    )
    _render_summary(snapshot, TerminalIO(StringIO(), output), "en")
    guided = output.getvalue()
    assert guided.count("20/25 omission details shown") == 2


def test_python_support_files_remain_graph_artifacts_but_not_runnable_targets(tmp_path) -> None:
    _write(
        tmp_path,
        "pyproject.toml",
        "[project]\nname='pkg'\n[tool.pytest.ini_options]\ntestpaths=['tests']\n",
    )
    _write(tmp_path, "src/pkg/__init__.py", "")
    _write(tmp_path, "src/pkg/core.py", "def target():\n    return 1\n")
    _write(
        tmp_path,
        "tests/test_core.py",
        "from pkg.core import target\n\ndef test_target():\n    assert target() == 1\n",
    )
    _write(
        tmp_path,
        "tests/typing/typing_support.py",
        "from pkg.core import target\n\nvalue = target\n",
    )
    _write(tmp_path, "tests/conftest.py", "from pkg.core import target\n")
    _write(tmp_path, "tests/__init__.py", "")

    graph = scan_repository(tmp_path, ProjectConfig(git_history_limit=0))
    target = "symbol:src/pkg/core.py::target"
    support = graph.nodes["file:tests/typing/typing_support.py"]
    conftest = graph.nodes["file:tests/conftest.py"]

    assert support.kind == "test" and support.metadata["test_role"] == "support"
    assert conftest.kind == "test" and conftest.metadata["test_role"] == "fixture"
    assert any(edge.source == support.id and edge.target == target for edge in graph.edges)
    result = recommend_tests(graph, target, minimum_confidence="low")
    assert [item.test.id for item in result.recommendations] == [
        "file:tests/test_core.py"
    ]


def test_safe_pytest_python_files_override_and_non_python_behavior(tmp_path) -> None:
    _write(
        tmp_path,
        "pyproject.toml",
        "[project]\nname='pkg'\n"
        "[tool.pytest.ini_options]\npython_files=['check_*.py']\n",
    )
    _write(tmp_path, "src/pkg/core.py", "def target():\n    return 1\n")
    _write(tmp_path, "tests/check_core.py", "from pkg.core import target\n")
    _write(tmp_path, "tests/test_core.py", "from pkg.core import target\n")

    scanned = scan_repository(tmp_path, ProjectConfig(git_history_limit=0))
    assert scanned.nodes["file:tests/check_core.py"].metadata["test_role"] == "runnable"
    assert scanned.nodes["file:tests/test_core.py"].metadata["test_role"] == "support"

    ambiguous = tmp_path / "ambiguous"
    _write(
        ambiguous,
        "pyproject.toml",
        "[project]\nname='ambiguous'\n"
        "[tool.pytest.ini_options]\npython_files=['../check_*.py']\n",
    )
    _write(ambiguous, "tests/test_core.py", "def test_core():\n    pass\n")
    abstained = scan_repository(ambiguous, ProjectConfig(git_history_limit=0))
    assert abstained.nodes["file:tests/test_core.py"].metadata["test_role"] == "support"

    graph = AtlasGraph()
    graph.extend(
        [
            Node("file:src/core.js", "file", "core.js", path="src/core.js"),
            Node(
                "file:tests/core.spec.js",
                "test",
                "core.spec.js",
                path="tests/core.spec.js",
                metadata={"size_bytes": 10, "language": "JavaScript"},
            ),
            Node(
                "file:core_test.go",
                "test",
                "core_test.go",
                path="core_test.go",
                metadata={"size_bytes": 10, "language": "Go"},
            ),
        ],
        [
            Edge("file:tests/core.spec.js", "file:src/core.js", "tests", "javascript-ast"),
            Edge("file:core_test.go", "file:src/core.js", "tests", "go-ast"),
        ],
    )
    result = recommend_tests(graph, "file:src/core.js", minimum_confidence="low")
    assert {item.test.id for item in result.recommendations} == {
        "file:tests/core.spec.js",
        "file:core_test.go",
    }


def test_pytest_testpaths_exclude_test_named_production_support(tmp_path) -> None:
    _write(
        tmp_path,
        "pyproject.toml",
        "[tool.pytest.ini_options]\ntestpaths=['tests']\n",
    )
    _write(tmp_path, "src/pkg/core.py", "def target():\n    return 1\n")
    _write(tmp_path, "src/pkg/test_helper.py", "from pkg.core import target\n")
    _write(tmp_path, "tests/test_core.py", "from pkg.core import target\n")

    graph = scan_repository(tmp_path, ProjectConfig(git_history_limit=0))

    assert graph.nodes["file:src/pkg/test_helper.py"].metadata["test_role"] == "support"
    assert graph.nodes["file:tests/test_core.py"].metadata["test_role"] == "runnable"
    result = recommend_tests(
        graph, "symbol:src/pkg/core.py::target", minimum_confidence="low"
    )
    assert [item.test.id for item in result.recommendations] == ["file:tests/test_core.py"]


@pytest.mark.parametrize(
    ("config_path", "content", "evidence"),
    [
        (
            "pyproject.toml",
            "[tool.pytest.ini_options]\npython_files=['check_*.py']\n",
            "pyproject-pytest-python-files",
        ),
        ("pytest.ini", "[pytest]\npython_files = check_*.py\n", "pytest.ini-pytest-python-files"),
        (
            "setup.cfg",
            "[tool:pytest]\npython_files = check_*.py\n",
            "setup.cfg-pytest-python-files",
        ),
        ("tox.ini", "[pytest]\npython_files = check_*.py\n", "tox.ini-pytest-python-files"),
    ],
)
def test_bounded_pytest_filename_configuration_sources(
    tmp_path: Path, config_path: str, content: str, evidence: str
) -> None:
    _write(tmp_path, config_path, content)

    policy = load_python_test_policy(tmp_path)

    assert policy.patterns == ("check_*.py",)
    assert policy.evidence == evidence
    assert classify_python_test(Path("tests/check_core.py"), policy).role == "runnable"
    assert classify_python_test(Path("tests/helper.py"), policy).role == "support"


def test_low_mode_and_static_direct_reference_tiers_are_explained(capsys) -> None:
    with pytest.raises(SystemExit) as exit_info:
        build_parser().parse_args(["recommend-tests", "--help"])
    assert exit_info.value.code == 0
    help_text = capsys.readouterr().out
    normalized_help = " ".join(help_text.split())
    assert "exploratory" in normalized_help and "medium or higher" in normalized_help

    english = Path("README.md").read_text(encoding="utf-8")
    turkish = Path("README.tr.md").read_text(encoding="utf-8")
    assert "exploratory" in english and "medium or higher" in english
    assert "80/medium" in english and "changed set" in english
    assert "keşif" in turkish and "medium veya üzeri" in turkish
    assert "80/medium" in turkish and "değişiklik kümesi" in turkish
