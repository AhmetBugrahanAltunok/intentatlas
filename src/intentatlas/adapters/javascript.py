from __future__ import annotations

import posixpath
import re
from collections import defaultdict
from collections.abc import Iterable
from pathlib import PurePosixPath

from ..models import Edge, Node
from .base import AdapterContext, GraphFragment, canonical_graph_fragment

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
    cache_input_suffixes = suffixes
    cache_version = 2
    evidence_kinds = frozenset(
        {
            "filename-convention",
            "javascript-structural",
            "javascript-symbol-reference",
        }
    )

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
                target = _resolve_local_module(relative, specifier, aliases, context)
                if target is not None and target != file_node:
                    edges.append(Edge(file_node, target, relation, "javascript-structural"))
            for specifier, imported_names in _javascript_imports(structural):
                target = _resolve_local_module(relative, specifier, aliases, context)
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
        return canonical_graph_fragment(nodes, edges)


def _symbols(relative: str, source: str) -> list[Node]:
    declarations: list[tuple[int, str, str, re.Match[str]]] = []
    for match in _DECLARATION.finditer(source):
        raw_kind, name = match.groups()
        symbol_kind = "function" if raw_kind.startswith("function") else raw_kind
        mode = "function" if symbol_kind == "function" else symbol_kind
        declarations.append((match.start(), name, mode, match))
    for match in _ARROW_DECLARATION.finditer(source):
        declarations.append((match.start(), match.group(1), "arrow", match))
    for match in _FUNCTION_EXPRESSION.finditer(source):
        declarations.append((match.start(), match.group(1), "function-expression", match))

    declarations.sort(key=lambda item: (item[0], item[1], item[2]))
    discovered: dict[str, tuple[str, int, int | None]] = {}
    for index, (start, name, mode, match) in enumerate(declarations):
        boundary = declarations[index + 1][0] if index + 1 < len(declarations) else len(source)
        symbol_kind = "function" if mode in {"function", "arrow", "function-expression"} else mode
        discovered.setdefault(
            name,
            (
                symbol_kind,
                _line_number(source, start),
                _javascript_end_line(source, match, mode, boundary),
            ),
        )

    return [
        Node(
            id=f"symbol:{relative}::{name}",
            kind="symbol",
            label=name,
            path=relative,
            metadata=_symbol_metadata(kind, line, end_line),
        )
        for name, (kind, line, end_line) in sorted(discovered.items())
    ]


def _line_number(source: str, offset: int) -> int:
    return source.count("\n", 0, offset) + 1


def _symbol_metadata(kind: str, line: int, end_line: int | None) -> dict[str, str | int]:
    metadata: dict[str, str | int] = {
        "symbol_kind": kind,
        "line": line,
        "owner": "scanner",
    }
    if end_line is not None:
        metadata["end_line"] = end_line
    return metadata


def _javascript_end_line(
    source: str,
    match: re.Match[str],
    mode: str,
    boundary: int,
) -> int | None:
    if mode == "type":
        return _statement_end_line(source, match.end(), boundary)
    if mode == "arrow":
        cursor = _next_content(source, match.end(), boundary)
        if cursor is None:
            return None
        if source[cursor] != "{":
            return _statement_end_line(source, cursor, boundary)
        end = _balanced_brace_end(source, cursor, boundary)
        return None if end is None else _line_number(source, end)
    if mode in {"function", "function-expression"}:
        body = _javascript_function_body(source, match.end(), boundary)
        if body is None:
            return None
        end = _balanced_brace_end(source, body, boundary)
        return None if end is None else _line_number(source, end)

    opening = _body_brace_after_header(source, match.end(), boundary)
    if opening is None:
        return None
    end = _balanced_brace_end(source, opening, boundary)
    return None if end is None else _line_number(source, end)


def _javascript_function_body(source: str, start: int, boundary: int) -> int | None:
    parameters = source.find("(", start, boundary)
    if parameters < 0:
        return None
    parameters_end = _matching_delimiter(source, parameters, "(", ")", boundary)
    if parameters_end is None:
        return None
    return _body_brace_after_header(source, parameters_end + 1, boundary)


def _body_brace_after_header(source: str, start: int, boundary: int) -> int | None:
    """Find a declaration body after balanced generic/return-type header shapes."""

    pairs = {"(": ")", "[": "]", "{": "}", "<": ">"}
    stack: list[str] = []
    index = start
    while index < boundary:
        character = source[index]
        if character in pairs:
            if character == "{" and not stack:
                prefix = source[start:index].rstrip()
                type_header = ":" in source[start:index]
                type_continuation = _next_content_after_balanced_brace(
                    source, index, boundary
                )
                if (
                    prefix.endswith((":", "=>", "|", "&", "?"))
                    or type_header
                    and type_continuation in {"?", ":", "|", "&"}
                ):
                    type_end = _matching_delimiter(
                        source, index, "{", "}", boundary
                    )
                    if type_end is None:
                        return None
                    index = type_end + 1
                    continue
                return index
            stack.append(pairs[character])
            index += 1
            continue
        if character in pairs.values():
            if not stack or stack.pop() != character:
                return None
            index += 1
            continue
        if character in {";", "="} and not stack:
            return None
        index += 1
    return None


def _next_content_after_balanced_brace(
    source: str, start: int, boundary: int
) -> str | None:
    end = _matching_delimiter(source, start, "{", "}", boundary)
    if end is None:
        return None
    content = _next_content(source, end + 1, boundary)
    return None if content is None else source[content]


def _statement_end_line(source: str, start: int, boundary: int) -> int | None:
    pairs = {"(": ")", "[": "]", "{": "}"}
    stack: list[str] = []
    last_content: int | None = None
    for index in range(start, boundary):
        character = source[index]
        if character in pairs:
            stack.append(pairs[character])
            last_content = index
            continue
        if character in pairs.values():
            if not stack or stack.pop() != character:
                return None
            last_content = index
            continue
        if character == ";" and not stack:
            return _line_number(source, index)
        if character == "\n" and not stack:
            return None if last_content is None else _line_number(source, last_content)
        if not character.isspace():
            last_content = index
    return None if stack or last_content is None else _line_number(source, last_content)


def _matching_delimiter(
    source: str,
    start: int,
    opening: str,
    closing: str,
    boundary: int,
) -> int | None:
    if start >= boundary or source[start] != opening:
        return None
    depth = 0
    for index in range(start, boundary):
        if source[index] == opening:
            depth += 1
        elif source[index] == closing:
            depth -= 1
            if depth == 0:
                return index
    return None


def _balanced_brace_end(source: str, start: int, boundary: int) -> int | None:
    """Find a brace end and reject unmatched closings before the next declaration."""

    if start >= boundary or source[start] != "{":
        return None
    depth = 0
    first_end: int | None = None
    for index in range(start, boundary):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            if depth == 0:
                return None
            depth -= 1
            if depth == 0 and first_end is None:
                first_end = index
    return first_end if depth == 0 else None


def _next_content(source: str, start: int, boundary: int) -> int | None:
    for index in range(start, boundary):
        if not source[index].isspace():
            return index
    return None


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
    return sorted(values)


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
    context: AdapterContext,
) -> str | None:
    if "?" in specifier or "#" in specifier:
        return None
    candidates: set[str] = set()
    if specifier.startswith("."):
        candidate = posixpath.normpath(
            posixpath.join(PurePosixPath(relative).parent.as_posix(), specifier)
        )
        candidates.update(_alias_targets(candidate, aliases))
    else:
        owners = context.workspace_owners.get(relative, ())
        if len(owners) != 1:
            return None
        for owner, pattern, targets in context.module_aliases:
            if owner != owners[0]:
                continue
            wildcard = _alias_wildcard(pattern, specifier)
            if wildcard is None:
                continue
            for target in targets:
                candidates.update(_alias_targets(target.replace("*", wildcard), aliases))
    return next(iter(candidates)) if len(candidates) == 1 else None


def _alias_targets(candidate: str, aliases: dict[str, set[str]]) -> set[str]:
    if candidate == ".." or candidate.startswith("../") or candidate.startswith("/"):
        return set()
    targets = set(aliases.get(candidate, set()))
    suffix = PurePosixPath(candidate).suffix.casefold()
    if suffix in JAVASCRIPT_SUFFIXES:
        targets.update(aliases.get(PurePosixPath(candidate).with_suffix("").as_posix(), set()))
    return targets


def _alias_wildcard(pattern: str, specifier: str) -> str | None:
    if pattern.count("*") > 1:
        return None
    if "*" not in pattern:
        return "" if pattern == specifier else None
    prefix, suffix = pattern.split("*", maxsplit=1)
    if not specifier.startswith(prefix) or not specifier.endswith(suffix):
        return None
    end = len(specifier) - len(suffix) if suffix else None
    return specifier[len(prefix) : end]


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
