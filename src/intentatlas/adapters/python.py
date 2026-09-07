from __future__ import annotations

import ast
from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from ..models import Edge, Node
from .base import AdapterContext, GraphFragment, canonical_graph_fragment


class PythonAdapter:
    name = "python"
    suffixes = frozenset({".py"})
    cache_input_suffixes = suffixes
    cache_version = 5
    evidence_kinds = frozenset(
        {"filename-convention", "python-ast", "python-symbol-reference"}
    )

    def scan(self, context: AdapterContext) -> GraphFragment:
        module_to_nodes, path_to_module = _build_module_maps(context)
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
            overload_names, typing_module_names = _typing_overload_bindings(parsed_tree)
            visitor = _SymbolVisitor(
                relative,
                overload_names,
                typing_module_names,
                _definition_contexts(parsed_tree),
                _scope_shadowed_names(parsed_tree),
            )
            visitor.visit(parsed_tree)
            file_symbols = _unique_symbol_nodes(visitor.nodes)
            nodes.extend(file_symbols)
            edges.extend(
                Edge(file_node, node.id, "defines", "python-ast") for node in file_symbols
            )

        symbol_resolver = _PythonSymbolResolver(
            trees,
            nodes,
            module_to_nodes,
            path_to_module,
            context,
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
                target = _resolve_module(
                    imported_module,
                    module_to_nodes,
                    _allowed_owners(context, relative),
                )
                if (
                    target is not None
                    and target != file_node
                    and not (relation == "tests" and target in precise_files)
                ):
                    edges.append(Edge(file_node, target, relation, "python-ast"))

        edges.extend(_filename_test_edges(context))
        return canonical_graph_fragment(nodes, edges)


_DefinitionToken = tuple[str, str, int, int]
_DefinitionContext = tuple[tuple[_DefinitionToken, ...], bool, _DefinitionToken]


@dataclass(frozen=True, slots=True)
class _SymbolCandidate:
    node: Node
    overload_declaration: bool
    lexical_scope: tuple[_DefinitionToken, ...]
    direct_definition: bool
    definition_token: _DefinitionToken


class _SymbolVisitor(ast.NodeVisitor):
    def __init__(
        self,
        relative: str,
        overload_names: Mapping[str, int],
        typing_module_names: Mapping[str, int],
        definition_contexts: Mapping[int, _DefinitionContext],
        scope_shadowed_names: Mapping[_DefinitionToken, frozenset[str]],
    ):
        self.relative = relative
        self.overload_names = overload_names
        self.typing_module_names = typing_module_names
        self.definition_contexts = definition_contexts
        self.scope_shadowed_names = scope_shadowed_names
        self.stack: list[str] = []
        self.nodes: list[_SymbolCandidate] = []

    def _visit_symbol(self, node: ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        qualname = ".".join([*self.stack, node.name])
        kind = "class" if isinstance(node, ast.ClassDef) else "function"
        decorator_lines = [decorator.lineno for decorator in node.decorator_list]
        start_line = min([node.lineno, *decorator_lines])
        end_line = node.end_lineno if node.end_lineno is not None else node.lineno
        lexical_scope, direct_definition, definition_token = self.definition_contexts[
            id(node)
        ]
        symbol = Node(
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
        self.nodes.append(
            _SymbolCandidate(
                symbol,
                not isinstance(node, ast.ClassDef)
                and self._is_overload_declaration(node),
                lexical_scope,
                direct_definition,
                definition_token,
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

    def _is_overload_declaration(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> bool:
        lexical_scope = self.definition_contexts[id(node)][0]
        for decorator in node.decorator_list:
            if (
                isinstance(decorator, ast.Name)
                and self._trusted_binding(
                    decorator.id,
                    decorator.lineno,
                    self.overload_names,
                    lexical_scope,
                )
            ):
                return True
            if (
                isinstance(decorator, ast.Attribute)
                and decorator.attr == "overload"
                and isinstance(decorator.value, ast.Name)
                and self._trusted_binding(
                    decorator.value.id,
                    decorator.lineno,
                    self.typing_module_names,
                    lexical_scope,
                )
            ):
                return True
        return False

    def _trusted_binding(
        self,
        name: str,
        decorator_line: int,
        trusted_imports: Mapping[str, int],
        lexical_scope: tuple[_DefinitionToken, ...],
    ) -> bool:
        import_line = trusted_imports.get(name)
        return (
            import_line is not None
            and import_line < decorator_line
            and not any(
                name in self.scope_shadowed_names.get(scope, frozenset())
                for scope in lexical_scope
            )
        )


def _typing_overload_bindings(
    tree: ast.AST,
) -> tuple[dict[str, int], dict[str, int]]:
    overload_imports: defaultdict[str, list[int]] = defaultdict(list)
    typing_module_imports: defaultdict[str, list[int]] = defaultdict(list)
    for statement in getattr(tree, "body", ()):
        if isinstance(statement, ast.ImportFrom) and statement.module in {
            "typing",
            "typing_extensions",
        }:
            for alias in statement.names:
                if alias.name == "overload":
                    overload_imports[alias.asname or alias.name].append(statement.lineno)
        elif isinstance(statement, ast.Import):
            for alias in statement.names:
                if alias.name in {"typing", "typing_extensions"}:
                    typing_module_imports[alias.asname or alias.name].append(
                        statement.lineno
                    )
    binding_counts: defaultdict[str, int] = defaultdict(int)
    for name in _body_bound_names(getattr(tree, "body", ())):
        binding_counts[name] += 1
    overload_names = {
        name: lines[0]
        for name, lines in sorted(overload_imports.items())
        if len(lines) == 1 and binding_counts[name] == 1
    }
    typing_module_names = {
        name: lines[0]
        for name, lines in sorted(typing_module_imports.items())
        if len(lines) == 1 and binding_counts[name] == 1
    }
    return overload_names, typing_module_names


def _body_bound_names(statements: Iterable[ast.stmt]) -> Iterable[str]:
    for statement in statements:
        yield from _statement_bound_names(statement)


def _statement_bound_names(node: ast.AST) -> Iterable[str]:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        yield node.name
        return
    if isinstance(node, ast.Lambda):
        return
    if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
        yield node.id
    elif isinstance(node, ast.alias):
        yield node.asname or node.name.split(".", 1)[0]
    elif isinstance(node, ast.ExceptHandler) and node.name:
        yield node.name
    for child in ast.iter_child_nodes(node):
        yield from _statement_bound_names(child)


def _scope_shadowed_names(
    tree: ast.AST,
) -> dict[_DefinitionToken, frozenset[str]]:
    shadowed: dict[_DefinitionToken, frozenset[str]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        names = set(_body_bound_names(node.body))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.update(
                argument.arg
                for argument in ast.walk(node.args)
                if isinstance(argument, ast.arg)
            )
        shadowed[_definition_token(node)] = frozenset(names)
    return shadowed


def _definition_token(
    node: ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef,
) -> _DefinitionToken:
    return type(node).__name__, node.name, node.lineno, node.col_offset


def _definition_contexts(tree: ast.AST) -> dict[int, _DefinitionContext]:
    contexts: dict[int, _DefinitionContext] = {}

    def visit(
        node: ast.AST,
        lexical_scope: tuple[_DefinitionToken, ...],
        direct_definition: bool,
    ) -> None:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            token = _definition_token(node)
            contexts[id(node)] = (lexical_scope, direct_definition, token)
            for statement in node.body:
                visit(statement, (*lexical_scope, token), True)
            return
        for child in ast.iter_child_nodes(node):
            visit(child, lexical_scope, False)

    for statement in getattr(tree, "body", ()):
        visit(statement, (), True)
    return contexts


def _build_module_maps(
    context: AdapterContext,
) -> tuple[dict[tuple[str, str], tuple[str, ...]], dict[str, str]]:
    module_candidates: defaultdict[tuple[str, str], set[str]] = defaultdict(set)
    path_to_module: dict[str, str] = {}
    for relative in sorted(context.files):
        path = Path(relative)
        if path.suffix.casefold() != ".py":
            continue
        module_path = PurePosixPath(relative).with_suffix("")
        owners = context.workspace_owners.get(relative, ())
        if len(owners) == 1:
            matching_roots = [
                root
                for root in context.source_roots.get(owners[0], ())
                if not root or relative == root or relative.startswith(f"{root}/")
            ]
            if matching_roots:
                source_root = max(
                    matching_roots,
                    key=lambda value: (len(PurePosixPath(value).parts), value),
                )
                if source_root:
                    module_path = PurePosixPath(relative).relative_to(source_root).with_suffix("")
        parts = list(module_path.parts)
        markerless_src_module = bool(
            not context.source_roots and parts and parts[0] == "src"
        )
        if markerless_src_module:
            parts = parts[1:]
        if parts and parts[-1] == "__init__":
            parts = parts[:-1]
        if not parts:
            continue
        module = ".".join(parts)
        owner = owners[0] if len(owners) == 1 else ""
        module_candidates[(owner, module)].add(f"file:{relative}")
        if markerless_src_module:
            module_candidates[(owner, f"src.{module}")].add(f"file:{relative}")
        path_to_module[relative] = module
    module_to_nodes = {
        module: tuple(sorted(candidates))
        for module, candidates in sorted(module_candidates.items())
    }
    return module_to_nodes, path_to_module


def _resolve_module(
    module: str,
    module_to_nodes: dict[tuple[str, str], tuple[str, ...]],
    owners: tuple[str, ...],
) -> str | None:
    candidate = module
    while candidate:
        targets = {
            target
            for owner in owners
            for target in module_to_nodes.get((owner, candidate), ())
        }
        if targets:
            return next(iter(targets)) if len(targets) == 1 else None
        candidate = candidate.rpartition(".")[0]
    return None


def _allowed_owners(context: AdapterContext, relative: str) -> tuple[str, ...]:
    owners = context.workspace_owners.get(relative, ())
    if len(owners) != 1:
        return ()
    owner = owners[0]
    dependencies = sorted(
        target for source, target in context.workspace_dependencies if source == owner
    )
    return (owner, *dependencies)


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
        module_to_nodes: dict[tuple[str, str], tuple[str, ...]],
        path_to_module: dict[str, str],
        context: AdapterContext,
    ) -> None:
        self.module_to_nodes = module_to_nodes
        self.path_to_module = path_to_module
        self.context = context
        self.direct: defaultdict[tuple[str, str, str], set[str]] = defaultdict(set)
        self.reexports: defaultdict[
            tuple[str, str, str], set[tuple[str, str]]
        ] = defaultdict(set)
        modules_by_file: defaultdict[tuple[str, str], set[str]] = defaultdict(set)
        for (owner, module_identity), targets in module_to_nodes.items():
            for target in targets:
                modules_by_file[(owner, target.removeprefix("file:"))].add(
                    module_identity
                )
        for node in nodes:
            if node.path is None or "." in node.label:
                continue
            owners = context.workspace_owners.get(node.path, ())
            if len(owners) == 1:
                for node_module in modules_by_file.get((owners[0], node.path), ()):
                    self.direct[(owners[0], node_module, node.label)].add(node.id)
        for relative, tree in trees.items():
            module = path_to_module.get(relative)
            owners = context.workspace_owners.get(relative, ())
            if not module or len(owners) != 1:
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
                    for module_identity in modules_by_file.get(
                        (owners[0], relative), (module,)
                    ):
                        self.reexports[(owners[0], module_identity, exported_name)].add(
                            (base, alias.name)
                        )

    def resolve(self, owners: tuple[str, ...], module: str, name: str) -> str | None:
        current = (module, name)
        seen: set[tuple[str, str]] = set()
        for _depth in range(8):
            if current in seen:
                return None
            seen.add(current)
            module_owners = [
                owner
                for owner in owners
                if self.module_to_nodes.get((owner, current[0]))
            ]
            if len(module_owners) != 1:
                return None
            module_owner = module_owners[0]
            direct = self.direct.get((module_owner, *current), set())
            forwarded = self.reexports.get((module_owner, *current), set())
            if direct and forwarded:
                return None
            if direct:
                return next(iter(direct)) if len(direct) == 1 else None
            if len(forwarded) != 1:
                return None
            current = next(iter(forwarded))
        return None

    def resolve_qualified(
        self,
        owners: tuple[str, ...],
        module: str,
        symbol_parts: tuple[str, ...],
    ) -> str | None:
        candidates: set[str] = set()
        for module_part_count in range(len(symbol_parts)):
            candidate_module = ".".join((module, *symbol_parts[:module_part_count]))
            candidate = self.resolve(
                owners,
                candidate_module,
                symbol_parts[module_part_count],
            )
            if candidate is not None:
                candidates.add(candidate)
        return next(iter(candidates)) if len(candidates) == 1 else None

    def references(self, relative: str, tree: ast.AST) -> set[str]:
        references: set[str] = set()
        owners = _allowed_owners(self.context, relative)
        if not owners:
            return references
        module_bindings: dict[str, tuple[str, tuple[str, ...]]] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                base = _python_import_base(node, relative, self.path_to_module)
                if not base:
                    continue
                for alias in node.names:
                    if alias.name == "*":
                        continue
                    target = self.resolve(owners, base, alias.name)
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
            target = self.resolve_qualified(owners, module, symbol_parts)
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


def _unique_symbol_nodes(nodes: list[_SymbolCandidate]) -> tuple[Node, ...]:
    candidates: defaultdict[str, list[_SymbolCandidate]] = defaultdict(list)
    for candidate in nodes:
        candidates[candidate.node.id].append(candidate)
    resolved: dict[str, _SymbolCandidate | None] = {}
    excluded_definition_tokens: set[_DefinitionToken] = set()
    for node_id, values in sorted(candidates.items()):
        if len(values) == 1 and values[0].node.id == node_id:
            resolved[node_id] = values[0]
            continue
        implementation = _overload_implementation(values)
        resolved[node_id] = implementation
        if implementation is None:
            excluded_definition_tokens.update(value.definition_token for value in values)
        else:
            excluded_definition_tokens.update(
                value.definition_token for value in values if value.overload_declaration
            )
    return tuple(
        candidate.node
        for node_id, candidate in sorted(resolved.items())
        if candidate is not None
        and candidate.node.id == node_id
        and not excluded_definition_tokens.intersection(candidate.lexical_scope)
    )


def _overload_implementation(
    values: list[_SymbolCandidate],
) -> _SymbolCandidate | None:
    implementations = [value for value in values if not value.overload_declaration]
    declarations = [value for value in values if value.overload_declaration]
    if len(implementations) != 1 or not declarations:
        return None
    implementation = implementations[0]
    if not all(
        value.direct_definition and value.lexical_scope == implementation.lexical_scope
        for value in values
    ):
        return None
    implementation_start = int(implementation.node.metadata["line"])
    if any(
        int(declaration.node.metadata["end_line"]) >= implementation_start
        for declaration in declarations
    ):
        return None
    return implementation
