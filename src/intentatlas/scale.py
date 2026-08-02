from __future__ import annotations

import ctypes
import json
import platform
import sys
from dataclasses import asdict, dataclass
from time import perf_counter
from typing import Any

from .graph import AtlasGraph
from .graph_query import GraphQuerySnapshot
from .models import Edge, Node
from .recommendations import recommend_tests

MAX_UNRELATED_EDGES = 100_000
MAX_BENCHMARK_ITERATIONS = 10_000
MAX_LARGE_NODES = 200_000
MAX_LARGE_EDGES = 1_000_000
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


@dataclass(frozen=True, slots=True)
class LargeGraphBenchmarkResult:
    node_count: int
    edge_count: int
    constructed_nodes: int
    constructed_edges: int
    overview_nodes: int
    overview_edges: int
    overview_omitted_nodes: int
    overview_omitted_edges: int
    overview_payload_bytes: int
    search_result_count: int
    neighborhood_node_count: int
    graph_build_seconds: float
    index_build_seconds: float
    overview_query_seconds: float
    search_query_seconds: float
    neighborhood_query_seconds: float
    peak_memory_bytes: int | None

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


def run_large_graph_benchmark(
    *, node_count: int = 100_000, edge_count: int = 500_000
) -> LargeGraphBenchmarkResult:
    _bounded_int(node_count, "large graph node count", 2, MAX_LARGE_NODES)
    _bounded_int(edge_count, "large graph edge count", 1, MAX_LARGE_EDGES)
    if edge_count > node_count * (node_count - 1):
        raise ValueError("Large graph edge count exceeds deterministic unique-edge capacity")

    graph_start = perf_counter()
    graph = AtlasGraph()
    for number in range(node_count):
        node_id = f"file:scale/node-{number:06d}.txt"
        graph.add_node(Node(node_id, "file", node_id.removeprefix("file:")))
    for number in range(edge_count):
        source_number = number % node_count
        layer = number // node_count
        target_number = (source_number + layer + 1) % node_count
        source = f"file:scale/node-{source_number:06d}.txt"
        target = f"file:scale/node-{target_number:06d}.txt"
        graph.add_edge(Edge(source, target, "imports", f"scale-layer-{layer}"))
    graph_build_seconds = perf_counter() - graph_start

    index_start = perf_counter()
    index = graph.index
    index_build_seconds = perf_counter() - index_start
    if index.edge_count != edge_count:
        raise ValueError("Large graph construction did not produce the requested unique edges")

    snapshot = GraphQuerySnapshot(graph, "scale-benchmark")
    overview_start = perf_counter()
    overview = snapshot.overview(node_limit=240, edge_limit=900)
    overview_query_seconds = perf_counter() - overview_start
    payload_bytes = len(
        json.dumps(overview, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    search_start = perf_counter()
    search = snapshot.search(f"node-{node_count - 1:06d}", limit=20)
    search_query_seconds = perf_counter() - search_start
    neighborhood_start = perf_counter()
    neighborhood = snapshot.neighborhood(
        "file:scale/node-000000.txt", depth=2, node_limit=240, edge_limit=900
    )
    neighborhood_query_seconds = perf_counter() - neighborhood_start
    return LargeGraphBenchmarkResult(
        node_count=node_count,
        edge_count=edge_count,
        constructed_nodes=len(graph.nodes),
        constructed_edges=graph.edge_count,
        overview_nodes=overview["returned_counts"]["nodes"],
        overview_edges=overview["returned_counts"]["edges"],
        overview_omitted_nodes=overview["omitted_counts"]["nodes"],
        overview_omitted_edges=overview["omitted_counts"]["edges"],
        overview_payload_bytes=payload_bytes,
        search_result_count=search["returned_counts"]["nodes"],
        neighborhood_node_count=neighborhood["returned_counts"]["nodes"],
        graph_build_seconds=round(graph_build_seconds, 6),
        index_build_seconds=round(index_build_seconds, 6),
        overview_query_seconds=round(overview_query_seconds, 6),
        search_query_seconds=round(search_query_seconds, 6),
        neighborhood_query_seconds=round(neighborhood_query_seconds, 6),
        peak_memory_bytes=_peak_memory_bytes(),
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


def _peak_memory_bytes() -> int | None:
    if platform.system() == "Windows":
        class ProcessMemoryCounters(ctypes.Structure):
            _fields_ = [
                ("cb", ctypes.c_ulong),
                ("PageFaultCount", ctypes.c_ulong),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        counters = ProcessMemoryCounters()
        counters.cb = ctypes.sizeof(counters)
        get_process = ctypes.windll.kernel32.GetCurrentProcess
        get_process.restype = ctypes.c_void_p
        handle = get_process()
        get_memory = ctypes.windll.psapi.GetProcessMemoryInfo
        get_memory.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ProcessMemoryCounters),
            ctypes.c_ulong,
        ]
        get_memory.restype = ctypes.c_int
        success = get_memory(
            handle, ctypes.byref(counters), counters.cb
        )
        return int(counters.PeakWorkingSetSize) if success else None
    try:
        import resource

        getrusage = resource.getrusage  # type: ignore[attr-defined]
        usage_self = resource.RUSAGE_SELF  # type: ignore[attr-defined]
        maximum = getrusage(usage_self).ru_maxrss
        return int(maximum if sys.platform == "darwin" else maximum * 1024)
    except (ImportError, OSError):
        return None
