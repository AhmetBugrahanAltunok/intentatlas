from __future__ import annotations

import json
from typing import Any

from .graph import AtlasGraph
from .models import Edge

DIFF_SCHEMA_VERSION = 1


def graph_diff(base: AtlasGraph, current: AtlasGraph) -> dict[str, Any]:
    base_nodes = {node_id: node.to_dict() for node_id, node in base.nodes.items()}
    current_nodes = {node_id: node.to_dict() for node_id, node in current.nodes.items()}
    added_node_ids = sorted(current_nodes.keys() - base_nodes.keys())
    removed_node_ids = sorted(base_nodes.keys() - current_nodes.keys())
    changed_node_ids = sorted(
        node_id
        for node_id in base_nodes.keys() & current_nodes.keys()
        if base_nodes[node_id] != current_nodes[node_id]
    )

    base_edges = {_edge_key(edge): edge.to_dict() for edge in base.edges}
    current_edges = {_edge_key(edge): edge.to_dict() for edge in current.edges}
    added_edge_keys = sorted(current_edges.keys() - base_edges.keys())
    removed_edge_keys = sorted(base_edges.keys() - current_edges.keys())

    result: dict[str, Any] = {
        "schema_version": DIFF_SCHEMA_VERSION,
        "has_changes": bool(
            added_node_ids
            or removed_node_ids
            or changed_node_ids
            or added_edge_keys
            or removed_edge_keys
        ),
        "summary": {
            "nodes_added": len(added_node_ids),
            "nodes_removed": len(removed_node_ids),
            "nodes_changed": len(changed_node_ids),
            "edges_added": len(added_edge_keys),
            "edges_removed": len(removed_edge_keys),
        },
        "nodes": {
            "added": [current_nodes[node_id] for node_id in added_node_ids],
            "removed": [base_nodes[node_id] for node_id in removed_node_ids],
            "changed": [
                {
                    "id": node_id,
                    "before": base_nodes[node_id],
                    "after": current_nodes[node_id],
                }
                for node_id in changed_node_ids
            ],
        },
        "edges": {
            "added": [current_edges[key] for key in added_edge_keys],
            "removed": [base_edges[key] for key in removed_edge_keys],
        },
    }
    return result


def render_graph_diff(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def _edge_key(edge: Edge) -> tuple[str, str, str, str]:
    return edge.source, edge.target, edge.relation, edge.evidence
