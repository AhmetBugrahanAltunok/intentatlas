from __future__ import annotations

import json

import pytest

from intentatlas.graph import AtlasGraph
from intentatlas.graph_query import GraphQuerySnapshot
from intentatlas.models import Edge, Node


def _snapshot() -> GraphQuerySnapshot:
    graph = AtlasGraph()
    graph.extend(
        [
            Node("REQ-1", "requirement", "Preserve login"),
            Node("file:app.py", "file", "app.py", "app.py"),
            Node("file:test_app.py", "test", "test_app.py", "test_app.py"),
            Node("commit:abc", "commit", "Change login"),
        ],
        [
            Edge("REQ-1", "file:app.py", "implemented-by", "fixture"),
            Edge("file:test_app.py", "file:app.py", "tests", "fixture"),
            Edge("commit:abc", "file:app.py", "changes", "fixture"),
        ],
    )
    return GraphQuerySnapshot(graph, "a" * 64)


def test_bounded_query_windows_carry_snapshot_totals_and_omissions() -> None:
    snapshot = _snapshot()
    overview = snapshot.overview(node_limit=2, edge_limit=1)
    assert overview["snapshot"] == "a" * 64
    assert overview["total_counts"] == {"nodes": 4, "edges": 3}
    assert overview["returned_counts"] == {"nodes": 2, "edges": 1}
    assert overview["omitted_counts"]["nodes"] == 2
    assert len(json.dumps(overview)) < 5_000

    search = snapshot.search("login", limit=1)
    assert search["matched_counts"]["nodes"] == 2
    assert search["returned_counts"]["nodes"] == 1
    assert search["omitted_counts"]["nodes"] == 1

    neighborhood = snapshot.neighborhood(
        "file:app.py", depth=1, node_limit=3, edge_limit=2
    )
    assert neighborhood["returned_counts"] == {"nodes": 3, "edges": 2}
    assert all(
        edge["source"] in {node["id"] for node in neighborhood["nodes"]}
        and edge["target"] in {node["id"] for node in neighborhood["nodes"]}
        for edge in neighborhood["edges"]
    )

    paths = snapshot.paths("REQ-1", result_limit=2)
    assert paths["work"]["visited_nodes"] <= paths["work"]["max_visited_nodes"]
    assert paths["returned_counts"]["paths"] == 2
    assert {item["destination"]["kind"] for item in paths["paths"]} == {
        "commit",
        "test",
    }
    assert paths["omitted_counts"]["paths"] == 0
    assert paths["truncated"]["paths"] is False

    truncated = snapshot.paths("REQ-1", result_limit=1)
    assert truncated["omitted_counts"]["paths"] is None
    assert truncated["truncated"]["paths"] is True

    exact_visited_boundary = snapshot.paths("REQ-1", visited_limit=4)
    assert exact_visited_boundary["work"]["visited_nodes"] == 4
    assert exact_visited_boundary["omitted_counts"]["visited"] == 0
    assert exact_visited_boundary["truncated"]["visited"] is False

    visited_truncated = snapshot.paths("REQ-1", visited_limit=3)
    assert visited_truncated["work"]["visited_nodes"] == 3
    assert visited_truncated["omitted_counts"]["visited"] is None
    assert visited_truncated["truncated"]["visited"] is True
    assert visited_truncated["omitted_counts"]["paths"] is None
    assert visited_truncated["truncated"]["paths"] is True


def test_paths_abstain_from_complete_count_when_an_alternative_route_is_deduplicated() -> None:
    graph = AtlasGraph()
    graph.extend(
        [
            Node("REQ", "requirement", "Requirement"),
            Node("file:a", "file", "a", path="a"),
            Node("file:b", "file", "b", path="b"),
            Node("file:test", "test", "test", path="test"),
        ],
        [
            Edge("REQ", "file:a", "implemented-by", "fixture"),
            Edge("REQ", "file:b", "implemented-by", "fixture"),
            Edge("file:test", "file:a", "tests", "fixture"),
            Edge("file:test", "file:b", "tests", "fixture"),
        ],
    )

    result = GraphQuerySnapshot(graph, "b" * 64).paths("REQ")

    assert result["returned_counts"]["paths"] == 1
    assert result["omitted_counts"]["paths"] is None
    assert result["truncated"]["paths"] is True


@pytest.mark.parametrize(
    ("operation", "message"),
    [
        (lambda query: query.overview(node_limit=501), "node_limit"),
        (lambda query: query.search(""), "query"),
        (lambda query: query.neighborhood("missing"), "Unknown"),
        (lambda query: query.paths("REQ-1", visited_limit=5_001), "visited_limit"),
    ],
)
def test_query_contract_rejects_unbounded_or_unknown_requests(operation, message) -> None:
    with pytest.raises(ValueError, match=message):
        operation(_snapshot())
