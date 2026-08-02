from __future__ import annotations

import re
import xml.etree.ElementTree as ET  # nosec B405
from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath
from typing import Any

from .models import Edge, Node
from .open_evidence import (
    execution_map_fragment,
    load_json_report,
    sarif_fragment,
    scip_fragment,
)
from .safe_io import read_bounded_regular_file

MAX_REPORT_BYTES = 10_000_000
MAX_REPORT_RECORDS = 100_000
MAX_DURATION_SECONDS = Decimal("1000000000")
UNSAFE_XML = re.compile(br"<!\s*(?:DOCTYPE|ENTITY)\b", re.IGNORECASE)
WINDOWS_ABSOLUTE = re.compile(r"^[A-Za-z]:[/\\]")


@dataclass(frozen=True, slots=True)
class EvidenceFragment:
    nodes: tuple[Node, ...] = ()
    edges: tuple[Edge, ...] = ()


def import_evidence(
    root: Path,
    *,
    files: dict[str, Path],
    kinds: dict[str, str],
    vault: Path,
    coverage_reports: list[str],
    test_reports: list[str],
    scip_reports: list[str],
    sarif_reports: list[str],
    test_execution_reports: list[str],
    head_revision: str | None,
    workspace_owners: dict[str, tuple[str, ...]] | None = None,
    graph_nodes: dict[str, Node] | None = None,
) -> EvidenceFragment:
    nodes: list[Node] = []
    edges: list[Edge] = []
    aliases = _file_aliases(files)

    for configured in coverage_reports:
        report, relative = _report_path(root, vault, configured, "coverage report")
        document = _read_xml(report, relative)
        report_nodes, report_edges = _coverage_fragment(document, relative, aliases)
        nodes.extend(report_nodes)
        edges.extend(report_edges)

    for configured in test_reports:
        report, relative = _report_path(root, vault, configured, "test report")
        document = _read_xml(report, relative)
        report_nodes, report_edges = _test_fragment(document, relative, aliases, kinds)
        nodes.extend(report_nodes)
        edges.extend(report_edges)

    for configured in scip_reports:
        report, relative = _report_path(root, vault, configured, "SCIP report")
        document = load_json_report(report, relative)
        report_nodes, report_edges = scip_fragment(
            document,
            relative,
            aliases,
            root=root,
            kinds=kinds,
            head_revision=head_revision,
            workspace_owners=workspace_owners or {},
            graph_nodes=graph_nodes or {},
        )
        nodes.extend(report_nodes)
        edges.extend(report_edges)

    for configured in sarif_reports:
        report, relative = _report_path(root, vault, configured, "SARIF report")
        document = load_json_report(report, relative)
        report_nodes, report_edges = sarif_fragment(document, relative, aliases)
        nodes.extend(report_nodes)
        edges.extend(report_edges)

    for configured in test_execution_reports:
        report, relative = _report_path(root, vault, configured, "test execution report")
        document = load_json_report(report, relative)
        report_nodes, report_edges = execution_map_fragment(
            document,
            relative,
            root,
            aliases,
            kinds,
            head_revision,
        )
        nodes.extend(report_nodes)
        edges.extend(report_edges)

    return EvidenceFragment(
        nodes=tuple(sorted(nodes, key=lambda item: item.id)),
        edges=tuple(
            sorted(
                edges,
                key=lambda item: (item.source, item.target, item.relation, item.evidence),
            )
        ),
    )


def _report_path(root: Path, vault: Path, configured: str, label: str) -> tuple[Path, str]:
    source = configured.strip().replace("\\", "/")
    pure = PurePosixPath(source)
    if not source or pure.is_absolute() or WINDOWS_ABSOLUTE.match(source) or ".." in pure.parts:
        raise ValueError(f"Configured {label} must be a project-relative path: {configured}")

    private_relatives = {
        "atlas/private",
        (vault.relative_to(root) / "Private").as_posix().casefold(),
    }
    normalized = pure.as_posix().removeprefix("./")
    folded = normalized.casefold()
    if any(
        folded == private or folded.startswith(f"{private}/")
        for private in private_relatives
    ):
        raise ValueError(f"Configured {label} may not be inside atlas/Private: {configured}")

    unresolved = root / Path(*pure.parts)
    if unresolved.is_symlink():
        raise ValueError(f"Configured {label} may not be a symbolic link: {configured}")
    candidate = unresolved.resolve()
    base = root.resolve()
    if base not in candidate.parents:
        raise ValueError(f"Configured {label} escapes project root: {configured}")
    private_roots = {
        base / "atlas" / "Private",
        vault / "Private",
    }
    if any(
        candidate == private or private in candidate.parents for private in private_roots
    ):
        raise ValueError(f"Configured {label} may not be inside atlas/Private: {configured}")
    if not candidate.is_file():
        raise ValueError(f"Configured {label} does not exist: {configured}")
    try:
        size = candidate.stat().st_size
    except OSError as exc:
        raise ValueError(f"Cannot inspect configured {label} {configured}: {exc}") from exc
    if size > MAX_REPORT_BYTES:
        raise ValueError(
            f"Configured {label} exceeds the {MAX_REPORT_BYTES}-byte limit: {configured}"
        )
    return candidate, candidate.relative_to(base).as_posix()


def _read_xml(path: Path, relative: str) -> ET.Element:
    # XML input is size-bounded and DTD/entity declarations are rejected before parsing.
    data = read_bounded_regular_file(path, MAX_REPORT_BYTES)
    if data is None:
        raise ValueError(f"Cannot read bounded regular evidence report {relative}")
    if UNSAFE_XML.search(data):
        raise ValueError(f"Evidence report contains a forbidden XML declaration: {relative}")
    try:
        # The byte limit and declaration rejection above remove the entity-expansion attack path.
        return ET.fromstring(data)  # nosec B314
    except ET.ParseError as exc:
        raise ValueError(f"Cannot parse evidence report {relative}: {exc}") from exc


def _coverage_fragment(
    document: ET.Element, report: str, aliases: dict[str, tuple[str, ...]]
) -> tuple[list[Node], list[Edge]]:
    if _local_name(document.tag) != "coverage":
        raise ValueError(f"Coverage report is not Cobertura XML: {report}")
    totals: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    records = 0
    for class_node in (node for node in document.iter() if _local_name(node.tag) == "class"):
        target = _resolve_file(class_node.get("filename", ""), aliases)
        lines = [node for node in class_node.iter() if _local_name(node.tag) == "line"]
        records += 1 + len(lines)
        _check_record_limit(records, report)
        if target is None:
            continue
        totals[target][1] += len(lines)
        totals[target][0] += sum(_nonnegative_int(line.get("hits")) > 0 for line in lines)

    nodes: list[Node] = []
    edges: list[Edge] = []
    for target in sorted(totals):
        covered, valid = totals[target]
        node_id = f"coverage:{report}:{target}"
        nodes.append(
            Node(
                id=node_id,
                kind="coverage",
                label=f"Coverage {target}",
                metadata={
                    "format": "cobertura-xml",
                    "report": report,
                    "lines_covered": covered,
                    "lines_valid": valid,
                    "line_rate": round(covered / valid, 6) if valid else 0.0,
                    "owner": "scanner",
                },
            )
        )
        edges.append(Edge(node_id, f"file:{target}", "proves", "cobertura-xml"))
    return nodes, edges


def _test_fragment(
    document: ET.Element,
    report: str,
    aliases: dict[str, tuple[str, ...]],
    kinds: dict[str, str],
) -> tuple[list[Node], list[Edge]]:
    if _local_name(document.tag) not in {"testsuite", "testsuites"}:
        raise ValueError(f"Test report is not JUnit XML: {report}")
    totals: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
            "duration": Decimal(0),
        }
    )
    records = 0
    for case in (node for node in document.iter() if _local_name(node.tag) == "testcase"):
        records += 1
        _check_record_limit(records, report)
        target = _test_target(case, aliases)
        if target is None or kinds.get(target) != "test":
            continue
        status = _test_status(case)
        totals[target]["total"] += 1
        totals[target][status] += 1
        totals[target]["duration"] += _duration(case.get("time"))

    nodes: list[Node] = []
    edges: list[Edge] = []
    for target in sorted(totals):
        result = totals[target]
        node_id = f"test-result:{report}:{target}"
        nodes.append(
            Node(
                id=node_id,
                kind="test-result",
                label=f"Test results {target}",
                metadata={
                    "format": "junit-xml",
                    "report": report,
                    "total": result["total"],
                    "passed": result["passed"],
                    "failed": result["failed"],
                    "errors": result["errors"],
                    "skipped": result["skipped"],
                    "duration_seconds": float(round(result["duration"], 6)),
                    "owner": "scanner",
                },
            )
        )
        edges.append(Edge(node_id, f"file:{target}", "proves", "junit-xml"))
    return nodes, edges


def _file_aliases(files: dict[str, Path]) -> dict[str, tuple[str, ...]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for relative in files:
        grouped[relative.casefold()].append(relative)
    return {key: tuple(sorted(values)) for key, values in grouped.items()}


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


def _test_target(case: ET.Element, aliases: dict[str, tuple[str, ...]]) -> str | None:
    direct = _resolve_file(case.get("file", ""), aliases)
    if direct is not None:
        return direct
    classname = case.get("classname", "").strip()
    if not classname or any(separator in classname for separator in ("/", "\\", ":")):
        return None
    return _resolve_file(classname.replace(".", "/") + ".py", aliases)


def _test_status(case: ET.Element) -> str:
    children = {child.tag.rsplit("}", 1)[-1].casefold() for child in case}
    if "error" in children:
        return "errors"
    if "failure" in children:
        return "failed"
    if "skipped" in children:
        return "skipped"
    return "passed"


def _duration(value: str | None) -> Decimal:
    try:
        duration = Decimal(value or "0")
    except InvalidOperation:
        return Decimal(0)
    if not duration.is_finite() or duration < 0 or duration > MAX_DURATION_SECONDS:
        return Decimal(0)
    return duration


def _nonnegative_int(value: str | None) -> int:
    try:
        parsed = int(value or "0")
    except ValueError:
        return 0
    return max(0, parsed)


def _check_record_limit(records: int, report: str) -> None:
    if records > MAX_REPORT_RECORDS:
        raise ValueError(
            f"Evidence report exceeds the {MAX_REPORT_RECORDS}-record limit: {report}"
        )


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].casefold()
