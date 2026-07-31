from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

from .graph import AtlasGraph, GraphIndex
from .models import Edge, Node

RECOMMENDATION_SCHEMA_VERSION = 1
MAX_RECOMMENDATIONS = 100
MAX_ARTIFACT_SIGNALS = 1_000
MAX_CANDIDATE_TESTS = 10_000
MAX_REASONS_PER_TEST = 25
MAX_OBSERVATIONS_PER_TEST = 25
CONFIDENCE_RANK = {"low": 0, "medium": 1, "high": 2}
ADVISORY = (
    "Recommendations are advisory structural evidence, not proof that a test is required or "
    "that omitted behavior is unaffected."
)


@dataclass(frozen=True, slots=True)
class RecommendationPath:
    nodes: tuple[str, ...]
    relations: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.nodes or len(self.relations) != len(self.nodes) - 1:
            raise ValueError("Recommendation path must connect every adjacent node")

    def to_dict(self) -> dict[str, list[str]]:
        return {"nodes": list(self.nodes), "relations": list(self.relations)}

    def render(self) -> str:
        value = self.nodes[0]
        for relation, node_id in zip(self.relations, self.nodes[1:], strict=True):
            value += f" --{relation}--> {node_id}"
        return value


@dataclass(frozen=True, slots=True)
class RecommendationReason:
    signal: str
    score: int
    summary: str
    path: RecommendationPath
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
class TestObservation:
    node_id: str
    report: str
    total: int
    passed: int
    failed: int
    errors: int
    skipped: int
    duration_seconds: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class TestRecommendation:
    test: Node
    score: int
    confidence: str
    reason_count: int
    reasons_truncated: bool
    reasons: tuple[RecommendationReason, ...]
    observation_count: int
    observations_truncated: bool
    observations: tuple[TestObservation, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "test": self.test.to_dict(),
            "score": self.score,
            "confidence": self.confidence,
            "reason_count": self.reason_count,
            "reasons_truncated": self.reasons_truncated,
            "reasons": [reason.to_dict() for reason in self.reasons],
            "observation_count": self.observation_count,
            "observations_truncated": self.observations_truncated,
            "observations": [observation.to_dict() for observation in self.observations],
        }


@dataclass(frozen=True, slots=True)
class RecommendationResult:
    target: Node
    minimum_confidence: str
    candidate_count: int
    recommendations: tuple[TestRecommendation, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": RECOMMENDATION_SCHEMA_VERSION,
            "advisory": ADVISORY,
            "target": self.target.to_dict(),
            "minimum_confidence": self.minimum_confidence,
            "candidate_count": self.candidate_count,
            "recommendations": [item.to_dict() for item in self.recommendations],
        }


@dataclass(frozen=True, slots=True)
class _ArtifactSignal:
    file: Node
    symbol: Node | None
    path: RecommendationPath
    evidence: tuple[str, ...]


def recommend_tests(
    graph: AtlasGraph,
    target_id: str,
    *,
    minimum_confidence: str = "medium",
    limit: int = 20,
) -> RecommendationResult:
    if minimum_confidence not in CONFIDENCE_RANK:
        raise ValueError(f"Unknown minimum confidence: {minimum_confidence}")
    if isinstance(limit, bool) or limit < 1 or limit > MAX_RECOMMENDATIONS:
        raise ValueError(f"Recommendation limit must be between 1 and {MAX_RECOMMENDATIONS}")
    target = graph.nodes.get(target_id)
    if target is None:
        raise ValueError(f"Unknown node: {target_id}")
    if target.kind not in {"commit", "file", "symbol", "test"}:
        raise ValueError(
            "Test recommendations currently support commit, file, symbol, or test targets; "
            f"received {target.kind}"
        )

    index = graph.index
    reasons_by_test: dict[str, list[RecommendationReason]] = {}
    signals = _artifact_signals(graph, target, index)
    if len(signals) > MAX_ARTIFACT_SIGNALS:
        raise ValueError(
            f"Recommendation target exceeds the {MAX_ARTIFACT_SIGNALS}-artifact signal limit"
        )
    for signal in signals:
        if signal.file.kind == "test":
            _add_reason(
                reasons_by_test,
                signal.file.id,
                RecommendationReason(
                    signal="changed-test",
                    score=100,
                    summary="The selected target or change directly includes this test file.",
                    path=signal.path,
                    evidence=_unique_values(signal.evidence),
                ),
            )
            continue
        for edge in _preferred_test_edges(index, signal.file.id):
            test = graph.nodes.get(edge.source)
            if test is None or test.kind != "test":
                continue
            convention = edge.evidence == "filename-convention"
            if signal.symbol is not None:
                score = 70 if convention else 80
                signal_name = "symbol-filename-test" if convention else "symbol-structural-test"
                summary = (
                    "The filename convention associates this test with the file containing an "
                    "exactly modified symbol."
                    if convention
                    else "The test structurally targets the file containing an exactly modified "
                    "symbol."
                )
                path = RecommendationPath(
                    (*signal.path.nodes, test.id),
                    (*signal.path.relations, "tested-by"),
                )
            else:
                score = 45 if convention else 65
                signal_name = "file-filename-test" if convention else "file-structural-test"
                summary = (
                    "The filename convention associates this test with a changed file."
                    if convention
                    else "The test structurally targets a changed file without exact symbol "
                    "evidence."
                )
                path = RecommendationPath(
                    (*signal.path.nodes, test.id),
                    (*signal.path.relations, "tested-by"),
                )
            _add_reason(
                reasons_by_test,
                test.id,
                RecommendationReason(
                    signal=signal_name,
                    score=score,
                    summary=summary,
                    path=path,
                    evidence=_unique_values((*signal.evidence, edge.evidence)),
                ),
            )

    if len(reasons_by_test) > MAX_CANDIDATE_TESTS:
        raise ValueError(
            f"Recommendation query exceeds the {MAX_CANDIDATE_TESTS}-test candidate limit"
        )
    recommendations = _recommendations(graph, reasons_by_test, index)
    candidate_count = len(recommendations)
    minimum_rank = CONFIDENCE_RANK[minimum_confidence]
    filtered = tuple(
        item
        for item in recommendations
        if CONFIDENCE_RANK[item.confidence] >= minimum_rank
    )[:limit]
    return RecommendationResult(target, minimum_confidence, candidate_count, filtered)


def render_recommendations(result: RecommendationResult, output_format: str = "text") -> str:
    if output_format == "json":
        return json.dumps(result.to_dict(), indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if output_format != "text":
        raise ValueError(f"Unknown recommendation output format: {output_format}")

    lines = [
        f"Test recommendations for {result.target.label} [{result.target.kind}]",
        f"Minimum confidence: {result.minimum_confidence}",
        f"Advisory: {ADVISORY}",
    ]
    if not result.recommendations:
        lines.append("No test recommendations meet the selected confidence threshold.")
        if result.candidate_count:
            lines.append(f"Lower-confidence candidates available: {result.candidate_count}")
        return "\n".join(lines) + "\n"

    for index, item in enumerate(result.recommendations, start=1):
        label = item.test.path or item.test.label
        lines.append(f"{index}. {label} [{item.confidence} {item.score}]")
        for reason in item.reasons:
            lines.append(f"   Why: {reason.summary}")
            lines.append(f"   Path: {reason.path.render()}")
            lines.append(f"   Evidence: {', '.join(reason.evidence)}")
        if item.reasons_truncated:
            lines.append(
                f"   Additional reasons omitted: {item.reason_count - len(item.reasons)}"
            )
        for observation in item.observations:
            lines.append(
                "   Observed: "
                f"{observation.report} — {observation.passed}/{observation.total} passed, "
                f"{observation.failed} failed, {observation.errors} errors, "
                f"{observation.skipped} skipped"
            )
        if item.observations_truncated:
            lines.append(
                "   Additional observations omitted: "
                f"{item.observation_count - len(item.observations)}"
            )
    return "\n".join(lines) + "\n"


def _artifact_signals(
    graph: AtlasGraph, target: Node, index: GraphIndex
) -> tuple[_ArtifactSignal, ...]:
    signals: list[_ArtifactSignal] = []
    if target.kind == "commit":
        for edge in index.outgoing(target.id):
            changed = graph.nodes.get(edge.target)
            if changed is None:
                continue
            if edge.relation == "modifies" and changed.kind == "symbol":
                symbol_file = _symbol_file(graph, changed, index)
                if symbol_file is not None:
                    file, defines_evidence = symbol_file
                    signals.append(
                        _ArtifactSignal(
                            file,
                            changed,
                            RecommendationPath(
                                (target.id, changed.id, file.id),
                                ("modifies", "defined-in"),
                            ),
                            (edge.evidence, defines_evidence),
                        )
                    )
            elif edge.relation == "changes" and changed.kind in {"file", "test"}:
                signals.append(
                    _ArtifactSignal(
                        changed,
                        None,
                        RecommendationPath((target.id, changed.id), ("changes",)),
                        (edge.evidence,),
                    )
                )
    elif target.kind == "symbol":
        symbol_file = _symbol_file(graph, target, index)
        if symbol_file is not None:
            file, evidence = symbol_file
            signals.append(
                _ArtifactSignal(
                    file,
                    target,
                    RecommendationPath((target.id, file.id), ("defined-in",)),
                    (evidence,),
                )
            )
    else:
        signals.append(
            _ArtifactSignal(
                target,
                None,
                RecommendationPath((target.id,), ()),
                ("selected-target",),
            )
        )
    unique = {
        (
            item.file.id,
            item.symbol.id if item.symbol else "",
            item.path.nodes,
            item.path.relations,
            item.evidence,
        ): item
        for item in signals
    }
    values = tuple(unique[key] for key in sorted(unique))
    symbol_files = {
        item.file.id
        for item in values
        if item.symbol is not None and item.file.kind != "test"
    }
    return tuple(
        item
        for item in values
        if (
            (item.file.kind == "test" and item.symbol is None)
            or (item.file.kind == "test" and target.kind == "symbol")
            or (
                item.file.kind != "test"
                and not (item.symbol is None and item.file.id in symbol_files)
            )
        )
    )


def _preferred_test_edges(index: GraphIndex, target_id: str) -> tuple[Edge, ...]:
    selected: dict[str, Edge] = {}
    for edge in index.incoming(target_id, "tests"):
        current = selected.get(edge.source)
        candidate_rank = (edge.evidence != "filename-convention", edge.evidence)
        current_rank = (
            (current.evidence != "filename-convention", current.evidence)
            if current is not None
            else None
        )
        if current_rank is None or candidate_rank > current_rank:
            selected[edge.source] = edge
    return tuple(selected[test_id] for test_id in sorted(selected))


def _symbol_file(
    graph: AtlasGraph, symbol: Node, index: GraphIndex
) -> tuple[Node, str] | None:
    if symbol.path is None:
        return None
    file = graph.nodes.get(f"file:{symbol.path}")
    if file is None or file.kind not in {"file", "test"}:
        return None
    evidence = sorted(
        {
            edge.evidence
            for edge in index.incoming(symbol.id, "defines")
            if edge.source == file.id
        }
    )
    return file, evidence[0] if evidence else "graph-symbol-path"


def _add_reason(
    values: dict[str, list[RecommendationReason]],
    test_id: str,
    reason: RecommendationReason,
) -> None:
    reasons = values.setdefault(test_id, [])
    if reason not in reasons:
        reasons.append(reason)


def _recommendations(
    graph: AtlasGraph,
    reasons_by_test: dict[str, list[RecommendationReason]],
    index: GraphIndex,
) -> tuple[TestRecommendation, ...]:
    values: list[TestRecommendation] = []
    for test_id in sorted(reasons_by_test):
        test = graph.nodes.get(test_id)
        if test is None or test.kind != "test":
            continue
        all_reasons = tuple(
            sorted(
                reasons_by_test[test_id],
                key=lambda item: (
                    -item.score,
                    item.signal,
                    item.path.nodes,
                    item.path.relations,
                    item.evidence,
                ),
            )
        )
        reasons = all_reasons[:MAX_REASONS_PER_TEST]
        score = max(reason.score for reason in all_reasons)
        all_observations = _test_observations(graph, test_id, index)
        observations = all_observations[:MAX_OBSERVATIONS_PER_TEST]
        values.append(
            TestRecommendation(
                test=test,
                score=score,
                confidence=_confidence(score),
                reason_count=len(all_reasons),
                reasons_truncated=len(all_reasons) > len(reasons),
                reasons=reasons,
                observation_count=len(all_observations),
                observations_truncated=len(all_observations) > len(observations),
                observations=observations,
            )
        )
    return tuple(sorted(values, key=lambda item: (-item.score, item.test.id)))


def _test_observations(
    graph: AtlasGraph, test_id: str, index: GraphIndex
) -> tuple[TestObservation, ...]:
    observations: list[TestObservation] = []
    for edge in index.incoming(test_id, "proves"):
        node = graph.nodes.get(edge.source)
        if node is None or node.kind != "test-result":
            continue
        metadata = node.metadata
        observations.append(
            TestObservation(
                node_id=node.id,
                report=str(metadata.get("report", "")),
                total=_safe_nonnegative_int(metadata.get("total")),
                passed=_safe_nonnegative_int(metadata.get("passed")),
                failed=_safe_nonnegative_int(metadata.get("failed")),
                errors=_safe_nonnegative_int(metadata.get("errors")),
                skipped=_safe_nonnegative_int(metadata.get("skipped")),
                duration_seconds=_safe_duration(metadata.get("duration_seconds")),
            )
        )
    return tuple(sorted(set(observations), key=lambda item: item.node_id))


def _safe_nonnegative_int(value: object) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else 0


def _safe_duration(value: object) -> float:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        parsed = float(value)
        if 0 <= parsed <= 31_536_000:
            return parsed
    return 0.0


def _confidence(score: int) -> str:
    if score >= 85:
        return "high"
    if score >= 65:
        return "medium"
    return "low"


def _unique_values(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))
