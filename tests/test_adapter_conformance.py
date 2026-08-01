from __future__ import annotations

from pathlib import Path

import pytest

import intentatlas.adapters.conformance as conformance_module
import intentatlas.scanner as scanner_module
from intentatlas.adapters import (
    ADAPTER_CONTRACT_VERSION,
    AdapterConformanceError,
    AdapterContext,
    GoAdapter,
    GraphFragment,
    JavaScriptAdapter,
    PythonAdapter,
    assert_adapter_conforms,
    canonical_graph_fragment,
    validate_adapter_definition,
    validate_adapter_fragment,
)
from intentatlas.config import ProjectConfig
from intentatlas.models import Edge, Node
from intentatlas.scanner import scan_repository, scan_repository_incremental


def build_conformance_context(root: Path) -> AdapterContext:
    sources = {
        "app.py": "def run():\n    return 1\n",
        "tests/test_app.py": "from app import run\n\ndef test_run():\n    assert run() == 1\n",
        "src/app.ts": "export function run(): number { return 1; }\n",
        "src/app.test.ts": "import { run } from './app';\nrun();\n",
        "go.mod": "module example.test/conformance\n\ngo 1.22\n",
        "internal/app/app.go": "package app\n\nfunc Run() int { return 1 }\n",
        "internal/app/app_test.go": "package app\n\nfunc TestRun() { Run() }\n",
    }
    files: dict[str, Path] = {}
    kinds: dict[str, str] = {}
    for relative, content in sources.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        files[relative] = path
        kinds[relative] = "test" if "test" in path.stem.casefold() else "file"
    return AdapterContext(files=files, kinds=kinds, max_parse_bytes=1_000_000)


@pytest.mark.parametrize("adapter", [PythonAdapter(), JavaScriptAdapter(), GoAdapter()])
def test_builtin_adapters_pass_one_executable_contract(tmp_path, adapter) -> None:
    report = assert_adapter_conforms(adapter, build_conformance_context(tmp_path))

    assert report.contract_version == ADAPTER_CONTRACT_VERSION
    assert report.adapter == adapter.name
    assert report.node_count > 0
    assert report.edge_count > 0


@pytest.mark.parametrize(
    ("attribute", "value", "message"),
    [
        ("name", "Unsafe/Name", "safe lowercase identifier"),
        ("suffixes", frozenset({"py"}), "supported suffixes"),
        ("cache_input_suffixes", frozenset({".toml"}), "must include"),
        ("cache_version", 0, "cache version"),
        ("evidence_kinds", frozenset(), "evidence declarations"),
    ],
)
def test_adapter_definition_rejects_invalid_declarations(attribute, value, message) -> None:
    adapter = PythonAdapter()
    setattr(adapter, attribute, value)

    with pytest.raises(AdapterConformanceError, match=message):
        validate_adapter_definition(adapter)


def test_adapter_contract_rejects_nondeterministic_output(tmp_path) -> None:
    class NondeterministicAdapter(PythonAdapter):
        calls = 0

        def scan(self, context):
            self.calls += 1
            label = f"run{self.calls}"
            node = symbol_node("app.py", label)
            return GraphFragment(nodes=(node,))

    with pytest.raises(AdapterConformanceError, match="nondeterministic"):
        assert_adapter_conforms(
            NondeterministicAdapter(),
            build_conformance_context(tmp_path),
        )


@pytest.mark.parametrize(
    ("context", "message"),
    [
        (AdapterContext(files={}, kinds={"app.py": "file"}, max_parse_bytes=10), "identical keys"),
        (AdapterContext(files={}, kinds={}, max_parse_bytes=0), "positive integer"),
    ],
)
def test_adapter_contract_rejects_invalid_fixture_context(context, message) -> None:
    with pytest.raises(AdapterConformanceError, match=message):
        assert_adapter_conforms(PythonAdapter(), context)


@pytest.mark.parametrize(
    ("fragment", "message"),
    [
        (
            lambda node, edge: GraphFragment(nodes=(node, node), edges=(edge,)),
            "duplicate nodes",
        ),
        (
            lambda node, edge: GraphFragment(nodes=(node,), edges=(edge, edge)),
            "duplicate edges",
        ),
        (
            lambda node, edge: GraphFragment(
                nodes=(node,),
                edges=(Edge(edge.source, edge.target, "defines", "undeclared"),),
            ),
            "undeclared edge semantics",
        ),
        (
            lambda node, edge: GraphFragment(
                nodes=(node,),
                edges=(Edge(node.id, edge.source, "defines", "python-ast"),),
            ),
            "invalid 'defines' endpoints",
        ),
    ],
)
def test_adapter_fragment_rejects_noncanonical_or_invalid_output(fragment, message) -> None:
    node = symbol_node("app.py", "run")
    edge = Edge("file:app.py", node.id, "defines", "python-ast")

    with pytest.raises(AdapterConformanceError, match=message):
        validate_adapter_fragment(
            PythonAdapter(),
            fragment(node, edge),
            frozenset({"file:app.py"}),
        )


def test_adapter_fragment_rejects_wrong_values_order_and_bounds(monkeypatch) -> None:
    adapter = PythonAdapter()
    first = symbol_node("app.py", "alpha")
    second = symbol_node("app.py", "beta")
    first_edge = Edge("file:app.py", first.id, "defines", "python-ast")
    second_edge = Edge("file:app.py", second.id, "defines", "python-ast")
    known = frozenset({"file:app.py"})

    with pytest.raises(AdapterConformanceError, match="must return GraphFragment"):
        validate_adapter_fragment(adapter, object(), known)
    with pytest.raises(AdapterConformanceError, match="invalid node value"):
        validate_adapter_fragment(adapter, GraphFragment(nodes=("bad",)), known)
    with pytest.raises(AdapterConformanceError, match="invalid edge value"):
        validate_adapter_fragment(adapter, GraphFragment(edges=("bad",)), known)
    with pytest.raises(AdapterConformanceError, match="unordered nodes"):
        validate_adapter_fragment(adapter, GraphFragment(nodes=(second, first)), known)
    with pytest.raises(AdapterConformanceError, match="unordered edges"):
        validate_adapter_fragment(
            adapter,
            GraphFragment(nodes=(first, second), edges=(second_edge, first_edge)),
            known,
        )
    monkeypatch.setattr(conformance_module, "MAX_FRAGMENT_NODES", 0)
    with pytest.raises(AdapterConformanceError, match="unbounded fragment"):
        validate_adapter_fragment(adapter, GraphFragment(nodes=(first,)), known)


def test_adapter_fragment_rejects_invalid_symbol_span_and_edge_shapes() -> None:
    adapter = PythonAdapter()
    node = symbol_node("app.py", "run")
    known = frozenset({"file:app.py", "file:other.py"})
    invalid_node = Node(
        node.id,
        node.kind,
        node.label,
        node.path,
        {**node.metadata, "owner": "external"},
    )
    with pytest.raises(AdapterConformanceError, match="invalid symbol node"):
        validate_adapter_fragment(adapter, GraphFragment(nodes=(invalid_node,)), known)

    invalid_span = Node(
        node.id,
        node.kind,
        node.label,
        node.path,
        {**node.metadata, "end_line": 0},
    )
    with pytest.raises(AdapterConformanceError, match="invalid symbol span"):
        validate_adapter_fragment(adapter, GraphFragment(nodes=(invalid_span,)), known)

    with pytest.raises(AdapterConformanceError, match="self edge"):
        validate_adapter_fragment(
            adapter,
            GraphFragment(nodes=(node,), edges=(Edge(node.id, node.id, "calls", "python-ast"),)),
            known,
        )
    with pytest.raises(AdapterConformanceError, match="cross-file definition"):
        validate_adapter_fragment(
            adapter,
            GraphFragment(
                nodes=(node,),
                edges=(Edge("file:other.py", node.id, "defines", "python-ast"),),
            ),
            known,
        )


def test_canonical_fragment_collapses_identical_values_and_rejects_collisions() -> None:
    node = symbol_node("app.py", "run")
    edge = Edge("file:app.py", node.id, "defines", "python-ast")
    assert canonical_graph_fragment((node, node), (edge, edge)) == GraphFragment(
        nodes=(node,), edges=(edge,)
    )

    conflicting = Node(
        node.id,
        node.kind,
        "other",
        node.path,
        node.metadata,
    )
    with pytest.raises(ValueError, match="Conflicting adapter node identity"):
        canonical_graph_fragment((node, conflicting), ())


def test_fresh_and_incremental_scans_reject_before_merge_or_cache(tmp_path, monkeypatch) -> None:
    source = tmp_path / "app.py"
    source.write_text("def run():\n    return 1\n", encoding="utf-8")
    node = symbol_node("app.py", "run")
    edge = Edge("file:app.py", node.id, "defines", "python-ast")

    class DuplicateAdapter(PythonAdapter):
        name = "duplicate-test"

        def scan(self, context):
            return GraphFragment(nodes=(node,), edges=(edge, edge))

    monkeypatch.setattr(scanner_module, "BUILTIN_ADAPTERS", (DuplicateAdapter(),))
    config = ProjectConfig(git_history_limit=0)

    with pytest.raises(AdapterConformanceError, match="duplicate edges"):
        scan_repository(tmp_path, config)
    with pytest.raises(AdapterConformanceError, match="duplicate edges"):
        scan_repository_incremental(tmp_path, config)
    assert not (tmp_path / ".intentatlas" / "adapter-cache" / "duplicate-test.json").exists()


def symbol_node(path: str, label: str) -> Node:
    return Node(
        id=f"symbol:{path}::{label}",
        kind="symbol",
        label=label,
        path=path,
        metadata={
            "symbol_kind": "function",
            "line": 1,
            "end_line": 1,
            "owner": "scanner",
        },
    )
