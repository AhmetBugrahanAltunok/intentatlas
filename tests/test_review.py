from __future__ import annotations

import json

import pytest

from intentatlas.change_analysis import ChangeAnalysis, ChangeAnalysisFile
from intentatlas.change_report import build_change_report
from intentatlas.change_set import ChangeFile, ChangeSet, DiffHunk
from intentatlas.graph import AtlasGraph
from intentatlas.models import Edge, Node
from intentatlas.review import build_review_report, render_review
from intentatlas.test_outcomes import TestOutcome as OutcomeRecord
from intentatlas.test_outcomes import TestOutcomeSet as OutcomeSet


def review_fixture() -> tuple[AtlasGraph, ChangeAnalysis]:
    graph = AtlasGraph()
    graph.extend(
        [
            Node("REQ-21", "requirement", "Review <auth> | safely"),
            Node("ISSUE-21", "issue", "Implement review"),
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
            Edge("REQ-21", "ISSUE-21", "tracked-by", "wikilink"),
            Edge(
                "ISSUE-21",
                "symbol:auth.py::login",
                "implemented-by",
                "wikilink",
            ),
            Edge("file:auth.py", "symbol:auth.py::login", "defines", "python-ast"),
            Edge(
                "file:test_auth.py",
                "symbol:auth.py::login",
                "tests",
                "python-symbol-reference",
            ),
        ],
    )
    change_set = ChangeSet(
        "range",
        "a" * 40,
        "b" * 40,
        (
            ChangeFile("modified", "auth.py", hunks=(DiffHunk("auth.py", 2, 1),)),
            ChangeFile(
                "modified",
                "settings.toml",
                hunks=(DiffHunk("settings.toml", 3, 2),),
            ),
        ),
    )
    analysis = ChangeAnalysis(
        change_set,
        "fallback",
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
            ChangeAnalysisFile(
                "settings.toml",
                "modified",
                "fallback",
                "aligned",
                "low",
                (),
                ("unscanned-file-fallback",),
            ),
        ),
    )
    return graph, analysis


def test_review_report_renders_deterministic_markdown_json_and_sarif() -> None:
    graph, analysis = review_fixture()
    report = build_review_report(build_change_report(graph, analysis))

    assert report.mode == "shadow"
    assert report.base_revision == "a" * 40
    assert report.head_revision == "b" * 40

    markdown = render_review(report, "markdown")
    assert markdown == render_review(report, "markdown")
    assert "# IntentAtlas change review" in markdown
    assert "Review &lt;auth&gt; \\| safely" in markdown
    assert "Targeted plus full suite" in markdown
    assert "settings.toml" in markdown

    json_payload = json.loads(render_review(report, "json"))
    assert json_payload["schema_version"] == 1
    assert json_payload["mode"] == "shadow"
    assert json_payload["change_report"]["schema_version"] == 1

    sarif_text = render_review(report, "sarif")
    assert sarif_text == render_review(report, "sarif")
    sarif = json.loads(sarif_text)
    assert sarif["version"] == "2.1.0"
    run = sarif["runs"][0]
    assert run["automationDetails"]["id"] == "intentatlas/shadow"
    assert [rule["id"] for rule in run["tool"]["driver"]["rules"]] == [
        "IA101",
        "IA200",
        "IA300",
    ]
    assert [result["ruleId"] for result in run["results"]] == [
        "IA101",
        "IA200",
        "IA300",
    ]
    fallback = run["results"][0]
    location = fallback["locations"][0]["physicalLocation"]
    assert location["artifactLocation"]["uri"] == "settings.toml"
    assert location["region"] == {"startLine": 3, "endLine": 4}
    assert "snippet" not in sarif_text
    assert "auth.py" not in fallback["message"]["text"]


def test_review_report_rejects_non_range_input_and_unknown_formats() -> None:
    graph, analysis = review_fixture()
    worktree = ChangeAnalysis(
        ChangeSet("worktree", "a" * 40, None, analysis.change_set.files),
        analysis.state,
        analysis.files,
    )
    with pytest.raises(ValueError, match="revision range"):
        build_review_report(build_change_report(graph, worktree))

    report = build_review_report(build_change_report(graph, analysis))
    with pytest.raises(ValueError, match="Unknown review output format"):
        render_review(report, "html")


@pytest.mark.parametrize("unsafe_path", ("../secret.py", "/secret.py", "C:\\secret.py"))
def test_review_sarif_omits_unsafe_artifact_locations(unsafe_path: str) -> None:
    graph = AtlasGraph()
    change_set = ChangeSet(
        "range",
        "a" * 40,
        "b" * 40,
        (ChangeFile("modified", unsafe_path, hunks=(DiffHunk(unsafe_path, 1, 1),)),),
    )
    analysis = ChangeAnalysis(
        change_set,
        "fallback",
        (
            ChangeAnalysisFile(
                unsafe_path,
                "modified",
                "fallback",
                "aligned",
                "low",
                (),
                ("unscanned-file-fallback",),
            ),
        ),
    )

    report = build_review_report(build_change_report(graph, analysis))
    result = json.loads(render_review(report, "sarif"))["runs"][0]["results"][0]
    assert result["ruleId"] == "IA101"
    assert "locations" not in result


def test_review_sarif_encodes_relative_paths_and_omits_empty_hunk_region() -> None:
    graph = AtlasGraph()
    path = "safe dir/deleted.py"
    change_set = ChangeSet(
        "range",
        "a" * 40,
        "b" * 40,
        (ChangeFile("deleted", path, hunks=(DiffHunk(path, 4, 0),)),),
    )
    analysis = ChangeAnalysis(
        change_set,
        "unknown",
        (
            ChangeAnalysisFile(
                path,
                "deleted",
                "unknown",
                "aligned",
                "none",
                (),
                ("deleted-artifact",),
            ),
        ),
    )

    report = build_review_report(build_change_report(graph, analysis))
    result = json.loads(render_review(report, "sarif"))["runs"][0]["results"][0]
    physical = result["locations"][0]["physicalLocation"]
    assert physical["artifactLocation"]["uri"] == "safe%20dir/deleted.py"
    assert "region" not in physical


def test_review_surfaces_only_aligned_commit_keyed_outcome_comparison() -> None:
    graph, analysis = review_fixture()
    change_report = build_change_report(graph, analysis)
    outcomes = OutcomeSet(
        "b" * 40,
        (
            OutcomeRecord("test_auth.py", "passed", 5),
            OutcomeRecord("test_extra.py", "failed", 7),
        ),
    )
    report = build_review_report(change_report, outcomes)

    assert report.test_outcomes is not None
    assert report.test_outcomes.freshness == "aligned"
    assert report.test_outcomes.predicted_and_executed == ("test_auth.py",)
    assert report.test_outcomes.predicted_not_executed == ()
    assert report.test_outcomes.executed_not_predicted == ("test_extra.py",)

    markdown = render_review(report, "markdown")
    assert "## Commit-keyed test outcomes" in markdown
    assert "Freshness: aligned" in markdown
    assert "`test_auth.py` — passed" in markdown
    assert "`test_extra.py` — failed" in markdown

    json_payload = json.loads(render_review(report, "json"))
    assert json_payload["test_outcomes"]["outcome_commit"] == "b" * 40
    sarif = json.loads(render_review(report, "sarif"))
    assert sarif["runs"][0]["properties"]["test_outcomes"]["freshness"] == "aligned"

    stale = build_review_report(
        change_report,
        OutcomeSet("c" * 40, outcomes.tests),
    )
    assert stale.test_outcomes is not None
    assert stale.test_outcomes.freshness == "stale"
    assert stale.test_outcomes.predicted_and_executed == ()
    assert "Comparison withheld because the outcome commit is stale." in render_review(
        stale, "markdown"
    )
