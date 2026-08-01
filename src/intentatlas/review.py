from __future__ import annotations

import html
import json
from dataclasses import dataclass
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any
from urllib.parse import quote

from . import __version__
from .change_report import ChangeReport
from .test_outcomes import (
    TestOutcomeComparison,
    TestOutcomeSet,
    compare_test_outcomes,
)

REVIEW_SCHEMA_VERSION = 1
SARIF_VERSION = "2.1.0"
MAX_SARIF_RESULTS = 1_000
_ADVISORY = (
    "Shadow review findings are advisory structural evidence. They do not prove that a "
    "requirement is affected, that a test is necessary, or that omitted behavior is safe."
)
_RULES = {
    "IA100": {
        "id": "IA100",
        "name": "unknown-analysis",
        "shortDescription": {"text": "A changed artifact could not be analyzed safely."},
        "helpUri": "https://github.com/AhmetBugrahanAltunok/intentatlas",
    },
    "IA101": {
        "id": "IA101",
        "name": "fallback-analysis",
        "shortDescription": {"text": "A changed artifact has only fallback evidence."},
        "helpUri": "https://github.com/AhmetBugrahanAltunok/intentatlas",
    },
    "IA200": {
        "id": "IA200",
        "name": "possible-requirement-impact",
        "shortDescription": {"text": "A requirement may be affected by the change."},
        "helpUri": "https://github.com/AhmetBugrahanAltunok/intentatlas",
    },
    "IA300": {
        "id": "IA300",
        "name": "full-suite-fallback",
        "shortDescription": {"text": "Incomplete evidence requires a full test fallback."},
        "helpUri": "https://github.com/AhmetBugrahanAltunok/intentatlas",
    },
}


@dataclass(frozen=True, slots=True)
class ReviewReport:
    change_report: ChangeReport
    mode: str = "shadow"
    test_outcomes: TestOutcomeComparison | None = None

    @property
    def base_revision(self) -> str:
        value = self.change_report.analysis.change_set.base_revision
        if value is None:
            raise ValueError("Review report is missing its base revision")
        return value

    @property
    def head_revision(self) -> str:
        value = self.change_report.analysis.change_set.head_revision
        if value is None:
            raise ValueError("Review report is missing its head revision")
        return value

    def to_dict(self) -> dict[str, Any]:
        value = {
            "schema_version": REVIEW_SCHEMA_VERSION,
            "mode": self.mode,
            "advisory": _ADVISORY,
            "base_revision": self.base_revision,
            "head_revision": self.head_revision,
            "change_report": self.change_report.to_dict(),
        }
        if self.test_outcomes is not None:
            value["test_outcomes"] = self.test_outcomes.to_dict()
        return value


def build_review_report(
    change_report: ChangeReport,
    test_outcomes: TestOutcomeSet | None = None,
) -> ReviewReport:
    change_set = change_report.analysis.change_set
    if (
        change_set.scope != "range"
        or change_set.base_revision is None
        or change_set.head_revision is None
    ):
        raise ValueError("Review report requires an explicit revision range")
    comparison = None
    if test_outcomes is not None:
        candidate_paths = tuple(
            item.test.path for item in change_report.tests if item.test.path is not None
        )
        comparison = compare_test_outcomes(
            change_set.head_revision,
            candidate_paths,
            test_outcomes,
        )
    return ReviewReport(change_report, test_outcomes=comparison)


def render_review(report: ReviewReport, output_format: str = "markdown") -> str:
    if output_format == "json":
        value = report.to_dict()
    elif output_format == "sarif":
        value = _sarif(report)
    elif output_format == "markdown":
        return _markdown(report)
    else:
        raise ValueError(f"Unknown review output format: {output_format}")
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def _markdown(report: ReviewReport) -> str:
    change = report.change_report
    lines = [
        "# IntentAtlas change review",
        "",
        f"- Mode: {_markdown_text(report.mode)}",
        f"- Base: `{_markdown_text(report.base_revision)}`",
        f"- Head: `{_markdown_text(report.head_revision)}`",
        f"- Analysis: {_markdown_text(change.analysis.state)}",
        f"- Test strategy: {_markdown_text(_title(change.test_strategy))}",
        "",
        "> " + _markdown_text(_ADVISORY),
        "",
        "## Possible requirement impacts",
        "",
    ]
    if change.requirements:
        for item in change.requirements:
            path = " → ".join(_markdown_text(node_id) for node_id in item.path.nodes)
            lines.extend(
                [
                    f"- **{_markdown_text(item.requirement.label)}** "
                    f"(`{_markdown_text(item.requirement.id)}`) — "
                    f"{_markdown_text(item.confidence)}, {item.score}/100",
                    f"  - Path: {path}",
                    f"  - Evidence: {_markdown_text(', '.join(item.evidence) or 'none')}",
                ]
            )
    else:
        lines.append("- No requirement candidate meets the selected confidence threshold.")
    lines.extend(["", "## Candidate tests", ""])
    if change.tests:
        for item in change.tests:
            label = item.test.path or item.test.label
            lines.extend(
                [
                    f"- **{_markdown_text(label)}** — "
                    f"{_markdown_text(item.confidence)}, {item.score}/100",
                    f"  - Evidence: {_markdown_text(', '.join(item.evidence) or 'none')}",
                ]
            )
    else:
        lines.append("- No bounded test candidate was found.")
    lines.extend(["", "## Commit-keyed test outcomes", ""])
    if report.test_outcomes is None:
        lines.append("- No commit-keyed test outcome sidecar was supplied.")
    else:
        comparison = report.test_outcomes
        lines.extend(
            [
                f"- Outcome commit: `{_markdown_text(comparison.outcome_commit)}`",
                f"- Freshness: {_markdown_text(comparison.freshness)}",
                f"- Policy: `{_markdown_text(comparison.test_set_policy)}`",
                "- Executed outcomes:",
            ]
        )
        if comparison.tests:
            for outcome in comparison.tests:
                duration = (
                    "" if outcome.duration_ms is None else f" ({outcome.duration_ms} ms)"
                )
                lines.append(
                    f"  - `{_markdown_text(outcome.path)}` — "
                    f"{_markdown_text(outcome.status)}{duration}"
                )
        else:
            lines.append("  - No test path was recorded for this execution.")
        if comparison.freshness == "stale":
            lines.append("- Comparison withheld because the outcome commit is stale.")
        else:
            lines.extend(
                [
                    "- Predicted and executed: "
                    + _markdown_paths(comparison.predicted_and_executed),
                    "- Predicted but not executed: "
                    + _markdown_paths(comparison.predicted_not_executed),
                    "- Executed but not predicted: "
                    + _markdown_paths(comparison.executed_not_predicted),
                ]
            )
    lines.extend(["", "## Analysis gaps", ""])
    gaps = tuple(item for item in change.analysis.files if item.state != "analyzed")
    if gaps:
        for item in gaps:
            lines.append(
                f"- `{_markdown_text(item.path)}` — {_markdown_text(item.state)}, "
                f"freshness {_markdown_text(item.freshness)}, confidence "
                f"{_markdown_text(item.confidence)}; "
                f"{_markdown_text(', '.join(item.evidence))}"
            )
    else:
        lines.append("- No structural analysis gap was reported for this range.")
    return "\n".join(lines) + "\n"


def _sarif(report: ReviewReport) -> dict[str, Any]:
    change = report.change_report
    change_files = {item.path: item for item in change.analysis.change_set.files}
    results: list[dict[str, Any]] = []
    for item in change.analysis.files:
        if item.state == "analyzed":
            continue
        rule_id = "IA100" if item.state == "unknown" else "IA101"
        result: dict[str, Any] = {
            "ruleId": rule_id,
            "level": "warning" if item.state == "unknown" else "note",
            "message": {
                "text": (
                    f"Analysis is {item.state} for {item.path} "
                    f"({item.freshness}; {item.confidence} confidence)."
                )
            },
            "properties": {
                "state": item.state,
                "freshness": item.freshness,
                "confidence": item.confidence,
                "evidence": list(item.evidence),
            },
        }
        location = _location(item.path, change_files.get(item.path))
        if location is not None:
            result["locations"] = [location]
        results.append(result)
    for item in change.requirements:
        results.append(
            {
                "ruleId": "IA200",
                "level": "note",
                "message": {
                    "text": (
                        f"Possible requirement impact: {item.requirement.label} "
                        f"[{item.requirement.id}] ({item.confidence}; {item.score}/100)."
                    )
                },
                "properties": {
                    "requirement_id": item.requirement.id,
                    "confidence": item.confidence,
                    "score": item.score,
                    "path": item.path.to_dict(),
                    "evidence": list(item.evidence),
                },
            }
        )
    if "full-suite" in change.test_strategy:
        results.append(
            {
                "ruleId": "IA300",
                "level": "warning",
                "message": {
                    "text": (
                        "Analysis evidence is incomplete; follow the "
                        f"{change.test_strategy} strategy."
                    )
                },
                "properties": {"test_strategy": change.test_strategy},
            }
        )
    results.sort(key=_sarif_result_key)
    if len(results) > MAX_SARIF_RESULTS:
        raise ValueError(f"Review exceeds the {MAX_SARIF_RESULTS}-result SARIF limit")
    used_rules = {str(result["ruleId"]) for result in results}
    candidate_tests = [
        {
            "id": item.test.id,
            "path": item.test.path,
            "score": item.score,
            "confidence": item.confidence,
        }
        for item in change.tests
    ]
    run_properties: dict[str, Any] = {
        "schema_version": REVIEW_SCHEMA_VERSION,
        "mode": report.mode,
        "base_revision": report.base_revision,
        "head_revision": report.head_revision,
        "analysis_state": change.analysis.state,
        "test_strategy": change.test_strategy,
        "candidate_tests": candidate_tests,
        "advisory": _ADVISORY,
    }
    if report.test_outcomes is not None:
        run_properties["test_outcomes"] = report.test_outcomes.to_dict()
    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": SARIF_VERSION,
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "IntentAtlas",
                        "semanticVersion": __version__,
                        "informationUri": (
                            "https://github.com/AhmetBugrahanAltunok/intentatlas"
                        ),
                        "rules": [_RULES[rule_id] for rule_id in sorted(used_rules)],
                    }
                },
                "automationDetails": {"id": "intentatlas/shadow"},
                "invocations": [
                    {
                        "executionSuccessful": True,
                        "properties": {"mode": report.mode, "blocking": False},
                    }
                ],
                "results": results,
                "properties": run_properties,
            }
        ],
    }


def _location(path: str, changed: object) -> dict[str, Any] | None:
    uri = _safe_uri(path)
    if uri is None:
        return None
    physical: dict[str, Any] = {"artifactLocation": {"uri": uri, "uriBaseId": "%SRCROOT%"}}
    hunks = getattr(changed, "hunks", ())
    if hunks and hunks[0].start > 0 and hunks[0].count > 0:
        hunk = hunks[0]
        end = hunk.start + hunk.count - 1
        physical["region"] = {"startLine": hunk.start, "endLine": end}
    return {"physicalLocation": physical}


def _safe_uri(path: str) -> str | None:
    normalized = path.replace("\\", "/")
    pure = PurePosixPath(normalized)
    if (
        not normalized
        or pure.is_absolute()
        or PureWindowsPath(path).is_absolute()
        or ".." in pure.parts
        or any(ord(character) < 32 for character in normalized)
    ):
        return None
    return quote(pure.as_posix(), safe="/-._~")


def _sarif_result_key(result: dict[str, Any]) -> tuple[str, str, str]:
    locations = result.get("locations", [])
    uri = ""
    if locations:
        uri = str(locations[0]["physicalLocation"]["artifactLocation"]["uri"])
    return str(result["ruleId"]), uri, str(result["message"]["text"])


def _markdown_text(value: str) -> str:
    escaped = html.escape(value, quote=False)
    return escaped.replace("\\", "\\\\").replace("|", "\\|").replace("`", "\\`")


def _markdown_paths(paths: tuple[str, ...]) -> str:
    if not paths:
        return "none"
    return ", ".join(f"`{_markdown_text(path)}`" for path in paths)


def _title(value: str) -> str:
    return value.replace("-", " ").capitalize()
