from __future__ import annotations

import json

import pytest

import intentatlas.storage as storage_module
from intentatlas.graph import AtlasGraph
from intentatlas.models import Edge, Node
from intentatlas.relations import relation_catalog


def sample_graph() -> AtlasGraph:
    graph = AtlasGraph()
    graph.extend(
        [
            Node("REQ-1", "requirement", "Understand impact"),
            Node("ADR-1", "decision", "Use a graph"),
            Node("file:app.py", "file", "app.py", "app.py"),
            Node("file:test_app.py", "test", "test_app.py", "test_app.py"),
        ]
    )
    assert graph.add_edge(Edge("REQ-1", "ADR-1", "drives", "wikilink"))
    assert graph.add_edge(Edge("ADR-1", "file:app.py", "implemented-by", "wikilink"))
    assert graph.add_edge(Edge("file:test_app.py", "file:app.py", "tests", "python-ast"))
    return graph


def test_graph_deduplicates_edges_and_rejects_invalid_edges() -> None:
    graph = sample_graph()
    original = len(graph.edges)
    assert graph.add_edge(Edge("REQ-1", "ADR-1", "drives", "wikilink"))
    assert len(graph.edges) == original
    assert not graph.add_edge(Edge("REQ-1", "missing", "drives"))
    assert not graph.add_edge(Edge("REQ-1", "REQ-1", "self"))


def test_graph_index_is_deterministic_reused_and_invalidated() -> None:
    graph = sample_graph()
    index = graph.index

    assert index.edge_count == 3
    assert [edge.target for edge in index.outgoing("REQ-1")] == ["ADR-1"]
    assert [edge.source for edge in index.incoming("file:app.py")] == [
        "ADR-1",
        "file:test_app.py",
    ]
    assert index.incoming("file:app.py", "tests") == (
        Edge("file:test_app.py", "file:app.py", "tests", "python-ast"),
    )
    assert index.outgoing("missing") == ()
    assert graph.index is index

    assert graph.add_edge(Edge("REQ-1", "ADR-1", "drives", "wikilink"))
    assert graph.index is index

    graph.add_node(Node("file:other.py", "file", "other.py", "other.py"))
    assert graph.add_edge(Edge("file:other.py", "file:app.py", "imports"))
    rebuilt = graph.index
    assert rebuilt is not index
    assert rebuilt.edge_count == 4
    assert graph.index is rebuilt


def test_graph_rejects_identity_collisions_but_merges_same_identity() -> None:
    graph = AtlasGraph()
    graph.add_node(Node("file:app.py", "file", "app.py", "app.py", {"owner": "scanner"}))
    graph.add_node(
        Node(
            "file:app.py",
            "file",
            "app.py",
            "app.py",
            {"owner": "scanner", "language": "Python"},
        )
    )
    assert graph.nodes["file:app.py"].metadata["language"] == "Python"

    with pytest.raises(ValueError, match="Graph node ID collision"):
        graph.add_node(
            Node(
                "file:app.py",
                "requirement",
                "Replace the file",
                "Requirements/Replace.md",
                {"owner": "user"},
            )
        )


def test_graph_round_trip_and_summary(tmp_path) -> None:
    graph = sample_graph()
    path = tmp_path / "graph.json"
    graph.save(path)
    restored = AtlasGraph.load(path)
    assert restored.summary() == {"decision": 1, "file": 1, "requirement": 1, "test": 1}
    assert restored.edges == graph.edges
    assert restored.find("app.py").id == "file:app.py"
    assert restored.orphans() == []
    payload = graph.to_dict()
    assert payload["schema_version"] == 4
    assert payload["relation_schema_version"] == 5
    drives = next(edge for edge in payload["edges"] if edge["relation"] == "drives")
    assert drives["category"] == "intent"
    assert drives["inverse"] == "driven-by"


def test_graph_atomic_save_preserves_previous_artifact_on_replace_failure(
    tmp_path, monkeypatch
) -> None:
    path = tmp_path / "graph.json"
    graph = sample_graph()
    graph.save(path)
    previous = path.read_bytes()
    graph.add_node(Node("file:new.py", "file", "new.py", "new.py"))

    def fail_replace(_source, _target) -> None:
        raise OSError("simulated replacement failure")

    monkeypatch.setattr(storage_module.os, "replace", fail_replace)
    with pytest.raises(OSError, match="simulated replacement failure"):
        graph.save(path)

    assert path.read_bytes() == previous
    assert list(tmp_path.glob(".graph.json.*.tmp")) == []


def test_find_reports_missing_and_ambiguous_targets() -> None:
    graph = sample_graph()
    graph.add_node(Node("file:nested/app.py", "file", "nested/app.py", "nested/app.py"))
    with pytest.raises(ValueError, match="ambiguous"):
        graph.find("app")
    with pytest.raises(ValueError, match="No graph node"):
        graph.find("nowhere")
    with pytest.raises(ValueError, match="empty"):
        graph.find("  ")


def test_impact_walks_both_directions_with_depth() -> None:
    graph = sample_graph()
    result = graph.impact("file:app.py", depth=2, direction="both")
    assert [(item.depth, item.node.id, item.direction) for item in result] == [
        (1, "ADR-1", "upstream"),
        (1, "file:test_app.py", "upstream"),
        (2, "REQ-1", "upstream"),
    ]
    assert graph.impact("REQ-1", depth=0) == []
    with pytest.raises(ValueError, match="Unknown direction"):
        graph.impact("REQ-1", direction="sideways")


def test_load_rejects_unknown_schema_and_invalid_edges(tmp_path) -> None:
    path = tmp_path / "graph.json"
    path.write_text(json.dumps({"schema_version": 9}), encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported"):
        AtlasGraph.load(path)

    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "nodes": [{"id": "a", "kind": "file", "label": "a"}],
                "edges": [{"source": "a", "target": "missing", "relation": "imports"}],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Invalid edge"):
        AtlasGraph.load(path)


@pytest.mark.parametrize(
    ("document", "message"),
    [
        ([], "expected a JSON object"),
        ({"schema_version": True}, "Unsupported graph schema"),
        ({"schema_version": 1, "nodes": {}, "edges": []}, "must be lists"),
        ({"schema_version": 1, "nodes": ["bad"], "edges": []}, "node at index 0"),
        ({"schema_version": 1, "nodes": [{}], "edges": []}, "node at index 0"),
        ({"schema_version": 1, "nodes": [], "edges": ["bad"]}, "edge at index 0"),
    ],
)
def test_load_rejects_malformed_graph_documents(tmp_path, document, message) -> None:
    path = tmp_path / "graph.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        AtlasGraph.load(path)

    path.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate JSON key"):
        AtlasGraph.load(path)


def test_load_migrates_schema_one_and_rejects_invalid_typed_relations(tmp_path) -> None:
    path = tmp_path / "graph.json"
    legacy = {
        "schema_version": 1,
        "nodes": [
            {"id": "REQ-1", "kind": "requirement", "label": "Requirement"},
            {"id": "ADR-1", "kind": "decision", "label": "Decision"},
        ],
        "edges": [
            {
                "source": "REQ-1",
                "target": "ADR-1",
                "relation": "drives",
                "evidence": "wikilink",
            }
        ],
    }
    path.write_text(json.dumps(legacy), encoding="utf-8")
    migrated = AtlasGraph.load(path)
    assert migrated.edges[0].category == "intent"
    assert migrated.to_dict()["schema_version"] == 4

    graph = AtlasGraph()
    graph.extend(
        [Node("REQ-1", "requirement", "Requirement"), Node("ADR-1", "decision", "Decision")]
    )
    with pytest.raises(ValueError, match="Unknown graph relation"):
        graph.add_edge(Edge("REQ-1", "ADR-1", "invented"))
    with pytest.raises(ValueError, match="Unknown graph relation"):
        graph.add_edge(Edge("missing", "also-missing", "invented"))

    invalid_v2 = {
        **legacy,
        "schema_version": 3,
        "relation_schema_version": 4,
        "relation_types": relation_catalog(),
        "edges": [{**legacy["edges"][0], "inverse": "wrong"}],
    }
    path.write_text(json.dumps(invalid_v2), encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid inverse"):
        AtlasGraph.load(path)

    invalid_v2["edges"] = legacy["edges"]
    invalid_v2["relation_types"] = []
    path.write_text(json.dumps(invalid_v2), encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid relation catalog"):
        AtlasGraph.load(path)

    prior_v2 = sample_graph().to_dict()
    prior_v2["schema_version"] = 2
    prior_v2["relation_schema_version"] = 3
    prior_v2["relation_types"] = [
        relation for relation in relation_catalog() if relation["name"] != "calls"
    ]
    path.write_text(json.dumps(prior_v2), encoding="utf-8")
    assert AtlasGraph.load(path).to_dict()["schema_version"] == 4
