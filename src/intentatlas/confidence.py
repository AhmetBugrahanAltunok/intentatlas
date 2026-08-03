from __future__ import annotations

CONFIDENCE_RANK = {"low": 0, "medium": 1, "high": 2}


def confidence_for_score(score: int) -> str:
    """Return the canonical ADR-009 confidence band for a bounded score."""

    if score >= 85:
        return "high"
    if score >= 65:
        return "medium"
    return "low"
