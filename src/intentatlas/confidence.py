from __future__ import annotations

CONFIDENCE_RANK = {"low": 0, "medium": 1, "high": 2}
LOW_CONFIDENCE_GUIDANCE = (
    "Low is exploratory discovery mode: weak evidence can create high fan-out and low precision. "
    "Use medium or higher for automated CI selection."
)
STATIC_REFERENCE_GUIDANCE = (
    "An exact static direct reference scores 80/medium; high is reserved for stronger evidence, "
    "such as a test directly present in the changed set."
)


def confidence_for_score(score: int) -> str:
    """Return the canonical ADR-009 confidence band for a bounded score."""

    if score >= 85:
        return "high"
    if score >= 65:
        return "medium"
    return "low"
