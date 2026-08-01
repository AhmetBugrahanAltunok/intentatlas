from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Iterable, Mapping
from pathlib import PurePosixPath

from ..models import Edge, Node
from .base import AdapterContext, GraphFragment, canonical_graph_fragment

_IDENTIFIER = r"[A-Za-z_][A-Za-z0-9_]*"
_FUNCTION_DECLARATION = re.compile(
    rf"(?m)^[ \t]*func[ \t]+"
    rf"(?:\([ \t]*(?:{_IDENTIFIER}[ \t]+)?\*?[ \t]*({_IDENTIFIER})"
    rf"(?:\[[^\]\n]*\])?[ \t]*\)[ \t]+)?"
    rf"({_IDENTIFIER})(?:[ \t]*\[[^\]\n]*\])?[ \t]*\("
)
_TYPE_DECLARATION = re.compile(
    rf"(?m)^[ \t]*type[ \t]+({_IDENTIFIER})(?:[ \t]*\[[^\]\n]*\])?[ \t]+"
)
_TYPE_BLOCK = re.compile(r"(?ms)^[ \t]*type[ \t]*\((.*?)^[ \t]*\)")
_BLOCK_TYPE_DECLARATION = re.compile(
    rf"(?m)^[ \t]*({_IDENTIFIER})(?:[ \t]*\[[^\]\n]*\])?[ \t]+"
)
_MODULE_DECLARATION = re.compile(r"(?m)^[ \t]*module[ \t]+([^ \t\r\n]+)")
_PACKAGE_DECLARATION = re.compile(rf"(?m)^[ \t]*package[ \t]+({_IDENTIFIER})")


class GoAdapter:
    name = "go"
    suffixes = frozenset({".go"})
    cache_input_suffixes = frozenset({".go", ".mod"})
    cache_version = 1
    evidence_kinds = frozenset(
        {"filename-convention", "go-call-reference", "go-structural", "go-symbol-reference"}
    )

    def scan(self, context: AdapterContext) -> GraphFragment:
        modules = _module_roots(context)
        package_files = _package_files(context)
        nodes: list[Node] = []
        edges: list[Edge] = []
        package_declarations: dict[
            tuple[str, str], dict[str, set[str]]
        ] = defaultdict(lambda: defaultdict(set))
        package_callables: dict[
            tuple[str, str], dict[str, set[str]]
        ] = defaultdict(lambda: defaultdict(set))
        package_calls: list[
            tuple[str, tuple[str, str], frozenset[str]]
        ] = []
        package_test_identifiers: list[
            tuple[str, str, str, frozenset[str]]
        ] = []
        package_test_imports: list[
            tuple[
                str,
                tuple[tuple[str, str], ...],
                tuple[tuple[str | None, str], ...],
            ]
        ] = []

        for relative in sorted(context.files):
            if PurePosixPath(relative).suffix.casefold() not in self.suffixes:
                continue
            source = context.read_text(relative)
            if source is None:
                continue
            tokens = _go_tokens(source)
            import_bindings = _import_bindings(tokens)
            symbol_source = _mask_comments_and_literals(source, keep_strings=False)
            file_node = f"file:{relative}"

            file_symbols = _symbols(relative, symbol_source)
            nodes.extend(file_symbols)
            edges.extend(
                Edge(file_node, node.id, "defines", "go-structural")
                for node in file_symbols
            )

            package = _package_name(symbol_source)
            if package is not None:
                directory = PurePosixPath(relative).parent.as_posix()
                directory = "" if directory == "." else directory
                if context.kinds[relative] == "test":
                    identifiers = frozenset(
                        value for kind, value in tokens if kind == "identifier"
                    )
                    package_test_identifiers.append(
                        (relative, directory, package, identifiers)
                    )
                else:
                    declarations = package_declarations[(directory, package)]
                    for node in file_symbols:
                        reference = node.label.rsplit(".", 1)[-1]
                        if node.metadata.get("symbol_kind") == "function":
                            package_callables[(directory, package)][reference].add(node.id)
                        if reference[:1].isupper():
                            declarations[reference].add(node.id)
                    package_calls.extend(
                        (caller_id, (directory, package), references)
                        for caller_id, references in _function_call_references(
                            relative, symbol_source
                        )
                    )

            if context.kinds[relative] == "test":
                package_test_imports.append((relative, tokens, import_bindings))
                continue
            for _alias, import_path in import_bindings:
                for target in _resolve_local_import(
                    import_path,
                    modules=modules,
                    package_files=package_files,
                ):
                    if target != file_node:
                        edges.append(Edge(file_node, target, "imports", "go-structural"))

        edges.extend(
            _package_symbol_test_edges(
                package_declarations,
                package_test_identifiers,
            )
        )
        edges.extend(
            _imported_package_test_edges(
                modules=modules,
                package_files=package_files,
                declarations=package_declarations,
                tests=package_test_imports,
            )
        )
        edges.extend(_package_call_edges(package_callables, package_calls))
        edges.extend(_filename_test_edges(context))
        return canonical_graph_fragment(nodes, edges)


def _symbols(relative: str, source: str) -> list[Node]:
    discovered: dict[str, tuple[str, int]] = {}
    for match in _TYPE_DECLARATION.finditer(source):
        name = match.group(1)
        discovered.setdefault(name, ("type", _line_number(source, match.start())))
    for block in _TYPE_BLOCK.finditer(source):
        body = block.group(1)
        body_offset = block.start(1)
        for match in _BLOCK_TYPE_DECLARATION.finditer(body):
            name = match.group(1)
            offset = body_offset + match.start()
            discovered.setdefault(name, ("type", _line_number(source, offset)))
    for match in _FUNCTION_DECLARATION.finditer(source):
        receiver, name = match.groups()
        label = f"{receiver}.{name}" if receiver else name
        discovered.setdefault(label, ("function", _line_number(source, match.start())))

    return [
        Node(
            id=f"symbol:{relative}::{name}",
            kind="symbol",
            label=name,
            path=relative,
            metadata={"symbol_kind": kind, "line": line, "owner": "scanner"},
        )
        for name, (kind, line) in sorted(discovered.items())
    ]


def _line_number(source: str, offset: int) -> int:
    return source.count("\n", 0, offset) + 1


def _function_call_references(
    relative: str, source: str
) -> list[tuple[str, frozenset[str]]]:
    matches = list(_FUNCTION_DECLARATION.finditer(source))
    references: list[tuple[str, frozenset[str]]] = []
    for index, match in enumerate(matches):
        receiver, name = match.groups()
        label = f"{receiver}.{name}" if receiver else name
        boundary = matches[index + 1].start() if index + 1 < len(matches) else len(source)
        body_start = _function_body_start(source, match.end() - 1, boundary)
        if body_start is None:
            continue
        body_end = _matching_delimiter(source, body_start, "{", "}")
        if body_end is None or body_end >= boundary:
            continue
        calls = _called_identifiers(_go_tokens(source[body_start + 1 : body_end]))
        references.append((f"symbol:{relative}::{label}", frozenset(calls)))
    return references


def _function_body_start(source: str, parameter_start: int, boundary: int) -> int | None:
    parameter_end = _matching_delimiter(source, parameter_start, "(", ")")
    if parameter_end is None or parameter_end >= boundary:
        return None
    cursor = parameter_end + 1
    while cursor < boundary:
        candidate = source.find("{", cursor, boundary)
        if candidate < 0:
            return None
        prefix_tokens = _go_tokens(source[cursor:candidate])
        if prefix_tokens and prefix_tokens[-1] in {
            ("identifier", "interface"),
            ("identifier", "struct"),
        }:
            type_end = _matching_delimiter(source, candidate, "{", "}")
            if type_end is None or type_end >= boundary:
                return None
            cursor = type_end + 1
            continue
        return candidate
    return None


def _matching_delimiter(
    source: str, start: int, opening: str, closing: str
) -> int | None:
    if start >= len(source) or source[start] != opening:
        return None
    depth = 0
    for index in range(start, len(source)):
        if source[index] == opening:
            depth += 1
        elif source[index] == closing:
            depth -= 1
            if depth == 0:
                return index
    return None


def _called_identifiers(tokens: tuple[tuple[str, str], ...]) -> set[str]:
    return {
        value
        for index, (kind, value) in enumerate(tokens[:-1])
        if kind == "identifier" and tokens[index + 1] == ("punctuation", "(")
    }


def _package_call_edges(
    declarations: Mapping[tuple[str, str], Mapping[str, set[str]]],
    calls: Iterable[tuple[str, tuple[str, str], frozenset[str]]],
) -> list[Edge]:
    edges: set[Edge] = set()
    for caller_id, package_key, references in sorted(calls):
        package_symbols = declarations.get(package_key, {})
        for reference in sorted(references):
            symbol_ids = package_symbols.get(reference, set())
            if len(symbol_ids) != 1:
                continue
            target_id = next(iter(symbol_ids))
            if target_id != caller_id:
                edges.add(Edge(caller_id, target_id, "calls", "go-call-reference"))
    return sorted(edges, key=lambda edge: (edge.source, edge.target, edge.evidence))


def _package_name(source: str) -> str | None:
    match = _PACKAGE_DECLARATION.search(source)
    return match.group(1) if match is not None else None


def _package_symbol_test_edges(
    declarations: Mapping[tuple[str, str], Mapping[str, set[str]]],
    tests: Iterable[tuple[str, str, str, frozenset[str]]],
) -> list[Edge]:
    edges: list[Edge] = []
    for relative, directory, package, identifiers in sorted(tests):
        package_key = (directory, package)
        package_symbols = declarations.get(package_key)
        if package_symbols is None and package.endswith("_test"):
            package_symbols = declarations.get((directory, package.removesuffix("_test")))
        if package_symbols is None:
            continue

        target_symbols = {
            next(iter(symbol_ids))
            for reference, symbol_ids in package_symbols.items()
            if reference in identifiers and len(symbol_ids) == 1
        }
        edges.extend(
            _go_symbol_test_edges(f"file:{relative}", target_symbols)
        )
    return edges


def _imported_package_test_edges(
    *,
    modules: Iterable[tuple[str, str]],
    package_files: Mapping[str, tuple[str, ...]],
    declarations: Mapping[tuple[str, str], Mapping[str, set[str]]],
    tests: Iterable[
        tuple[
            str,
            tuple[tuple[str, str], ...],
            tuple[tuple[str | None, str], ...],
        ]
    ],
) -> list[Edge]:
    edges: list[Edge] = []
    package_keys_by_directory: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for package_key in declarations:
        package_keys_by_directory[package_key[0]].append(package_key)
    for relative, tokens, bindings in sorted(tests):
        target_symbols: set[str] = set()
        for alias, import_path in bindings:
            package_targets = _resolve_local_import(
                import_path,
                modules=modules,
                package_files=package_files,
            )
            if not package_targets or alias == "_":
                continue
            target_path = PurePosixPath(package_targets[0].removeprefix("file:"))
            directory = target_path.parent.as_posix()
            directory = "" if directory == "." else directory
            package_keys = sorted(package_keys_by_directory[directory])
            if len(package_keys) != 1:
                continue
            package_key = package_keys[0]
            package_alias = package_key[1] if alias is None else alias
            references = (
                {value for kind, value in tokens if kind == "identifier"}
                if package_alias == "."
                else _qualified_identifiers(tokens, package_alias)
            )
            target_symbols.update(
                next(iter(symbol_ids))
                for reference, symbol_ids in declarations[package_key].items()
                if reference in references and len(symbol_ids) == 1
            )
        edges.extend(
            _go_symbol_test_edges(f"file:{relative}", target_symbols)
        )
    return edges


def _go_symbol_test_edges(test_id: str, symbol_ids: Iterable[str]) -> list[Edge]:
    """Retain exact symbol evidence and a separate file-level navigation edge."""

    targets: set[str] = set()
    for symbol_id in symbol_ids:
        targets.add(symbol_id)
        symbol_path = symbol_id.removeprefix("symbol:").split("::", 1)[0]
        targets.add(f"file:{symbol_path}")
    return [
        Edge(test_id, target, "tests", "go-symbol-reference")
        for target in sorted(targets)
    ]


def _qualified_identifiers(
    tokens: tuple[tuple[str, str], ...], alias: str
) -> set[str]:
    return {
        tokens[index + 2][1]
        for index in range(len(tokens) - 2)
        if tokens[index] == ("identifier", alias)
        and tokens[index + 1] == ("punctuation", ".")
        and tokens[index + 2][0] == "identifier"
    }


def _module_roots(context: AdapterContext) -> tuple[tuple[str, str], ...]:
    modules: list[tuple[str, str]] = []
    for relative in sorted(context.files):
        path = PurePosixPath(relative)
        if path.name.casefold() != "go.mod":
            continue
        source = context.read_text(relative)
        if source is None:
            continue
        structural = _mask_comments_and_literals(source, keep_strings=True)
        match = _MODULE_DECLARATION.search(structural)
        if match is None:
            continue
        module = match.group(1).strip().rstrip("/")
        if module and not any(character in module for character in {'"', "'", "`"}):
            root = path.parent.as_posix()
            modules.append((module, "" if root == "." else root))
    return tuple(sorted(set(modules), key=lambda item: (-len(item[0]), item)))


def _package_files(context: AdapterContext) -> Mapping[str, tuple[str, ...]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for relative in sorted(context.files):
        path = PurePosixPath(relative)
        if path.suffix.casefold() != ".go" or context.kinds[relative] == "test":
            continue
        directory = path.parent.as_posix()
        grouped["" if directory == "." else directory].append(f"file:{relative}")
    return {directory: tuple(files) for directory, files in sorted(grouped.items())}


def _import_paths(source: str) -> tuple[str, ...]:
    return tuple(sorted({path for _alias, path in _import_bindings(_go_tokens(source))}))


def _import_bindings(
    tokens: tuple[tuple[str, str], ...],
) -> tuple[tuple[str | None, str], ...]:
    imports: set[tuple[str | None, str]] = set()
    brace_depth = 0
    index = 0
    while index < len(tokens):
        kind, value = tokens[index]
        if kind == "punctuation" and value == "{":
            brace_depth += 1
        elif kind == "punctuation" and value == "}":
            brace_depth = max(0, brace_depth - 1)
        elif kind == "identifier" and value == "import" and brace_depth == 0:
            index = _collect_import_declaration(tokens, index + 1, imports)
        index += 1
    return tuple(sorted(imports, key=lambda item: (item[1], item[0] or "")))


def _collect_import_declaration(
    tokens: tuple[tuple[str, str], ...],
    index: int,
    imports: set[tuple[str | None, str]],
) -> int:
    if index >= len(tokens):
        return index
    if tokens[index] == ("punctuation", "("):
        index += 1
        candidates: set[tuple[str | None, str]] = set()
        while index < len(tokens):
            kind, value = tokens[index]
            if (kind, value) == ("punctuation", ")"):
                imports.update(candidates)
                return index
            if (kind, value) == ("punctuation", ";"):
                index += 1
                continue
            if kind == "string":
                if not _valid_import_path(value):
                    return index
                candidates.add((None, value))
                index += 1
                continue
            if kind == "identifier" or (kind == "punctuation" and value == "."):
                grouped_alias = value
                index += 1
                if index >= len(tokens) or tokens[index][0] != "string":
                    return index
                import_path = tokens[index][1]
                if not _valid_import_path(import_path):
                    return index
                candidates.add((grouped_alias, import_path))
                index += 1
                continue
            return index
        return index

    alias: str | None = None
    kind, value = tokens[index]
    if kind == "identifier" or (kind == "punctuation" and value == "."):
        alias = value
        index += 1
    if index < len(tokens):
        kind, value = tokens[index]
        if kind == "string" and _valid_import_path(value):
            imports.add((alias, value))
    return index


def _valid_import_path(value: str) -> bool:
    return (
        bool(value)
        and "\\" not in value
        and not any(ord(character) <= 32 for character in value)
    )


def _go_tokens(source: str) -> tuple[tuple[str, str], ...]:
    tokens: list[tuple[str, str]] = []
    index = 0
    while index < len(source):
        current = source[index]
        following = source[index + 1] if index + 1 < len(source) else ""
        if current.isspace():
            index += 1
            continue
        if current == "/" and following == "/":
            newline = source.find("\n", index + 2)
            index = len(source) if newline < 0 else newline + 1
            continue
        if current == "/" and following == "*":
            closing = source.find("*/", index + 2)
            index = len(source) if closing < 0 else closing + 2
            continue
        if current.isascii() and (current.isalpha() or current == "_"):
            end = index + 1
            while end < len(source):
                character = source[end]
                if not character.isascii() or not (character.isalnum() or character == "_"):
                    break
                end += 1
            tokens.append(("identifier", source[index:end]))
            index = end
            continue
        if current in {'"', "`"}:
            quote = current
            end = index + 1
            while end < len(source):
                if quote == '"' and source[end] == "\\":
                    end += 2
                    continue
                if source[end] == quote:
                    tokens.append(("string", source[index + 1 : end]))
                    end += 1
                    break
                end += 1
            index = end
            continue
        if current == "'":
            end = index + 1
            while end < len(source):
                if source[end] == "\\":
                    end += 2
                    continue
                if source[end] == "'":
                    end += 1
                    break
                end += 1
            index = end
            continue
        tokens.append(("punctuation", current))
        index += 1
    return tuple(tokens)


def _resolve_local_import(
    import_path: str,
    *,
    modules: Iterable[tuple[str, str]],
    package_files: Mapping[str, tuple[str, ...]],
) -> tuple[str, ...]:
    for module, root in modules:
        if import_path == module:
            suffix = ""
        elif import_path.startswith(f"{module}/"):
            suffix = import_path[len(module) + 1 :]
        else:
            continue
        if not suffix:
            directory = root
        elif root:
            directory = f"{root}/{suffix}"
        else:
            directory = suffix
        return package_files.get(directory, ())
    return ()


def _filename_test_edges(context: AdapterContext) -> list[Edge]:
    source_by_path = {
        relative.removesuffix(".go"): f"file:{relative}"
        for relative in context.files
        if PurePosixPath(relative).suffix.casefold() == ".go"
        and context.kinds[relative] != "test"
    }
    edges: list[Edge] = []
    for relative in sorted(context.files):
        path = PurePosixPath(relative)
        if path.suffix.casefold() != ".go" or context.kinds[relative] != "test":
            continue
        if not path.stem.casefold().endswith("_test"):
            continue
        candidate = relative[: -len("_test.go")]
        target = source_by_path.get(candidate)
        if target is not None:
            edges.append(
                Edge(
                    f"file:{relative}",
                    target,
                    "tests",
                    "filename-convention",
                )
            )
    return edges


def _mask_comments_and_literals(source: str, *, keep_strings: bool) -> str:
    """Mask comments and optionally literals while preserving offsets and newlines."""

    result = list(source)
    index = 0
    state = "code"
    quote = ""
    while index < len(source):
        current = source[index]
        following = source[index + 1] if index + 1 < len(source) else ""

        if state == "code":
            if current == "/" and following == "/":
                result[index] = result[index + 1] = " "
                index += 2
                state = "line-comment"
                continue
            if current == "/" and following == "*":
                result[index] = result[index + 1] = " "
                index += 2
                state = "block-comment"
                continue
            if current in {'"', "'", "`"}:
                quote = current
                state = "raw" if current == "`" else "quoted"
                if not keep_strings:
                    result[index] = " "
        elif state == "line-comment":
            if current == "\n":
                state = "code"
            else:
                result[index] = " "
        elif state == "block-comment":
            if current == "*" and following == "/":
                result[index] = result[index + 1] = " "
                index += 2
                state = "code"
                continue
            if current != "\n":
                result[index] = " "
        elif state == "quoted":
            if not keep_strings and current != "\n":
                result[index] = " "
            if current == "\\" and index + 1 < len(source):
                if not keep_strings and source[index + 1] != "\n":
                    result[index + 1] = " "
                index += 2
                continue
            if current == quote:
                state = "code"
        elif state == "raw":
            if not keep_strings and current != "\n":
                result[index] = " "
            if current == "`":
                state = "code"
        index += 1
    return "".join(result)
