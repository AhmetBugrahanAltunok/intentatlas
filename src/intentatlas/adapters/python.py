from __future__ import annotations

import ast
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path

from ..models import Edge, Node
from .base import AdapterContext, GraphFragment, canonical_graph_fragment


class PythonAdapter:
    name = "python"
    suffixes = frozenset({".py"})
    cache_input_suffixes = suffixes
    cache_version = 2
    evidence_kinds = frozenset(
        {"filename-convention", "python-ast", "python-symbol-reference"}
    )

    def scan(self, context: AdapterContext) -> GraphFragment:
        module_to_nodes, path_to_module = _build_module_maps(context.files)
        nodes: list[Node] = []
        edges: list[Edge] = []
        trees: dict[str, ast.AST] = {}

        for relative in sorted(context.files):
            if Path(relative).suffix.casefold() not in self.suffixes:
                continue
            source = context.read_text(relative)
            if source is None:
                continue
            try:
                parsed_tree = ast.parse(source, filename=relative)
            except (SyntaxError, ValueError):
                continue
            trees[relative] = parsed_tree

            file_node = f"file:{relative}"
            visitor = _SymbolVisitor(relative)
            visitor.visit(parsed_tree)
            nodes.extend(visitor.nodes)
            edges.extend(
                Edge(file_node, node.id, "defines", "python-ast") for node in visitor.nodes
            )

        symbol_resolver = _PythonSymbolResolver(
            trees,
            nodes,
            module_to_nodes,
            path_to_module,
        )
        for relative in sorted(trees):
            tree = trees[relative]
            file_node = f"file:{relative}"
            relation = "tests" if context.kinds[relative] == "test" else "imports"
            symbol_targets = symbol_resolver.references(relative, tree)
            precise_files: set[str] = set()
            for symbol_target in sorted(symbol_targets):
                edges.append(
                    Edge(file_node, symbol_target, relation, "python-symbol-reference")
                )
                symbol_path = symbol_target.removeprefix("symbol:").split("::", 1)[0]
                precise_files.add(f"file:{symbol_path}")

            for imported_module in sorted(_python_imports(tree, relative, path_to_module)):
                target = _resolve_module(imported_module, module_to_nodes)
                if (
                    target is not None
                    and target != file_node
                    and not (relation == "tests" and target in precise_files)
                ):
                    edges.append(Edge(file_node, target, relation, "python-ast"))

        edges.extend(_filename_test_edges(context))
        return canonical_graph_fragment(nodes, edges)


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


def _build_module_maps(
    files: Iterable[str],
) -> tuple[dict[str, tuple[str, ...]], dict[str, str]]:
    module_candidates: defaultdict[str, set[str]] = defaultdict(set)
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
        module_candidates[module].add(f"file:{relative}")
        path_to_module[relative] = module
    module_to_nodes = {
        module: tuple(sorted(candidates))
        for module, candidates in sorted(module_candidates.items())
    }
    return module_to_nodes, path_to_module


def _resolve_module(
    module: str, module_to_nodes: dict[str, tuple[str, ...]]
) -> str | None:
    candidate = module
    while candidate:
        targets = module_to_nodes.get(candidate)
        if targets is not None:
            return targets[0] if len(targets) == 1 else None
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


class _PythonSymbolResolver:
    def __init__(
        self,
        trees: dict[str, ast.AST],
        nodes: Iterable[Node],
        module_to_nodes: dict[str, tuple[str, ...]],
        path_to_module: dict[str, str],
    ) -> None:
        self.module_to_nodes = module_to_nodes
        self.path_to_module = path_to_module
        self.direct: defaultdict[tuple[str, str], set[str]] = defaultdict(set)
        self.reexports: defaultdict[
            tuple[str, str], set[tuple[str, str]]
        ] = defaultdict(set)
        for node in nodes:
            if node.path is None or "." in node.label:
                continue
            module = path_to_module.get(node.path)
            if module:
                self.direct[(module, node.label)].add(node.id)
        for relative, tree in trees.items():
            module = path_to_module.get(relative)
            if not module:
                continue
            for statement in getattr(tree, "body", ()):
                if not isinstance(statement, ast.ImportFrom):
                    continue
                base = _python_import_base(statement, relative, path_to_module)
                if not base:
                    continue
                for alias in statement.names:
                    if alias.name == "*":
                        continue
                    exported_name = alias.asname or alias.name
                    self.reexports[(module, exported_name)].add((base, alias.name))

    def resolve(self, module: str, name: str) -> str | None:
        current = (module, name)
        seen: set[tuple[str, str]] = set()
        for _depth in range(8):
            if current in seen:
                return None
            seen.add(current)
            owners = self.module_to_nodes.get(current[0])
            if owners is not None and len(owners) != 1:
                return None
            direct = self.direct.get(current, set())
            forwarded = self.reexports.get(current, set())
            if direct and forwarded:
                return None
            if direct:
                return next(iter(direct)) if len(direct) == 1 else None
            if len(forwarded) != 1:
                return None
            current = next(iter(forwarded))
        return None

    def references(self, relative: str, tree: ast.AST) -> set[str]:
        references: set[str] = set()
        module_bindings: dict[str, tuple[str, tuple[str, ...]]] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                base = _python_import_base(node, relative, self.path_to_module)
                if not base:
                    continue
                for alias in node.names:
                    if alias.name == "*":
                        continue
                    target = self.resolve(base, alias.name)
                    if target is not None:
                        references.add(target)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    parts = tuple(alias.name.split("."))
                    local_name = alias.asname or parts[0]
                    remaining = () if alias.asname else parts[1:]
                    module_bindings[local_name] = (alias.name, remaining)

        for node in ast.walk(tree):
            chain = _python_attribute_chain(node)
            if chain is None:
                continue
            root, attributes = chain
            binding = module_bindings.get(root)
            if binding is None:
                continue
            module, module_suffix = binding
            if attributes[: len(module_suffix)] != module_suffix:
                continue
            symbol_parts = attributes[len(module_suffix) :]
            if not symbol_parts:
                continue
            target = self.resolve(module, symbol_parts[0])
            if target is not None:
                references.add(target)
        return references


def _python_import_base(
    node: ast.ImportFrom,
    relative: str,
    path_to_module: dict[str, str],
) -> str:
    current = path_to_module.get(relative, "")
    is_package = Path(relative).name == "__init__.py"
    package = current.split(".") if is_package else current.split(".")[:-1]
    if node.level:
        remove = max(0, node.level - 1)
        package = package[: len(package) - remove] if remove else package
    else:
        package = []
    module_parts = node.module.split(".") if node.module else []
    return ".".join([*package, *module_parts])


def _python_attribute_chain(node: ast.AST) -> tuple[str, tuple[str, ...]] | None:
    if not isinstance(node, ast.Attribute):
        return None
    attributes: list[str] = []
    current: ast.AST = node
    while isinstance(current, ast.Attribute):
        attributes.append(current.attr)
        current = current.value
    if not isinstance(current, ast.Name):
        return None
    return current.id, tuple(reversed(attributes))


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
