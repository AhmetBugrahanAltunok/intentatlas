from __future__ import annotations

import copy
import json
import random
from pathlib import Path
from typing import Any

import pytest

from intentatlas.graph import AtlasGraph
from intentatlas.models import Edge, Node
from intentatlas.open_evidence import load_json_report

SEEDS = tuple(range(32))


@pytest.mark.parametrize("seed", SEEDS)
def test_generated_graphs_round_trip_with_stable_adjacency(seed: int, tmp_path: Path) -> None:
    randomizer = random.Random(seed)
    graph = AtlasGraph()
    node_count = randomizer.randint(2, 40)
    nodes = [
        Node(
            id=f"file:src/module_{index}.py",
            kind="file",
            label=f"module_{index}.py",
            path=f"src/module_{index}.py",
            metadata={"owner": "scanner", "ordinal": index},
        )
        for index in range(node_count)
    ]
    randomizer.shuffle(nodes)
    graph.extend(nodes)
    expected_edges: set[tuple[str, str, str, str]] = set()
    for _ in range(randomizer.randint(node_count, node_count * 4)):
        source, target = randomizer.sample(nodes, 2)
        relation = randomizer.choice(("imports", "calls", "tests", "references"))
        evidence = randomizer.choice(("property-fixture", "property-observation"))
        graph.add_edge(Edge(source.id, target.id, relation, evidence))
        expected_edges.add((source.id, target.id, relation, evidence))

    path = tmp_path / f"graph-{seed}.json"
    graph.save(path)
    restored = AtlasGraph.load(path)

    assert set(restored.nodes) == {node.id for node in nodes}
    assert {
        (edge.source, edge.target, edge.relation, edge.evidence) for edge in restored.edges
    } == expected_edges
    assert restored.edges == sorted(
        restored.edges,
        key=lambda edge: (edge.source, edge.target, edge.relation, edge.evidence),
    )
    for node in nodes:
        assert restored.index.outgoing(node.id) == tuple(
            edge for edge in restored.edges if edge.source == node.id
        )
        assert restored.index.incoming(node.id) == tuple(
            edge for edge in restored.edges if edge.target == node.id
        )


@pytest.mark.parametrize("seed", SEEDS)
def test_graph_document_mutations_fail_closed_or_preserve_invariants(
    seed: int, tmp_path: Path
) -> None:
    graph = AtlasGraph()
    graph.extend(
        [
            Node("file:a.py", "file", "a.py", "a.py", {"owner": "scanner"}),
            Node("file:b.py", "file", "b.py", "b.py", {"owner": "scanner"}),
        ],
        [Edge("file:a.py", "file:b.py", "imports", "python-ast")],
    )
    document = graph.to_dict()
    randomizer = random.Random(seed)
    mutations = (
        lambda value: value.__setitem__("schema_version", randomizer.choice([None, True, -1, 99])),
        lambda value: value.__setitem__("relation_schema_version", 99),
        lambda value: value.__setitem__("relation_types", []),
        lambda value: value.__setitem__("nodes", randomizer.choice([None, {}, "nodes"])),
        lambda value: value.__setitem__("edges", randomizer.choice([None, {}, "edges"])),
        lambda value: value["nodes"][0].__setitem__("id", "file:b.py"),
        lambda value: value["nodes"][0].pop("label"),
        lambda value: value["edges"][0].__setitem__("source", "file:missing.py"),
        lambda value: value["edges"][0].__setitem__("target", "file:a.py"),
        lambda value: value["edges"][0].__setitem__("relation", "unknown-relation"),
        lambda value: value["edges"][0].__setitem__("inverse", "wrong"),
    )
    mutation = randomizer.choice(mutations)
    mutated = copy.deepcopy(document)
    mutation(mutated)
    path = tmp_path / f"mutated-{seed}.json"
    path.write_text(json.dumps(mutated), encoding="utf-8")

    try:
        restored = AtlasGraph.load(path)
    except ValueError:
        return

    assert all(edge.source in restored.nodes for edge in restored.edges)
    assert all(edge.target in restored.nodes for edge in restored.edges)
    assert all(edge.source != edge.target for edge in restored.edges)
    assert len(restored.nodes) == len(set(restored.nodes))


@pytest.mark.parametrize("seed", SEEDS)
def test_generated_json_evidence_round_trips_without_parser_side_effects(
    seed: int, tmp_path: Path
) -> None:
    randomizer = random.Random(seed)
    value = _json_value(randomizer, depth=0)
    path = tmp_path / f"evidence-{seed}.json"
    before = json.dumps(value, ensure_ascii=False, sort_keys=True)
    path.write_text(before, encoding="utf-8")

    loaded = load_json_report(path, path.name)

    assert loaded == value
    assert path.read_text(encoding="utf-8") == before


@pytest.mark.parametrize(
    "payload",
    [
        b'{"duplicate": 1, "duplicate": 2}',
        b'{"constant": NaN}',
        b'{"unterminated": ',
        b'\xff\xfe\x00\x00',
        ("[" * 20 + "0" + "]" * 20).encode(),
    ],
)
def test_hostile_json_corpus_is_rejected_as_a_bounded_value_error(
    payload: bytes, tmp_path: Path
) -> None:
    path = tmp_path / "hostile.json"
    path.write_bytes(payload)

    with pytest.raises(ValueError):
        load_json_report(path, path.name)


def _json_value(randomizer: random.Random, depth: int) -> Any:
    scalar = randomizer.choice(
        [None, True, False, randomizer.randint(-10_000, 10_000), "intent-çğü-🗺️"]
    )
    if depth >= 4:
        return scalar
    kind = randomizer.randrange(3)
    if kind == 0:
        return scalar
    if kind == 1:
        return [_json_value(randomizer, depth + 1) for _ in range(randomizer.randrange(5))]
    return {
        f"key-{depth}-{index}": _json_value(randomizer, depth + 1)
        for index in range(randomizer.randrange(5))
    }
