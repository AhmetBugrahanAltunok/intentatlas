from __future__ import annotations

import ast
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path

from ..models import Edge, Node
from .base import AdapterContext, GraphFragment


class PythonAdapter:
    name = "python"
    suffixes = frozenset({".py"})

    def scan(self, context: AdapterContext) -> GraphFragment:
        module_to_node, path_to_module = _build_module_maps(context.files)
        nodes: list[Node] = []
        edges: list[Edge] = []

        for relative in sorted(context.files):
            if Path(relative).suffix.casefold() not in self.suffixes:
                continue
            source = context.read_text(relative)
            if source is None:
                continue
            try:
                tree = ast.parse(source, filename=relative)
            except (SyntaxError, ValueError):
                continue

            file_node = f"file:{relative}"
            visitor = _SymbolVisitor(relative)
            visitor.visit(tree)
            nodes.extend(visitor.nodes)
            edges.extend(
                Edge(file_node, node.id, "defines", "python-ast") for node in visitor.nodes
            )

            relation = "tests" if context.kinds[relative] == "test" else "imports"
            for imported_module in sorted(_python_imports(tree, relative, path_to_module)):
                target = _resolve_module(imported_module, module_to_node)
                if target is not None and target != file_node:
                    edges.append(Edge(file_node, target, relation, "python-ast"))

        edges.extend(_filename_test_edges(context))
        return GraphFragment(
            nodes=tuple(sorted(nodes, key=lambda node: node.id)),
            edges=tuple(
                sorted(
                    edges,
                    key=lambda edge: (
                        edge.source,
                        edge.target,
                        edge.relation,
                        edge.evidence,
                    ),
                )
            ),
        )


class _SymbolVisitor(ast.NodeVisitor):
    def __init__(self, relative: str):
        self.relative = relative
        self.stack: list[str] = []
        self.nodes: list[Node] = []

    def _visit_symbol(self, node: ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        qualname = ".".join([*self.stack, node.name])
        kind = "class" if isinstance(node, ast.ClassDef) else "function"
        decorator_lines = [decorator.lineno for decorator in node.decorator_list]
        start_line = min([node.lineno, *decorator_lines])
        end_line = node.end_lineno if node.end_lineno is not None else node.lineno
        self.nodes.append(
            Node(
                id=f"symbol:{self.relative}::{qualname}",
                kind="symbol",
                label=qualname,
                path=self.relative,
                metadata={
                    "symbol_kind": kind,
                    "line": start_line,
                    "end_line": end_line,
                    "owner": "scanner",
                },
            )
        )
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
        self._visit_symbol(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
        self._visit_symbol(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # noqa: N802
        self._visit_symbol(node)


def _build_module_maps(files: Iterable[str]) -> tuple[dict[str, str], dict[str, str]]:
    module_to_node: dict[str, str] = {}
    path_to_module: dict[str, str] = {}
    for relative in sorted(files):
        path = Path(relative)
        if path.suffix.casefold() != ".py":
            continue
        parts = list(path.with_suffix("").parts)
        if parts and parts[0] == "src":
            parts = parts[1:]
        if parts and parts[-1] == "__init__":
            parts = parts[:-1]
        if not parts:
            continue
        module = ".".join(parts)
        module_to_node[module] = f"file:{relative}"
        path_to_module[relative] = module
    return module_to_node, path_to_module


def _resolve_module(module: str, module_to_node: dict[str, str]) -> str | None:
    candidate = module
    while candidate:
        target = module_to_node.get(candidate)
        if target is not None:
            return target
        candidate = candidate.rpartition(".")[0]
    return None


def _python_imports(tree: ast.AST, relative: str, path_to_module: dict[str, str]) -> Iterable[str]:
    current = path_to_module.get(relative, "")
    is_package = Path(relative).name == "__init__.py"
    package = current.split(".") if is_package else current.split(".")[:-1]

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            yield from (alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base_parts = list(package)
            if node.level:
                remove = max(0, node.level - 1)
                base_parts = base_parts[: len(base_parts) - remove] if remove else base_parts
            elif node.module:
                base_parts = []
            module_parts = node.module.split(".") if node.module else []
            base = ".".join([*base_parts, *module_parts])
            if base:
                yield base
            for alias in node.names:
                if alias.name != "*":
                    yield ".".join(part for part in (base, alias.name) if part)


def _filename_test_edges(context: AdapterContext) -> Iterable[Edge]:
    sources_by_stem: dict[str, list[str]] = defaultdict(list)
    for relative in context.files:
        if Path(relative).suffix.casefold() != ".py" or context.kinds[relative] == "test":
            continue
        sources_by_stem[Path(relative).stem].append(f"file:{relative}")

    for relative in context.files:
        if Path(relative).suffix.casefold() != ".py" or context.kinds[relative] != "test":
            continue
        stem = Path(relative).stem
        candidate_stem = stem.removeprefix("test_").removesuffix("_test")
        candidates = sources_by_stem.get(candidate_stem, [])
        if len(candidates) == 1:
            yield Edge(
                f"file:{relative}",
                candidates[0],
                "tests",
                "filename-convention",
            )
