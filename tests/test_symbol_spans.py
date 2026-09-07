from __future__ import annotations

from dataclasses import dataclass

import pytest

from intentatlas.models import Node
from intentatlas.symbol_spans import (
    map_hunks_to_most_specific_symbols,
    symbol_spans_by_path,
)


@dataclass(frozen=True, slots=True)
class ExampleHunk:
    path: str
    start: int
    count: int


def symbol(node_id: str, start: int, end: int, path: str = "src/app.py") -> Node:
    return Node(
        node_id,
        "symbol",
        node_id,
        path=path,
        metadata={"line": start, "end_line": end},
    )


def test_span_mapping_selects_innermost_symbols_deterministically() -> None:
    parent = symbol("symbol:parent", 1, 30)
    first = symbol("symbol:first", 3, 8)
    second = symbol("symbol:second", 15, 20)
    equal_a = symbol("symbol:equal-a", 24, 26)
    equal_b = symbol("symbol:equal-b", 24, 26)
    spans = symbol_spans_by_path([second, equal_b, parent, first, equal_a])

    match = map_hunks_to_most_specific_symbols(
        (
            ExampleHunk("src/app.py", 4, 1),
            ExampleHunk("src/app.py", 18, 1),
            ExampleHunk("src/app.py", 25, 1),
        ),
        spans,
    )

    assert match.symbol_ids == (
        "symbol:equal-a",
        "symbol:equal-b",
        "symbol:first",
        "symbol:second",
    )
    assert match.complete is True


def test_span_mapping_preserves_partial_matches_but_marks_incomplete_coverage() -> None:
    spans = symbol_spans_by_path(
        [
            symbol("symbol:valid", 3, 8),
            Node(
                "symbol:invalid",
                "symbol",
                "invalid",
                path="src/app.py",
                metadata={"line": True, "end_line": 10},
            ),
        ]
    )

    partial = map_hunks_to_most_specific_symbols(
        (
            ExampleHunk("src/app.py", 4, 1),
            ExampleHunk("src/app.py", 40, 1),
        ),
        spans,
    )
    empty = map_hunks_to_most_specific_symbols((), spans)

    assert tuple(spans) == ("src/app.py",)
    assert [node.id for node in spans["src/app.py"]] == ["symbol:valid"]
    assert partial.symbol_ids == ("symbol:valid",)
    assert partial.complete is False
    assert empty.symbol_ids == ()
    assert empty.complete is False


@pytest.mark.parametrize(
    ("start", "count", "ranges"),
    [
        (1, 4, [(3, 8)]),
        (7, 4, [(3, 8)]),
        (3, 8, [(3, 5), (7, 10)]),
        (0, 0, [(1, 8)]),
        (4, 0, [(1, 8)]),
    ],
)
def test_partial_and_deletion_ranges_never_claim_complete_coverage(
    start: int, count: int, ranges: list[tuple[int, int]]
) -> None:
    spans = symbol_spans_by_path(
        symbol(f"symbol:{index}", first, last)
        for index, (first, last) in enumerate(ranges)
    )
    result = map_hunks_to_most_specific_symbols(
        [ExampleHunk("src/app.py", start, count)], spans
    )
    assert result.complete is False
    if count == 0:
        assert result.symbol_ids == ()


def test_nested_ownership_is_invariant_to_hunk_segmentation_and_symbol_order() -> None:
    nodes = [symbol("parent", 1, 30), symbol("child", 5, 10), symbol("nested", 7, 8)]
    expected = ("child", "nested", "parent")
    for ordered in (nodes, list(reversed(nodes))):
        spans = symbol_spans_by_path(ordered)
        for hunks in (
            [ExampleHunk("src/app.py", 2, 10)],
            [ExampleHunk("src/app.py", start, 1) for start in range(2, 12)],
        ):
            result = map_hunks_to_most_specific_symbols(hunks, spans)
            assert result.symbol_ids == expected
            assert result.complete is True


def test_adjacent_symbols_cover_a_large_range_without_per_line_expansion() -> None:
    spans = symbol_spans_by_path(
        [symbol("first", 1, 500_000_000), symbol("second", 500_000_001, 1_000_000_000)]
    )
    result = map_hunks_to_most_specific_symbols(
        [ExampleHunk("src/app.py", 1, 1_000_000_000)], spans
    )
    assert result.symbol_ids == ("first", "second")
    assert result.complete is True


def test_deletion_keeps_independent_positive_symbol_evidence_without_completeness() -> None:
    spans = symbol_spans_by_path([symbol("selected", 1, 8)])
    result = map_hunks_to_most_specific_symbols(
        [ExampleHunk("src/app.py", 2, 1), ExampleHunk("src/app.py", 4, 0)], spans
    )
    assert result.symbol_ids == ("selected",)
    assert result.complete is False
