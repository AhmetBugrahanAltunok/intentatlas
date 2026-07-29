from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class Node:
    """A stable entity in the project intent graph."""

    id: str
    kind: str
    label: str
    path: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        value: dict[str, Any] = {
            "id": self.id,
            "kind": self.kind,
            "label": self.label,
            "metadata": self.metadata,
        }
        if self.path is not None:
            value["path"] = self.path
        return value

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> Node:
        return cls(
            id=str(value["id"]),
            kind=str(value["kind"]),
            label=str(value["label"]),
            path=str(value["path"]) if value.get("path") is not None else None,
            metadata=dict(value.get("metadata", {})),
        )


@dataclass(frozen=True, slots=True)
class Edge:
    """A directed, evidence-bearing relationship between two nodes."""

    source: str
    target: str
    relation: str
    evidence: str = "scanner"

    def to_dict(self) -> dict[str, str]:
        return {
            "source": self.source,
            "target": self.target,
            "relation": self.relation,
            "evidence": self.evidence,
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> Edge:
        return cls(
            source=str(value["source"]),
            target=str(value["target"]),
            relation=str(value["relation"]),
            evidence=str(value.get("evidence", "scanner")),
        )


@dataclass(frozen=True, slots=True)
class ImpactRecord:
    depth: int
    node: Node
    edge: Edge
    direction: str
