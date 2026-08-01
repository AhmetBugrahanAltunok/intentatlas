from __future__ import annotations

import posixpath
import re
from collections import defaultdict
from collections.abc import Iterable
from pathlib import PurePosixPath

from ..models import Edge, Node
from .base import AdapterContext, GraphFragment

JAVASCRIPT_SUFFIXES = frozenset({".js", ".jsx", ".ts", ".tsx"})
_IDENTIFIER = r"[A-Za-z_$][A-Za-z0-9_$]*"
_DECLARATION = re.compile(
    rf"(?m)^[ \t]*(?:export[ \t]+)?(?:default[ \t]+)?(?:declare[ \t]+)?"
    rf"(?:abstract[ \t]+)?(?:async[ \t]+)?"
    rf"(class|function\*?|interface|type|enum)[ \t]+({_IDENTIFIER})"
)
_ARROW_DECLARATION = re.compile(
    rf"(?m)^[ \t]*(?:export[ \t]+)?(?:declare[ \t]+)?(?:const|let|var)[ \t]+"
    rf"({_IDENTIFIER})(?:[ \t]*:[^=\n]+)?[ \t]*=[ \t]*(?:async[ \t]+)?"
    rf"(?:\([^\n)]*\)|{_IDENTIFIER})(?:[ \t]*:[^=\n]+)?[ \t]*=>"
)
_FUNCTION_EXPRESSION = re.compile(
    rf"(?m)^[ \t]*(?:export[ \t]+)?(?:const|let|var)[ \t]+({_IDENTIFIER})"
    r"(?:[ \t]*:[^=\n]+)?[ \t]*=[ \t]*(?:async[ \t]+)?function\b"
)
_IMPORT_FROM = re.compile(
    r"(?m)^[ \t]*import[ \t]+(?:type[ \t]+)?[^;\n]*?[ \t]+from[ \t]*"
    r"['\"]([^'\"]+)['\"]"
)
_IMPORT_SIDE_EFFECT = re.compile(
    r"(?m)^[ \t]*import[ \t]*['\"]([^'\"]+)['\"]"
)
_EXPORT_FROM = re.compile(
    r"(?m)^[ \t]*export[ \t]+(?:type[ \t]+)?(?:\*|\{[^;\n]*\})[ \t]+from[ \t]*"
    r"['\"]([^'\"]+)['\"]"
)
_REQUIRE = re.compile(
    r"(?m)^[ \t]*(?:(?:const|let|var)\b[^;\n]*?=[ \t]*)?require\([ \t]*"
    r"['\"]([^'\"]+)['\"][ \t]*\)"
)
_IMPORT_BINDINGS = re.compile(
    r"(?s)^\s*import\s+(?:type\s+)?(.+?)\s+from\s*['\"]([^'\"]+)['\"]"
)
_DEFAULT_EXPORT_DECLARATION = re.compile(
    rf"(?m)^\s*export\s+default\s+(?:async\s+)?(?:class|function\*?)\s+({_IDENTIFIER})"
)


class JavaScriptAdapter:
    name = "javascript-typescript"
    suffixes = JAVASCRIPT_SUFFIXES

    def scan(self, context: AdapterContext) -> GraphFragment:
        aliases = _module_aliases(context.files)
        nodes: list[Node] = []
        edges: list[Edge] = []
        structural_sources: dict[str, str] = {}
        symbols_by_file: dict[str, dict[str, str]] = {}
        default_symbols: dict[str, str] = {}

        for relative in sorted(context.files):
            if PurePosixPath(relative).suffix.casefold() not in self.suffixes:
                continue
            source = context.read_text(relative)
            if source is None:
                continue
            structural = _mask_comments_and_templates(source)
            structural_sources[relative] = structural
            symbol_source = _mask_quoted_strings(structural)
            file_node = f"file:{relative}"

            file_symbols = _symbols(relative, symbol_source)
            nodes.extend(file_symbols)
            symbols_by_file[file_node] = {node.label: node.id for node in file_symbols}
            default_name = _default_export_name(symbol_source)
            if default_name is not None and default_name in symbols_by_file[file_node]:
                default_symbols[file_node] = symbols_by_file[file_node][default_name]
            edges.extend(
                Edge(file_node, node.id, "defines", "javascript-structural")
                for node in file_symbols
            )

        for relative in sorted(structural_sources):
            structural = structural_sources[relative]
            file_node = f"file:{relative}"
            relation = "tests" if context.kinds[relative] == "test" else "imports"
            for specifier in _module_specifiers(structural):
                target = _resolve_local_module(relative, specifier, aliases)
                if target is not None and target != file_node:
                    edges.append(Edge(file_node, target, relation, "javascript-structural"))
            for specifier, imported_names in _javascript_imports(structural):
                target = _resolve_local_module(relative, specifier, aliases)
                if target is None or target == file_node:
                    continue
                for imported_name in imported_names:
                    symbol_target = (
                        default_symbols.get(target)
                        if imported_name == "default"
                        else symbols_by_file.get(target, {}).get(imported_name)
                    )
                    if symbol_target is not None:
                        edges.append(
                            Edge(
                                file_node,
                                symbol_target,
                                relation,
                                "javascript-symbol-reference",
                            )
                        )

        edges.extend(_filename_test_edges(context, aliases))
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
    for match in _DECLARATION.finditer(source):
        raw_kind, name = match.groups()
        symbol_kind = "function" if raw_kind.startswith("function") else raw_kind
        discovered.setdefault(name, (symbol_kind, _line_number(source, match.start())))
    for pattern in (_ARROW_DECLARATION, _FUNCTION_EXPRESSION):
        for match in pattern.finditer(source):
            name = match.group(1)
            discovered.setdefault(name, ("function", _line_number(source, match.start())))

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


def _default_export_name(source: str) -> str | None:
    match = _DEFAULT_EXPORT_DECLARATION.search(source)
    return match.group(1) if match is not None else None


def _javascript_imports(source: str) -> list[tuple[str, tuple[str, ...]]]:
    statements = _module_statements(source)
    statements.extend(line for line in source.splitlines() if line.lstrip().startswith("import "))
    values: set[tuple[str, tuple[str, ...]]] = set()
    for statement in statements:
        flattened = " ".join(statement.splitlines())
        match = _IMPORT_BINDINGS.match(flattened)
        if match is None:
            continue
        clause, specifier = match.groups()
        if not specifier.startswith("."):
            continue
        imported: set[str] = set()
        leading = clause.split(",", 1)[0].strip()
        if leading and not leading.startswith(("{", "*")):
            imported.add("default")
        named_match = re.search(r"\{(.*?)\}", clause)
        if named_match is not None:
            for item in named_match.group(1).split(","):
                name = item.strip().removeprefix("type ").split()[0] if item.strip() else ""
                if re.fullmatch(_IDENTIFIER, name):
                    imported.add(name)
        if imported:
            values.add((specifier, tuple(sorted(imported))))
    return sorted(values)


def _module_specifiers(source: str) -> list[str]:
    values = {
        match.group(1)
        for pattern in (_IMPORT_FROM, _IMPORT_SIDE_EFFECT, _EXPORT_FROM, _REQUIRE)
        for match in pattern.finditer(source)
    }
    for statement in _module_statements(source):
        flattened = " ".join(statement.splitlines())
        for pattern in (_IMPORT_FROM, _IMPORT_SIDE_EFFECT, _EXPORT_FROM):
            match = pattern.search(flattened)
            if match is not None:
                values.add(match.group(1))
    return sorted(value for value in values if value.startswith("."))


def _module_statements(source: str) -> list[str]:
    statements: list[str] = []
    lines = source.splitlines()
    index = 0
    while index < len(lines):
        stripped = lines[index].lstrip()
        is_import = stripped.startswith("import ")
        is_reexport = re.match(r"export\s+(?:type\s+)?(?:\{|\*)", stripped) is not None
        if not (is_import or is_reexport):
            index += 1
            continue

        collected: list[str] = []
        brace_depth = 0
        while index < len(lines) and len(collected) < 50:
            line = lines[index]
            collected.append(line)
            brace_depth += line.count("{") - line.count("}")
            flattened = " ".join(collected)
            if any(
                pattern.search(flattened)
                for pattern in (_IMPORT_FROM, _IMPORT_SIDE_EFFECT, _EXPORT_FROM)
            ):
                break
            if ";" in line and brace_depth <= 0:
                break
            index += 1
            if index < len(lines) and brace_depth <= 0:
                next_line = lines[index]
                if next_line and not next_line[0].isspace():
                    break
        statements.append("\n".join(collected))
        index += 1
    return statements


def _module_aliases(files: Iterable[str]) -> dict[str, set[str]]:
    aliases: dict[str, set[str]] = defaultdict(set)
    for relative in files:
        path = PurePosixPath(relative)
        if path.suffix.casefold() not in JAVASCRIPT_SUFFIXES:
            continue
        node_id = f"file:{relative}"
        aliases[path.as_posix()].add(node_id)
        aliases[path.with_suffix("").as_posix()].add(node_id)
        if path.stem.casefold() == "index":
            aliases[path.parent.as_posix()].add(node_id)
    return aliases


def _resolve_local_module(
    relative: str,
    specifier: str,
    aliases: dict[str, set[str]],
) -> str | None:
    if not specifier.startswith(".") or "?" in specifier or "#" in specifier:
        return None
    candidate = posixpath.normpath(
        posixpath.join(PurePosixPath(relative).parent.as_posix(), specifier)
    )
    if candidate == ".." or candidate.startswith("../") or candidate.startswith("/"):
        return None

    direct = aliases.get(candidate, set())
    if len(direct) == 1:
        return next(iter(direct))
    suffix = PurePosixPath(candidate).suffix.casefold()
    if suffix in JAVASCRIPT_SUFFIXES:
        without_suffix = aliases.get(PurePosixPath(candidate).with_suffix("").as_posix(), set())
        if len(without_suffix) == 1:
            return next(iter(without_suffix))
    return None


def _filename_test_edges(
    context: AdapterContext,
    aliases: dict[str, set[str]],
) -> list[Edge]:
    edges: list[Edge] = []
    for relative in sorted(context.files):
        path = PurePosixPath(relative)
        if path.suffix.casefold() not in JAVASCRIPT_SUFFIXES or context.kinds[relative] != "test":
            continue
        stem = path.stem
        for marker in (".test", ".spec", "_test"):
            if not stem.casefold().endswith(marker):
                continue
            source_stem = stem[: -len(marker)]
            candidate = (path.parent / source_stem).as_posix()
            matches = aliases.get(candidate, set())
            if len(matches) == 1:
                edges.append(
                    Edge(
                        f"file:{relative}",
                        next(iter(matches)),
                        "tests",
                        "filename-convention",
                    )
                )
            break
    return edges


def _mask_comments_and_templates(source: str) -> str:
    """Mask comments and template contents while preserving offsets and quoted import strings."""

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
            if current in {"'", '"'}:
                quote = current
                state = "string"
            elif current == "`":
                result[index] = " "
                state = "template"
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
        elif state == "string":
            if current == "\\":
                index += 2
                continue
            if current == quote:
                state = "code"
        elif state == "template":
            if current == "\\":
                result[index] = " "
                if index + 1 < len(source) and source[index + 1] != "\n":
                    result[index + 1] = " "
                index += 2
                continue
            if current == "`":
                result[index] = " "
                state = "code"
            elif current != "\n":
                result[index] = " "
        index += 1
    return "".join(result)


def _mask_quoted_strings(source: str) -> str:
    result = list(source)
    index = 0
    quote = ""
    while index < len(source):
        current = source[index]
        if not quote:
            if current in {"'", '"'}:
                quote = current
                result[index] = " "
        elif current == "\\":
            result[index] = " "
            if index + 1 < len(source) and source[index + 1] != "\n":
                result[index + 1] = " "
            index += 2
            continue
        elif current == quote:
            result[index] = " "
            quote = ""
        elif current != "\n":
            result[index] = " "
        index += 1
    return "".join(result)
