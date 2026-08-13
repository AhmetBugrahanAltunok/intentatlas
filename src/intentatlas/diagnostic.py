from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess  # nosec B404
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from .adapters import BUILTIN_ADAPTERS
from .config import CONFIG_NAME, ProjectConfig
from .graph import AtlasGraph
from .scanner import MAX_PARSE_BYTES

DIAGNOSTIC_SCHEMA_VERSION = 1
MAX_DIAGNOSTIC_FILES = 20_000
MAX_GIT_STATUS_BYTES = 1_000_000
_PROJECT_MARKERS = frozenset({"go.mod", "package.json", "pnpm-workspace.yaml", "pyproject.toml"})
_SOURCE_ROOT_NAMES = frozenset({"app", "apps", "cmd", "internal", "lib", "packages", "pkg", "src"})
_LANGUAGE_NAMES = {
    ".c": "c",
    ".cc": "cpp",
    ".cpp": "cpp",
    ".cs": "csharp",
    ".go": "go",
    ".h": "c-cpp-header",
    ".hpp": "cpp-header",
    ".java": "java",
    ".js": "javascript",
    ".jsx": "javascript",
    ".php": "php",
    ".py": "python",
    ".rb": "ruby",
    ".rs": "rust",
    ".swift": "swift",
    ".ts": "typescript",
    ".tsx": "typescript",
}
_ADVISORY = (
    "This diagnostic reports bounded local readiness, not proof of complete analysis. "
    "Run the shown preview command before persistent initialization; absence is not proof "
    "of no impact."
)


@dataclass(frozen=True, slots=True)
class DiagnosticCapability:
    adapter: str
    support_level: str
    suffixes: tuple[str, ...]
    detected_file_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RepositoryDiagnostic:
    project_root: str
    config_state: str
    config_detail: str
    git_state: str
    head_revision: str | None
    discovered_file_count: int
    discovery_truncated: bool
    oversized_supported_file_count: int
    capabilities: tuple[DiagnosticCapability, ...]
    unsupported_languages: tuple[str, ...]
    project_roots: tuple[str, ...]
    source_roots: tuple[str, ...]
    ambiguity_state: str
    ambiguity_reasons: tuple[str, ...]
    evidence_state: str
    configured_evidence_source_count: int
    graph_state: str
    report_state: str
    recommended_scope: str
    scope_detail: str
    symbol_test_state: str
    python_test_count: int
    exact_symbol_test_link_count: int
    symbol_test_detail: str
    next_safe_command: str

    @property
    def ambiguity_detail(self) -> str:
        return (
            "Detected roots are bounded readiness heuristics, not proof that symbol resolution "
            "abstained; the scanner independently requires unique declared workspace ownership, "
            "module identity, and symbol identity. No action is required for this heuristic "
            "alone. If an actual result reports ambiguous ownership, exclude unrelated nested "
            "fixtures/projects in intentatlas.json or correct the relevant project manifests, "
            "then run scan again."
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": DIAGNOSTIC_SCHEMA_VERSION,
            "advisory": _ADVISORY,
            "read_only": True,
            "network_required": False,
            "project_root": self.project_root,
            "config": {
                "state": self.config_state,
                "detail": self.config_detail,
            },
            "repository": {
                "git_state": self.git_state,
                "head_revision": self.head_revision,
                "discovered_file_count": self.discovered_file_count,
                "discovery_truncated": self.discovery_truncated,
                "oversized_supported_file_count": self.oversized_supported_file_count,
            },
            "capabilities": [item.to_dict() for item in self.capabilities],
            "unsupported_languages": list(self.unsupported_languages),
            "project_roots": list(self.project_roots),
            "source_roots": list(self.source_roots),
            "ambiguity": {
                "state": self.ambiguity_state,
                "reasons": list(self.ambiguity_reasons),
                "detail": self.ambiguity_detail,
            },
            "evidence": {
                "state": self.evidence_state,
                "configured_source_count": self.configured_evidence_source_count,
                "freshness": "not-assessed",
                "detail": (
                    "Freshness is established by a revision-scoped preview; configured files "
                    "are not treated as aligned by this diagnostic."
                ),
            },
            "artifacts": {
                "graph_state": self.graph_state,
                "change_report_state": self.report_state,
            },
            "recommended_change_scope": {
                "scope": self.recommended_scope,
                "detail": self.scope_detail,
            },
            "symbol_test_links": {
                "state": self.symbol_test_state,
                "python_test_count": self.python_test_count,
                "exact_link_count": self.exact_symbol_test_link_count,
                "freshness": "not-assessed",
                "detail": self.symbol_test_detail,
            },
            "next_safe_command": self.next_safe_command,
        }


@dataclass(frozen=True, slots=True)
class _DiscoveredMetadata:
    relative: str
    suffix: str
    size: int


def diagnose_repository(root: Path) -> RepositoryDiagnostic:
    """Inspect bounded repository readiness without creating or modifying project state."""

    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"Project path is not a directory: {root}")

    config_path = root / CONFIG_NAME
    config_state = "missing"
    config_detail = "No configuration exists; safe defaults are used in memory only."
    config = ProjectConfig()
    if config_path.is_symlink():
        config_state = "invalid"
        config_detail = "Configuration is a symbolic link and was not read."
    elif config_path.exists():
        try:
            config = ProjectConfig.load(root)
            config.vault_path(root)
            config.graph_path(root)
        except ValueError as exc:
            config_state = "invalid"
            config_detail = str(exc).replace(str(root), ".")
            config = ProjectConfig()
        else:
            config_state = "ready"
            config_detail = "Configuration schema 1 is valid."

    discovered, truncated = _discover_metadata(root, config)
    capabilities = _capabilities(discovered)
    unsupported_languages = _unsupported_languages(discovered, capabilities)
    project_roots = _project_roots(discovered)
    source_roots = _source_roots(discovered, capabilities)
    ambiguity_reasons: list[str] = []
    if len(project_roots) > 1:
        ambiguity_reasons.append("multiple-project-roots")
    if len(source_roots) > 1:
        ambiguity_reasons.append("multiple-source-roots")
    if truncated:
        ambiguity_reasons.append("discovery-limit-reached")

    git_state, head_revision = _git_readiness(root)
    graph_state = _graph_state(root, config, config_state)
    (
        symbol_test_state,
        python_test_count,
        exact_symbol_test_link_count,
        symbol_test_detail,
    ) = _symbol_test_health(root, config, graph_state)
    configured_evidence_count = sum(
        len(values)
        for values in (
            config.coverage_reports,
            config.test_reports,
            config.scip_reports,
            config.sarif_reports,
            config.test_execution_reports,
        )
    )
    evidence_state = "not-configured" if configured_evidence_count == 0 else "configured-unverified"
    if git_state in {"ready", "empty"}:
        recommended_scope, scope_detail = _recommended_change_scope(
            root,
            config,
            head_revision,
        )
        selector = {
            "commit": "--commit HEAD",
            "staged": "--staged",
            "worktree": "--worktree",
        }[recommended_scope]
        next_command = f"intentatlas changes {_command_path(root)} {selector} --report"
        report_state = (
            "worktree-available-unassessed"
            if git_state == "empty"
            else "available-unassessed"
        )
    else:
        recommended_scope = "unavailable"
        scope_detail = "A local Git change scope is unavailable for this path."
        next_command = "intentatlas demo --report text"
        report_state = "unavailable"

    return RepositoryDiagnostic(
        project_root=str(root),
        config_state=config_state,
        config_detail=config_detail,
        git_state=git_state,
        head_revision=head_revision,
        discovered_file_count=len(discovered),
        discovery_truncated=truncated,
        oversized_supported_file_count=sum(
            item.size > MAX_PARSE_BYTES
            for item in discovered
            if any(item.suffix in capability.suffixes for capability in capabilities)
        ),
        capabilities=capabilities,
        unsupported_languages=unsupported_languages,
        project_roots=project_roots,
        source_roots=source_roots,
        ambiguity_state="detected" if ambiguity_reasons else "none",
        ambiguity_reasons=tuple(ambiguity_reasons),
        evidence_state=evidence_state,
        configured_evidence_source_count=configured_evidence_count,
        graph_state=graph_state,
        report_state=report_state,
        recommended_scope=recommended_scope,
        scope_detail=scope_detail,
        symbol_test_state=symbol_test_state,
        python_test_count=python_test_count,
        exact_symbol_test_link_count=exact_symbol_test_link_count,
        symbol_test_detail=symbol_test_detail,
        next_safe_command=next_command,
    )


def render_diagnostic(result: RepositoryDiagnostic, output_format: str = "text") -> str:
    if output_format == "json":
        return json.dumps(result.to_dict(), indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if output_format != "text":
        raise ValueError(f"Unknown diagnostic output format: {output_format}")
    head = result.head_revision or "n/a"
    lines = [
        "IntentAtlas read-only diagnostic",
        "Read only: yes; network required: no",
        f"Project: {result.project_root}",
        f"Configuration: {result.config_state} - {result.config_detail}",
        f"Git: {result.git_state}; HEAD {head}",
        (
            f"Discovery: {result.discovered_file_count} files; "
            f"truncated {'yes' if result.discovery_truncated else 'no'}; "
            f"oversized supported files {result.oversized_supported_file_count}"
        ),
        "Capabilities:",
    ]
    for capability in result.capabilities:
        lines.append(
            f"- {capability.adapter}: {capability.support_level}; "
            f"{capability.detected_file_count} detected; "
            f"suffixes {', '.join(capability.suffixes)}"
        )
    unsupported = ", ".join(result.unsupported_languages) or "none detected"
    lines.extend(
        [
            f"Unsupported languages: {unsupported}",
            f"Project roots: {', '.join(result.project_roots) or 'none detected'}",
            f"Source roots: {', '.join(result.source_roots) or 'none detected'}",
            (
                f"Ambiguity: {result.ambiguity_state}"
                + (
                    f" ({', '.join(result.ambiguity_reasons)})"
                    if result.ambiguity_reasons
                    else ""
                )
            ),
            f"Ambiguity guidance: {result.ambiguity_detail}",
            (
                f"Evidence: {result.evidence_state}; freshness not-assessed; "
                f"configured sources {result.configured_evidence_source_count}"
            ),
            f"Artifacts: graph {result.graph_state}; change report {result.report_state}",
            f"Recommended change scope: {result.recommended_scope} - {result.scope_detail}",
            (
                f"Exact Python symbol-test links: {result.symbol_test_state}; "
                f"tests {result.python_test_count}; links "
                f"{result.exact_symbol_test_link_count}"
            ),
            f"Symbol-test guidance: {result.symbol_test_detail}",
            f"Next safe command: {result.next_safe_command}",
            f"Advisory: {_ADVISORY}",
        ]
    )
    return "\n".join(lines) + "\n"


def _command_path(root: Path) -> str:
    value = str(root)
    if os.name == "nt":
        return subprocess.list2cmdline([value])
    return shlex.quote(value)


def _discover_metadata(
    root: Path, config: ProjectConfig
) -> tuple[tuple[_DiscoveredMetadata, ...], bool]:
    exclude_patterns = tuple(
        tuple(part.casefold() for part in PurePosixPath(item).parts)
        for item in config.exclude
    )
    try:
        vault_parts = tuple(
            part.casefold()
            for part in config.vault_path(root).relative_to(root).parts
        )
    except ValueError:
        vault_parts = ("atlas",)
    found: list[_DiscoveredMetadata] = []
    truncated = False
    for current, directories, filenames in os.walk(
        root, topdown=True, onerror=lambda _error: None, followlinks=False
    ):
        current_path = Path(current)
        current_relative = current_path.relative_to(root)
        kept: list[str] = []
        for name in sorted(directories, key=str.casefold):
            relative = current_relative / name
            candidate = current_path / name
            if _excluded(relative, exclude_patterns, vault_parts) or _directory_link(candidate):
                continue
            kept.append(name)
        directories[:] = kept
        for name in sorted(filenames, key=str.casefold):
            relative = current_relative / name
            if _excluded(relative, exclude_patterns, vault_parts):
                continue
            candidate = current_path / name
            try:
                if candidate.is_symlink() or not candidate.is_file():
                    continue
                size = candidate.stat().st_size
            except OSError:
                continue
            found.append(
                _DiscoveredMetadata(relative.as_posix(), candidate.suffix.casefold(), size)
            )
            if len(found) >= MAX_DIAGNOSTIC_FILES:
                truncated = True
                directories[:] = []
                break
        if truncated:
            break
    return tuple(found), truncated


def _excluded(
    relative: Path,
    exclude_patterns: tuple[tuple[str, ...], ...],
    vault_parts: tuple[str, ...],
) -> bool:
    parts = tuple(part.casefold() for part in relative.parts)
    if parts[:2] == ("atlas", "private"):
        return True
    if vault_parts and parts[: len(vault_parts)] == vault_parts:
        return True
    for pattern in exclude_patterns:
        if len(pattern) == 1 and pattern[0] in parts:
            return True
        if len(pattern) > 1 and parts[: len(pattern)] == pattern:
            return True
    return False


def _directory_link(path: Path) -> bool:
    try:
        return path.is_symlink() or (path.is_dir() and path.resolve() != path.absolute())
    except OSError:
        return True


def _capabilities(
    discovered: tuple[_DiscoveredMetadata, ...],
) -> tuple[DiagnosticCapability, ...]:
    return tuple(
        DiagnosticCapability(
            adapter=adapter.name,
            support_level="experimental",
            suffixes=tuple(sorted(adapter.suffixes)),
            detected_file_count=sum(item.suffix in adapter.suffixes for item in discovered),
        )
        for adapter in sorted(BUILTIN_ADAPTERS, key=lambda item: item.name)
    )


def _unsupported_languages(
    discovered: tuple[_DiscoveredMetadata, ...],
    capabilities: tuple[DiagnosticCapability, ...],
) -> tuple[str, ...]:
    supported = {suffix for capability in capabilities for suffix in capability.suffixes}
    return tuple(
        sorted(
            {
                language
                for item in discovered
                if item.suffix not in supported
                for language in [_LANGUAGE_NAMES.get(item.suffix)]
                if language is not None
            }
        )
    )


def _project_roots(discovered: tuple[_DiscoveredMetadata, ...]) -> tuple[str, ...]:
    roots = {
        str(PurePosixPath(item.relative).parent)
        for item in discovered
        if PurePosixPath(item.relative).name in _PROJECT_MARKERS
    }
    return tuple(sorted("." if root == "." else root for root in roots))


def _source_roots(
    discovered: tuple[_DiscoveredMetadata, ...],
    capabilities: tuple[DiagnosticCapability, ...],
) -> tuple[str, ...]:
    supported = {suffix for capability in capabilities for suffix in capability.suffixes}
    roots: set[str] = set()
    for item in discovered:
        if item.suffix not in supported:
            continue
        parts = PurePosixPath(item.relative).parts
        if not parts:
            continue
        if len(parts) >= 2 and parts[0].casefold() in _SOURCE_ROOT_NAMES:
            if parts[0].casefold() in {"apps", "packages"} and len(parts) >= 3:
                roots.add("/".join(parts[:2]))
            else:
                roots.add(parts[0])
        else:
            roots.add(".")
    return tuple(sorted(roots))


def _git_readiness(root: Path) -> tuple[str, str | None]:
    dot_git = root / ".git"
    if dot_git.is_symlink():
        return "unsafe", None
    if not dot_git.exists():
        return "not-a-repository", None
    executable = shutil.which("git")
    if executable is None:
        return "unavailable", None
    inside = _git_value(root, executable, "rev-parse", "--is-inside-work-tree")
    if inside != "true":
        return "not-a-repository", None
    top_level = _git_value(root, executable, "rev-parse", "--show-toplevel")
    if top_level is None or Path(top_level).resolve() != root:
        return "not-a-repository", None
    head = _git_value(root, executable, "rev-parse", "--verify", "HEAD")
    if head is None:
        return "empty", None
    return "ready", head


def _git_value(root: Path, executable: str, *arguments: str) -> str | None:
    completed = subprocess.run(  # noqa: S603  # nosec B603
        [executable, *arguments],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=10,
    )
    if completed.returncode != 0:
        return None
    value = completed.stdout.strip()
    return value if value else None


def _recommended_change_scope(
    root: Path,
    config: ProjectConfig,
    head_revision: str | None,
) -> tuple[str, str]:
    executable = shutil.which("git")
    if executable is None:
        return "worktree", "Git is unavailable; worktree is the conservative fallback."
    pathspecs = _diagnostic_pathspecs(config)
    try:
        conflict = _git_changed(
            root,
            executable,
            "diff",
            "--quiet",
            "--diff-filter=U",
            "--no-ext-diff",
            "--ignore-submodules=all",
            "--",
            *pathspecs,
        )
        unstaged = _git_changed(
            root,
            executable,
            "diff",
            "--quiet",
            "--no-ext-diff",
            "--ignore-submodules=all",
            "--",
            *pathspecs,
        )
        untracked = bool(
            _git_status_output(
                root,
                executable,
                "ls-files",
                "--others",
                "--exclude-standard",
                "-z",
                "--",
                *pathspecs,
            )
        )
        staged = _git_changed(
            root,
            executable,
            "diff",
            "--cached",
            "--quiet",
            "--no-ext-diff",
            "--ignore-submodules=all",
            "--",
            *pathspecs,
        )
    except ValueError:
        return (
            "worktree",
            "Git change state could not be fully inspected; worktree is the conservative "
            "fallback.",
        )
    if conflict or unstaged or untracked:
        return (
            "worktree",
            "Uncommitted, untracked, or conflicted changes exist; analyze the current working "
            "copy.",
        )
    if staged:
        return "staged", "Only staged changes exist; analyze the index."
    if head_revision is not None:
        return "commit", "The working copy is clean; analyze exact HEAD."
    return "worktree", "The repository has no commit yet; analyze the current working copy."


def _diagnostic_pathspecs(config: ProjectConfig) -> tuple[str, ...]:
    excluded = {
        value.strip().replace("\\", "/").strip("/")
        for value in (*config.exclude, config.vault, "atlas/Private")
        if value.strip().replace("\\", "/").strip("/")
    }
    return (".", *(f":(exclude,literal){value}" for value in sorted(excluded)))


def _git_changed(root: Path, executable: str, *arguments: str) -> bool:
    completed = subprocess.run(  # noqa: S603  # nosec B603
        [executable, *arguments],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=10,
    )
    if completed.returncode not in {0, 1}:
        raise ValueError("Cannot inspect Git change state")
    return completed.returncode == 1


def _git_status_output(root: Path, executable: str, *arguments: str) -> str:
    completed = subprocess.run(  # noqa: S603  # nosec B603
        [executable, *arguments],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=10,
    )
    if completed.returncode != 0:
        raise ValueError("Cannot inspect Git change state")
    if len(completed.stdout.encode("utf-8")) > MAX_GIT_STATUS_BYTES:
        raise ValueError("Git change metadata exceeds the diagnostic limit")
    return completed.stdout


def _graph_state(root: Path, config: ProjectConfig, config_state: str) -> str:
    if config_state == "invalid":
        return "unavailable-invalid-config"
    unresolved = root / config.graph
    if unresolved.is_symlink():
        return "unsafe-link"
    try:
        graph_path = config.graph_path(root)
    except ValueError:
        return "unsafe-path"
    try:
        if graph_path.is_file():
            return "available"
        if graph_path.exists():
            return "unavailable-non-file"
    except OSError:
        return "unavailable"
    return "missing"


def _symbol_test_health(
    root: Path,
    config: ProjectConfig,
    graph_state: str,
) -> tuple[str, int, int, str]:
    if graph_state != "available":
        return (
            "not-assessed",
            0,
            0,
            "Run `intentatlas scan PATH`, then repeat diagnose to inspect the saved graph. "
            "Readiness alone does not prove that exact symbol-test links were formed.",
        )
    try:
        graph = AtlasGraph.load(config.graph_path(root))
    except (OSError, ValueError):
        return (
            "unavailable",
            0,
            0,
            "The saved graph could not be validated. Run `intentatlas scan PATH`, then repeat "
            "diagnose.",
        )
    python_tests = {
        node.id
        for node in graph.nodes.values()
        if node.kind == "test" and node.metadata.get("language") == "Python"
    }
    exact_links = {
        (edge.source, edge.target)
        for edge in graph.edges
        if edge.source in python_tests
        and edge.relation == "tests"
        and edge.evidence == "python-symbol-reference"
        and graph.nodes.get(edge.target) is not None
        and graph.nodes[edge.target].kind == "symbol"
    }
    if not python_tests:
        return (
            "not-applicable",
            0,
            0,
            "The saved graph contains no detected Python test files. Graph freshness is not "
            "assessed by diagnose.",
        )
    if exact_links:
        return (
            "ready",
            len(python_tests),
            len(exact_links),
            "The saved graph contains at least one exact Python symbol-test link. This does not "
            "prove that every test was linked, and graph freshness is not assessed.",
        )
    return (
        "missing-exact-links",
        len(python_tests),
        0,
        "Python tests were detected, but the saved graph has no exact symbol-test links. Check "
        "the tests' local import paths and project/source-root metadata, then scan again.",
    )
