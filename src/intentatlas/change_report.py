from __future__ import annotations

import json
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .change_analysis import ChangeAnalysis, _analyze_change_set_with_graph
from .change_set import ChangeSet
from .confidence import CONFIDENCE_RANK, confidence_for_score
from .config import ProjectConfig
from .graph import AtlasGraph
from .models import Node
from .recommendations import recommend_tests
from .scanner import scan_repository

CHANGE_REPORT_SCHEMA_VERSION = 1
MAX_REPORT_RESULTS = 100
MAX_REPORT_ARTIFACTS = 200
MAX_REPORT_TEST_CANDIDATES = 10_000
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
class RequirementImpact:
    requirement: Node
    score: int
    confidence: str
    source_artifact_id: str
    path: RequirementImpactPath
    evidence: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "requirement": self.requirement.to_dict(),
            "score": self.score,
            "confidence": self.confidence,
            "reason": "confidence-meets-minimum-threshold",
            "source_artifact_id": self.source_artifact_id,
            "path": self.path.to_dict(),
            "evidence": list(self.evidence),
        }


@dataclass(frozen=True, slots=True)
class ChangeReportTest:
    test: Node
    score: int
    confidence: str
    artifact_ids: tuple[str, ...]
    evidence: tuple[str, ...]
    reasons: tuple[str, ...]
    paths: tuple[RequirementImpactPath, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "test": self.test.to_dict(),
            "score": self.score,
            "confidence": self.confidence,
            "artifact_ids": list(self.artifact_ids),
            "evidence": list(self.evidence),
            "reasons": list(self.reasons),
            "paths": [path.to_dict() for path in self.paths],
        }


@dataclass(frozen=True, slots=True)
class OmittedCandidate:
    candidate_type: str
    node: Node
    score: int
    confidence: str
    reason: str
    evidence: tuple[str, ...]
    paths: tuple[RequirementImpactPath, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_type": self.candidate_type,
            "node": self.node.to_dict(),
            "score": self.score,
            "confidence": self.confidence,
            "reason": self.reason,
            "evidence": list(self.evidence),
            "paths": [path.to_dict() for path in self.paths],
        }


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

    artifact_ids = tuple(
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
        artifact_ids = ()
    if len(artifact_ids) > MAX_REPORT_ARTIFACTS:
        raise ValueError(
            f"Change report exceeds the {MAX_REPORT_ARTIFACTS}-artifact analysis limit"
        )

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
    test_candidates = _test_recommendations(graph, artifact_ids)
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

    coverage_complete = analysis.state == "analyzed" or not analysis.files
    if not analysis.files:
        strategy = "no-changes"
    elif analysis.state == "unknown":
        strategy = "abstain-and-full-suite"
    elif analysis.state == "fallback" and tests:
        strategy = "targeted-plus-full-suite"
    elif analysis.state == "fallback":
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
        f"Test strategy: {report.test_strategy}",
        (
            "Requirement impacts: "
            f"{len(report.requirements)} selected / "
            f"{report.requirement_candidate_count} candidates; "
            f"{report.requirement_filtered_count} filtered; "
            f"{report.requirement_limit_omitted_count} omitted by limit"
        ),
    ]
    if report.revision_action is not None:
        lines.append(f"Revision action: {report.revision_action}")
    for requirement_item in report.requirements:
        lines.append(
            f"- {requirement_item.requirement.id}: {requirement_item.score}/100 "
            f"({requirement_item.confidence}); selected because confidence meets "
            f"{report.minimum_confidence}; path {_path_text(requirement_item.path)}; "
            f"evidence {', '.join(requirement_item.evidence) or 'none'}"
        )
    if report.omitted_requirements:
        lines.append("Omitted requirement candidates:")
        lines.extend(_omission_text(item) for item in report.omitted_requirements)
    lines.append(
        f"Recommended tests: {len(report.tests)} selected / "
        f"{report.test_candidate_count} candidates; {report.test_filtered_count} filtered; "
        f"{report.test_limit_omitted_count} omitted by limit"
    )
    for test_item in report.tests:
        lines.append(
            f"- {test_item.test.id}: {test_item.score}/100 ({test_item.confidence}); "
            f"selected from {len(test_item.artifact_ids)} changed artifacts; "
            f"path {_path_text(test_item.paths[0]) if test_item.paths else 'none'}; "
            f"evidence {', '.join(test_item.evidence) or 'none'}"
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


def _test_recommendations(
    graph: AtlasGraph, artifact_ids: tuple[str, ...]
) -> tuple[ChangeReportTest, ...]:
    aggregated: dict[
        str,
        tuple[
            Node,
            int,
            str,
            set[str],
            set[str],
            set[str],
            dict[tuple[tuple[str, ...], tuple[str, ...]], RequirementImpactPath],
        ],
    ] = {}
    signal_count = 0
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
        signal_count += len(targets)
        if signal_count > MAX_REPORT_ARTIFACTS:
            raise ValueError(
                "Change report exceeds the bounded file-symbol analysis limit"
            )
        for recommendation_target, file_fallback in targets:
            result = recommend_tests(
                graph,
                recommendation_target,
                minimum_confidence="low",
                limit=MAX_REPORT_RESULTS,
            )
            for recommendation in result.recommendations:
                score = min(recommendation.score, 65) if file_fallback else recommendation.score
                confidence = confidence_for_score(score)
                evidence = {
                    value
                    for reason in recommendation.reasons
                    for value in reason.evidence
                }
                reasons = {reason.summary for reason in recommendation.reasons}
                paths = {
                    (reason.path.nodes, reason.path.relations): RequirementImpactPath(
                        reason.path.nodes,
                        reason.path.relations,
                    )
                    for reason in recommendation.reasons
                }
                if file_fallback:
                    evidence.add("file-level-fallback")
                    reasons.add(
                        "The candidate is retained as file-level fallback; "
                        "it is not exact-symbol proof."
                    )
                current = aggregated.get(recommendation.test.id)
                if current is None:
                    aggregated[recommendation.test.id] = (
                        recommendation.test,
                        score,
                        confidence,
                        {artifact_id},
                        evidence,
                        reasons,
                        paths,
                    )
                    if len(aggregated) > MAX_REPORT_TEST_CANDIDATES:
                        raise ValueError(
                            "Change report exceeds the bounded test-candidate limit"
                        )
                    continue
                (
                    node,
                    current_score,
                    current_confidence,
                    sources,
                    combined_evidence,
                    combined_reasons,
                    combined_paths,
                ) = current
                sources.add(artifact_id)
                combined_evidence.update(evidence)
                combined_reasons.update(reasons)
                combined_paths.update(paths)
                if score > current_score:
                    current_score = score
                    current_confidence = confidence
                aggregated[recommendation.test.id] = (
                    node,
                    current_score,
                    current_confidence,
                    sources,
                    combined_evidence,
                    combined_reasons,
                    combined_paths,
                )
                if len(aggregated) > MAX_REPORT_TEST_CANDIDATES:
                    raise ValueError(
                        "Change report exceeds the bounded test-candidate limit"
                    )
    return tuple(
        sorted(
            (
                ChangeReportTest(
                    node,
                    score,
                    confidence,
                    tuple(sorted(sources)),
                    tuple(sorted(evidence)),
                    tuple(sorted(reasons)),
                    tuple(
                        paths[key]
                        for key in sorted(paths)
                    ),
                )
                for (
                    node,
                    score,
                    confidence,
                    sources,
                    evidence,
                    reasons,
                    paths,
                ) in aggregated.values()
            ),
            key=lambda item: (-item.score, item.test.id),
        )
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
        item.evidence,
        (item.path,),
    )


def _omitted_test(item: ChangeReportTest, reason: str) -> OmittedCandidate:
    return OmittedCandidate(
        "test",
        item.test,
        item.score,
        item.confidence,
        reason,
        item.evidence,
        item.paths,
    )


def _path_text(path: RequirementImpactPath) -> str:
    parts = [path.nodes[0]]
    for relation, node in zip(path.relations, path.nodes[1:], strict=True):
        parts.extend((f"-[{relation}]->", node))
    return " ".join(parts)


def _omission_text(item: OmittedCandidate) -> str:
    path = _path_text(item.paths[0]) if item.paths else "none"
    return (
        f"- {item.node.id}: {item.score}/100 ({item.confidence}); {item.reason}; "
        f"path {path}; evidence {', '.join(item.evidence) or 'none'}"
    )
