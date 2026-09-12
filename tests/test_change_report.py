from __future__ import annotations

import json
import shutil
import subprocess

import pytest

import intentatlas.change_report as change_report_module
from intentatlas.change_analysis import ChangeAnalysis, ChangeAnalysisFile
from intentatlas.change_report import (
    build_change_report,
    collect_change_report,
    render_change_report,
)
from intentatlas.change_set import ChangeFile, ChangeSet, DiffHunk, collect_change_set
from intentatlas.config import ProjectConfig
from intentatlas.graph import AtlasGraph
from intentatlas.models import Edge, Node


def report_graph() -> AtlasGraph:
    graph = AtlasGraph()
    graph.extend(
        [
            Node("REQ-9", "requirement", "Authenticate users"),
            Node("ADR-9", "decision", "Token authentication"),
            Node("ISSUE-9", "issue", "Implement login"),
            Node("REQ-18", "requirement", "Audit authentication"),
            Node("ADR-18", "decision", "Audit policy"),
            Node("ISSUE-18", "issue", "Implement audit"),
            Node("file:auth.py", "file", "auth.py", path="auth.py"),
            Node(
                "symbol:auth.py::login",
                "symbol",
                "login",
                path="auth.py",
                metadata={"line": 1, "end_line": 2},
            ),
            Node(
                "symbol:auth.py::audit",
                "symbol",
                "audit",
                path="auth.py",
                metadata={"line": 4, "end_line": 5},
            ),
            Node("file:test_auth.py", "test", "test_auth.py", path="test_auth.py"),
        ],
        [
            Edge("REQ-9", "ADR-9", "drives", "wikilink"),
            Edge("ADR-9", "ISSUE-9", "tracked-by", "wikilink"),
            Edge(
                "ISSUE-9",
                "symbol:auth.py::login",
                "implemented-by",
                "wikilink",
            ),
            Edge("REQ-18", "ADR-18", "drives", "wikilink"),
            Edge("ADR-18", "ISSUE-18", "tracked-by", "wikilink"),
            Edge("ISSUE-18", "file:auth.py", "implemented-by", "wikilink"),
            Edge("file:auth.py", "symbol:auth.py::login", "defines", "python-ast"),
            Edge("file:auth.py", "symbol:auth.py::audit", "defines", "python-ast"),
            Edge(
                "file:test_auth.py",
                "symbol:auth.py::login",
                "tests",
                "python-symbol-reference",
            ),
        ],
    )
    return graph


def exact_analysis() -> ChangeAnalysis:
    change_set = ChangeSet(
        "worktree",
        "a" * 40,
        None,
        (ChangeFile("modified", "auth.py", hunks=(DiffHunk("auth.py", 2, 1),)),),
    )
    return ChangeAnalysis(
        change_set,
        "analyzed",
        (
            ChangeAnalysisFile(
                "auth.py",
                "modified",
                "analyzed",
                "aligned",
                "high",
                ("symbol:auth.py::login",),
                ("validated-symbol-span",),
            ),
        ),
    )


def test_change_report_keeps_file_level_requirements_below_default_threshold() -> None:
    result = build_change_report(report_graph(), exact_analysis())

    assert result.requirement_candidate_count == 2
    assert [(item.requirement.id, item.score, item.confidence) for item in result.requirements] == [
        ("REQ-9", 80, "medium")
    ]
    impact = result.requirements[0]
    assert impact.path.nodes == (
        "REQ-9",
        "ADR-9",
        "ISSUE-9",
        "symbol:auth.py::login",
    )
    assert impact.path.relations == ("drives", "tracked-by", "implemented-by")
    assert [(item.test.id, item.score) for item in result.tests] == [
        ("file:test_auth.py", 80)
    ]
    assert result.test_strategy == "targeted"
    assert result.analysis_coverage_complete is True

    rendered = render_change_report(result, "json")
    assert rendered == render_change_report(result, "json")
    payload = json.loads(rendered)
    assert payload["schema_version"] == 1
    assert payload["lower_confidence_requirement_count"] == 1
    assert payload["scope"] == "worktree"
    assert payload["freshness"] == "aligned"
    assert payload["requirement_selection"] == {
        "selected_count": 1,
        "total_candidate_count": 2,
        "filtered_count": 1,
        "limit_omitted_count": 0,
        "omitted_shown_count": 1,
    }
    assert payload["requirements"][0]["reason"] == "confidence-meets-minimum-threshold"
    assert payload["requirements"][0]["path"]["relations"] == [
        "drives",
        "tracked-by",
        "implemented-by",
    ]
    assert payload["tests"][0]["reasons"]
    assert payload["tests"][0]["paths"][0]["nodes"][-1] == "file:test_auth.py"
    assert payload["omitted_requirements"][0]["node"]["id"] == "REQ-18"
    assert payload["omitted_requirements"][0]["reason"] == "below-minimum-confidence"

    text = render_change_report(result, explain=True)
    assert "Confidence bands: low 0-64; medium 65-84; high 85-100" in text
    assert "Requirement threshold: 1 candidate(s) are below medium" in text
    assert "  Why: The requirement is connected" in text
    assert "  Path: REQ-9 -[drives]-> ADR-9" in text
    assert "  Why: The test directly references" in text
    assert "  Additional signals: 0 (inspect `tests[].reason_details`" in text


def test_change_report_distinguishes_result_limit_omissions() -> None:
    graph = report_graph()
    graph.extend(
        [Node("file:test_auth_alt.py", "test", "test_auth_alt.py", path="test_auth_alt.py")],
        [
            Edge(
                "file:test_auth_alt.py",
                "symbol:auth.py::login",
                "tests",
                "python-symbol-reference",
            )
        ],
    )

    report = build_change_report(graph, exact_analysis(), limit=1)
    payload = report.to_dict()

    assert payload["test_selection"]["selected_count"] == 1
    assert payload["test_selection"]["total_candidate_count"] == 2
    assert payload["test_selection"]["limit_omitted_count"] == 1
    assert payload["omitted_tests"][0]["reason"] == "result-limit"
    assert payload["omitted_tests"][0]["paths"]


def test_change_report_counts_high_fanout_candidates_before_result_limit() -> None:
    graph = report_graph()
    additional_tests = [
        Node(
            f"file:test_auth_{index:03}.py",
            "test",
            f"test_auth_{index:03}.py",
            path=f"test_auth_{index:03}.py",
        )
        for index in range(100)
    ]
    graph.extend(
        additional_tests,
        [
            Edge(
                test.id,
                "symbol:auth.py::login",
                "tests",
                "python-symbol-reference",
            )
            for test in additional_tests
        ],
    )

    report = build_change_report(graph, exact_analysis(), limit=100)
    payload = report.to_dict()

    assert report.test_candidate_count == 101
    assert len(report.tests) == 100
    assert report.test_limit_omitted_count == 1
    assert report.test_candidate_count_complete is True
    assert payload["test_selection"] == {
        "selected_count": 100,
        "total_candidate_count": 101,
        "filtered_count": 0,
        "limit_omitted_count": 1,
        "omitted_shown_count": 1,
    }
    assert payload["omitted_tests"][0]["node"]["id"] == "file:test_auth_099.py"
    assert payload["omitted_tests"][0]["reason"] == "result-limit"


def test_change_report_truncates_artifacts_with_explicit_lower_bound_semantics(
    monkeypatch,
) -> None:
    monkeypatch.setattr(change_report_module, "MAX_REPORT_ARTIFACTS", 1)
    base = exact_analysis()
    analysis = ChangeAnalysis(
        base.change_set,
        "analyzed",
        (
            ChangeAnalysisFile(
                "auth.py",
                "modified",
                "analyzed",
                "aligned",
                "high",
                ("symbol:auth.py::login", "symbol:auth.py::audit"),
                ("validated-symbol-span",),
            ),
        ),
    )

    report = build_change_report(report_graph(), analysis)
    payload = report.to_dict()

    assert report.analysis_coverage_complete is False
    assert report.requirement_candidate_count_complete is False
    assert report.test_candidate_count_complete is False
    assert report.test_strategy == "full-suite-fallback"
    assert payload["analysis_coverage"] == {
        "complete": False,
        "requirement_candidate_count_complete": False,
        "test_candidate_count_complete": False,
        "artifact_selection": {
            "analysis_limit": 1,
            "total_candidate_count": 2,
            "analyzed_count": 1,
            "limit_omitted_count": 1,
            "bounded_selection_complete": False,
        },
        "test_signal_selection": {
            "analysis_limit": 1,
            "total_candidate_count": 1,
            "analyzed_count": 1,
            "limit_omitted_count": 0,
            "bounded_selection_complete": False,
        },
    }
    rendered = render_change_report(report, explain=True)
    assert "1/2 artifacts analyzed; 1 omitted by the 1-artifact limit" in rendered
    assert "Candidate totals include only the analyzed subset and are lower bounds" in rendered


def test_change_report_truncates_file_symbol_signals_without_failing(monkeypatch) -> None:
    monkeypatch.setattr(change_report_module, "MAX_REPORT_ARTIFACTS", 2)
    base = exact_analysis()
    analysis = ChangeAnalysis(
        base.change_set,
        "analyzed",
        (
            ChangeAnalysisFile(
                "auth.py",
                "modified",
                "analyzed",
                "aligned",
                "high",
                ("file:auth.py",),
                ("validated-file-artifact",),
            ),
        ),
    )

    report = build_change_report(report_graph(), analysis, minimum_confidence="low")
    coverage = report.analysis_coverage

    assert coverage.artifact_candidate_count == 1
    assert coverage.artifact_limit_omitted_count == 0
    assert coverage.test_signal_candidate_count == 3
    assert coverage.test_signal_analyzed_count == 2
    assert coverage.test_signal_limit_omitted_count == 1
    assert report.requirement_candidate_count_complete is True
    assert report.test_candidate_count_complete is False
    assert report.analysis_coverage_complete is False
    assert report.test_strategy == "targeted-plus-full-suite"


def test_change_report_requires_full_suite_for_fallback_or_unknown_analysis() -> None:
    change_set = exact_analysis().change_set
    fallback = ChangeAnalysis(
        change_set,
        "fallback",
        (
            ChangeAnalysisFile(
                "auth.py",
                "modified",
                "fallback",
                "aligned",
                "low",
                ("file:auth.py",),
                ("file-level-fallback",),
            ),
        ),
    )
    fallback_report = build_change_report(report_graph(), fallback)
    assert fallback_report.requirements == ()
    assert fallback_report.requirement_candidate_count == 2
    assert fallback_report.test_strategy == "targeted-plus-full-suite"
    assert fallback_report.analysis_coverage_complete is False

    unknown = ChangeAnalysis(
        change_set,
        "unknown",
        (
            ChangeAnalysisFile(
                "auth.py",
                "modified",
                "unknown",
                "stale",
                "none",
                (),
                ("revision-worktree-mismatch",),
            ),
        ),
    )
    unknown_report = build_change_report(report_graph(), unknown)
    assert unknown_report.requirements == ()
    assert unknown_report.tests == ()
    assert unknown_report.test_strategy == "abstain-and-full-suite"
    assert unknown_report.analysis_coverage_complete is False
    assert unknown_report.revision_action == (
        "Use a clean checkout whose HEAD exactly matches "
        f"{change_set.base_revision}, then run intentatlas changes --commit HEAD --report there."
    )
    assert unknown_report.to_dict()["revision_action"] == unknown_report.revision_action
    rendered = render_change_report(unknown_report, explain=True)
    assert "Revision action: Use a clean checkout" in rendered
    assert "Analysis limitations: 1 file" in rendered
    assert "auth.py: unknown; freshness stale" in rendered
    assert "evidence revision-worktree-mismatch" in rendered


def test_change_report_abstains_if_any_changed_artifact_is_unknown() -> None:
    change_set = exact_analysis().change_set
    mixed = ChangeAnalysis(
        change_set,
        "unknown",
        (
            exact_analysis().files[0],
            ChangeAnalysisFile(
                "missing.py",
                "deleted",
                "unknown",
                "unknown",
                "none",
                (),
                ("artifact-unavailable",),
            ),
        ),
    )

    report = build_change_report(report_graph(), mixed)
    assert report.requirements == ()
    assert report.tests == ()
    assert report.test_strategy == "abstain-and-full-suite"

    empty = build_change_report(
        report_graph(),
        ChangeAnalysis(ChangeSet("worktree", "a" * 40, None, ()), "unknown", ()),
    )
    assert empty.test_strategy == "no-changes"
    assert empty.analysis_coverage_complete is True


@pytest.mark.skipif(shutil.which("git") is None, reason="Git is required")
def test_staged_same_file_requirement_holdout_preserves_symbol_precision(tmp_path) -> None:
    def git(*arguments: str) -> None:
        subprocess.run(["git", *arguments], cwd=tmp_path, check=True, capture_output=True)

    git("init", "-q")
    git("config", "user.name", "Change Report Test")
    git("config", "user.email", "change-report@example.invalid")
    (tmp_path / "auth.py").write_text(
        "def login(token):\n    return token == 'old'\n\ndef audit(event):\n    return event\n",
        encoding="utf-8",
    )
    (tmp_path / "test_auth.py").write_text(
        "from auth import login\n\ndef test_login():\n    assert login('old')\n",
        encoding="utf-8",
    )
    vault = tmp_path / "atlas"
    for area in ("Requirements", "Decisions", "Issues"):
        (vault / area).mkdir(parents=True, exist_ok=True)
    notes = {
        "Requirements/REQ-9.md": (
            "---\nid: REQ-9\ntype: requirement\n---\n# Login\n\n"
            "- drives:: [[ADR-9]]\n"
        ),
        "Decisions/ADR-9.md": (
            "---\nid: ADR-9\ntype: decision\n---\n# Login decision\n\n"
            "- tracked-by:: [[ISSUE-9]]\n"
        ),
        "Issues/ISSUE-9.md": (
            "---\nid: ISSUE-9\ntype: issue\n---\n# Login work\n\n"
            "- implemented-by:: [[symbol:auth.py::login]]\n"
        ),
        "Requirements/REQ-18.md": (
            "---\nid: REQ-18\ntype: requirement\n---\n# Audit\n\n"
            "- drives:: [[ADR-18]]\n"
        ),
        "Decisions/ADR-18.md": (
            "---\nid: ADR-18\ntype: decision\n---\n# Audit decision\n\n"
            "- tracked-by:: [[ISSUE-18]]\n"
        ),
        "Issues/ISSUE-18.md": (
            "---\nid: ISSUE-18\ntype: issue\n---\n# Audit work\n\n"
            "- implemented-by:: [[file:auth.py]]\n"
        ),
    }
    for path, content in notes.items():
        (vault / path).write_text(content, encoding="utf-8")
    git("add", ".")
    git("commit", "-qm", "baseline")

    (tmp_path / "auth.py").write_text(
        "def login(token):\n    return token == 'new'\n\ndef audit(event):\n    return event\n",
        encoding="utf-8",
    )
    git("add", "auth.py")

    report = collect_change_report(
        tmp_path,
        collect_change_set(tmp_path, scope="staged"),
        ProjectConfig(git_history_limit=0),
    )

    assert report.analysis.state == "analyzed"
    assert [item.requirement.id for item in report.requirements] == ["REQ-9"]
    assert report.requirement_candidate_count == 2
    assert [(item.test.path, item.score) for item in report.tests] == [
        ("test_auth.py", 80)
    ]
    assert report.test_strategy == "targeted"


def test_default_text_leads_with_the_answer_not_the_machinery() -> None:
    text = render_change_report(build_change_report(report_graph(), exact_analysis()))
    lines = text.splitlines()

    assert lines[0] == "Changed: login (auth.py)"
    assert lines[1] == "Run 1 test:"
    assert "  test_auth.py   [medium confidence]" in lines
    assert "    The test directly references an exactly modified symbol." in lines
    assert "    login -> test_auth.py" in lines
    assert "  REQ-9   [medium confidence]" in lines


def test_default_text_hides_the_machinery_without_hiding_the_boundary() -> None:
    text = render_change_report(build_change_report(report_graph(), exact_analysis()))

    for machinery in (
        "Change report:",
        "Revision:",
        "Analysis state:",
        "Confidence bands:",
        "Analysis coverage:",
        "omission details shown",
        "Requirement impacts:",
        "80/100",
        "symbol:auth.py::login",
        "file:test_auth.py",
        "-[tested-by]->",
    ):
        assert machinery not in text, machinery

    # The advisory is wrapped for the terminal, so compare it as prose.
    unwrapped = " ".join(text.split())
    assert "not proof that an omitted requirement is unaffected" in unwrapped
    assert "1 weaker candidate not shown at medium confidence." in unwrapped
    assert "Full detail: --explain    Machine-readable: --format json" in text


def test_default_text_wraps_long_prose_for_a_terminal() -> None:
    text = render_change_report(build_change_report(report_graph(), exact_analysis()))

    assert all(len(line) <= 100 for line in text.splitlines())


def test_explain_preserves_the_established_detailed_rendering() -> None:
    report = build_change_report(report_graph(), exact_analysis())
    text = render_change_report(report, explain=True)

    assert text.startswith("Change report: ")
    assert "Confidence bands: low 0-64; medium 65-84; high 85-100" in text
    assert "  Path: symbol:auth.py::login -[tested-by]-> file:test_auth.py" in text
    assert text.rstrip().endswith(change_report_module._ADVISORY)


def test_json_is_unchanged_by_the_plain_default() -> None:
    report = build_change_report(report_graph(), exact_analysis())

    assert render_change_report(report, "json") == render_change_report(
        report, "json", explain=True
    )
