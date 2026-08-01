from __future__ import annotations

import json
import math
import re
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import unquote, urlsplit

from .git_history import git_paths_match_head
from .models import Edge, Node

MAX_RECORDS = 100_000
MAX_JSON_VALUES = 500_000
MAX_JSON_DEPTH = 16
MAX_STRING = 4096
MAX_RULES = 64
MAX_LOCATIONS_PER_RESULT = 32
MAX_FILES_PER_TEST = 10_000
MAX_LINE = 1_000_000_000
FULL_SHA = re.compile(r"[0-9a-f]{40}")
WINDOWS_ABSOLUTE = re.compile(r"^[A-Za-z]:[/\\]")


def load_json_report(path: Path, relative: str) -> Any:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=_invalid_constant,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError(f"Cannot parse JSON evidence report {relative}: {exc}") from exc
    _validate_json_tree(value, relative)
    return value


def scip_fragment(
    document: Any,
    report: str,
    aliases: dict[str, tuple[str, ...]],
) -> tuple[list[Node], list[Edge]]:
    if not isinstance(document, dict) or not isinstance(document.get("documents"), list):
        raise ValueError(f"SCIP report is not protobuf JSON: {report}")
    if set(document) - {"metadata", "documents", "externalSymbols"}:
        raise ValueError(f"SCIP report contains unknown top-level fields: {report}")
    if "metadata" in document and not isinstance(document["metadata"], dict):
        raise ValueError(f"SCIP report metadata must be an object: {report}")
    external_symbols = document.get("externalSymbols", [])
    if not isinstance(external_symbols, list):
        raise ValueError(f"SCIP externalSymbols must be a list: {report}")
    totals: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0, 0])
    records = len(document["documents"]) + len(external_symbols)
    _check_records(records, report)
    for item in document["documents"]:
        if not isinstance(item, dict) or set(item) - {
            "relativePath",
            "language",
            "occurrences",
            "symbols",
        }:
            raise ValueError(f"SCIP report contains an invalid document: {report}")
        relative_path = _bounded_string(item.get("relativePath"), "SCIP relativePath", report)
        occurrences = item.get("occurrences", [])
        if not isinstance(occurrences, list):
            raise ValueError(f"SCIP document occurrences must be a list: {report}")
        symbols = item.get("symbols", [])
        if not isinstance(symbols, list):
            raise ValueError(f"SCIP document symbols must be a list: {report}")
        records += len(symbols)
        _check_records(records, report)
        target = _resolve_file(relative_path, aliases)
        counts = [0, 0, 0, 0]
        for occurrence in occurrences:
            records += 1
            _check_records(records, report)
            if not isinstance(occurrence, dict) or set(occurrence) - {
                "range",
                "symbol",
                "symbolRoles",
                "diagnostics",
                "syntaxKind",
                "overrideDocumentation",
            }:
                raise ValueError(f"SCIP report contains an invalid occurrence: {report}")
            _scip_range(occurrence.get("range"), report)
            symbol = occurrence.get("symbol", "")
            if not isinstance(symbol, str) or len(symbol) > MAX_STRING:
                raise ValueError(f"SCIP occurrence has an invalid symbol: {report}")
            roles = occurrence.get("symbolRoles", 0)
            if type(roles) is not int or roles < 0 or roles > (1 << 31) - 1:
                raise ValueError(f"SCIP occurrence has invalid symbol roles: {report}")
            diagnostics = occurrence.get("diagnostics", [])
            if not isinstance(diagnostics, list) or any(
                not isinstance(diagnostic, dict) for diagnostic in diagnostics
            ):
                raise ValueError(f"SCIP occurrence diagnostics must be a list: {report}")
            records += len(diagnostics)
            _check_records(records, report)
            counts[0] += 1
            counts[1 if roles & 1 else 2] += 1
            counts[3] += len(diagnostics)
        if target is not None:
            for index, value in enumerate(counts):
                totals[target][index] += value

    nodes: list[Node] = []
    edges: list[Edge] = []
    for target in sorted(totals):
        occurrences, definitions, references, diagnostics = totals[target]
        node_id = f"code-index:{report}:{target}"
        nodes.append(
            Node(
                id=node_id,
                kind="code-index",
                label=f"SCIP index {target}",
                metadata={
                    "format": "scip-protobuf-json",
                    "report": report,
                    "occurrences": occurrences,
                    "definitions": definitions,
                    "references": references,
                    "diagnostics": diagnostics,
                    "owner": "scanner",
                },
            )
        )
        edges.append(Edge(node_id, f"file:{target}", "references", "scip-json"))
    return nodes, edges


def sarif_fragment(
    document: Any,
    report: str,
    aliases: dict[str, tuple[str, ...]],
) -> tuple[list[Node], list[Edge]]:
    if (
        not isinstance(document, dict)
        or document.get("version") != "2.1.0"
        or not isinstance(document.get("runs"), list)
    ):
        raise ValueError(f"SARIF report is not version 2.1.0: {report}")
    totals: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"results": 0, "none": 0, "note": 0, "warning": 0, "error": 0, "rules": set()}
    )
    records = len(document["runs"])
    _check_records(records, report)
    for run in document["runs"]:
        if not isinstance(run, dict):
            raise ValueError(f"SARIF run must be an object: {report}")
        results = run.get("results", [])
        if not isinstance(results, list):
            raise ValueError(f"SARIF results must be a list: {report}")
        for result in results:
            records += 1
            _check_records(records, report)
            if not isinstance(result, dict):
                raise ValueError(f"SARIF result must be an object: {report}")
            level = result.get("level", "warning")
            if level not in {"none", "note", "warning", "error"}:
                raise ValueError(f"SARIF result has an invalid level: {report}")
            rule = result.get("ruleId")
            if rule is not None and (
                not isinstance(rule, str) or not rule or len(rule) > MAX_STRING
            ):
                raise ValueError(f"SARIF result has an invalid ruleId: {report}")
            locations = result.get("locations", [])
            if not isinstance(locations, list) or len(locations) > MAX_LOCATIONS_PER_RESULT:
                raise ValueError(f"SARIF result has invalid or excessive locations: {report}")
            records += len(locations)
            _check_records(records, report)
            targets: set[str] = set()
            for location in locations:
                target = _sarif_target(location, aliases)
                if target is not None:
                    targets.add(target)
            for target in targets:
                totals[target]["results"] += 1
                totals[target][level] += 1
                if rule is not None:
                    totals[target]["rules"].add(rule)

    nodes: list[Node] = []
    edges: list[Edge] = []
    for target in sorted(totals):
        result = totals[target]
        rules = sorted(result["rules"])
        node_id = f"finding-summary:{report}:{target}"
        nodes.append(
            Node(
                id=node_id,
                kind="finding-summary",
                label=f"SARIF findings {target}",
                metadata={
                    "format": "sarif-2.1.0",
                    "report": report,
                    "results": result["results"],
                    "none": result["none"],
                    "notes": result["note"],
                    "warnings": result["warning"],
                    "errors": result["error"],
                    "rule_count": len(rules),
                    "rules": rules[:MAX_RULES],
                    "rules_truncated": len(rules) > MAX_RULES,
                    "owner": "scanner",
                },
            )
        )
        edges.append(Edge(node_id, f"file:{target}", "references", "sarif-2.1.0"))
    return nodes, edges


def execution_map_fragment(
    document: Any,
    report: str,
    root: Path,
    aliases: dict[str, tuple[str, ...]],
    kinds: dict[str, str],
    head_revision: str | None,
) -> tuple[list[Node], list[Edge]]:
    if not isinstance(document, dict) or set(document) != {
        "schema_version",
        "commit",
        "completeness",
        "tests",
    }:
        raise ValueError(f"Invalid test execution map: {report}")
    if type(document["schema_version"]) is not int or document["schema_version"] != 1:
        raise ValueError(f"Unsupported test execution map schema: {report}")
    commit = document["commit"]
    if not isinstance(commit, str) or FULL_SHA.fullmatch(commit) is None:
        raise ValueError(f"Test execution map has an invalid commit: {report}")
    if document["completeness"] != "complete-observed-set":
        raise ValueError(f"Test execution map has an invalid completeness policy: {report}")
    tests = document["tests"]
    if not isinstance(tests, list) or len(tests) > MAX_RECORDS:
        raise ValueError(f"Test execution map has invalid or excessive tests: {report}")
    seen_tests: set[str] = set()
    records = len(tests)
    _check_records(records, report)
    mapped: list[tuple[str, tuple[str, ...]]] = []
    mapped_paths: set[str] = set()
    for item in tests:
        if not isinstance(item, dict) or set(item) != {"test", "files"}:
            raise ValueError(f"Test execution map contains an invalid test record: {report}")
        test_value = _bounded_string(item["test"], "execution test path", report)
        test = _resolve_file(test_value, aliases)
        if test is None or kinds.get(test) != "test" or test in seen_tests:
            raise ValueError(
                f"Test execution map contains an unresolved or duplicate test: {report}"
            )
        seen_tests.add(test)
        file_values = item["files"]
        if not isinstance(file_values, list) or len(file_values) > MAX_FILES_PER_TEST:
            raise ValueError(f"Test execution map contains invalid or excessive files: {report}")
        records += len(file_values)
        _check_records(records, report)
        observed: list[str] = []
        seen_files: set[str] = set()
        for value in file_values:
            source_value = _bounded_string(value, "execution source path", report)
            source = _resolve_file(source_value, aliases)
            if source is None or kinds.get(source) == "test" or source in seen_files:
                raise ValueError(
                    f"Test execution map contains an unresolved or duplicate source: {report}"
                )
            seen_files.add(source)
            observed.append(source)
        observed_tuple = tuple(sorted(observed))
        mapped.append((test, observed_tuple))
        mapped_paths.update((test, *observed_tuple))

    if head_revision is None:
        freshness = "unknown"
    elif commit != head_revision:
        freshness = "stale"
    else:
        path_alignment = git_paths_match_head(root, tuple(sorted(mapped_paths)))
        if path_alignment is True:
            freshness = "aligned"
        elif path_alignment is False:
            freshness = "stale"
        else:
            freshness = "unknown"

    nodes: list[Node] = []
    edges: list[Edge] = []
    for test, observed in mapped:
        node_id = f"test-execution:{report}:{test}"
        nodes.append(
            Node(
                id=node_id,
                kind="test-execution",
                label=f"Test execution {test}",
                metadata={
                    "format": "intentatlas-test-execution-map",
                    "report": report,
                    "commit": commit,
                    "freshness": freshness,
                    "completeness": "complete-observed-set",
                    "observed_files": len(observed),
                    "owner": "scanner",
                },
            )
        )
        edges.append(Edge(node_id, f"file:{test}", "references", "test-execution-map"))
        if freshness == "aligned":
            edges.extend(
                Edge(f"file:{test}", f"file:{source}", "tests", "test-execution-map")
                for source in observed
            )
    return nodes, edges


def _sarif_target(location: Any, aliases: dict[str, tuple[str, ...]]) -> str | None:
    if not isinstance(location, dict):
        return None
    physical = location.get("physicalLocation")
    if not isinstance(physical, dict):
        return None
    artifact = physical.get("artifactLocation")
    if not isinstance(artifact, dict):
        return None
    base_id = artifact.get("uriBaseId")
    if base_id not in {None, "%SRCROOT%"}:
        return None
    uri = artifact.get("uri")
    if not isinstance(uri, str) or len(uri) > MAX_STRING:
        return None
    try:
        parsed = urlsplit(uri)
    except ValueError:
        return None
    if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment:
        return None
    try:
        decoded = unquote(parsed.path, errors="strict")
    except (UnicodeDecodeError, ValueError):
        return None
    return _resolve_file(decoded, aliases)


def _resolve_file(value: str, aliases: dict[str, tuple[str, ...]]) -> str | None:
    candidate = value.strip().replace("\\", "/").removeprefix("./")
    pure = PurePosixPath(candidate)
    if (
        not candidate
        or pure.is_absolute()
        or WINDOWS_ABSOLUTE.match(candidate)
        or ".." in pure.parts
    ):
        return None
    matches = aliases.get(pure.as_posix().casefold(), ())
    return matches[0] if len(matches) == 1 else None


def _scip_range(value: Any, report: str) -> None:
    if (
        not isinstance(value, list)
        or len(value) not in {3, 4}
        or any(type(item) is not int or item < 0 or item > MAX_LINE for item in value)
    ):
        raise ValueError(f"SCIP occurrence has an invalid range: {report}")


def _bounded_string(value: Any, label: str, report: str) -> str:
    if not isinstance(value, str) or not value or len(value) > MAX_STRING:
        raise ValueError(f"{label} is invalid: {report}")
    return value


def _check_records(records: int, report: str) -> None:
    if records > MAX_RECORDS:
        raise ValueError(f"Open evidence report exceeds the {MAX_RECORDS}-record limit: {report}")


def _validate_json_tree(value: Any, report: str) -> None:
    remaining = MAX_JSON_VALUES
    stack: list[tuple[Any, int]] = [(value, 0)]
    while stack:
        current, depth = stack.pop()
        remaining -= 1
        if remaining < 0 or depth > MAX_JSON_DEPTH:
            raise ValueError(f"JSON evidence report is too deeply nested or large: {report}")
        if isinstance(current, str):
            if len(current) > MAX_STRING:
                raise ValueError(f"JSON evidence report contains an oversized string: {report}")
        elif isinstance(current, dict):
            if any(not isinstance(key, str) or len(key) > MAX_STRING for key in current):
                raise ValueError(f"JSON evidence report contains an invalid key: {report}")
            stack.extend((item, depth + 1) for item in current.values())
        elif isinstance(current, list):
            stack.extend((item, depth + 1) for item in current)
        elif type(current) is float and not math.isfinite(current):
            raise ValueError(f"JSON evidence report contains a non-finite number: {report}")
        elif current is not None and type(current) not in {bool, int, float}:
            raise ValueError(f"JSON evidence report contains an unsupported value: {report}")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"Duplicate JSON key: {key}")
        value[key] = item
    return value


def _invalid_constant(value: str) -> None:
    raise ValueError(f"Invalid JSON numeric constant: {value}")
