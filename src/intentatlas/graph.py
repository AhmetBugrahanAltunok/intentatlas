from __future__ import annotations

import json
from collections import Counter, deque
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .models import Edge, ImpactRecord, Node
from .relations import RELATION_SCHEMA_VERSION, relation_catalog, relation_type


class AtlasGraph:
    """Language-neutral, deterministic graph of project intent and implementation."""

    schema_version = 2
    supported_schema_versions = {1, schema_version}

    def __init__(self) -> None:
        self.nodes: dict[str, Node] = {}
        self._edges: dict[tuple[str, str, str, str], Edge] = {}

    @property
    def edges(self) -> list[Edge]:
        return sorted(
            self._edges.values(),
            key=lambda edge: (edge.source, edge.target, edge.relation, edge.evidence),
        )

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
        self._edges[key] = edge
        return True

    def extend(self, nodes: Iterable[Node], edges: Iterable[Edge] = ()) -> None:
        for node in nodes:
            self.add_node(node)
        for edge in edges:
            self.add_edge(edge)

    def degree(self, node_id: str) -> int:
        return sum(
            edge.source == node_id or edge.target == node_id for edge in self._edges.values()
        )

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
        edges = self.edges

        while queue:
            current, current_depth = queue.popleft()
            if current_depth >= depth:
                continue
            candidates: list[tuple[str, Edge, str]] = []
            if direction in {"both", "downstream"}:
                candidates.extend(
                    (edge.target, edge, "downstream") for edge in edges if edge.source == current
                )
            if direction in {"both", "upstream"}:
                candidates.extend(
                    (edge.source, edge, "upstream") for edge in edges if edge.target == current
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
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    @classmethod
    def load(cls, path: Path) -> AtlasGraph:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Cannot read graph at {path}: {exc}") from exc
        schema_version = value.get("schema_version")
        if schema_version not in cls.supported_schema_versions:
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
        graph = cls()
        for item in value.get("nodes", []):
            graph.add_node(Node.from_dict(item))
        for item in value.get("edges", []):
            edge = Edge.from_dict(item)
            if not graph.add_edge(edge):
                raise ValueError(f"Invalid edge in graph: {edge.source} -> {edge.target}")
        return graph
