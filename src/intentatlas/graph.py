from __future__ import annotations

import json
from collections import Counter, deque
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from types import MappingProxyType
from typing import Any, TypeVar

from .models import Edge, ImpactRecord, Node
from .relations import RELATION_SCHEMA_VERSION, relation_catalog, relation_type
from .safe_io import read_bounded_regular_file
from .storage import atomic_write_text

_BucketKey = TypeVar("_BucketKey")
MAX_GRAPH_DOCUMENT_BYTES = 256 * 1024 * 1024
MAX_GRAPH_DOCUMENT_NODES = 1_000_000
MAX_GRAPH_DOCUMENT_EDGES = 4_000_000


@dataclass(frozen=True, slots=True)
class GraphIndex:
    """Deterministic immutable views over graph edge adjacency."""

    edge_count: int
    _outgoing_by_node: Mapping[str, tuple[Edge, ...]]
    _incoming_by_node: Mapping[str, tuple[Edge, ...]]
    _outgoing_by_relation: Mapping[tuple[str, str], tuple[Edge, ...]]
    _incoming_by_relation: Mapping[tuple[str, str], tuple[Edge, ...]]

    @classmethod
    def build(cls, edges: Iterable[Edge]) -> GraphIndex:
        ordered = tuple(
            sorted(
                edges,
                key=lambda edge: (edge.source, edge.target, edge.relation, edge.evidence),
            )
        )
        outgoing_by_node: dict[str, list[Edge]] = {}
        incoming_by_node: dict[str, list[Edge]] = {}
        outgoing_by_relation: dict[tuple[str, str], list[Edge]] = {}
        incoming_by_relation: dict[tuple[str, str], list[Edge]] = {}
        for edge in ordered:
            outgoing_by_node.setdefault(edge.source, []).append(edge)
            incoming_by_node.setdefault(edge.target, []).append(edge)
            outgoing_by_relation.setdefault((edge.source, edge.relation), []).append(edge)
            incoming_by_relation.setdefault((edge.target, edge.relation), []).append(edge)
        return cls(
            edge_count=len(ordered),
            _outgoing_by_node=_freeze_buckets(outgoing_by_node),
            _incoming_by_node=_freeze_buckets(incoming_by_node),
            _outgoing_by_relation=_freeze_buckets(outgoing_by_relation),
            _incoming_by_relation=_freeze_buckets(incoming_by_relation),
        )

    def outgoing(self, node_id: str, relation: str | None = None) -> tuple[Edge, ...]:
        if relation is None:
            return self._outgoing_by_node.get(node_id, ())
        return self._outgoing_by_relation.get((node_id, relation), ())

    def incoming(self, node_id: str, relation: str | None = None) -> tuple[Edge, ...]:
        if relation is None:
            return self._incoming_by_node.get(node_id, ())
        return self._incoming_by_relation.get((node_id, relation), ())


class AtlasGraph:
    """Language-neutral, deterministic graph of project intent and implementation."""

    schema_version = 4
    supported_schema_versions = {1, 2, 3, schema_version}

    def __init__(self) -> None:
        self.nodes: dict[str, Node] = {}
        self._edges: dict[tuple[str, str, str, str], Edge] = {}
        self._index: GraphIndex | None = None

    @property
    def edges(self) -> list[Edge]:
        return sorted(
            self._edges.values(),
            key=lambda edge: (edge.source, edge.target, edge.relation, edge.evidence),
        )

    @property
    def edge_count(self) -> int:
        return len(self._edges)

    @property
    def index(self) -> GraphIndex:
        if self._index is None:
            self._index = GraphIndex.build(self._edges.values())
        return self._index

    def add_node(self, node: Node) -> None:
        existing = self.nodes.get(node.id)
        if existing is not None and existing != node:
            same_identity = (
                existing.kind == node.kind
                and existing.label == node.label
                and existing.path == node.path
                and existing.metadata.get("owner") == node.metadata.get("owner")
            )
            if not same_identity:
                raise ValueError(
                    f"Graph node ID collision for {node.id!r}: "
                    f"{existing.kind} {existing.path or existing.label!r} conflicts with "
                    f"{node.kind} {node.path or node.label!r}"
                )
            merged_metadata = {**existing.metadata, **node.metadata}
            node = Node(
                id=node.id,
                kind=node.kind,
                label=node.label,
                path=node.path or existing.path,
                metadata=merged_metadata,
            )
        self.nodes[node.id] = node

    def add_edge(self, edge: Edge) -> bool:
        if edge.source == edge.target:
            return False
        relation_type(edge.relation)
        if edge.source not in self.nodes or edge.target not in self.nodes:
            return False
        key = (edge.source, edge.target, edge.relation, edge.evidence)
        is_new = key not in self._edges
        self._edges[key] = edge
        if is_new:
            self._index = None
        return True

    def extend(self, nodes: Iterable[Node], edges: Iterable[Edge] = ()) -> None:
        for node in nodes:
            self.add_node(node)
        for edge in edges:
            self.add_edge(edge)

    def degree(self, node_id: str) -> int:
        index = self.index
        return len(index.outgoing(node_id)) + len(index.incoming(node_id))

    def summary(self) -> dict[str, int]:
        counts = Counter(node.kind for node in self.nodes.values())
        return {kind: counts[kind] for kind in sorted(counts)}

    def orphans(self, kinds: set[str] | None = None) -> list[Node]:
        return sorted(
            (
                node
                for node in self.nodes.values()
                if (kinds is None or node.kind in kinds) and self.degree(node.id) == 0
            ),
            key=lambda node: (node.kind, node.label.casefold()),
        )

    def find(self, query: str) -> Node:
        needle = query.strip().casefold()
        if not needle:
            raise ValueError("Target cannot be empty")

        exact_groups = (
            [node for node in self.nodes.values() if node.id.casefold() == needle],
            [node for node in self.nodes.values() if node.label.casefold() == needle],
            [node for node in self.nodes.values() if (node.path or "").casefold() == needle],
        )
        for exact in exact_groups:
            if len(exact) == 1:
                return exact[0]
            if len(exact) > 1:
                raise ValueError(self._ambiguous_message(query, exact))

        partial = [
            node
            for node in self.nodes.values()
            if needle in node.label.casefold()
            or needle in node.id.casefold()
            or needle in (node.path or "").casefold()
        ]
        if len(partial) == 1:
            return partial[0]
        if not partial:
            raise ValueError(f"No graph node matches {query!r}")
        raise ValueError(self._ambiguous_message(query, partial))

    @staticmethod
    def _ambiguous_message(query: str, nodes: list[Node]) -> str:
        candidates = ", ".join(node.id for node in sorted(nodes, key=lambda item: item.id)[:8])
        suffix = " ..." if len(nodes) > 8 else ""
        return f"Target {query!r} is ambiguous: {candidates}{suffix}"

    def impact(
        self, node_id: str, *, depth: int = 2, direction: str = "both"
    ) -> list[ImpactRecord]:
        if node_id not in self.nodes:
            raise ValueError(f"Unknown node: {node_id}")
        if depth < 1:
            return []
        if direction not in {"both", "upstream", "downstream"}:
            raise ValueError(f"Unknown direction: {direction}")

        results: list[ImpactRecord] = []
        visited = {node_id}
        queue: deque[tuple[str, int]] = deque([(node_id, 0)])
        index = self.index

        while queue:
            current, current_depth = queue.popleft()
            if current_depth >= depth:
                continue
            candidates: list[tuple[str, Edge, str]] = []
            if direction in {"both", "downstream"}:
                candidates.extend(
                    (edge.target, edge, "downstream") for edge in index.outgoing(current)
                )
            if direction in {"both", "upstream"}:
                candidates.extend(
                    (edge.source, edge, "upstream") for edge in index.incoming(current)
                )
            for neighbor_id, edge, edge_direction in sorted(
                candidates, key=lambda value: (value[0], value[1].relation, value[2])
            ):
                if neighbor_id in visited:
                    continue
                visited.add(neighbor_id)
                next_depth = current_depth + 1
                results.append(
                    ImpactRecord(next_depth, self.nodes[neighbor_id], edge, edge_direction)
                )
                queue.append((neighbor_id, next_depth))
        return results

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "relation_schema_version": RELATION_SCHEMA_VERSION,
            "generated_at": datetime.now(UTC).isoformat(),
            "summary": self.summary(),
            "relation_types": relation_catalog(),
            "nodes": [self.nodes[node_id].to_dict() for node_id in sorted(self.nodes)],
            "edges": [edge.to_dict() for edge in self.edges],
        }

    def save(self, path: Path) -> None:
        atomic_write_text(
            path,
            json.dumps(self.to_dict(), indent=2, ensure_ascii=False) + "\n",
        )

    @classmethod
    def load(cls, path: Path) -> AtlasGraph:
        data = read_bounded_regular_file(path, MAX_GRAPH_DOCUMENT_BYTES)
        if data is None:
            raise ValueError(
                f"Cannot read graph at {path}: not a stable regular file within the "
                f"{MAX_GRAPH_DOCUMENT_BYTES}-byte limit"
            )
        try:
            value = json.loads(
                data.decode("utf-8"),
                object_pairs_hook=_unique_object,
            )
        except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
            raise ValueError(f"Cannot read graph at {path}: {exc}") from exc
        return cls.from_dict(value, source=str(path))

    @classmethod
    def from_dict(cls, value: Any, *, source: str = "graph document") -> AtlasGraph:
        if not isinstance(value, dict):
            raise ValueError(f"Invalid graph document at {source}: expected a JSON object")
        schema_version = value.get("schema_version")
        if type(schema_version) is not int or schema_version not in cls.supported_schema_versions:
            raise ValueError(f"Unsupported graph schema: {schema_version}")
        if (
            schema_version == cls.schema_version
            and value.get("relation_schema_version") != RELATION_SCHEMA_VERSION
        ):
            raise ValueError(
                f"Unsupported relation schema: {value.get('relation_schema_version')}"
            )
        if (
            schema_version == cls.schema_version
            and value.get("relation_types") != relation_catalog()
        ):
            raise ValueError("Invalid relation catalog")
        nodes = value.get("nodes", [])
        edges = value.get("edges", [])
        if not isinstance(nodes, list) or not isinstance(edges, list):
            raise ValueError(f"Invalid graph document at {source}: nodes and edges must be lists")
        if len(nodes) > MAX_GRAPH_DOCUMENT_NODES:
            raise ValueError(
                f"Invalid graph document at {source}: exceeds the "
                f"{MAX_GRAPH_DOCUMENT_NODES}-node limit"
            )
        if len(edges) > MAX_GRAPH_DOCUMENT_EDGES:
            raise ValueError(
                f"Invalid graph document at {source}: exceeds the "
                f"{MAX_GRAPH_DOCUMENT_EDGES}-edge limit"
            )
        if schema_version in {2, 3}:
            relation_schema_version = value.get("relation_schema_version")
            if (
                type(relation_schema_version) is not int
                or relation_schema_version < 1
                or relation_schema_version >= RELATION_SCHEMA_VERSION
            ):
                raise ValueError(f"Unsupported relation schema: {relation_schema_version}")
            _validate_legacy_relation_catalog(value.get("relation_types"), edges)
        graph = cls()
        for index, item in enumerate(nodes):
            if not isinstance(item, dict):
                raise ValueError(f"Invalid graph node at index {index}")
            try:
                node = Node.from_dict(item)
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"Invalid graph node at index {index}: {exc}") from exc
            graph.add_node(node)
        for index, item in enumerate(edges):
            if not isinstance(item, dict):
                raise ValueError(f"Invalid graph edge at index {index}")
            try:
                edge = Edge.from_dict(item)
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"Invalid graph edge at index {index}: {exc}") from exc
            if not graph.add_edge(edge):
                raise ValueError(f"Invalid edge in graph: {edge.source} -> {edge.target}")
        return graph


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"Duplicate JSON key: {key}")
        value[key] = item
    return value


def _validate_legacy_relation_catalog(catalog: Any, edges: list[Any]) -> None:
    if not isinstance(catalog, list) or not catalog:
        raise ValueError("Invalid relation catalog")
    current = {item["name"]: item for item in relation_catalog()}
    declared: set[str] = set()
    for item in catalog:
        if not isinstance(item, dict):
            raise ValueError("Invalid relation catalog")
        name = item.get("name")
        if not isinstance(name, str) or name in declared or item != current.get(name):
            raise ValueError("Invalid relation catalog")
        declared.add(name)
    for edge in edges:
        if not isinstance(edge, dict) or edge.get("relation") not in declared:
            raise ValueError("Invalid relation catalog")


def _freeze_buckets(
    values: dict[_BucketKey, list[Edge]],
) -> Mapping[_BucketKey, tuple[Edge, ...]]:
    return MappingProxyType({key: tuple(edges) for key, edges in values.items()})
