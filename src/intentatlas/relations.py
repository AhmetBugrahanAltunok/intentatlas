from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class RelationType:
    """Stable semantics for a graph edge and its reverse traversal."""

    name: str
    inverse: str
    category: str
    description: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


_RELATION_TYPES = (
    RelationType(
        "addressed-by",
        "addresses",
        "delivery",
        "An issue is addressed by a pull request.",
    ),
    RelationType(
        "changes",
        "changed-by",
        "history",
        "A version-control delivery record changes an artifact.",
    ),
    RelationType(
        "calls",
        "called-by",
        "structure",
        "A code symbol directly calls another code symbol.",
    ),
    RelationType("defines", "defined-in", "structure", "A file defines a symbol."),
    RelationType("drives", "driven-by", "intent", "A requirement drives a decision."),
    RelationType(
        "implemented-by",
        "implements",
        "implementation",
        "An intent or delivery item is implemented by code.",
    ),
    RelationType("imports", "imported-by", "structure", "A file imports another file."),
    RelationType(
        "modifies",
        "modified-by",
        "history",
        "A commit directly modifies a symbol through validated diff evidence.",
    ),
    RelationType("proves", "proven-by", "evidence", "Evidence proves a linked claim."),
    RelationType("recorded-in", "records", "history", "Evidence is recorded in a commit."),
    RelationType("references", "referenced-by", "reference", "A note references another node."),
    RelationType("tests", "tested-by", "verification", "A test verifies code behavior."),
    RelationType("tracked-by", "tracks", "delivery", "A decision is tracked by an issue."),
)

RELATION_TYPES = {relation.name: relation for relation in _RELATION_TYPES}
USER_RELATIONS = frozenset(
    {"drives", "implemented-by", "proves", "recorded-in", "references", "tracked-by"}
)
RELATION_SCHEMA_VERSION = 4


def relation_type(name: str) -> RelationType:
    try:
        return RELATION_TYPES[name]
    except KeyError as exc:
        raise ValueError(f"Unknown graph relation: {name!r}") from exc


def relation_catalog() -> list[dict[str, str]]:
    return [RELATION_TYPES[name].to_dict() for name in sorted(RELATION_TYPES)]
