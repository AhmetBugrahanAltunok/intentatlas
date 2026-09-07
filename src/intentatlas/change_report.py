from __future__ import annotations

import json
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .change_analysis import ChangeAnalysis, _analyze_change_set_with_graph
from .change_set import ChangeSet
from .confidence import CONFIDENCE_RANK, LOW_CONFIDENCE_GUIDANCE, confidence_for_score
from .config import ProjectConfig
from .graph import AtlasGraph
from .models import Node
from .recommendations import _recommendation_candidates
from .scanner import scan_repository

CHANGE_REPORT_SCHEMA_VERSION = 1
MAX_REPORT_RESULTS = 100
MAX_REPORT_ARTIFACTS = 200
MAX_REPORT_TEST_CANDIDATES = 10_000
MAX_REPORT_ANALYSIS_LIMITATIONS = 20
MAX_REQUIREMENT_VISITS = 1_000
MAX_REQUIREMENT_DEPTH = 5
_INTENT_RELATIONS = {"defines", "implemented-by", "tracked-by", "drives"}
_ADVISORY = (
    "Impact and test recommendations are bounded structural evidence, not proof that an "
    "omitted requirement is unaffected or that a suggested test is sufficient."
)


@dataclass(frozen=True, slots=True)
class RequirementImpactPath:
    nodes: tuple[str, ...]
    relations: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.nodes or len(self.relations) != len(self.nodes) - 1:
            raise ValueError("Requirement impact path must connect every adjacent node")

    def to_dict(self) -> dict[str, list[str]]:
        return {"nodes": list(self.nodes), "relations": list(self.relations)}


@dataclass(frozen=True, slots=True)
class ReportReason:
    signal: str
    score: int
    summary: str
    path: RequirementImpactPath
    evidence: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "signal": self.signal,
            "score": self.score,
            "summary": self.summary,
            "path": self.path.to_dict(),
            "evidence": list(self.evidence),
        }


@dataclass(frozen=True, slots=True)
class RequirementImpact:
    requirement: Node
    score: int
    confidence: str
    source_artifact_id: str
    path: RequirementImpactPath
    evidence: tuple[str, ...]

    @property
    def primary_reason(self) -> ReportReason:
        return ReportReason(
            "requirement-impact",
            self.score,
            "The requirement is connected to an analyzed changed artifact.",
            self.path,
            self.evidence,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "requirement": self.requirement.to_dict(),
            "score": self.score,
            "confidence": self.confidence,
            "reason": "confidence-meets-minimum-threshold",
            "source_artifact_id": self.source_artifact_id,
            "path": self.path.to_dict(),
            "evidence": list(self.evidence),
            "primary_reason": self.primary_reason.to_dict(),
            "reason_details": [self.primary_reason.to_dict()],
        }


@dataclass(frozen=True, slots=True)
class ChangeReportTest:
    test: Node
    score: int
    confidence: str
    artifact_ids: tuple[str, ...]
    reason_details: tuple[ReportReason, ...]

    def __post_init__(self) -> None:
        if not self.reason_details or self.reason_details[0].score != self.score:
            raise ValueError("Primary test reason must produce the final score")

    @property
    def primary_reason(self) -> ReportReason:
        return self.reason_details[0]

    @property
    def evidence(self) -> tuple[str, ...]:
        return tuple(
            sorted({value for reason in self.reason_details for value in reason.evidence})
        )

    @property
    def reasons(self) -> tuple[str, ...]:
        return tuple(sorted({reason.summary for reason in self.reason_details}))

    @property
    def paths(self) -> tuple[RequirementImpactPath, ...]:
        return tuple(
            sorted(
                {reason.path for reason in self.reason_details},
                key=lambda path: (path.nodes, path.relations),
            )
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "test": self.test.to_dict(),
            "score": self.score,
            "confidence": self.confidence,
            "artifact_ids": list(self.artifact_ids),
            "evidence": list(self.evidence),
            "reasons": list(self.reasons),
            "paths": [path.to_dict() for path in self.paths],
            "primary_reason": self.primary_reason.to_dict(),
            "reason_details": [reason.to_dict() for reason in self.reason_details],
        }


@dataclass(frozen=True, slots=True)
class OmittedCandidate:
    candidate_type: str
    node: Node
    score: int
    confidence: str
    selection_reason: str
    reason_details: tuple[ReportReason, ...]

    @property
    def reason(self) -> str:
        return self.selection_reason

    @property
    def primary_reason(self) -> ReportReason:
        return self.reason_details[0]

    @property
    def evidence(self) -> tuple[str, ...]:
        return tuple(
            sorted({value for reason in self.reason_details for value in reason.evidence})
        )

    @property
    def paths(self) -> tuple[RequirementImpactPath, ...]:
        return tuple(
            sorted(
                {reason.path for reason in self.reason_details},
                key=lambda path: (path.nodes, path.relations),
            )
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_type": self.candidate_type,
            "node": self.node.to_dict(),
            "score": self.score,
            "confidence": self.confidence,
            "reason": self.selection_reason,
            "selection_reason": self.selection_reason,
            "evidence": list(self.evidence),
            "paths": [path.to_dict() for path in self.paths],
            "primary_reason": self.primary_reason.to_dict(),
            "reason_details": [reason.to_dict() for reason in self.reason_details],
        }


@dataclass(frozen=True, slots=True)
class ReportAnalysisCoverage:
    artifact_limit: int
    artifact_candidate_count: int
    artifact_analyzed_count: int
    test_signal_limit: int
    test_signal_candidate_count: int
    test_signal_analyzed_count: int

    @property
    def artifact_limit_omitted_count(self) -> int:
        return self.artifact_candidate_count - self.artifact_analyzed_count

    @property
    def test_signal_limit_omitted_count(self) -> int:
        return self.test_signal_candidate_count - self.test_signal_analyzed_count

    @property
    def artifact_selection_complete(self) -> bool:
        return self.artifact_limit_omitted_count == 0

    @property
    def test_signal_selection_complete(self) -> bool:
        return (
            self.artifact_selection_complete
            and self.test_signal_limit_omitted_count == 0
        )

    def to_dict(
        self,
        *,
        complete: bool,
        requirement_candidate_count_complete: bool,
        test_candidate_count_complete: bool,
    ) -> dict[str, Any]:
        return {
            "complete": complete,
            "requirement_candidate_count_complete": (
                requirement_candidate_count_complete
            ),
            "test_candidate_count_complete": test_candidate_count_complete,
            "artifact_selection": {
                "analysis_limit": self.artifact_limit,
                "total_candidate_count": self.artifact_candidate_count,
                "analyzed_count": self.artifact_analyzed_count,
                "limit_omitted_count": self.artifact_limit_omitted_count,
                "bounded_selection_complete": self.artifact_selection_complete,
            },
            "test_signal_selection": {
                "analysis_limit": self.test_signal_limit,
                "total_candidate_count": self.test_signal_candidate_count,
                "analyzed_count": self.test_signal_analyzed_count,
                "limit_omitted_count": self.test_signal_limit_omitted_count,
                "bounded_selection_complete": self.test_signal_selection_complete,
            },
        }


_EMPTY_ANALYSIS_COVERAGE = ReportAnalysisCoverage(
    MAX_REPORT_ARTIFACTS,
    0,
    0,
    MAX_REPORT_ARTIFACTS,
    0,
    0,
)


@dataclass(frozen=True, slots=True)
class ChangeReport:
    analysis: ChangeAnalysis
    freshness: str
    minimum_confidence: str
    requirement_candidate_count: int
    requirements: tuple[RequirementImpact, ...]
    requirement_filtered_count: int
    requirement_limit_omitted_count: int
    omitted_requirements: tuple[OmittedCandidate, ...]
    test_candidate_count: int
    tests: tuple[ChangeReportTest, ...]
    test_filtered_count: int
    test_limit_omitted_count: int
    omitted_tests: tuple[OmittedCandidate, ...]
    test_strategy: str
    analysis_coverage_complete: bool
    analysis_coverage: ReportAnalysisCoverage = _EMPTY_ANALYSIS_COVERAGE

    @property
    def requirement_candidate_count_complete(self) -> bool:
        source_analysis_available = self.analysis.state != "unknown" or not self.analysis.files
        return (
            source_analysis_available
            and self.analysis_coverage.artifact_selection_complete
        )

    @property
    def test_candidate_count_complete(self) -> bool:
        source_analysis_available = self.analysis.state != "unknown" or not self.analysis.files
        return (
            source_analysis_available
            and self.analysis_coverage.test_signal_selection_complete
        )

    @property
    def revision_action(self) -> str | None:
        if self.freshness != "stale":
            return None
        revision = (
            self.analysis.change_set.head_revision
            or self.analysis.change_set.base_revision
        )
        if revision is None:
            return None
        return (
            "Use a clean checkout whose HEAD exactly matches "
            f"{revision}, then run intentatlas changes --commit HEAD --report there."
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": CHANGE_REPORT_SCHEMA_VERSION,
            "advisory": _ADVISORY,
            "scope": self.analysis.change_set.scope,
            "base_revision": self.analysis.change_set.base_revision,
            "head_revision": self.analysis.change_set.head_revision,
            "minimum_confidence": self.minimum_confidence,
            "analysis_state": self.analysis.state,
            "freshness": self.freshness,
            "analysis_coverage_complete": self.analysis_coverage_complete,
            "analysis_coverage": self.analysis_coverage.to_dict(
                complete=self.analysis_coverage_complete,
                requirement_candidate_count_complete=(
                    self.requirement_candidate_count_complete
                ),
                test_candidate_count_complete=self.test_candidate_count_complete,
            ),
            "test_strategy": self.test_strategy,
            "revision_action": self.revision_action,
            "requirement_candidate_count": self.requirement_candidate_count,
            "lower_confidence_requirement_count": (
                self.requirement_candidate_count - len(self.requirements)
            ),
            "requirement_selection": {
                "selected_count": len(self.requirements),
                "total_candidate_count": self.requirement_candidate_count,
                "filtered_count": self.requirement_filtered_count,
                "limit_omitted_count": self.requirement_limit_omitted_count,
                "omitted_shown_count": len(self.omitted_requirements),
            },
            "requirements": [item.to_dict() for item in self.requirements],
            "omitted_requirements": [
                item.to_dict() for item in self.omitted_requirements
            ],
            "test_candidate_count": self.test_candidate_count,
            "test_selection": {
                "selected_count": len(self.tests),
                "total_candidate_count": self.test_candidate_count,
                "filtered_count": self.test_filtered_count,
                "limit_omitted_count": self.test_limit_omitted_count,
                "omitted_shown_count": len(self.omitted_tests),
            },
            "tests": [item.to_dict() for item in self.tests],
            "omitted_tests": [item.to_dict() for item in self.omitted_tests],
            "analysis": self.analysis.to_dict(),
        }


def collect_change_report(
    root: Path,
    change_set: ChangeSet,
    config: ProjectConfig | None = None,
    *,
    minimum_confidence: str = "medium",
    limit: int = 20,
) -> ChangeReport:
    """Refresh the graph once, align the change set, and build its report."""

    _graph, report = collect_change_report_context(
        root,
        change_set,
        config,
        minimum_confidence=minimum_confidence,
        limit=limit,
    )
    return report


def collect_change_report_context(
    root: Path,
    change_set: ChangeSet,
    config: ProjectConfig | None = None,
    *,
    minimum_confidence: str = "medium",
    limit: int = 20,
) -> tuple[AtlasGraph, ChangeReport]:
    """Return the single fresh graph and report used by interactive presentation."""

    root = root.resolve()
    active_config = config or ProjectConfig.load(root)
    graph = scan_repository(root, active_config)
    analysis = _analyze_change_set_with_graph(root, change_set, graph, active_config)
    report = build_change_report(
        graph,
        analysis,
        minimum_confidence=minimum_confidence,
        limit=limit,
    )
    return graph, report


def build_change_report(
    graph: AtlasGraph,
    analysis: ChangeAnalysis,
    *,
    minimum_confidence: str = "medium",
    limit: int = 20,
) -> ChangeReport:
    """Build a deterministic, uncertainty-aware report from change artifacts."""

    if minimum_confidence not in CONFIDENCE_RANK:
        raise ValueError(f"Unknown minimum confidence: {minimum_confidence}")
    if isinstance(limit, bool) or limit < 1 or limit > MAX_REPORT_RESULTS:
        raise ValueError(f"Report limit must be between 1 and {MAX_REPORT_RESULTS}")

    artifact_candidates = tuple(
        sorted(
            {
                artifact_id
                for item in analysis.files
                if item.state != "unknown"
                for artifact_id in item.artifact_ids
                if artifact_id in graph.nodes
            }
        )
    )
    if analysis.state == "unknown":
        artifact_candidates = ()
    artifact_ids = artifact_candidates[:MAX_REPORT_ARTIFACTS]

    requirement_candidates = _requirement_impacts(graph, analysis, artifact_ids)
    minimum_rank = CONFIDENCE_RANK[minimum_confidence]
    eligible_requirements = tuple(
        item
        for item in requirement_candidates
        if CONFIDENCE_RANK[item.confidence] >= minimum_rank
    )
    filtered_requirements = tuple(
        item
        for item in requirement_candidates
        if CONFIDENCE_RANK[item.confidence] < minimum_rank
    )
    requirements = eligible_requirements[:limit]
    limit_omitted_requirements = eligible_requirements[limit:]
    test_analysis = _test_recommendations(graph, artifact_ids)
    test_candidates = test_analysis.candidates
    eligible_tests = tuple(
        item
        for item in test_candidates
        if CONFIDENCE_RANK[item.confidence] >= minimum_rank
    )
    filtered_tests = tuple(
        item
        for item in test_candidates
        if CONFIDENCE_RANK[item.confidence] < minimum_rank
    )
    tests = eligible_tests[:limit]
    limit_omitted_tests = eligible_tests[limit:]

    analysis_coverage = ReportAnalysisCoverage(
        MAX_REPORT_ARTIFACTS,
        len(artifact_candidates),
        len(artifact_ids),
        MAX_REPORT_ARTIFACTS,
        test_analysis.signal_candidate_count,
        test_analysis.signal_analyzed_count,
    )
    bounded_selection_complete = analysis_coverage.test_signal_selection_complete
    coverage_complete = (
        analysis.state == "analyzed" or not analysis.files
    ) and bounded_selection_complete
    if not analysis.files:
        strategy = "no-changes"
    elif analysis.state == "unknown":
        strategy = "abstain-and-full-suite"
    elif (analysis.state == "fallback" or not bounded_selection_complete) and tests:
        strategy = "targeted-plus-full-suite"
    elif analysis.state == "fallback" or not bounded_selection_complete:
        strategy = "full-suite-fallback"
    elif tests:
        strategy = "targeted"
    else:
        strategy = "no-targets-found"

    return ChangeReport(
        analysis,
        _aggregate_freshness(analysis),
        minimum_confidence,
        len(requirement_candidates),
        requirements,
        len(filtered_requirements),
        len(limit_omitted_requirements),
        tuple(
            [
                _omitted_requirement(item, "below-minimum-confidence")
                for item in filtered_requirements
            ]
            + [
                _omitted_requirement(item, "result-limit")
                for item in limit_omitted_requirements
            ]
        )[:limit],
        len(test_candidates),
        tests,
        len(filtered_tests),
        len(limit_omitted_tests),
        tuple(
            [
                _omitted_test(item, "below-minimum-confidence")
                for item in filtered_tests
            ]
            + [_omitted_test(item, "result-limit") for item in limit_omitted_tests]
        )[:limit],
        strategy,
        coverage_complete,
        analysis_coverage,
    )


def render_change_report(report: ChangeReport, output_format: str = "text") -> str:
    if output_format == "json":
        return json.dumps(report.to_dict(), indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if output_format != "text":
        raise ValueError(f"Unknown change-report output format: {output_format}")

    lines = [
        f"Change report: {report.analysis.change_set.scope}",
        (
            "Revision: "
            f"base {report.analysis.change_set.base_revision or 'n/a'}; "
            f"head {report.analysis.change_set.head_revision or 'worktree'}"
        ),
        f"Analysis state: {report.analysis.state}; freshness {report.freshness}",
        f"Minimum confidence: {report.minimum_confidence}",
        "Confidence bands: low 0-64; medium 65-84; high 85-100",
        f"Test strategy: {report.test_strategy}",
        (
            "Analysis coverage: "
            f"{report.analysis_coverage.artifact_analyzed_count}/"
            f"{report.analysis_coverage.artifact_candidate_count} artifacts analyzed; "
            f"{report.analysis_coverage.artifact_limit_omitted_count} omitted by the "
            f"{report.analysis_coverage.artifact_limit}-artifact limit; "
            f"{report.analysis_coverage.test_signal_analyzed_count}/"
            f"{report.analysis_coverage.test_signal_candidate_count} test signals analyzed; "
            f"{report.analysis_coverage.test_signal_limit_omitted_count} omitted by the "
            f"{report.analysis_coverage.test_signal_limit}-signal limit"
        ),
        (
            "Requirement impacts: "
            f"{len(report.requirements)} selected / "
            f"{report.requirement_candidate_count} candidates; "
            f"{report.requirement_filtered_count} filtered; "
            f"{report.requirement_limit_omitted_count} omitted by limit; "
            f"{len(report.omitted_requirements)}/"
            f"{report.requirement_filtered_count + report.requirement_limit_omitted_count} "
            "omission details shown"
        ),
    ]
    if (
        not report.requirement_candidate_count_complete
        or not report.test_candidate_count_complete
    ):
        lines.append(
            "Coverage note: Candidate totals include only the analyzed subset and are lower "
            "bounds; omitted or unavailable artifacts and signals were not classified."
        )
    if report.minimum_confidence == "low":
        lines.append(f"Threshold note: {LOW_CONFIDENCE_GUIDANCE}")
    elif report.requirement_filtered_count:
        lines.append(
            "Requirement threshold: "
            f"{report.requirement_filtered_count} candidate(s) are below "
            f"{report.minimum_confidence}. Use `--minimum-confidence low` only to inspect "
            "weaker exploratory evidence; it is not stronger proof."
        )
    if report.revision_action is not None:
        lines.append(f"Revision action: {report.revision_action}")
    limitations = tuple(
        item
        for item in report.analysis.files
        if item.state != "analyzed" or item.freshness != "aligned"
    )
    if limitations:
        shown = limitations[:MAX_REPORT_ANALYSIS_LIMITATIONS]
        noun = "file" if len(limitations) == 1 else "files"
        lines.append(f"Analysis limitations: {len(limitations)} {noun}")
        for item in shown:
            lines.append(
                f"- {item.path}: {item.state}; freshness {item.freshness}; "
                f"confidence {item.confidence}; "
                f"evidence {', '.join(item.evidence) or 'none'}"
            )
        if len(limitations) > len(shown):
            lines.append(
                f"- {len(limitations) - len(shown)} additional limitation(s) omitted"
            )
    for requirement_item in report.requirements:
        primary = requirement_item.primary_reason
        lines.extend(
            [
                f"- {requirement_item.requirement.id}: {requirement_item.score}/100 "
                f"({requirement_item.confidence})",
                f"  Why: {primary.summary}",
                f"  Path: {_path_text(requirement_item.path)}",
                f"  Evidence: {', '.join(requirement_item.evidence) or 'none'}",
            ]
        )
    if report.omitted_requirements:
        lines.append("Omitted requirement candidates:")
        lines.extend(_omission_text(item) for item in report.omitted_requirements)
    lines.append(
        f"Recommended tests: {len(report.tests)} selected / "
        f"{report.test_candidate_count} candidates; {report.test_filtered_count} filtered; "
        f"{report.test_limit_omitted_count} omitted by limit; "
        f"{len(report.omitted_tests)}/"
        f"{report.test_filtered_count + report.test_limit_omitted_count} "
        "omission details shown"
    )
    for test_item in report.tests:
        primary = test_item.primary_reason
        additional = len(test_item.reason_details) - 1
        lines.extend(
            [
                f"- {test_item.test.id}: {test_item.score}/100 ({test_item.confidence}); "
                f"selected from {len(test_item.artifact_ids)} changed artifacts",
                f"  Why: {primary.summary} ({primary.signal}, {primary.score}/100)",
                f"  Path: {_path_text(primary.path)}",
                f"  Evidence: {', '.join(primary.evidence) or 'none'}",
                "  Additional signals: "
                f"{additional} (inspect `tests[].reason_details` in `--format json`)",
            ]
        )
    if report.omitted_tests:
        lines.append("Omitted test candidates:")
        lines.extend(_omission_text(item) for item in report.omitted_tests)
    lines.append(f"Advisory: {_ADVISORY}")
    return "\n".join(lines) + "\n"


def _requirement_impacts(
    graph: AtlasGraph,
    analysis: ChangeAnalysis,
    artifact_ids: tuple[str, ...],
) -> tuple[RequirementImpact, ...]:
    evidence_by_artifact = {
        artifact_id: item.evidence
        for item in analysis.files
        for artifact_id in item.artifact_ids
    }
    best: dict[str, RequirementImpact] = {}
    visits = 0
    for artifact_id in artifact_ids:
        artifact = graph.nodes[artifact_id]
        initially_degraded = artifact.kind == "file"
        seeds: list[
            tuple[str, tuple[str, ...], tuple[str, ...], bool, tuple[str, ...]]
        ] = [(artifact_id, (artifact_id,), (), initially_degraded, ())]
        if artifact.kind == "file":
            seeds.extend(
                (edge.target, (edge.target,), (), True, (edge.evidence,))
                for edge in graph.index.outgoing(artifact_id, "defines")
                if edge.target in graph.nodes
            )
        queue: deque[
            tuple[str, tuple[str, ...], tuple[str, ...], bool, tuple[str, ...]]
        ] = deque(seeds)
        seen = {(node_id, degraded) for node_id, _nodes, _relations, degraded, _evidence in seeds}
        while queue:
            node_id, reverse_nodes, reverse_relations, degraded, edge_evidence = queue.popleft()
            depth = len(reverse_relations)
            node = graph.nodes[node_id]
            if node.kind == "requirement":
                score = _requirement_score(depth, degraded)
                impact = RequirementImpact(
                    node,
                    score,
                    confidence_for_score(score),
                    artifact_id,
                    RequirementImpactPath(
                        tuple(reversed(reverse_nodes)),
                        tuple(reversed(reverse_relations)),
                    ),
                    tuple(
                        dict.fromkeys(
                            (*evidence_by_artifact.get(artifact_id, ()), *edge_evidence)
                        )
                    ),
                )
                current = best.get(node.id)
                if current is None or _impact_sort_key(impact) < _impact_sort_key(current):
                    best[node.id] = impact
                continue
            if depth >= MAX_REQUIREMENT_DEPTH:
                continue
            for edge in graph.index.incoming(node_id):
                if edge.relation not in _INTENT_RELATIONS or edge.source not in graph.nodes:
                    continue
                next_degraded = degraded or edge.relation == "defines"
                state = (edge.source, next_degraded)
                if state in seen:
                    continue
                visits += 1
                if visits > MAX_REQUIREMENT_VISITS:
                    raise ValueError(
                        "Change report exceeds the bounded requirement traversal limit"
                    )
                seen.add(state)
                queue.append(
                    (
                        edge.source,
                        (*reverse_nodes, edge.source),
                        (*reverse_relations, edge.relation),
                        next_degraded,
                        (*edge_evidence, edge.evidence),
                    )
                )
    return tuple(sorted(best.values(), key=_impact_sort_key))


def _requirement_score(depth: int, degraded: bool) -> int:
    if degraded:
        return max(1, 60 - max(depth - 1, 0) * 3)
    return max(1, 95 - depth * 5) if depth else 100


def _impact_sort_key(item: RequirementImpact) -> tuple[object, ...]:
    return (-item.score, item.requirement.id, item.source_artifact_id, item.path.nodes)


@dataclass(frozen=True, slots=True)
class _TestRecommendationAnalysis:
    candidates: tuple[ChangeReportTest, ...]
    signal_candidate_count: int
    signal_analyzed_count: int


def _test_recommendations(
    graph: AtlasGraph, artifact_ids: tuple[str, ...]
) -> _TestRecommendationAnalysis:
    aggregated: dict[
        str,
        tuple[
            Node,
            set[str],
            set[ReportReason],
        ],
    ] = {}
    signals: list[tuple[str, str, bool]] = []
    signal_candidate_count = 0
    for artifact_id in artifact_ids:
        target = graph.nodes[artifact_id]
        if target.kind not in {"commit", "file", "symbol", "test"}:
            continue
        targets = [(artifact_id, False)]
        if target.kind == "file":
            expanded = [
                (edge.target, True)
                for edge in graph.index.outgoing(artifact_id, "defines")
                if edge.target in graph.nodes and graph.nodes[edge.target].kind == "symbol"
            ]
            targets.extend(expanded)
        signal_candidate_count += len(targets)
        available = max(0, MAX_REPORT_ARTIFACTS - len(signals))
        signals.extend(
            (artifact_id, recommendation_target, file_fallback)
            for recommendation_target, file_fallback in targets[:available]
        )
    for artifact_id, recommendation_target, file_fallback in signals:
        _target, recommendations = _recommendation_candidates(
            graph, recommendation_target
        )
        for recommendation in recommendations:
            reason_details = {
                ReportReason(
                    (
                        f"file-fallback-{reason.signal}"
                        if file_fallback
                        else reason.signal
                    ),
                    min(reason.score, 65) if file_fallback else reason.score,
                    (
                        "File-level fallback: the changed file contains the ranked symbol, "
                        "but the change was not proven exact to that symbol. " + reason.summary
                        if file_fallback
                        else reason.summary
                    ),
                    RequirementImpactPath(reason.path.nodes, reason.path.relations),
                    tuple(
                        dict.fromkeys(
                            (
                                *reason.evidence,
                                *(("file-level-fallback",) if file_fallback else ()),
                            )
                        )
                    ),
                )
                for reason in recommendation.reasons
            }
            current = aggregated.get(recommendation.test.id)
            if current is None:
                aggregated[recommendation.test.id] = (
                    recommendation.test,
                    {artifact_id},
                    reason_details,
                )
                if len(aggregated) > MAX_REPORT_TEST_CANDIDATES:
                    raise ValueError(
                        "Change report exceeds the bounded test-candidate limit"
                    )
                continue
            (
                node,
                sources,
                combined_reason_details,
            ) = current
            sources.add(artifact_id)
            combined_reason_details.update(reason_details)
            aggregated[recommendation.test.id] = (
                node,
                sources,
                combined_reason_details,
            )
            if len(aggregated) > MAX_REPORT_TEST_CANDIDATES:
                raise ValueError(
                    "Change report exceeds the bounded test-candidate limit"
                )
    candidates = tuple(
        sorted(
            (
                ChangeReportTest(
                    node,
                    ordered_reasons[0].score,
                    confidence_for_score(ordered_reasons[0].score),
                    tuple(sorted(sources)),
                    ordered_reasons,
                )
                for (
                    node,
                    sources,
                    reason_details,
                ) in aggregated.values()
                if (
                    ordered_reasons := tuple(
                        sorted(reason_details, key=_reason_sort_key)
                    )
                )
            ),
            key=lambda item: (-item.score, item.test.id),
        )
    )
    return _TestRecommendationAnalysis(
        candidates,
        signal_candidate_count,
        len(signals),
    )


def _aggregate_freshness(analysis: ChangeAnalysis) -> str:
    values = {item.freshness for item in analysis.files}
    if not values:
        return "not-applicable"
    if "stale" in values:
        return "stale"
    if "unknown" in values:
        return "unknown"
    return "aligned"


def _omitted_requirement(item: RequirementImpact, reason: str) -> OmittedCandidate:
    return OmittedCandidate(
        "requirement",
        item.requirement,
        item.score,
        item.confidence,
        reason,
        (item.primary_reason,),
    )


def _omitted_test(item: ChangeReportTest, reason: str) -> OmittedCandidate:
    return OmittedCandidate(
        "test",
        item.test,
        item.score,
        item.confidence,
        reason,
        item.reason_details,
    )


def _path_text(path: RequirementImpactPath) -> str:
    parts = [path.nodes[0]]
    for relation, node in zip(path.relations, path.nodes[1:], strict=True):
        parts.extend((f"-[{relation}]->", node))
    return " ".join(parts)


def _omission_text(item: OmittedCandidate) -> str:
    primary = item.primary_reason
    return (
        f"- {item.node.id}: {item.score}/100 ({item.confidence}); not selected: "
        f"{item.selection_reason}\n"
        f"  Why: {primary.summary} ({primary.signal}, {primary.score}/100)\n"
        f"  Path: {_path_text(primary.path)}\n"
        f"  Evidence: {', '.join(primary.evidence) or 'none'}"
    )


def _reason_sort_key(reason: ReportReason) -> tuple[object, ...]:
    return (
        -reason.score,
        reason.signal,
        reason.path.nodes,
        reason.path.relations,
        reason.evidence,
        reason.summary,
    )
