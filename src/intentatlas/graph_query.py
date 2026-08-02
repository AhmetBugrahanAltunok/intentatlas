from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any

from .graph import AtlasGraph
from .models import Edge, Node

MAX_QUERY_TEXT = 512
MAX_QUERY_NODES = 500
MAX_QUERY_EDGES = 2_000
MAX_QUERY_DEPTH = 8
MAX_QUERY_VISITED = 5_000
MAX_QUERY_PATHS = 20
PROOF_KINDS = frozenset(
    {"commit", "coverage", "evidence", "pull-request", "test", "test-result"}
)


@dataclass(frozen=True, slots=True)
class GraphQuerySnapshot:
    graph: AtlasGraph
    snapshot: str

    def overview(self, *, node_limit: int = 240, edge_limit: int = 900) -> dict[str, Any]:
        node_limit = _bounded(node_limit, "node_limit", 1, MAX_QUERY_NODES)
        edge_limit = _bounded(edge_limit, "edge_limit", 0, MAX_QUERY_EDGES)
        grouped: dict[str, list[Node]] = {}
        for node in self.graph.nodes.values():
            grouped.setdefault(node.kind, []).append(node)
        for values in grouped.values():
            values.sort(key=lambda node: (-self.graph.degree(node.id), node.id))
        groups = [grouped[kind] for kind in sorted(grouped)]
        selected: list[Node] = []
        offset = 0
        while len(selected) < node_limit:
            added = False
            for values in groups:
                if offset >= len(values):
                    continue
                selected.append(values[offset])
                added = True
                if len(selected) == node_limit:
                    break
            if not added:
                break
            offset += 1
        return self._window(selected, edge_limit=edge_limit)

    def search(self, query: str, *, limit: int = 20) -> dict[str, Any]:
        needle = _query(query)
        limit = _bounded(limit, "limit", 1, 100)
        matches = [
            node
            for node in self.graph.nodes.values()
            if needle in f"{node.id} {node.label} {node.path or ''} {node.kind}".casefold()
        ]
        matches.sort(
            key=lambda node: (
                0 if node.id.casefold() == needle else 1,
                0 if node.label.casefold() == needle else 1,
                node.id,
            )
        )
        selected = matches[:limit]
        return self._response(nodes=selected, edges=[], matched_nodes=len(matches))

    def neighborhood(
        self,
        node_id: str,
        *,
        depth: int = 2,
        node_limit: int = 240,
        edge_limit: int = 900,
    ) -> dict[str, Any]:
        node_id = _node_id(node_id)
        depth = _bounded(depth, "depth", 0, MAX_QUERY_DEPTH)
        node_limit = _bounded(node_limit, "node_limit", 1, MAX_QUERY_NODES)
        edge_limit = _bounded(edge_limit, "edge_limit", 0, MAX_QUERY_EDGES)
        if node_id not in self.graph.nodes:
            raise ValueError(f"Unknown graph node: {node_id}")
        included = {node_id}
        queue: deque[tuple[str, int]] = deque([(node_id, 0)])
        while queue and len(included) < node_limit:
            current, current_depth = queue.popleft()
            if current_depth >= depth:
                continue
            adjacent = {
                edge.target for edge in self.graph.index.outgoing(current)
            } | {edge.source for edge in self.graph.index.incoming(current)}
            for neighbor in sorted(adjacent):
                if neighbor in included:
                    continue
                included.add(neighbor)
                queue.append((neighbor, current_depth + 1))
                if len(included) == node_limit:
                    break
        selected = [self.graph.nodes[node] for node in sorted(included)]
        return self._window(selected, edge_limit=edge_limit)

    def paths(
        self,
        start: str,
        *,
        target: str | None = None,
        depth: int = 6,
        visited_limit: int = 800,
        result_limit: int = 6,
    ) -> dict[str, Any]:
        start = _node_id(start)
        if start not in self.graph.nodes:
            raise ValueError(f"Unknown graph node: {start}")
        if target is not None:
            target = _node_id(target)
            if target not in self.graph.nodes:
                raise ValueError(f"Unknown graph node: {target}")
        depth = _bounded(depth, "depth", 1, MAX_QUERY_DEPTH)
        visited_limit = _bounded(visited_limit, "visited_limit", 1, MAX_QUERY_VISITED)
        result_limit = _bounded(result_limit, "result_limit", 1, MAX_QUERY_PATHS)
        visited = {start}
        queue: deque[tuple[str, tuple[str, ...], tuple[str, ...]]] = deque(
            [(start, (start,), ())]
        )
        results: list[dict[str, Any]] = []
        while queue and len(visited) < visited_limit and len(results) < result_limit:
            current, nodes, relations = queue.popleft()
            if len(relations) >= depth:
                continue
            hops: list[tuple[str, str]] = []
            hops.extend(
                (edge.target, edge.relation) for edge in self.graph.index.outgoing(current)
            )
            hops.extend(
                (edge.source, edge.inverse) for edge in self.graph.index.incoming(current)
            )
            for neighbor, relation in sorted(hops):
                if neighbor in visited:
                    continue
                visited.add(neighbor)
                next_nodes = (*nodes, neighbor)
                next_relations = (*relations, relation)
                destination = self.graph.nodes[neighbor]
                matched = (
                    neighbor == target
                    if target is not None
                    else destination.kind in PROOF_KINDS
                )
                if matched:
                    results.append(
                        {
                            "nodes": list(next_nodes),
                            "relations": list(next_relations),
                            "destination": destination.to_dict(),
                        }
                    )
                if len(results) == result_limit or len(visited) == visited_limit:
                    break
                queue.append((neighbor, next_nodes, next_relations))
        return {
            "schema_version": 1,
            "snapshot": self.snapshot,
            "total_counts": {
                "nodes": len(self.graph.nodes),
                "edges": self.graph.edge_count,
            },
            "returned_counts": {"paths": len(results)},
            "omitted_counts": {
                "paths": 1 if queue and len(results) == result_limit else 0,
                "visited": max(0, len(visited) - visited_limit),
            },
            "work": {"visited_nodes": len(visited), "max_visited_nodes": visited_limit},
            "paths": results,
        }

    def _window(self, nodes: list[Node], *, edge_limit: int) -> dict[str, Any]:
        ids = {node.id for node in nodes}
        edges: dict[tuple[str, str, str, str], Edge] = {}
        for node_id in sorted(ids):
            for edge in self.graph.index.outgoing(node_id):
                if edge.target in ids:
                    edges[(edge.source, edge.target, edge.relation, edge.evidence)] = edge
        selected_edges = [edges[key] for key in sorted(edges)[:edge_limit]]
        return self._response(nodes=nodes, edges=selected_edges, matched_edges=len(edges))

    def _response(
        self,
        *,
        nodes: list[Node],
        edges: list[Edge],
        matched_nodes: int | None = None,
        matched_edges: int | None = None,
    ) -> dict[str, Any]:
        node_total = len(self.graph.nodes) if matched_nodes is None else matched_nodes
        edge_total = self.graph.edge_count if matched_edges is None else matched_edges
        return {
            "schema_version": 1,
            "snapshot": self.snapshot,
            "total_counts": {
                "nodes": len(self.graph.nodes),
                "edges": self.graph.edge_count,
            },
            "matched_counts": {"nodes": node_total, "edges": edge_total},
            "returned_counts": {"nodes": len(nodes), "edges": len(edges)},
            "omitted_counts": {
                "nodes": max(0, node_total - len(nodes)),
                "edges": max(0, edge_total - len(edges)),
            },
            "nodes": [node.to_dict() for node in sorted(nodes, key=lambda item: item.id)],
            "edges": [edge.to_dict() for edge in edges],
        }


def _bounded(value: int, label: str, minimum: int, maximum: int) -> int:
    if type(value) is not int or value < minimum or value > maximum:
        raise ValueError(f"{label} must be between {minimum} and {maximum}")
    return value


def _query(value: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > MAX_QUERY_TEXT:
        raise ValueError("query must be a non-empty bounded string")
    return value.strip().casefold()


def _node_id(value: str) -> str:
    if not isinstance(value, str) or not value or len(value) > MAX_QUERY_TEXT:
        raise ValueError("node id must be a non-empty bounded string")
    return value
