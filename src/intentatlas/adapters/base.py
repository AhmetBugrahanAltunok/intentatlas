from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from ..models import Edge, Node


@dataclass(frozen=True, slots=True)
class AdapterContext:
    """Read-only repository view provided to built-in language adapters."""

    files: Mapping[str, Path]
    kinds: Mapping[str, str]
    max_parse_bytes: int
    workspace_owners: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    source_roots: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    module_aliases: tuple[tuple[str, str, tuple[str, ...]], ...] = ()
    workspace_dependencies: frozenset[tuple[str, str]] = frozenset()

    def read_text(self, relative: str) -> str | None:
        path = self.files.get(relative)
        if path is None:
            return None
        try:
            if path.stat().st_size > self.max_parse_bytes:
                return None
            return path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None


@dataclass(frozen=True, slots=True)
class GraphFragment:
    """Deterministic structural output returned by one language adapter."""

    nodes: tuple[Node, ...] = ()
    edges: tuple[Edge, ...] = ()


def canonical_graph_fragment(
    nodes: Iterable[Node],
    edges: Iterable[Edge],
) -> GraphFragment:
    """Build stable adapter output while collapsing identical discoveries."""

    node_values: dict[str, Node] = {}
    for node in nodes:
        existing = node_values.get(node.id)
        if existing is not None and existing != node:
            raise ValueError(f"Conflicting adapter node identity: {node.id!r}")
        node_values[node.id] = node
    edge_values = {
        (edge.source, edge.target, edge.relation, edge.evidence): edge for edge in edges
    }
    return GraphFragment(
        nodes=tuple(sorted(node_values.values(), key=lambda node: node.id)),
        edges=tuple(
            sorted(
                edge_values.values(),
                key=lambda edge: (
                    edge.source,
                    edge.target,
                    edge.relation,
                    edge.evidence,
                ),
            )
        ),
    )


class LanguageAdapter(Protocol):
    """Contract implemented by offline, non-executing language analyzers."""

    name: str
    suffixes: frozenset[str]
    cache_input_suffixes: frozenset[str]
    cache_version: int
    evidence_kinds: frozenset[str]

    def scan(self, context: AdapterContext) -> GraphFragment: ...
