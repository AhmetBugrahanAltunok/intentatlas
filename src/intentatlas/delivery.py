from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import quote, urlsplit

from .models import Edge, Node

MAX_REPORT_BYTES = 10_000_000
MAX_RECORDS = 10_000
MAX_LINKS = 100_000
MAX_LIST_ITEMS = 1_000
WINDOWS_ABSOLUTE = re.compile(r"^[A-Za-z]:[/\\]")
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,99}$")
SAFE_STATE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,39}$")


@dataclass(frozen=True, slots=True)
class DeliveryFragment:
    nodes: tuple[Node, ...] = ()
    edges: tuple[Edge, ...] = ()


def import_delivery(
    root: Path,
    *,
    files: dict[str, Path],
    graph_nodes: dict[str, Node],
    vault: Path,
    reports: list[str],
) -> DeliveryFragment:
    nodes: list[Node] = []
    edges: list[Edge] = []
    aliases = _file_aliases(files)
    for configured in reports:
        path, relative = _report_path(root, vault, configured)
        document = _read_json(path, relative)
        report_nodes, report_edges = _delivery_fragment(
            document, report=relative, aliases=aliases, graph_nodes=graph_nodes
        )
        nodes.extend(report_nodes)
        edges.extend(report_edges)
    return DeliveryFragment(
        nodes=tuple(sorted(nodes, key=lambda item: item.id)),
        edges=tuple(
            sorted(
                edges,
                key=lambda item: (item.source, item.target, item.relation, item.evidence),
            )
        ),
    )


def _delivery_fragment(
    document: dict[str, Any],
    *,
    report: str,
    aliases: dict[str, tuple[str, ...]],
    graph_nodes: dict[str, Node],
) -> tuple[list[Node], list[Edge]]:
    _only_keys(
        document,
        {"schema_version", "source", "repository", "issues", "pull_requests"},
        "delivery report",
    )
    if document.get("schema_version") != 1:
        raise ValueError(f"Unsupported delivery report schema in {report}")
    source = _text(document.get("source"), "source", 100)
    repository = _text(document.get("repository"), "repository", 200)
    issues = _records(document.get("issues", []), "issues")
    pull_requests = _records(document.get("pull_requests", []), "pull requests")
    if len(issues) + len(pull_requests) > MAX_RECORDS:
        raise ValueError(f"Delivery report exceeds the {MAX_RECORDS}-record limit: {report}")

    namespace = f"{_component(source)}:{_component(repository)}"
    nodes: list[Node] = []
    edges: list[Edge] = []
    issue_nodes: dict[str, str] = {}
    link_count = 0

    for record in issues:
        _only_keys(record, {"id", "title", "state", "url", "labels", "intent_ids"}, "issue")
        external_id = _external_id(record.get("id"), "issue")
        if external_id in issue_nodes:
            raise ValueError(f"Duplicate issue ID in {report}: {external_id}")
        title = _text(record.get("title"), "issue title", 300)
        state = _state(record.get("state"), "issue")
        url = _url(record.get("url"), "issue")
        labels = sorted(set(_strings(record.get("labels", []), "issue labels", 50, 100)))
        intent_ids = _strings(record.get("intent_ids", []), "issue intent IDs")
        node_id = f"delivery-issue:{namespace}:{_component(external_id)}"
        issue_nodes[external_id] = node_id
        nodes.append(
            Node(
                id=node_id,
                kind="delivery-issue",
                label=f"Issue {external_id} — {title}",
                metadata={
                    "source": source,
                    "repository": repository,
                    "external_id": external_id,
                    "state": state,
                    "url": url,
                    "labels": labels,
                    "report": report,
                    "owner": "scanner",
                },
            )
        )
        for intent_id in intent_ids:
            intent_target = graph_nodes.get(intent_id)
            if intent_target is not None and intent_target.kind in {"requirement", "decision"}:
                edges.append(Edge(intent_id, node_id, "tracked-by", "delivery-json"))
                link_count += 1
        if link_count > MAX_LINKS:
            raise ValueError(f"Delivery report exceeds the {MAX_LINKS}-link limit: {report}")

    pr_ids: set[str] = set()
    for record in pull_requests:
        _only_keys(
            record,
            {
                "id",
                "title",
                "state",
                "url",
                "draft",
                "issue_ids",
                "changed_files",
                "commit_shas",
            },
            "pull request",
        )
        external_id = _external_id(record.get("id"), "pull request")
        if external_id in pr_ids:
            raise ValueError(f"Duplicate pull-request ID in {report}: {external_id}")
        pr_ids.add(external_id)
        title = _text(record.get("title"), "pull-request title", 300)
        state = _state(record.get("state"), "pull request")
        url = _url(record.get("url"), "pull request")
        draft = record.get("draft", False)
        if not isinstance(draft, bool):
            raise ValueError("Pull-request draft must be a boolean")
        issue_ids = _strings(record.get("issue_ids", []), "pull-request issue IDs")
        changed_files = _strings(record.get("changed_files", []), "changed files")
        commit_shas = _strings(record.get("commit_shas", []), "commit SHAs")
        node_id = f"pull-request:{namespace}:{_component(external_id)}"
        nodes.append(
            Node(
                id=node_id,
                kind="pull-request",
                label=f"PR {external_id} — {title}",
                metadata={
                    "source": source,
                    "repository": repository,
                    "external_id": external_id,
                    "state": state,
                    "url": url,
                    "draft": draft,
                    "report": report,
                    "owner": "scanner",
                },
            )
        )
        for issue_id in issue_ids:
            issue_node = issue_nodes.get(issue_id)
            if issue_node is not None:
                edges.append(Edge(issue_node, node_id, "addressed-by", "delivery-json"))
                link_count += 1
        for changed_file in changed_files:
            file_target = _resolve_file(changed_file, aliases)
            if file_target is not None:
                edges.append(Edge(node_id, f"file:{file_target}", "changes", "delivery-json"))
                link_count += 1
        for sha in commit_shas:
            commit_id = f"commit:{sha}"
            if commit_id in graph_nodes:
                edges.append(Edge(node_id, commit_id, "references", "delivery-json"))
                link_count += 1
        if link_count > MAX_LINKS:
            raise ValueError(f"Delivery report exceeds the {MAX_LINKS}-link limit: {report}")
    return nodes, edges


def _report_path(root: Path, vault: Path, configured: str) -> tuple[Path, str]:
    source = configured.strip().replace("\\", "/")
    pure = PurePosixPath(source)
    if not source or pure.is_absolute() or WINDOWS_ABSOLUTE.match(source) or ".." in pure.parts:
        raise ValueError(f"Configured delivery report must be project-relative: {configured}")
    private_relative = (vault.relative_to(root) / "Private").as_posix().casefold()
    normalized = pure.as_posix().removeprefix("./").casefold()
    if normalized == private_relative or normalized.startswith(f"{private_relative}/"):
        raise ValueError(
            f"Configured delivery report may not be inside atlas/Private: {configured}"
        )
    unresolved = root / Path(*pure.parts)
    if unresolved.is_symlink():
        raise ValueError(f"Configured delivery report may not be a symbolic link: {configured}")
    candidate = unresolved.resolve()
    base = root.resolve()
    private = (vault / "Private").resolve()
    if base not in candidate.parents:
        raise ValueError(f"Configured delivery report escapes project root: {configured}")
    if candidate == private or private in candidate.parents:
        raise ValueError(
            f"Configured delivery report may not be inside atlas/Private: {configured}"
        )
    if not candidate.is_file():
        raise ValueError(f"Configured delivery report does not exist: {configured}")
    try:
        size = candidate.stat().st_size
    except OSError as exc:
        raise ValueError(f"Cannot inspect delivery report {configured}: {exc}") from exc
    if size > MAX_REPORT_BYTES:
        raise ValueError(
            f"Configured delivery report exceeds the {MAX_REPORT_BYTES}-byte limit: {configured}"
        )
    return candidate, candidate.relative_to(base).as_posix()


def _read_json(path: Path, relative: str) -> dict[str, Any]:
    try:
        data = path.read_bytes()
        value = json.loads(data.decode("utf-8"), object_pairs_hook=_unique_object)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError(f"Cannot parse delivery report {relative}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"Delivery report must be a JSON object: {relative}")
    return value


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"Duplicate JSON key: {key}")
        value[key] = item
    return value


def _records(value: Any, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise ValueError(f"Delivery {label} must be a list of objects")
    return value


def _only_keys(value: dict[str, Any], allowed: set[str], label: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise ValueError(f"Unknown {label} field: {unknown[0]}")


def _text(value: Any, label: str, limit: int) -> str:
    if not isinstance(value, str):
        raise ValueError(f"Delivery {label} must be a string")
    text = value.strip()
    if not text or len(text) > limit or any(ord(character) < 32 for character in text):
        raise ValueError(f"Invalid delivery {label}")
    return text


def _external_id(value: Any, label: str) -> str:
    text = str(value) if isinstance(value, int) and not isinstance(value, bool) else value
    if not isinstance(text, str) or SAFE_ID.fullmatch(text) is None:
        raise ValueError(f"Invalid {label} ID")
    return text


def _state(value: Any, label: str) -> str:
    if not isinstance(value, str) or SAFE_STATE.fullmatch(value) is None:
        raise ValueError(f"Invalid {label} state")
    return value.casefold()


def _url(value: Any, label: str) -> str:
    if value is None or value == "":
        return ""
    text = _text(value, f"{label} URL", 2_048)
    parsed = urlsplit(text)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError(f"Invalid delivery {label} URL")
    return text


def _strings(
    value: Any,
    label: str,
    limit: int = MAX_LIST_ITEMS,
    item_limit: int = 200,
) -> list[str]:
    if not isinstance(value, list) or len(value) > limit:
        raise ValueError(f"Delivery {label} must be a bounded list")
    items = [_text(item, label, item_limit) for item in value]
    return list(dict.fromkeys(items))


def _file_aliases(files: dict[str, Path]) -> dict[str, tuple[str, ...]]:
    grouped: dict[str, list[str]] = {}
    for relative in files:
        grouped.setdefault(relative.casefold(), []).append(relative)
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


def _component(value: str) -> str:
    return quote(value, safe="")
