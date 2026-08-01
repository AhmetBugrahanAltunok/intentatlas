from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from ..models import Edge, Node


@dataclass(frozen=True, slots=True)
class AdapterContext:
    """Read-only repository view provided to built-in language adapters."""

    files: Mapping[str, Path]
    kinds: Mapping[str, str]
    max_parse_bytes: int

    def read_text(self, relative: str) -> str | None:
        path = self.files.get(relative)
        if path is None:
            return None
        try:
            if path.stat().st_size > self.max_parse_bytes:
                return None
            return path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None


@dataclass(frozen=True, slots=True)
class GraphFragment:
    """Deterministic structural output returned by one language adapter."""

    nodes: tuple[Node, ...] = ()
    edges: tuple[Edge, ...] = ()


class LanguageAdapter(Protocol):
    """Contract implemented by offline, non-executing language analyzers."""

    name: str
    suffixes: frozenset[str]
    cache_input_suffixes: frozenset[str]
    cache_version: int

    def scan(self, context: AdapterContext) -> GraphFragment: ...
