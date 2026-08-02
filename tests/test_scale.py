from __future__ import annotations

import json

import pytest

from intentatlas.cli import main
from intentatlas.scale import (
    render_scale_benchmark,
    run_large_graph_benchmark,
    run_scale_benchmark,
)


def test_scale_benchmark_has_stable_counts_and_local_lookup_work() -> None:
    result = run_scale_benchmark(unrelated_edges=100, iterations=3)

    assert result.node_count == 203
    assert result.edge_count == 102
    assert result.index_edge_count == 102
    assert result.recommendation_count == 1
    assert result.impact_count == 2
    assert result.legacy_full_edge_inspections_per_iteration == 714
    assert result.indexed_bucket_edges_per_iteration == 5
    assert result.graph_build_seconds >= 0
    assert result.index_build_seconds >= 0
    assert result.warm_queries_seconds >= 0
    assert result.mean_combined_query_ms >= 0

    value = json.loads(render_scale_benchmark(result, "json"))
    assert value["schema_version"] == 1
    assert value["recommendation_count"] == 1
    assert "environment-specific" in value["advisory"]
    text = render_scale_benchmark(result)
    assert "Graph: 203 nodes, 102 edges" in text
    assert "legacy 714, indexed buckets 5" in text


@pytest.mark.parametrize(
    ("options", "message"),
    [
        ({"unrelated_edges": True}, "Unrelated edge count"),
        ({"unrelated_edges": -1}, "Unrelated edge count"),
        ({"unrelated_edges": 100_001}, "Unrelated edge count"),
        ({"iterations": True}, "Benchmark iteration count"),
        ({"iterations": 0}, "Benchmark iteration count"),
        ({"iterations": 10_001}, "Benchmark iteration count"),
    ],
)
def test_scale_benchmark_rejects_invalid_bounds(options, message) -> None:
    with pytest.raises(ValueError, match=message):
        run_scale_benchmark(**options)


def test_scale_benchmark_cli_and_format_errors(capsys) -> None:
    assert (
        main(
            [
                "benchmark-scale",
                "--unrelated-edges",
                "10",
                "--iterations",
                "2",
                "--format",
                "json",
            ]
        )
        == 0
    )
    value = json.loads(capsys.readouterr().out)
    assert value["edge_count"] == 12
    assert value["index_edge_count"] == 12

    assert main(["benchmark-scale", "--iterations", "0"]) == 2
    assert "between 1 and 10000" in capsys.readouterr().err

    result = run_scale_benchmark(unrelated_edges=0, iterations=1)
    with pytest.raises(ValueError, match="Unknown scale benchmark output format"):
        render_scale_benchmark(result, "yaml")


def test_large_graph_benchmark_has_exact_work_counts_and_bounded_queries() -> None:
    result = run_large_graph_benchmark(node_count=100, edge_count=500)
    assert result.node_count == result.constructed_nodes == 100
    assert result.edge_count == result.constructed_edges == 500
    assert result.overview_nodes == 100
    assert result.overview_edges == 500
    assert result.overview_omitted_nodes == 0
    assert result.overview_omitted_edges == 0
    assert 0 < result.overview_payload_bytes < 1_000_000
    assert result.search_result_count == 1
    assert 0 < result.neighborhood_node_count <= 240
    assert result.graph_build_seconds >= 0
    assert result.index_build_seconds >= 0
    assert result.overview_query_seconds >= 0
