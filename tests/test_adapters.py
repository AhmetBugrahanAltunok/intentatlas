from __future__ import annotations

from pathlib import Path
from types import MappingProxyType

import pytest

import intentatlas.scanner as scanner_module
from intentatlas.adapters import AdapterContext, GraphFragment, JavaScriptAdapter, PythonAdapter
from intentatlas.config import ProjectConfig
from intentatlas.models import Edge
from intentatlas.scanner import scan_repository


def test_adapter_contract_is_offline_bounded_and_immutable(tmp_path: Path) -> None:
    source = tmp_path / "small.ts"
    source.write_text("export const value = () => 1;\n", encoding="utf-8")
    oversized = tmp_path / "large.ts"
    oversized.write_text("x" * 40, encoding="utf-8")
    files = MappingProxyType({"small.ts": source, "large.ts": oversized})
    kinds = MappingProxyType({"small.ts": "file", "large.ts": "file"})
    context = AdapterContext(files=files, kinds=kinds, max_parse_bytes=32)

    assert context.read_text("small.ts") == "export const value = () => 1;\n"
    assert context.read_text("large.ts") is None
    assert context.read_text("missing.ts") is None
    assert GraphFragment().nodes == ()
    assert PythonAdapter().suffixes == frozenset({".py"})
    assert JavaScriptAdapter().suffixes == frozenset({".js", ".jsx", ".ts", ".tsx"})


def test_scanner_rejects_invalid_adapter_fragments(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "README.md").write_text("# Fixture\n", encoding="utf-8")

    class InvalidAdapter:
        name = "invalid"
        suffixes = frozenset({".md"})

        def scan(self, _context: AdapterContext) -> GraphFragment:
            return GraphFragment(
                edges=(Edge("file:README.md", "file:missing.ts", "imports", "invalid"),)
            )

    monkeypatch.setattr(scanner_module, "BUILTIN_ADAPTERS", (InvalidAdapter(),))
    with pytest.raises(ValueError, match="emitted invalid edge"):
        scan_repository(tmp_path, ProjectConfig(git_history_limit=0))
