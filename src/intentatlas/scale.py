from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from time import perf_counter
from typing import Any

from .graph import AtlasGraph
from .models import Edge, Node
from .recommendations import recommend_tests

MAX_UNRELATED_EDGES = 100_000
MAX_BENCHMARK_ITERATIONS = 10_000
ADVISORY = (
    "Timing is environment-specific and is not a portable latency guarantee; stable counts and "
    "result identities are the regression contract."
)


@dataclass(frozen=True, slots=True)
class ScaleBenchmarkResult:
    unrelated_edges: int
    iterations: int
    node_count: int
    edge_count: int
    index_edge_count: int
    recommendation_count: int
    impact_count: int
    legacy_full_edge_inspections_per_iteration: int
    indexed_bucket_edges_per_iteration: int
    graph_build_seconds: float
    index_build_seconds: float
    warm_queries_seconds: float
    mean_combined_query_ms: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_scale_benchmark(
    *,
    unrelated_edges: int = 25_000,
    iterations: int = 200,
) -> ScaleBenchmarkResult:
    _bounded_int(unrelated_edges, "unrelated edge count", 0, MAX_UNRELATED_EDGES)
    _bounded_int(iterations, "benchmark iteration count", 1, MAX_BENCHMARK_ITERATIONS)

    graph_start = perf_counter()
    graph = AtlasGraph()
    graph.extend(
        [
            Node("commit:scale", "commit", "Scale benchmark change"),
            Node("file:src/scale.py", "file", "src/scale.py", path="src/scale.py"),
            Node(
                "file:tests/test_scale_target.py",
                "test",
                "tests/test_scale_target.py",
                path="tests/test_scale_target.py",
            ),
        ],
        [
            Edge("commit:scale", "file:src/scale.py", "changes", "benchmark"),
            Edge(
                "file:tests/test_scale_target.py",
                "file:src/scale.py",
                "tests",
                "benchmark",
            ),
        ],
    )
    for number in range(unrelated_edges):
        source_id = f"file:noise/source-{number}.txt"
        target_id = f"file:noise/target-{number}.txt"
        graph.add_node(Node(source_id, "file", source_id.removeprefix("file:")))
        graph.add_node(Node(target_id, "file", target_id.removeprefix("file:")))
        graph.add_edge(Edge(source_id, target_id, "imports", "benchmark-noise"))
    graph_build_seconds = perf_counter() - graph_start

    index_start = perf_counter()
    index = graph.index
    index_build_seconds = perf_counter() - index_start

    recommendation_count = 0
    impact_count = 0
    warm_start = perf_counter()
    for _ in range(iterations):
        recommendation_count = len(
            recommend_tests(graph, "commit:scale", minimum_confidence="medium").recommendations
        )
        impact_count = len(graph.impact("commit:scale", depth=2, direction="both"))
    warm_queries_seconds = perf_counter() - warm_start

    edge_count = len(graph.edges)
    return ScaleBenchmarkResult(
        unrelated_edges=unrelated_edges,
        iterations=iterations,
        node_count=len(graph.nodes),
        edge_count=edge_count,
        index_edge_count=index.edge_count,
        recommendation_count=recommendation_count,
        impact_count=impact_count,
        legacy_full_edge_inspections_per_iteration=edge_count * 7,
        indexed_bucket_edges_per_iteration=5,
        graph_build_seconds=round(graph_build_seconds, 6),
        index_build_seconds=round(index_build_seconds, 6),
        warm_queries_seconds=round(warm_queries_seconds, 6),
        mean_combined_query_ms=round(warm_queries_seconds * 1_000 / iterations, 6),
    )


def render_scale_benchmark(result: ScaleBenchmarkResult, output_format: str = "text") -> str:
    value = {"schema_version": 1, "advisory": ADVISORY, **result.to_dict()}
    if output_format == "json":
        return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if output_format != "text":
        raise ValueError(f"Unknown scale benchmark output format: {output_format}")
    lines = [
        "IntentAtlas indexed query scale benchmark",
        f"Graph: {result.node_count} nodes, {result.edge_count} edges",
        f"Unrelated edges: {result.unrelated_edges}",
        f"Iterations: {result.iterations}",
        f"Graph build: {result.graph_build_seconds:.6f} s",
        f"Cold index build: {result.index_build_seconds:.6f} s",
        f"Warm combined queries: {result.warm_queries_seconds:.6f} s",
        f"Mean combined query: {result.mean_combined_query_ms:.6f} ms",
        f"Recommendation count: {result.recommendation_count}",
        f"Impact count: {result.impact_count}",
        "Reference edge inspections per iteration: "
        f"legacy {result.legacy_full_edge_inspections_per_iteration}, "
        f"indexed buckets {result.indexed_bucket_edges_per_iteration}",
        f"Advisory: {ADVISORY}",
    ]
    return "\n".join(lines) + "\n"


def _bounded_int(value: int, label: str, minimum: int, maximum: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum or value > maximum:
        raise ValueError(f"{label.capitalize()} must be between {minimum} and {maximum}")
