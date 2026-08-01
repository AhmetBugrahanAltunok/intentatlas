from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .adapters import GraphFragment, LanguageAdapter
from .models import Edge, Node
from .storage import atomic_write_text

CACHE_SCHEMA_VERSION = 1
MAX_CACHE_BYTES = 64 * 1024 * 1024
MAX_FRAGMENT_NODES = 500_000
MAX_FRAGMENT_EDGES = 2_000_000
MAX_CACHE_STRING = 4096
SAFE_ADAPTER_NAME = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?")
HEX_SHA256 = re.compile(r"[0-9a-f]{64}")
ADAPTER_EVIDENCE = {
    "go": {"filename-convention", "go-call-reference", "go-structural", "go-symbol-reference"},
    "javascript-typescript": {
        "filename-convention",
        "javascript-structural",
        "javascript-symbol-reference",
    },
    "python": {"filename-convention", "python-ast", "python-symbol-reference"},
}


@dataclass(frozen=True, slots=True)
class CacheLoad:
    fragment: GraphFragment | None
    reason: str


class AdapterFragmentCache:
    """Disposable, content-addressed storage for complete language-adapter fragments."""

    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        lexical = self.project_root / ".intentatlas" / "adapter-cache"
        resolved = lexical.resolve()
        self.root = lexical
        self.enabled = resolved == lexical and self.project_root in resolved.parents

    def load(
        self,
        adapter: LanguageAdapter,
        fingerprint: str,
        known_file_nodes: frozenset[str],
    ) -> CacheLoad:
        path = self._path(adapter.name)
        if path is None or not path.is_file() or path.is_symlink():
            return CacheLoad(None, "missing-or-unsafe")
        try:
            size = path.stat().st_size
            if size <= 0 or size > MAX_CACHE_BYTES:
                return CacheLoad(None, "invalid-size")
            raw = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
            fragment = _fragment_from_document(
                raw,
                adapter,
                fingerprint,
                known_file_nodes,
            )
        except (
            OSError,
            UnicodeDecodeError,
            json.JSONDecodeError,
            KeyError,
            TypeError,
            ValueError,
            RecursionError,
        ):
            return CacheLoad(None, "invalid")
        return CacheLoad(fragment, "hit")

    def store(
        self,
        adapter: LanguageAdapter,
        fingerprint: str,
        fragment: GraphFragment,
    ) -> bool:
        path = self._path(adapter.name)
        if path is None or path.is_symlink():
            return False
        canonical = _canonical_fragment(fragment)
        if canonical is None:
            return False
        document = {
            "schema_version": CACHE_SCHEMA_VERSION,
            "adapter": adapter.name,
            "cache_version": adapter.cache_version,
            "fingerprint": fingerprint,
            "fragment": {
                "nodes": [node.to_dict() for node in canonical.nodes],
                "edges": [edge.to_dict() for edge in canonical.edges],
            },
        }
        content = json.dumps(document, indent=2, ensure_ascii=False) + "\n"
        if len(content.encode("utf-8")) > MAX_CACHE_BYTES:
            return False
        try:
            atomic_write_text(path, content)
        except OSError:
            return False
        return True

    def _path(self, adapter_name: str) -> Path | None:
        if not self.enabled or SAFE_ADAPTER_NAME.fullmatch(adapter_name) is None:
            return None
        return self.root / f"{adapter_name}.json"


def _fragment_from_document(
    raw: Any,
    adapter: LanguageAdapter,
    fingerprint: str,
    known_file_nodes: frozenset[str],
) -> GraphFragment:
    if not isinstance(raw, dict) or set(raw) != {
        "schema_version",
        "adapter",
        "cache_version",
        "fingerprint",
        "fragment",
    }:
        raise ValueError("Invalid adapter cache document")
    if type(raw["schema_version"]) is not int or raw["schema_version"] != CACHE_SCHEMA_VERSION:
        raise ValueError("Unsupported adapter cache schema")
    if (
        raw["adapter"] != adapter.name
        or type(raw["cache_version"]) is not int
        or raw["cache_version"] != adapter.cache_version
    ):
        raise ValueError("Incompatible adapter cache contract")
    if (
        not isinstance(raw["fingerprint"], str)
        or HEX_SHA256.fullmatch(raw["fingerprint"]) is None
        or raw["fingerprint"] != fingerprint
    ):
        raise ValueError("Stale adapter cache fingerprint")
    fragment = raw["fragment"]
    if not isinstance(fragment, dict) or set(fragment) != {"nodes", "edges"}:
        raise ValueError("Invalid adapter cache fragment")
    node_values = fragment["nodes"]
    edge_values = fragment["edges"]
    if (
        not isinstance(node_values, list)
        or len(node_values) > MAX_FRAGMENT_NODES
        or not isinstance(edge_values, list)
        or len(edge_values) > MAX_FRAGMENT_EDGES
    ):
        raise ValueError("Unbounded adapter cache fragment")

    nodes = tuple(_strict_node(item) for item in node_values)
    edges = tuple(_strict_edge(item, adapter.name) for item in edge_values)
    if len({node.id for node in nodes}) != len(nodes):
        raise ValueError("Duplicate adapter cache node")
    edge_keys = {(edge.source, edge.target, edge.relation, edge.evidence) for edge in edges}
    if len(edge_keys) != len(edges):
        raise ValueError("Duplicate adapter cache edge")
    if tuple(sorted(nodes, key=lambda node: node.id)) != nodes:
        raise ValueError("Unordered adapter cache nodes")
    if tuple(sorted(edges, key=_edge_key)) != edges:
        raise ValueError("Unordered adapter cache edges")
    node_ids = {node.id for node in nodes}
    valid_endpoints = known_file_nodes | node_ids
    if any(f"file:{node.path}" not in known_file_nodes for node in nodes):
        raise ValueError("Cached symbol does not belong to a discovered file")
    if any(
        edge.source not in valid_endpoints or edge.target not in valid_endpoints
        for edge in edges
    ):
        raise ValueError("Cached edge references an unknown node")
    return GraphFragment(nodes=nodes, edges=edges)


def _strict_node(value: Any) -> Node:
    if not isinstance(value, dict) or not {"id", "kind", "label", "metadata"} <= set(value):
        raise ValueError("Invalid cached node")
    if set(value) - {"id", "kind", "label", "path", "metadata"}:
        raise ValueError("Unknown cached node field")
    for key in ("id", "kind", "label"):
        if not isinstance(value[key], str) or not value[key] or len(value[key]) > MAX_CACHE_STRING:
            raise ValueError("Invalid cached node string")
    path = value.get("path")
    if path is not None and (not isinstance(path, str) or len(path) > MAX_CACHE_STRING):
        raise ValueError("Invalid cached node path")
    metadata = value["metadata"]
    if (
        value["kind"] != "symbol"
        or not value["id"].startswith("symbol:")
        or path is None
        or value["id"] != f"symbol:{path}::{value['label']}"
        or not isinstance(metadata, dict)
        or not {"symbol_kind", "line", "owner"} <= set(metadata)
        or set(metadata) - {"symbol_kind", "line", "end_line", "owner"}
        or metadata["owner"] != "scanner"
        or not isinstance(metadata["symbol_kind"], str)
        or not metadata["symbol_kind"]
        or len(metadata["symbol_kind"]) > 64
        or type(metadata["line"]) is not int
        or metadata["line"] < 1
    ):
        raise ValueError("Invalid cached node metadata")
    end_line = metadata.get("end_line")
    if end_line is not None and (
        type(end_line) is not int or end_line < metadata["line"]
    ):
        raise ValueError("Invalid cached node span")
    return Node.from_dict(value)


def _strict_edge(value: Any, adapter_name: str) -> Edge:
    if not isinstance(value, dict) or set(value) != {
        "source",
        "target",
        "relation",
        "category",
        "inverse",
        "evidence",
    }:
        raise ValueError("Invalid cached edge")
    for key in value:
        if not isinstance(value[key], str) or not value[key] or len(value[key]) > MAX_CACHE_STRING:
            raise ValueError("Invalid cached edge string")
    edge = Edge.from_dict(value)
    if edge.relation not in {"calls", "defines", "imports", "tests"}:
        raise ValueError("Invalid cached adapter relation")
    if edge.evidence not in ADAPTER_EVIDENCE.get(adapter_name, set()):
        raise ValueError("Invalid cached adapter evidence")
    return edge


def _edge_key(edge: Edge) -> tuple[str, str, str, str]:
    return edge.source, edge.target, edge.relation, edge.evidence


def _canonical_fragment(fragment: GraphFragment) -> GraphFragment | None:
    nodes: dict[str, Node] = {}
    for node in fragment.nodes:
        existing = nodes.get(node.id)
        if existing is not None and existing != node:
            return None
        nodes[node.id] = node
    edges = {_edge_key(edge): edge for edge in fragment.edges}
    return GraphFragment(
        nodes=tuple(sorted(nodes.values(), key=lambda node: node.id)),
        edges=tuple(sorted(edges.values(), key=_edge_key)),
    )


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"Duplicate JSON key: {key}")
        value[key] = item
    return value
