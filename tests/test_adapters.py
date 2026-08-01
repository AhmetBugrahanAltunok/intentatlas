from __future__ import annotations

from pathlib import Path
from types import MappingProxyType

import pytest

import intentatlas.scanner as scanner_module
from intentatlas.adapters import (
    AdapterContext,
    GoAdapter,
    GraphFragment,
    JavaScriptAdapter,
    PythonAdapter,
)
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
    assert GoAdapter().suffixes == frozenset({".go"})


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


def test_go_adapter_skips_oversized_files_and_unclosed_import_blocks(tmp_path: Path) -> None:
    module = tmp_path / "go.mod"
    module.write_text("module example.com/fixture\n", encoding="utf-8")
    target = tmp_path / "internal" / "value.go"
    target.parent.mkdir()
    target.write_text("package internal\n\nfunc Value() int { return 1 }\n", encoding="utf-8")
    broken = tmp_path / "broken.go"
    broken.write_text(
        'package fixture\n\nimport (\n\t"example.com/fixture/internal"\n',
        encoding="utf-8",
    )
    oversized = tmp_path / "large.go"
    oversized.write_text("package fixture\n" + "x" * 100, encoding="utf-8")
    files = MappingProxyType(
        {
            "broken.go": broken,
            "go.mod": module,
            "internal/value.go": target,
            "large.go": oversized,
        }
    )
    kinds = MappingProxyType(
        {relative: "config" if relative == "go.mod" else "file" for relative in files}
    )
    context = AdapterContext(files=files, kinds=kinds, max_parse_bytes=64)

    fragment = GoAdapter().scan(context)

    assert "symbol:internal/value.go::Value" in {node.id for node in fragment.nodes}
    assert not any(node.path == "large.go" for node in fragment.nodes)
    assert not any(edge.source == "file:broken.go" for edge in fragment.edges)


def test_go_adapter_links_only_unique_exported_symbol_references(tmp_path: Path) -> None:
    sources = {
        "go.mod": "module example.com/fixture\n",
        "alpha.go": (
            "package sample\n\n"
            "func Alpha() int { return 1 }\n"
            "func Shared() int { return 2 }\n"
        ),
        "beta.go": (
            "package sample\n\n"
            "type Beta struct{}\n"
            "func (Beta) Shared() int { return 3 }\n"
        ),
        "focused_test.go": (
            "package sample\n\n"
            "func TestFocused() { _ = Alpha(); _ = Shared() }\n"
        ),
        "ambiguous_test.go": (
            "package sample_test\n\n"
            "func TestAmbiguous() { _ = Shared; _ = \"Alpha\" }\n"
        ),
        "internal/value.go": (
            "package internal\n\n"
            "func Value() int { return 4 }\n"
        ),
        "default_alias_test.go": (
            "package sample_test\n\n"
            'import "example.com/fixture/internal"\n\n'
            "func TestDefaultAlias() { _ = internal.Value() }\n"
        ),
        "dot_import_test.go": (
            "package sample_test\n\n"
            'import . "example.com/fixture/internal"\n\n'
            "func TestDotImport() { _ = Value() }\n"
        ),
        "blank_import_test.go": (
            "package sample_test\n\n"
            'import _ "example.com/fixture/internal"\n\n'
            "func TestBlankImport() {}\n"
        ),
    }
    files = {}
    kinds = {}
    for relative, source in sources.items():
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source, encoding="utf-8")
        files[relative] = path
        kinds[relative] = (
            "config"
            if relative == "go.mod"
            else "test"
            if relative.endswith("_test.go")
            else "file"
        )
    context = AdapterContext(
        files=MappingProxyType(files),
        kinds=MappingProxyType(kinds),
        max_parse_bytes=1_000,
    )

    fragment = GoAdapter().scan(context)
    symbol_edges = {
        (edge.source, edge.target)
        for edge in fragment.edges
        if edge.evidence == "go-symbol-reference"
    }

    assert ("file:focused_test.go", "file:alpha.go") in symbol_edges
    assert ("file:default_alias_test.go", "file:internal/value.go") in symbol_edges
    assert ("file:dot_import_test.go", "file:internal/value.go") in symbol_edges
    assert not any(source == "file:ambiguous_test.go" for source, _target in symbol_edges)
    assert not any(source == "file:blank_import_test.go" for source, _target in symbol_edges)
    assert ("file:focused_test.go", "file:beta.go") not in symbol_edges
