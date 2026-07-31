from __future__ import annotations

from intentatlas.graph import AtlasGraph
from intentatlas.graph_diff import graph_diff, render_graph_diff
from intentatlas.models import Edge, Node


def test_graph_diff_is_complete_versioned_and_deterministic() -> None:
    base = AtlasGraph()
    base.extend(
        [
            Node("A", "file", "A", metadata={"value": 1}),
            Node("B", "file", "B"),
        ],
        [Edge("A", "B", "references", "fixture")],
    )
    current = AtlasGraph()
    current.extend(
        [
            Node("A", "file", "A", metadata={"value": 2}),
            Node("C", "file", "C"),
        ],
        [Edge("C", "A", "references", "fixture")],
    )

    value = graph_diff(base, current)
    rendered = render_graph_diff(value)

    assert value["schema_version"] == 1
    assert value["has_changes"] is True
    assert value["summary"] == {
        "nodes_added": 1,
        "nodes_removed": 1,
        "nodes_changed": 1,
        "edges_added": 1,
        "edges_removed": 1,
    }
    assert value["nodes"]["added"][0]["id"] == "C"
    assert value["nodes"]["removed"][0]["id"] == "B"
    assert value["nodes"]["changed"][0]["id"] == "A"
    assert "generated_at" not in rendered
    assert rendered == render_graph_diff(graph_diff(base, current))


def test_graph_diff_reports_identical_graphs_without_changes() -> None:
    graph = AtlasGraph()
    graph.add_node(Node("A", "file", "A"))

    value = graph_diff(graph, graph)

    assert value["has_changes"] is False
    assert all(count == 0 for count in value["summary"].values())
