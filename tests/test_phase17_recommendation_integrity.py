from __future__ import annotations

from pathlib import Path

from intentatlas.change_analysis import ChangeAnalysis, ChangeAnalysisFile
from intentatlas.change_report import build_change_report
from intentatlas.change_set import ChangeFile, ChangeSet
from intentatlas.config import ProjectConfig
from intentatlas.graph import AtlasGraph
from intentatlas.models import Edge, Node
from intentatlas.recommendations import recommend_tests
from intentatlas.scanner import scan_repository


def _write(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _exact_analysis(target: str) -> ChangeAnalysis:
    change_set = ChangeSet(
        "worktree",
        "a" * 40,
        None,
        (ChangeFile("modified", "src/core.py"),),
    )
    return ChangeAnalysis(
        change_set,
        "analyzed",
        (
            ChangeAnalysisFile(
                "src/core.py",
                "modified",
                "analyzed",
                "aligned",
                "high",
                (target,),
                ("validated-symbol-span",),
            ),
        ),
    )


def _dependent_graph() -> AtlasGraph:
    graph = AtlasGraph()
    graph.extend(
        [
            Node("file:src/core.py", "file", "core", path="src/core.py"),
            Node(
                "symbol:src/core.py::target",
                "symbol",
                "target",
                path="src/core.py",
            ),
            Node("file:src/dependent.py", "file", "dependent", path="src/dependent.py"),
            Node(
                "file:tests/test_dependent.py",
                "test",
                "test_dependent.py",
                path="tests/test_dependent.py",
                metadata={"size_bytes": 100},
            ),
            Node(
                "file:tests/test_weak.py",
                "test",
                "test_weak.py",
                path="tests/test_weak.py",
                metadata={"size_bytes": 100},
            ),
        ],
        [
            Edge(
                "file:src/core.py",
                "symbol:src/core.py::target",
                "defines",
                "python-ast",
            ),
            Edge(
                "file:src/dependent.py",
                "symbol:src/core.py::target",
                "imports",
                "python-symbol-reference",
            ),
            Edge(
                "file:tests/test_dependent.py",
                "file:src/dependent.py",
                "tests",
                "python-ast",
            ),
            Edge(
                "file:tests/test_weak.py",
                "file:src/dependent.py",
                "tests",
                "filename-convention",
            ),
        ],
    )
    return graph


def test_change_report_uses_canonical_confidence_and_filters_tests() -> None:
    graph = _dependent_graph()
    target = "symbol:src/core.py::target"

    direct = recommend_tests(graph, target, minimum_confidence="low")
    assert [(item.test.id, item.score, item.confidence) for item in direct.recommendations] == [
        ("file:tests/test_dependent.py", 65, "medium"),
        ("file:tests/test_weak.py", 45, "low"),
    ]

    report = build_change_report(graph, _exact_analysis(target), minimum_confidence="medium")
    assert [(item.test.id, item.score, item.confidence) for item in report.tests] == [
        ("file:tests/test_dependent.py", 65, "medium")
    ]
    assert report.test_candidate_count == 2
    assert report.test_filtered_count == 1
    assert report.test_limit_omitted_count == 0
    assert [(item.node.id, item.reason) for item in report.omitted_tests] == [
        ("file:tests/test_weak.py", "below-minimum-confidence")
    ]
    assert report.test_strategy == "targeted"


def test_empty_test_marker_is_not_an_executable_recommendation() -> None:
    graph = AtlasGraph()
    graph.extend(
        [
            Node("file:src/core.py", "file", "core", path="src/core.py"),
            Node(
                "symbol:src/core.py::target",
                "symbol",
                "target",
                path="src/core.py",
            ),
            Node("file:src/package.py", "file", "package", path="src/package.py"),
            Node(
                "file:tests/__init__.py",
                "test",
                "__init__.py",
                path="tests/__init__.py",
                metadata={"size_bytes": 0},
            ),
        ],
        [
            Edge(
                "file:src/core.py",
                "symbol:src/core.py::target",
                "defines",
                "python-ast",
            ),
            Edge(
                "file:src/package.py",
                "symbol:src/core.py::target",
                "imports",
                "python-symbol-reference",
            ),
            Edge(
                "file:tests/__init__.py",
                "file:src/package.py",
                "tests",
                "python-ast",
            ),
        ],
    )

    result = recommend_tests(
        graph,
        "symbol:src/core.py::target",
        minimum_confidence="low",
    )

    assert result.candidate_count == 0
    assert result.recommendations == ()


def test_single_broad_commit_cochange_does_not_outrank_direct_evidence() -> None:
    graph = _dependent_graph()
    nodes = [
        Node(
            "commit:broad",
            "commit",
            "broad",
            metadata={"date": "2026-01-02", "owner": "scanner"},
        ),
        Node(
            "file:tests/test_noise.py",
            "test",
            "test_noise.py",
            path="tests/test_noise.py",
            metadata={"size_bytes": 100},
        ),
    ]
    nodes.extend(
        Node(f"file:src/unrelated_{index}.py", "file", f"unrelated_{index}.py")
        for index in range(25)
    )
    edges = [
        Edge("commit:broad", "file:src/core.py", "changes", "git-log"),
        Edge("commit:broad", "file:tests/test_noise.py", "changes", "git-log"),
    ]
    edges.extend(
        Edge("commit:broad", f"file:src/unrelated_{index}.py", "changes", "git-log")
        for index in range(25)
    )
    graph.extend(nodes, edges)

    result = recommend_tests(
        graph,
        "symbol:src/core.py::target",
        minimum_confidence="low",
    )

    ranked = {item.test.id: item for item in result.recommendations}
    assert ranked["file:tests/test_dependent.py"].score == 65
    assert "file:tests/test_noise.py" not in ranked


def test_narrow_single_cochange_remains_low_confidence() -> None:
    graph = AtlasGraph()
    graph.extend(
        [
            Node("file:src/core.py", "file", "core.py", path="src/core.py"),
            Node(
                "commit:narrow",
                "commit",
                "narrow",
                metadata={"date": "2026-01-02", "owner": "scanner"},
            ),
            Node(
                "commit:narrow-again",
                "commit",
                "narrow again",
                metadata={"date": "2026-01-02", "owner": "scanner"},
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
            Edge("commit:narrow", "file:src/core.py", "changes", "git-log"),
            Edge("commit:narrow", "file:tests/test_core.py", "changes", "git-log"),
            Edge("commit:narrow-again", "file:src/core.py", "changes", "git-log"),
            Edge(
                "commit:narrow-again",
                "file:tests/test_core.py",
                "changes",
                "git-log",
            ),
        ],
    )

    result = recommend_tests(graph, "file:src/core.py", minimum_confidence="low")

    assert [(item.test.id, item.score, item.confidence) for item in result.recommendations] == [
        ("file:tests/test_core.py", 60, "low")
    ]
    assert result.recommendations[0].reason_count == 2


def test_flit_src_layout_prefers_exact_caller_over_reexport_marker(tmp_path) -> None:
    _write(
        tmp_path,
        "pyproject.toml",
        "[project]\nname = 'click'\n"
        "[build-system]\nbuild-backend = 'flit_core.buildapi'\n"
        "[tool.flit.module]\nname = 'click'\n",
    )
    _write(tmp_path, "src/click/__init__.py", "from .formatting import wrap_text as wrap_text\n")
    _write(tmp_path, "src/click/formatting.py", "def wrap_text(value):\n    return value\n")
    _write(tmp_path, "tests/test_utils/__init__.py", "")
    _write(
        tmp_path,
        "tests/test_formatting.py",
        "import click\n\ndef test_wrap_text():\n"
        "    assert click.formatting.wrap_text('x') == 'x'\n",
    )
    _write(
        tmp_path,
        "tests/test_unrelated.py",
        "from click import echo\n\ndef test_echo():\n    assert echo is not None\n",
    )

    graph = scan_repository(tmp_path, ProjectConfig(git_history_limit=0))
    target = "symbol:src/click/formatting.py::wrap_text"

    assert any(
        edge.source == "file:tests/test_formatting.py"
        and edge.target == target
        and edge.relation == "tests"
        and edge.evidence == "python-symbol-reference"
        for edge in graph.edges
    )
    result = recommend_tests(graph, target)
    assert [(item.test.id, item.score) for item in result.recommendations] == [
        ("file:tests/test_formatting.py", 80)
    ]


def test_hatchling_and_conventional_src_layout_resolve_qualified_modules(tmp_path) -> None:
    for project, pyproject in (
        (
            "hatch",
            "[project]\nname = 'hatch-pkg'\n"
            "[build-system]\nbuild-backend = 'hatchling.build'\n"
            "[tool.hatch.build.targets.wheel]\npackages = ['src/hatch_pkg']\n",
        ),
        ("conventional", "[project]\nname = 'conventional-pkg'\n"),
    ):
        root = tmp_path / project
        _write(root, "pyproject.toml", pyproject)
        package = f"{project}_pkg"
        _write(root, f"src/{package}/__init__.py", "")
        _write(root, f"src/{package}/submodule.py", "def target():\n    return 1\n")
        _write(
            root,
            "tests/test_target.py",
            f"import {package}\nimport {package}.submodule\n\n"
            f"def test_target():\n    assert {package}.submodule.target() == 1\n",
        )

        graph = scan_repository(root, ProjectConfig(git_history_limit=0))
        target = f"symbol:src/{package}/submodule.py::target"
        assert any(
            edge.source == "file:tests/test_target.py"
            and edge.target == target
            and edge.relation == "tests"
            and edge.evidence == "python-symbol-reference"
            for edge in graph.edges
        )


def test_self_scan_resolves_intentatlas_absolute_imports() -> None:
    graph = scan_repository(Path.cwd(), ProjectConfig(git_history_limit=0))
    target = "symbol:src/intentatlas/recommendations.py::recommend_tests"

    assert any(
        edge.source == "file:tests/test_recommendations.py"
        and edge.target == target
        and edge.relation == "tests"
        and edge.evidence == "python-symbol-reference"
        for edge in graph.edges
    )


def test_pyproject_root_and_src_collision_abstains(tmp_path) -> None:
    _write(tmp_path, "pyproject.toml", "[project]\nname = 'ambiguous'\n")
    _write(tmp_path, "pkg/submodule.py", "def target():\n    return 'root'\n")
    _write(tmp_path, "src/pkg/submodule.py", "def target():\n    return 'src'\n")
    _write(
        tmp_path,
        "tests/test_target.py",
        "from pkg.submodule import target\n\ndef test_target():\n    assert target()\n",
    )

    graph = scan_repository(tmp_path, ProjectConfig(git_history_limit=0))

    assert not any(
        edge.source == "file:tests/test_target.py"
        and edge.evidence == "python-symbol-reference"
        and edge.target.endswith("::target")
        for edge in graph.edges
    )
