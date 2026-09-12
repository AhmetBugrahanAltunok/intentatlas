from __future__ import annotations

import json
from pathlib import Path

from intentatlas.change_analysis import ChangeAnalysis, ChangeAnalysisFile
from intentatlas.change_report import build_change_report, render_change_report
from intentatlas.change_set import ChangeFile, ChangeSet, DiffHunk
from intentatlas.diagnostic import diagnose_repository, render_diagnostic
from intentatlas.graph import AtlasGraph
from intentatlas.models import Edge, Node


def _task_graph() -> AtlasGraph:
    graph = AtlasGraph()
    graph.extend(
        [
            Node("REQ-1", "requirement", "Authenticate users"),
            Node("ADR-1", "decision", "Use token authentication"),
            Node("ISSUE-1", "issue", "Implement login"),
            Node("REQ-2", "requirement", "Record authentication events"),
            Node("ADR-2", "decision", "Keep an audit trail"),
            Node("ISSUE-2", "issue", "Implement audit logging"),
            Node("file:auth.py", "file", "auth.py", path="auth.py"),
            Node(
                "symbol:auth.py::login",
                "symbol",
                "login",
                path="auth.py",
                metadata={"line": 1, "end_line": 2},
            ),
            Node("file:test_auth.py", "test", "test_auth.py", path="test_auth.py"),
        ],
        [
            Edge("REQ-1", "ADR-1", "drives", "wikilink"),
            Edge("ADR-1", "ISSUE-1", "tracked-by", "wikilink"),
            Edge("ISSUE-1", "symbol:auth.py::login", "implemented-by", "wikilink"),
            Edge("REQ-2", "ADR-2", "drives", "wikilink"),
            Edge("ADR-2", "ISSUE-2", "tracked-by", "wikilink"),
            Edge("ISSUE-2", "file:auth.py", "implemented-by", "wikilink"),
            Edge("file:auth.py", "symbol:auth.py::login", "defines", "python-ast"),
            Edge(
                "file:test_auth.py",
                "symbol:auth.py::login",
                "tests",
                "python-symbol-reference",
            ),
        ],
    )
    return graph


def _analysis(*, state: str = "analyzed", freshness: str = "aligned") -> ChangeAnalysis:
    artifacts = ("symbol:auth.py::login",) if state == "analyzed" else ()
    confidence = "high" if state == "analyzed" else "none"
    evidence = ("validated-symbol-span",) if state == "analyzed" else (
        "revision-worktree-mismatch",
    )
    return ChangeAnalysis(
        ChangeSet(
            "commit",
            "a" * 40,
            "b" * 40,
            (ChangeFile("modified", "auth.py", hunks=(DiffHunk("auth.py", 2, 1),)),),
        ),
        state,
        (
            ChangeAnalysisFile(
                "auth.py",
                "modified",
                state,
                freshness,
                confidence,
                artifacts,
                evidence,
            ),
        ),
    )


def test_walkthrough_01_decide_the_safe_first_command_without_configuration(
    tmp_path: Path,
) -> None:
    (tmp_path / "app.py").write_text("def answer():\n    return 42\n", encoding="utf-8")

    before = tuple(sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*")))
    first = render_diagnostic(diagnose_repository(tmp_path), "json")
    second = render_diagnostic(diagnose_repository(tmp_path), "json")
    payload = json.loads(first)

    assert first == second
    assert payload["read_only"] is True
    assert payload["network_required"] is False
    assert payload["next_safe_command"] == "intentatlas demo --report text"
    assert tuple(sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*"))) == before


def test_walkthrough_02_explain_an_aligned_change_with_recorded_paths() -> None:
    payload = build_change_report(_task_graph(), _analysis()).to_dict()

    assert payload["analysis_state"] == "analyzed"
    assert payload["freshness"] == "aligned"
    assert payload["requirements"][0]["requirement"]["id"] == "REQ-1"
    assert payload["requirements"][0]["path"]["relations"] == [
        "drives",
        "tracked-by",
        "implemented-by",
    ]
    assert payload["tests"][0]["test"]["id"] == "file:test_auth.py"
    assert payload["test_strategy"] == "targeted"


def test_walkthrough_03_interpret_an_omission_without_claiming_no_impact() -> None:
    report = build_change_report(_task_graph(), _analysis())
    payload = report.to_dict()
    text = render_change_report(report, "text", explain=True)

    assert payload["requirement_selection"] == {
        "selected_count": 1,
        "total_candidate_count": 2,
        "filtered_count": 1,
        "limit_omitted_count": 0,
        "omitted_shown_count": 1,
    }
    assert payload["omitted_requirements"][0]["node"]["id"] == "REQ-2"
    assert payload["omitted_requirements"][0]["reason"] == "below-minimum-confidence"
    assert "not proof that an omitted requirement is unaffected" in text


def test_walkthrough_04_choose_the_safe_strategy_for_stale_analysis() -> None:
    payload = build_change_report(
        _task_graph(), _analysis(state="unknown", freshness="stale")
    ).to_dict()

    assert payload["analysis_state"] == "unknown"
    assert payload["freshness"] == "stale"
    assert payload["requirements"] == []
    assert payload["tests"] == []
    assert payload["test_strategy"] == "abstain-and-full-suite"


def test_walkthrough_05_recognize_ambiguity_and_unsupported_scope(tmp_path: Path) -> None:
    for relative in (
        "src/app.py",
        "packages/client/index.ts",
        "packages/server/index.ts",
        "native/lib.rs",
        "package.json",
        "packages/client/package.json",
    ):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}\n", encoding="utf-8")
    (tmp_path / "src/large.py").write_bytes(b"x" * 1_000_001)

    payload = diagnose_repository(tmp_path).to_dict()

    assert payload["ambiguity"]["state"] == "detected"
    assert payload["ambiguity"]["reasons"] == [
        "multiple-project-roots",
        "multiple-source-roots",
    ]
    assert payload["unsupported_languages"] == ["rust"]
    assert payload["repository"]["oversized_supported_file_count"] == 1
    assert payload["read_only"] is True
    assert payload["network_required"] is False
