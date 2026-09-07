from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Protocol

from .models import Node


class HunkSpan(Protocol):
    @property
    def path(self) -> str: ...

    @property
    def start(self) -> int: ...

    @property
    def count(self) -> int: ...


@dataclass(frozen=True, slots=True)
class SymbolSpanMatch:
    symbol_ids: tuple[str, ...]
    complete: bool


def valid_symbol_span(node: Node) -> bool:
    start = node.metadata.get("line")
    end = node.metadata.get("end_line")
    return (
        node.kind == "symbol"
        and isinstance(start, int)
        and not isinstance(start, bool)
        and isinstance(end, int)
        and not isinstance(end, bool)
        and start >= 1
        and end >= start
    )


def symbol_spans_by_path(nodes: Iterable[Node]) -> dict[str, tuple[Node, ...]]:
    """Group validated symbol spans into deterministic path-local indexes."""

    grouped: defaultdict[str, list[Node]] = defaultdict(list)
    for node in nodes:
        if node.path is None or not valid_symbol_span(node):
            continue
        grouped[node.path].append(node)
    return {
        path: tuple(sorted(values, key=_symbol_span_sort_key))
        for path, values in sorted(grouped.items())
    }


def map_hunks_to_most_specific_symbols(
    hunks: Iterable[HunkSpan],
    symbols_by_path: Mapping[str, Iterable[Node]],
) -> SymbolSpanMatch:
    """Map hunks to innermost overlapping symbols and report full hunk coverage."""

    hunk_items = tuple(hunks)
    modified: set[str] = set()
    complete = bool(hunk_items)
    for hunk in hunk_items:
        if hunk.start < 1 or hunk.count <= 0:
            # A deletion has no current-side lines to attribute to a symbol.
            complete = False
            continue
        hunk_end = hunk.start + hunk.count - 1
        candidates = tuple(
            symbol
            for symbol in symbols_by_path.get(hunk.path, ())
            if valid_symbol_span(symbol)
            and int(symbol.metadata["line"]) <= hunk_end
            and int(symbol.metadata["end_line"]) >= hunk.start
        )
        if not _covers_range(
            hunk.start, hunk_end, (_symbol_span(symbol) for symbol in candidates)
        ):
            complete = False
        for candidate in candidates:
            start, end = _symbol_span(candidate)
            descendants = (
                _symbol_span(other)
                for other in candidates
                if start <= _symbol_span(other)[0]
                and end >= _symbol_span(other)[1]
                and (start, end) != _symbol_span(other)
            )
            # Retain the parent only for changed lines not owned by descendants.
            # Work on interval boundaries, never on every line in a large hunk.
            if not _covers_range(max(start, hunk.start), min(end, hunk_end), descendants):
                modified.add(candidate.id)
    return SymbolSpanMatch(tuple(sorted(modified)), complete)


def _covers_range(start: int, end: int, spans: Iterable[tuple[int, int]]) -> bool:
    cursor = start
    for first, last in sorted(spans):
        if first > cursor:
            return False
        cursor = max(cursor, last + 1)
        if cursor > end:
            return True
    return False


def _symbol_span(node: Node) -> tuple[int, int]:
    return int(node.metadata["line"]), int(node.metadata["end_line"])


def _symbol_span_sort_key(node: Node) -> tuple[int, int, str]:
    start, end = _symbol_span(node)
    return start, end, node.id
