from __future__ import annotations

import hashlib
import json
import math
import re
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import unquote, urlsplit

from .git_history import git_paths_match_head
from .models import Edge, Node
from .safe_io import read_bounded_regular_file

MAX_REPORT_BYTES = 10_000_000
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
        data = read_bounded_regular_file(path, MAX_REPORT_BYTES)
        if data is None:
            raise ValueError("report is not a stable bounded regular file")
        value = json.loads(
            data.decode("utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=_invalid_constant,
        )
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError(f"Cannot parse JSON evidence report {relative}: {exc}") from exc
    _validate_json_tree(value, relative)
    return value


def scip_fragment(
    document: Any,
    report: str,
    aliases: dict[str, tuple[str, ...]],
    *,
    root: Path | None = None,
    kinds: dict[str, str] | None = None,
    head_revision: str | None = None,
    workspace_owners: dict[str, tuple[str, ...]] | None = None,
    graph_nodes: dict[str, Node] | None = None,
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
    metadata = document.get("metadata", {})
    producer, producer_version, schema, revision, compatible = _scip_metadata(
        metadata, report
    )
    owners_by_path = workspace_owners or {}
    file_kinds = kinds or {}
    symbols_by_path = _symbols_by_path(graph_nodes or {})
    totals: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0, 0, 0, 0])
    observations: list[dict[str, Any]] = []
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
        counts = [0, 0, 0, 0, 0, 0]
        unique_owner = (
            owners_by_path.get(target, ())[0]
            if target is not None and len(owners_by_path.get(target, ())) == 1
            else None
        )
        freshness = _scip_freshness(root, target, revision, head_revision)
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
            normalized_range = _scip_range(occurrence.get("range"), report)
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
            supported_role = roles in {0, 1}
            confidence = (
                "exact"
                if target is not None
                and unique_owner is not None
                and compatible
                and freshness == "aligned"
                and supported_role
                and symbol
                else "fallback"
            )
            if confidence == "exact":
                counts[4] += 1
            else:
                counts[5] += 1
            if target is not None and symbol:
                observations.append(
                    {
                        "path": target,
                        "range": normalized_range,
                        "symbol": symbol,
                        "role": "definition" if roles & 1 else "reference",
                        "confidence": confidence,
                        "freshness": freshness,
                        "owner": unique_owner,
                    }
                )
        if target is not None:
            for index, value in enumerate(counts):
                totals[target][index] += value

    nodes: list[Node] = []
    edges: list[Edge] = []
    for target in sorted(totals):
        occurrences, definitions, references, diagnostics, exact, rejected = totals[target]
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
                    "producer": producer,
                    "producer_version": producer_version,
                    "schema": schema,
                    "revision": revision or "unavailable",
                    "freshness": _scip_freshness(root, target, revision, head_revision),
                    "exact_occurrences": exact,
                    "fallback_occurrences": rejected,
                    "owner": "scanner",
                },
            )
        )
        edges.append(Edge(node_id, f"file:{target}", "references", "scip-json"))
    definitions_by_symbol: dict[str, set[str]] = defaultdict(set)
    for observation in observations:
        if observation["confidence"] != "exact" or observation["role"] != "definition":
            continue
        candidates = _symbols_at_range(
            symbols_by_path.get(observation["path"], ()), observation["range"]
        )
        if len(candidates) == 1:
            definitions_by_symbol[observation["symbol"]].add(candidates[0])

    for observation in observations:
        fingerprint = hashlib.sha256(observation["symbol"].encode("utf-8")).hexdigest()
        identity = json.dumps(
            [report, observation["path"], observation["range"], fingerprint, observation["role"]],
            separators=(",", ":"),
        )
        node_id = f"semantic-observation:{hashlib.sha256(identity.encode('utf-8')).hexdigest()}"
        nodes.append(
            Node(
                node_id,
                "semantic-observation",
                f"SCIP {observation['role']} {observation['path']}",
                observation["path"],
                {
                    "format": "scip-protobuf-json",
                    "report": report,
                    "producer": producer,
                    "producer_version": producer_version,
                    "schema": schema,
                    "revision": revision or "unavailable",
                    "freshness": observation["freshness"],
                    "confidence": observation["confidence"],
                    "range": observation["range"],
                    "role": observation["role"],
                    "workspace_owner": observation["owner"] or "ambiguous",
                    "symbol_fingerprint": fingerprint,
                    "owner": "scanner",
                },
            )
        )
        edges.append(Edge(node_id, f"file:{observation['path']}", "references", "scip-json"))
        if observation["confidence"] != "exact":
            continue
        targets = definitions_by_symbol.get(observation["symbol"], set())
        if len(targets) != 1:
            continue
        target = next(iter(targets))
        if observation["role"] == "definition":
            edges.append(Edge(node_id, target, "proves", "scip-exact"))
        else:
            relation = "tests" if file_kinds.get(observation["path"]) == "test" else "references"
            edges.append(
                Edge(f"file:{observation['path']}", target, relation, "scip-exact")
            )
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
        observed_files: list[str] = []
        seen_files: set[str] = set()
        for value in file_values:
            source_value = _bounded_string(value, "execution source path", report)
            source = _resolve_file(source_value, aliases)
            if source is None or kinds.get(source) == "test" or source in seen_files:
                raise ValueError(
                    f"Test execution map contains an unresolved or duplicate source: {report}"
                )
            seen_files.add(source)
            observed_files.append(source)
        observed_tuple = tuple(sorted(observed_files))
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
    for test, observed_paths in mapped:
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
                    "observed_files": len(observed_paths),
                    "owner": "scanner",
                },
            )
        )
        edges.append(Edge(node_id, f"file:{test}", "references", "test-execution-map"))
        if freshness == "aligned":
            edges.extend(
                Edge(f"file:{test}", f"file:{source}", "tests", "test-execution-map")
                for source in observed_paths
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


def _scip_range(value: Any, report: str) -> list[int]:
    if (
        not isinstance(value, list)
        or len(value) not in {3, 4}
        or any(type(item) is not int or item < 0 or item > MAX_LINE for item in value)
    ):
        raise ValueError(f"SCIP occurrence has an invalid range: {report}")
    if len(value) == 3 and value[2] < value[1]:
        raise ValueError(f"SCIP occurrence has an invalid range: {report}")
    if len(value) == 4 and (value[2], value[3]) < (value[0], value[1]):
        raise ValueError(f"SCIP occurrence has an invalid range: {report}")
    return list(value)


def _scip_metadata(
    metadata: dict[str, Any], report: str
) -> tuple[str, str, str, str | None, bool]:
    if not isinstance(metadata, dict):
        raise ValueError(f"SCIP report metadata must be an object: {report}")
    tool = metadata.get("toolInfo", {})
    if not isinstance(tool, dict):
        raise ValueError(f"SCIP toolInfo must be an object: {report}")
    producer = _scip_metadata_string(tool.get("name", "unknown"), "producer", report)
    producer_version = _scip_metadata_string(
        tool.get("version", "unknown"), "producer version", report
    )
    schema = _scip_metadata_string(
        metadata.get("version", metadata.get("protocolVersion", "unknown")),
        "schema",
        report,
    )
    revision = metadata.get("revision")
    if revision is not None and (
        not isinstance(revision, str) or FULL_SHA.fullmatch(revision) is None
    ):
        raise ValueError(f"SCIP revision is invalid: {report}")
    compatible = schema == "0.3.0" and producer in {
        "scip-go",
        "scip-python",
        "scip-typescript",
    }
    return producer, producer_version, schema, revision, compatible


def _scip_metadata_string(value: Any, label: str, report: str) -> str:
    if not isinstance(value, str) or not value or len(value) > MAX_STRING:
        raise ValueError(f"SCIP {label} is invalid: {report}")
    return value


def _scip_freshness(
    root: Path | None,
    target: str | None,
    revision: str | None,
    head_revision: str | None,
) -> str:
    if root is None or target is None or revision is None or head_revision is None:
        return "unknown"
    if revision != head_revision:
        return "stale"
    alignment = git_paths_match_head(root, (target,))
    if alignment is True:
        return "aligned"
    return "stale" if alignment is False else "unknown"


def _symbols_by_path(nodes: dict[str, Node]) -> dict[str, tuple[Node, ...]]:
    grouped: dict[str, list[Node]] = defaultdict(list)
    for node in nodes.values():
        if node.kind == "symbol" and node.path is not None:
            grouped[node.path].append(node)
    return {
        path: tuple(sorted(values, key=lambda item: item.id))
        for path, values in sorted(grouped.items())
    }


def _symbols_at_range(nodes: tuple[Node, ...], value: list[int]) -> tuple[str, ...]:
    line = value[0] + 1
    candidates = [
        node.id
        for node in nodes
        if node.metadata.get("line") == line
        and (
            "end_line" not in node.metadata
            or int(node.metadata["end_line"]) >= (value[2] + 1 if len(value) == 4 else line)
        )
    ]
    return tuple(sorted(candidates))


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
