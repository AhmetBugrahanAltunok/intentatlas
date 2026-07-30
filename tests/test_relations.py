from __future__ import annotations

import pytest

from intentatlas.models import Edge
from intentatlas.relations import USER_RELATIONS, relation_catalog, relation_type


def test_relation_catalog_is_typed_deterministic_and_invertible() -> None:
    catalog = relation_catalog()
    assert [item["name"] for item in catalog] == sorted(item["name"] for item in catalog)
    assert relation_type("drives").inverse == "driven-by"
    assert relation_type("tests").category == "verification"
    assert "drives" in USER_RELATIONS
    assert "imports" not in USER_RELATIONS


def test_edge_serialization_derives_and_validates_relation_metadata() -> None:
    edge = Edge("REQ-1", "ADR-1", "drives", "wikilink")
    assert edge.to_dict()["category"] == "intent"
    assert edge.to_dict()["inverse"] == "driven-by"

    with pytest.raises(ValueError, match="Invalid category"):
        Edge.from_dict({**edge.to_dict(), "category": "structure"})

    with pytest.raises(ValueError, match="Unknown graph relation"):
        relation_type("invented")
