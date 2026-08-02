from __future__ import annotations

import re
from collections.abc import Set as AbstractSet
from dataclasses import dataclass
from types import MappingProxyType
from typing import TypeGuard

from ..models import Edge, Node
from .base import AdapterContext, GraphFragment, LanguageAdapter

ADAPTER_CONTRACT_VERSION = 1
MAX_FRAGMENT_NODES = 500_000
MAX_FRAGMENT_EDGES = 2_000_000
MAX_ADAPTER_EVIDENCE_KINDS = 32
SAFE_ADAPTER_NAME = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?")
SAFE_ADAPTER_SUFFIX = re.compile(r"\.[a-z0-9](?:[a-z0-9+_-]{0,14}[a-z0-9])?")
SAFE_EVIDENCE_KIND = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?")
ADAPTER_RELATIONS = frozenset({"calls", "defines", "imports", "tests"})


class AdapterConformanceError(ValueError):
    """An adapter definition or fragment violates the public adapter contract."""


@dataclass(frozen=True, slots=True)
class AdapterConformanceReport:
    """Successful result from the executable adapter conformance helper."""

    contract_version: int
    adapter: str
    node_count: int
    edge_count: int


def validate_adapter_definition(adapter: LanguageAdapter) -> None:
    """Validate stable adapter identity, inputs, cache, and evidence declarations."""

    name = getattr(adapter, "name", None)
    if not isinstance(name, str) or SAFE_ADAPTER_NAME.fullmatch(name) is None:
        raise AdapterConformanceError("adapter name must be a safe lowercase identifier")

    suffixes = getattr(adapter, "suffixes", None)
    inputs = getattr(adapter, "cache_input_suffixes", None)
    if not _valid_suffixes(suffixes):
        raise AdapterConformanceError(f"adapter {name!r} has invalid supported suffixes")
    if not _valid_suffixes(inputs) or not suffixes <= inputs:
        raise AdapterConformanceError(
            f"adapter {name!r} cache inputs must include every supported suffix"
        )

    cache_version = getattr(adapter, "cache_version", None)
    if type(cache_version) is not int or cache_version < 1 or cache_version > 2_147_483_647:
        raise AdapterConformanceError(f"adapter {name!r} has invalid cache version")

    evidence_kinds = getattr(adapter, "evidence_kinds", None)
    if (
        not isinstance(evidence_kinds, frozenset)
        or not evidence_kinds
        or len(evidence_kinds) > MAX_ADAPTER_EVIDENCE_KINDS
        or any(
            not isinstance(value, str) or SAFE_EVIDENCE_KIND.fullmatch(value) is None
            for value in evidence_kinds
        )
    ):
        raise AdapterConformanceError(f"adapter {name!r} has invalid evidence declarations")


def validate_adapter_fragment(
    adapter: LanguageAdapter,
    fragment: GraphFragment,
    known_file_nodes: AbstractSet[str],
) -> None:
    """Reject an unsafe or non-canonical adapter fragment before graph merge or cache use."""

    validate_adapter_definition(adapter)
    name = adapter.name
    if type(fragment) is not GraphFragment:
        raise AdapterConformanceError(f"adapter {name!r} must return GraphFragment")
    if len(fragment.nodes) > MAX_FRAGMENT_NODES or len(fragment.edges) > MAX_FRAGMENT_EDGES:
        raise AdapterConformanceError(f"adapter {name!r} emitted an unbounded fragment")
    if any(type(node) is not Node for node in fragment.nodes):
        raise AdapterConformanceError(f"adapter {name!r} emitted an invalid node value")
    if any(type(edge) is not Edge for edge in fragment.edges):
        raise AdapterConformanceError(f"adapter {name!r} emitted an invalid edge value")
    if tuple(sorted(fragment.nodes, key=lambda node: node.id)) != fragment.nodes:
        raise AdapterConformanceError(f"adapter {name!r} emitted unordered nodes")
    if tuple(sorted(fragment.edges, key=_edge_key)) != fragment.edges:
        raise AdapterConformanceError(f"adapter {name!r} emitted unordered edges")
    if len({node.id for node in fragment.nodes}) != len(fragment.nodes):
        raise AdapterConformanceError(f"adapter {name!r} emitted duplicate nodes")
    if len({_edge_key(edge) for edge in fragment.edges}) != len(fragment.edges):
        raise AdapterConformanceError(f"adapter {name!r} emitted duplicate edges")

    node_ids = {node.id for node in fragment.nodes}
    valid_endpoints = set(known_file_nodes) | node_ids
    for node in fragment.nodes:
        _validate_symbol_node(name, adapter.suffixes, node, known_file_nodes)
    for edge in fragment.edges:
        _validate_edge(name, adapter.evidence_kinds, edge, valid_endpoints)


def assert_adapter_conforms(
    adapter: LanguageAdapter,
    context: AdapterContext,
) -> AdapterConformanceReport:
    """Run the executable contract against an immutable fixture context twice."""

    validate_adapter_definition(adapter)
    if set(context.files) != set(context.kinds):
        raise AdapterConformanceError(
            f"adapter {adapter.name!r} fixture files and kinds must have identical keys"
        )
    if type(context.max_parse_bytes) is not int or context.max_parse_bytes < 1:
        raise AdapterConformanceError(
            f"adapter {adapter.name!r} fixture parse limit must be a positive integer"
        )
    frozen = AdapterContext(
        files=MappingProxyType(dict(context.files)),
        kinds=MappingProxyType(dict(context.kinds)),
        max_parse_bytes=context.max_parse_bytes,
    )
    first = adapter.scan(frozen)
    second = adapter.scan(frozen)
    if first != second:
        raise AdapterConformanceError(
            f"adapter {adapter.name!r} emitted nondeterministic repeated output"
        )
    validate_adapter_fragment(
        adapter,
        first,
        frozenset(f"file:{relative}" for relative in frozen.files),
    )
    return AdapterConformanceReport(
        contract_version=ADAPTER_CONTRACT_VERSION,
        adapter=adapter.name,
        node_count=len(first.nodes),
        edge_count=len(first.edges),
    )


def _valid_suffixes(value: object) -> TypeGuard[frozenset[str]]:
    return (
        isinstance(value, frozenset)
        and bool(value)
        and len(value) <= 64
        and all(
            isinstance(item, str)
            and item == item.casefold()
            and SAFE_ADAPTER_SUFFIX.fullmatch(item) is not None
            for item in value
        )
    )


def _validate_symbol_node(
    adapter_name: str,
    suffixes: frozenset[str],
    node: Node,
    known_file_nodes: AbstractSet[str],
) -> None:
    metadata = node.metadata
    if (
        node.kind != "symbol"
        or not node.id.startswith("symbol:")
        or node.path is None
        or node.id != f"symbol:{node.path}::{node.label}"
        or f"file:{node.path}" not in known_file_nodes
        or not any(node.path.casefold().endswith(suffix) for suffix in suffixes)
        or not isinstance(metadata, dict)
        or not {"symbol_kind", "line", "owner"} <= set(metadata)
        or set(metadata) - {
            "symbol_kind",
            "line",
            "end_line",
            "owner",
            "workspace_candidates",
            "workspace_owners",
            "workspace_state",
        }
        or metadata["owner"] != "scanner"
        or not isinstance(metadata["symbol_kind"], str)
        or not metadata["symbol_kind"]
        or len(metadata["symbol_kind"]) > 64
        or type(metadata["line"]) is not int
        or metadata["line"] < 1
    ):
        raise AdapterConformanceError(
            f"adapter {adapter_name!r} emitted an invalid symbol node: {node.id!r}"
        )
    end_line = metadata.get("end_line")
    if end_line is not None and (type(end_line) is not int or end_line < metadata["line"]):
        raise AdapterConformanceError(
            f"adapter {adapter_name!r} emitted an invalid symbol span: {node.id!r}"
        )
    workspace_fields = {"workspace_candidates", "workspace_owners", "workspace_state"}
    if workspace_fields & set(metadata):
        if not workspace_fields <= set(metadata):
            raise AdapterConformanceError(
                f"adapter {adapter_name!r} emitted incomplete workspace metadata: {node.id!r}"
            )
        if metadata["workspace_state"] not in {"aligned", "ambiguous"}:
            raise AdapterConformanceError(
                f"adapter {adapter_name!r} emitted invalid workspace state: {node.id!r}"
            )
        if any(
            not isinstance(metadata[key], list)
            or any(not isinstance(item, str) or not item for item in metadata[key])
            for key in ("workspace_candidates", "workspace_owners")
        ):
            raise AdapterConformanceError(
                f"adapter {adapter_name!r} emitted invalid workspace candidates: {node.id!r}"
            )


def _validate_edge(
    adapter_name: str,
    evidence_kinds: frozenset[str],
    edge: Edge,
    valid_endpoints: set[str],
) -> None:
    if edge.source == edge.target:
        raise AdapterConformanceError(f"adapter {adapter_name!r} emitted a self edge")
    if edge.source not in valid_endpoints or edge.target not in valid_endpoints:
        raise AdapterConformanceError(
            f"adapter {adapter_name!r} emitted an edge with an unknown endpoint"
        )
    if edge.relation not in ADAPTER_RELATIONS or edge.evidence not in evidence_kinds:
        raise AdapterConformanceError(
            f"adapter {adapter_name!r} emitted undeclared edge semantics"
        )
    source_kind = _endpoint_kind(edge.source)
    target_kind = _endpoint_kind(edge.target)
    valid_shape = {
        "calls": source_kind == "symbol" and target_kind == "symbol",
        "defines": source_kind == "file" and target_kind == "symbol",
        "imports": source_kind == "file" and target_kind in {"file", "symbol"},
        "tests": source_kind == "file" and target_kind in {"file", "symbol"},
    }[edge.relation]
    if not valid_shape:
        raise AdapterConformanceError(
            f"adapter {adapter_name!r} emitted invalid {edge.relation!r} endpoints"
        )
    if edge.relation == "defines":
        symbol_path = edge.target.removeprefix("symbol:").split("::", 1)[0]
        if edge.source != f"file:{symbol_path}":
            raise AdapterConformanceError(
                f"adapter {adapter_name!r} emitted a cross-file definition edge"
            )


def _endpoint_kind(node_id: str) -> str:
    if node_id.startswith("file:"):
        return "file"
    if node_id.startswith("symbol:"):
        return "symbol"
    return "other"


def _edge_key(edge: Edge) -> tuple[str, str, str, str]:
    return edge.source, edge.target, edge.relation, edge.evidence
