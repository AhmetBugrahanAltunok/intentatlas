from __future__ import annotations

import json
from pathlib import Path

import pytest

import intentatlas.scan_cache as cache_module
from intentatlas.adapters.base import GraphFragment
from intentatlas.adapters.python import PythonAdapter
from intentatlas.config import ProjectConfig
from intentatlas.models import Edge, Node
from intentatlas.scan_cache import AdapterFragmentCache
from intentatlas.scanner import scan_repository, scan_repository_incremental


def build_multilanguage_project(root: Path) -> None:
    (root / "app.py").write_text(
        "def run():\n    return 'private-value-not-for-cache'\n", encoding="utf-8"
    )
    (root / "app.js").write_text(
        "export function run() { return 1; }\n", encoding="utf-8"
    )
    (root / "go.mod").write_text("module example.com/cache\n", encoding="utf-8")
    (root / "main.go").write_text(
        "package cache\n\nfunc Run() int { return 1 }\n", encoding="utf-8"
    )


def graph_projection(graph) -> tuple[list[dict], list[dict]]:
    value = graph.to_dict()
    return value["nodes"], value["edges"]


def test_incremental_scan_reuses_exact_fragments_and_invalidates_only_inputs(
    tmp_path,
) -> None:
    build_multilanguage_project(tmp_path)
    config = ProjectConfig(git_history_limit=0)

    first = scan_repository_incremental(tmp_path, config)
    assert first.statistics.reused_adapters == ()
    assert first.statistics.rebuilt_adapters == (
        "go",
        "javascript-typescript",
        "python",
    )
    assert first.statistics.skipped_cache_writes == ()

    second = scan_repository_incremental(tmp_path, config)
    assert second.statistics.reused_adapters == (
        "go",
        "javascript-typescript",
        "python",
    )
    assert second.statistics.rebuilt_adapters == ()
    assert graph_projection(second.graph) == graph_projection(scan_repository(tmp_path, config))

    (tmp_path / "app.py").write_text("def run():\n    return 2\n", encoding="utf-8")
    python_change = scan_repository_incremental(tmp_path, config)
    assert python_change.statistics.reused_adapters == ("go", "javascript-typescript")
    assert python_change.statistics.rebuilt_adapters == ("python",)
    assert graph_projection(python_change.graph) == graph_projection(
        scan_repository(tmp_path, config)
    )

    (tmp_path / "go.mod").write_text(
        "module example.com/cache/v2\n", encoding="utf-8"
    )
    module_change = scan_repository_incremental(tmp_path, config)
    assert module_change.statistics.reused_adapters == (
        "javascript-typescript",
        "python",
    )
    assert module_change.statistics.rebuilt_adapters == ("go",)


def test_corrupt_cache_rebuilds_without_retaining_source_content(tmp_path) -> None:
    build_multilanguage_project(tmp_path)
    config = ProjectConfig(git_history_limit=0)
    scan_repository_incremental(tmp_path, config)
    cache_path = tmp_path / ".intentatlas" / "adapter-cache" / "python.json"
    assert "private-value-not-for-cache" not in cache_path.read_text(encoding="utf-8")

    cache_path.write_text(
        '{"schema_version":1,"schema_version":1}\n', encoding="utf-8"
    )
    result = scan_repository_incremental(tmp_path, config)

    assert result.statistics.rebuilt_adapters == ("python",)
    assert result.statistics.reused_adapters == ("go", "javascript-typescript")
    assert json.loads(cache_path.read_text(encoding="utf-8"))["adapter"] == "python"

    document = json.loads(cache_path.read_text(encoding="utf-8"))
    document["fragment"]["nodes"][0]["metadata"]["source"] = "raw source injection"
    cache_path.write_text(json.dumps(document), encoding="utf-8")
    injected = scan_repository_incremental(tmp_path, config)
    assert injected.statistics.rebuilt_adapters == ("python",)
    assert "raw source injection" not in cache_path.read_text(encoding="utf-8")

    document = json.loads(cache_path.read_text(encoding="utf-8"))
    document["fragment"]["edges"][0]["target"] = "file:missing.py"
    cache_path.write_text(json.dumps(document), encoding="utf-8")
    dangling = scan_repository_incremental(tmp_path, config)
    assert dangling.statistics.rebuilt_adapters == ("python",)


def test_unsafe_cache_entry_is_not_followed_or_required(tmp_path) -> None:
    build_multilanguage_project(tmp_path)
    cache_path = tmp_path / ".intentatlas" / "adapter-cache" / "python.json"
    cache_path.mkdir(parents=True)

    result = scan_repository_incremental(tmp_path, ProjectConfig(git_history_limit=0))

    assert "python" in result.statistics.rebuilt_adapters
    assert result.statistics.skipped_cache_writes == ("python",)
    assert cache_path.is_dir()


def test_cache_write_failure_preserves_previous_fragment(tmp_path, monkeypatch) -> None:
    build_multilanguage_project(tmp_path)
    config = ProjectConfig(git_history_limit=0)
    scan_repository_incremental(tmp_path, config)
    cache_path = tmp_path / ".intentatlas" / "adapter-cache" / "python.json"
    previous = cache_path.read_bytes()
    (tmp_path / "app.py").write_text("def changed():\n    return 3\n", encoding="utf-8")

    def fail_write(_path, _content) -> None:
        raise OSError("simulated cache replacement failure")

    monkeypatch.setattr(cache_module, "atomic_write_text", fail_write)
    result = scan_repository_incremental(tmp_path, config)

    assert result.statistics.rebuilt_adapters == ("python",)
    assert result.statistics.skipped_cache_writes == ("python",)
    assert cache_path.read_bytes() == previous
    assert "symbol:app.py::changed" in result.graph.nodes


def test_cache_canonicalizes_duplicate_adapter_edges(tmp_path) -> None:
    cache = AdapterFragmentCache(tmp_path)
    adapter = PythonAdapter()
    node = Node(
        "symbol:app.py::run",
        "symbol",
        "run",
        "app.py",
        {"symbol_kind": "function", "line": 1, "end_line": 1, "owner": "scanner"},
    )
    edge = Edge("file:app.py", node.id, "defines", "python-ast")
    fingerprint = "a" * 64

    assert cache.store(
        adapter,
        fingerprint,
        GraphFragment(nodes=(node,), edges=(edge, edge)),
    )
    loaded = cache.load(adapter, fingerprint, frozenset({"file:app.py"}))

    assert loaded.reason == "hit"
    assert loaded.fragment == GraphFragment(nodes=(node,), edges=(edge,))


def test_scan_fails_closed_when_adapter_inputs_change_during_analysis(
    tmp_path, monkeypatch
) -> None:
    build_multilanguage_project(tmp_path)
    source = tmp_path / "app.py"
    original_scan = PythonAdapter.scan

    def changing_scan(self, context):
        fragment = original_scan(self, context)
        source.write_text("def changed_during_scan():\n    return 4\n", encoding="utf-8")
        return fragment

    monkeypatch.setattr(PythonAdapter, "scan", changing_scan)
    with pytest.raises(ValueError, match="inputs changed during scan"):
        scan_repository_incremental(tmp_path, ProjectConfig(git_history_limit=0))

    cache = AdapterFragmentCache(tmp_path)
    assert cache.root.joinpath("python.json").exists() is False
