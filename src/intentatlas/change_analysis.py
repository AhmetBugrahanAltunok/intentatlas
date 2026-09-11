from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .change_set import ChangeFile, ChangeSet, change_file_freshness
from .config import ProjectConfig
from .graph import AtlasGraph
from .models import Node
from .scanner import FRONTMATTER_IDENTITY, scan_repository
from .symbol_spans import map_hunks_to_most_specific_symbols, valid_symbol_span
from .vault import USER_KINDS

CHANGE_ANALYSIS_SCHEMA_VERSION = 1
_STATE_RANK = {"analyzed": 0, "fallback": 1, "unknown": 2}
_GENERATED_VAULT_AREAS = {"code", "symbols", "tests", "commits", "dashboard"}
_USER_VAULT_AREAS = {
    "brain",
    "requirements",
    "decisions",
    "issues",
    "evidence",
    "reviews",
    "sessions",
}


@dataclass(frozen=True, slots=True)
class ChangeAnalysisFile:
    path: str
    status: str
    state: str
    freshness: str
    confidence: str
    artifact_ids: tuple[str, ...]
    evidence: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "status": self.status,
            "state": self.state,
            "freshness": self.freshness,
            "confidence": self.confidence,
            "artifact_ids": list(self.artifact_ids),
            "evidence": list(self.evidence),
        }


@dataclass(frozen=True, slots=True)
class ChangeAnalysis:
    change_set: ChangeSet
    state: str
    files: tuple[ChangeAnalysisFile, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": CHANGE_ANALYSIS_SCHEMA_VERSION,
            "state": self.state,
            "change_set": self.change_set.to_dict(),
            "files": [item.to_dict() for item in self.files],
        }


def analyze_change_set(
    root: Path,
    change_set: ChangeSet,
    config: ProjectConfig | None = None,
) -> ChangeAnalysis:
    """Analyze against a fresh read-only worktree graph and preserve uncertainty."""

    root = root.resolve()
    active_config = config or ProjectConfig.load(root)
    graph = scan_repository(root, active_config)
    return _analyze_change_set_with_graph(root, change_set, graph, active_config)


def _analyze_change_set_with_graph(
    root: Path,
    change_set: ChangeSet,
    graph: AtlasGraph,
    config: ProjectConfig,
) -> ChangeAnalysis:
    """Analyze a change set against an already refreshed graph."""

    files = tuple(
        _analyze_file(root, change_set, item, graph, config)
        for item in change_set.files
    )
    state = max(
        (item.state for item in files),
        key=lambda value: _STATE_RANK[value],
        default="unknown",
    )
    return ChangeAnalysis(change_set, state, files)


def render_change_analysis(analysis: ChangeAnalysis, output_format: str = "text") -> str:
    if output_format == "json":
        return json.dumps(
            analysis.to_dict(), indent=2, ensure_ascii=False, sort_keys=True
        ) + "\n"
    if output_format != "text":
        raise ValueError(f"Unknown change-analysis output format: {output_format}")
    lines = [
        f"Change analysis: {analysis.change_set.scope}",
        f"Overall state: {analysis.state}",
        f"Files: {len(analysis.files)}",
    ]
    for item in analysis.files:
        artifacts = (
            f" — artifacts {', '.join(item.artifact_ids)}" if item.artifact_ids else ""
        )
        lines.append(
            f"- {item.path}: {item.state}, freshness {item.freshness}, "
            f"confidence {item.confidence}{artifacts}"
        )
    return "\n".join(lines) + "\n"


def _analyze_file(
    root: Path,
    change_set: ChangeSet,
    item: ChangeFile,
    graph: AtlasGraph,
    config: ProjectConfig,
) -> ChangeAnalysisFile:
    freshness = change_file_freshness(root, change_set, item)
    base_evidence = ["change-set-schema-1", "fresh-worktree-scan"]
    if freshness != "aligned":
        return ChangeAnalysisFile(
            item.path,
            item.status,
            "unknown",
            freshness,
            "none",
            (),
            tuple((*base_evidence, "revision-worktree-mismatch")),
        )
    vault_classification = _vault_artifact(root, config, graph, item)
    if vault_classification is not None:
        return vault_classification
    file_node = graph.nodes.get(f"file:{item.path}")
    if item.status == "deleted":
        return ChangeAnalysisFile(
            item.path,
            item.status,
            "unknown",
            freshness,
            "none",
            (),
            tuple((*base_evidence, "artifact-unavailable")),
        )
    if file_node is None:
        candidate = root.joinpath(*Path(item.path).parts)
        try:
            available = not candidate.is_symlink() and candidate.is_file()
        except OSError:
            available = False
        if available:
            return ChangeAnalysisFile(
                item.path,
                item.status,
                "fallback",
                freshness,
                "low",
                (),
                tuple((*base_evidence, "unscanned-file-fallback")),
            )
        return ChangeAnalysisFile(
            item.path,
            item.status,
            "unknown",
            freshness,
            "none",
            (),
            tuple((*base_evidence, "artifact-unavailable")),
        )
    symbol_ids, complete = _exact_symbols(graph, file_node, item)
    if complete and symbol_ids:
        return ChangeAnalysisFile(
            item.path,
            item.status,
            "analyzed",
            freshness,
            "high",
            symbol_ids,
            tuple((*base_evidence, "git-zero-context-hunk", "validated-symbol-span")),
        )
    evidence = [*base_evidence, "file-level-fallback"]
    if item.status == "untracked":
        evidence.append("untracked-content-not-read")
    elif not item.hunks:
        evidence.append("no-current-side-hunks")
    else:
        evidence.append("incomplete-symbol-span-coverage")
    return ChangeAnalysisFile(
        item.path,
        item.status,
        "fallback",
        freshness,
        "low",
        (file_node.id,),
        tuple(evidence),
    )


def _exact_symbols(
    graph: AtlasGraph, file_node: Node, item: ChangeFile
) -> tuple[tuple[str, ...], bool]:
    symbols = tuple(
        graph.nodes[edge.target]
        for edge in graph.index.outgoing(file_node.id, "defines")
        if edge.target in graph.nodes and valid_symbol_span(graph.nodes[edge.target])
    )
    match = map_hunks_to_most_specific_symbols(
        item.hunks,
        {hunk.path: symbols for hunk in item.hunks},
    )
    return match.symbol_ids, match.complete


def _vault_artifact(
    root: Path,
    config: ProjectConfig,
    graph: AtlasGraph,
    item: ChangeFile,
) -> ChangeAnalysisFile | None:
    try:
        vault_relative = config.vault_path(root).relative_to(root).as_posix()
    except ValueError:
        return None
    prefix = f"{vault_relative}/"
    if not item.path.startswith(prefix):
        return None
    relative = item.path[len(prefix) :]
    area = relative.split("/", 1)[0]
    normalized_area = area.casefold()
    base_evidence = ("change-set-schema-1", "fresh-worktree-scan")
    if normalized_area == "private":
        return ChangeAnalysisFile(
            item.path,
            item.status,
            "unknown",
            "unknown",
            "none",
            (),
            (*base_evidence, "private-boundary-excluded"),
        )
    if normalized_area in _GENERATED_VAULT_AREAS:
        return ChangeAnalysisFile(
            item.path,
            item.status,
            "analyzed",
            "aligned",
            "high",
            (),
            (*base_evidence, "generated-vault-output", "excluded-derived-artifact"),
        )
    if normalized_area in _USER_VAULT_AREAS and item.status == "deleted":
        return ChangeAnalysisFile(
            item.path,
            item.status,
            "unknown",
            "aligned",
            "none",
            (),
            (*base_evidence, "deleted-durable-intent-artifact"),
        )
    durable_nodes = tuple(
        sorted(
            (
                node
                for node in graph.nodes.values()
                if node.kind in USER_KINDS and node.path == relative
            ),
            key=lambda node: node.id,
        )
    )
    if durable_nodes:
        # A note without frontmatter still receives a stable path-derived identity. Only
        # claim a declared identity when the scanner recorded one, and abstain from the
        # stronger claim when an older graph carries no provenance at all.
        declared = all(
            node.metadata.get("identity") == FRONTMATTER_IDENTITY for node in durable_nodes
        )
        identity_evidence = "vault-frontmatter-id" if declared else "vault-path-identity"
        return ChangeAnalysisFile(
            item.path,
            item.status,
            "analyzed",
            "aligned",
            "high",
            tuple(node.id for node in durable_nodes),
            (*base_evidence, identity_evidence, "durable-intent-artifact"),
        )
    return ChangeAnalysisFile(
        item.path,
        item.status,
        "fallback",
        "aligned",
        "low",
        (),
        (*base_evidence, "vault-file-fallback"),
    )
