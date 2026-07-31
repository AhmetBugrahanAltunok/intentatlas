from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Iterable, Mapping
from pathlib import PurePosixPath

from ..models import Edge, Node
from .base import AdapterContext, GraphFragment

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


class GoAdapter:
    name = "go"
    suffixes = frozenset({".go"})

    def scan(self, context: AdapterContext) -> GraphFragment:
        modules = _module_roots(context)
        package_files = _package_files(context)
        nodes: list[Node] = []
        edges: list[Edge] = []

        for relative in sorted(context.files):
            if PurePosixPath(relative).suffix.casefold() not in self.suffixes:
                continue
            source = context.read_text(relative)
            if source is None:
                continue
            symbol_source = _mask_comments_and_literals(source, keep_strings=False)
            file_node = f"file:{relative}"

            file_symbols = _symbols(relative, symbol_source)
            nodes.extend(file_symbols)
            edges.extend(
                Edge(file_node, node.id, "defines", "go-structural")
                for node in file_symbols
            )

            relation = "tests" if context.kinds[relative] == "test" else "imports"
            for import_path in _import_paths(source):
                for target in _resolve_local_import(
                    import_path,
                    modules=modules,
                    package_files=package_files,
                ):
                    if target != file_node:
                        edges.append(Edge(file_node, target, relation, "go-structural"))

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
    tokens = _go_tokens(source)
    imports: set[str] = set()
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
    return tuple(sorted(imports))


def _collect_import_declaration(
    tokens: tuple[tuple[str, str], ...],
    index: int,
    imports: set[str],
) -> int:
    if index >= len(tokens):
        return index
    if tokens[index] == ("punctuation", "("):
        index += 1
        candidates: set[str] = set()
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
                candidates.add(value)
                index += 1
                continue
            if kind == "identifier" or (kind == "punctuation" and value == "."):
                index += 1
                if index >= len(tokens) or tokens[index][0] != "string":
                    return index
                import_path = tokens[index][1]
                if not _valid_import_path(import_path):
                    return index
                candidates.add(import_path)
                index += 1
                continue
            return index
        return index

    kind, value = tokens[index]
    if kind == "identifier" or (kind == "punctuation" and value == "."):
        index += 1
    if index < len(tokens):
        kind, value = tokens[index]
        if kind == "string" and _valid_import_path(value):
            imports.add(value)
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
