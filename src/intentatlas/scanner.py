from __future__ import annotations

import hashlib
import os
import re
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import Protocol

from .adapters import (
    BUILTIN_ADAPTERS,
    AdapterContext,
    GraphFragment,
    LanguageAdapter,
    validate_adapter_definition,
    validate_adapter_fragment,
)
from .config import ProjectConfig
from .delivery import import_delivery
from .evidence import import_evidence
from .git_history import DiffHunk, collect_git_history, resolve_git_head
from .graph import AtlasGraph
from .models import Edge, Node
from .naming import note_title, safe_filename
from .relations import USER_RELATIONS
from .scan_cache import AdapterFragmentCache
from .symbol_spans import map_hunks_to_most_specific_symbols, symbol_spans_by_path
from .test_eligibility import classify_python_test, load_python_test_policy
from .vault import ProjectVault
from .workspace import WorkspaceModel, discover_workspace, owner_id

SUPPORTED_SUFFIXES = {
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".go",
    ".h",
    ".hpp",
    ".java",
    ".js",
    ".jsx",
    ".md",
    ".mod",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".rst",
    ".swift",
    ".toml",
    ".ts",
    ".tsx",
    ".yaml",
    ".yml",
}
CONFIG_SUFFIXES = {".mod", ".toml", ".yaml", ".yml"}
DOCUMENT_SUFFIXES = {".md", ".rst"}
WORKSPACE_METADATA_NAMES = {"go.work", "jsconfig.json", "package.json", "tsconfig.json"}
MAX_PARSE_BYTES = 1_000_000
MAX_REPOSITORY_FILES = 250_000
MAX_REPOSITORY_BYTES = 8 * 1024 * 1024 * 1024
MAX_GRAPH_NODES = 1_000_000
MAX_GRAPH_EDGES = 4_000_000
USER_VAULT_AREAS = {
    "Brain": "memory",
    "Requirements": "requirement",
    "Decisions": "decision",
    "Issues": "issue",
    "Evidence": "evidence",
    "Reviews": "review",
    "Sessions": "session",
}
WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
TYPED_RELATION_PREFIX = re.compile(r"\s*(?:[-*+]\s+)?([a-z][a-z0-9-]*)::\s*")
FRONTMATTER_ID_LINE = re.compile(r"^id:\s*(.+?)\s*$")
UNSAFE_USER_ID = re.compile(r"[\x00-\x20\x7f\[\]|]")
RESERVED_USER_ID_PREFIXES = ("commit:", "file:", "symbol:")
FRONTMATTER_IDENTITY = "frontmatter"
PATH_IDENTITY = "path"
PRIVATE_PARTS = ("atlas", "private")


@dataclass(slots=True)
class PendingLink:
    source: str
    target: str
    relation: str
    evidence: str


class _HashWriter(Protocol):
    def update(self, value: bytes, /) -> None: ...


@dataclass(frozen=True, slots=True)
class ScanStatistics:
    reused_adapters: tuple[str, ...] = ()
    rebuilt_adapters: tuple[str, ...] = ()
    skipped_cache_writes: tuple[str, ...] = ()
    workspace_partitions: tuple[str, ...] = ()
    workspace_diagnostics: tuple[str, ...] = ()
    reused_partitions: tuple[str, ...] = ()
    rebuilt_partitions: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class IncrementalScanResult:
    graph: AtlasGraph
    statistics: ScanStatistics


def scan_repository(root: Path, config: ProjectConfig | None = None) -> AtlasGraph:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"Project path is not a directory: {root}")
    config = config or ProjectConfig.load(root)
    scanner = RepositoryScanner(root, config)
    return scanner.scan()


def scan_repository_incremental(
    root: Path, config: ProjectConfig | None = None
) -> IncrementalScanResult:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"Project path is not a directory: {root}")
    config = config or ProjectConfig.load(root)
    scanner = RepositoryScanner(root, config)
    return scanner.scan_incremental()


class RepositoryScanner:
    def __init__(self, root: Path, config: ProjectConfig):
        self.root = root.resolve()
        self.config = config
        self.graph = AtlasGraph()
        self.files: dict[str, Path] = {}
        self.pending_links: list[PendingLink] = []
        self.reused_adapters: list[str] = []
        self.rebuilt_adapters: list[str] = []
        self.skipped_cache_writes: list[str] = []
        self.workspace: WorkspaceModel | None = None
        self.discovered_bytes = 0
        self.reused_partitions: list[str] = []
        self.rebuilt_partitions: list[str] = []
        self.exclude_patterns = _exclude_patterns(config.exclude)
        self.vault_relative = config.vault_path(self.root).relative_to(self.root).as_posix()
        self.vault_parts = tuple(
            part.casefold() for part in PurePosixPath(self.vault_relative).parts
        )
        self.python_test_policy = load_python_test_policy(self.root)

    def scan(self) -> AtlasGraph:
        return self._scan(cache=None)

    def scan_incremental(self) -> IncrementalScanResult:
        graph = self._scan(cache=AdapterFragmentCache(self.root))
        return IncrementalScanResult(
            graph=graph,
            statistics=ScanStatistics(
                reused_adapters=tuple(self.reused_adapters),
                rebuilt_adapters=tuple(self.rebuilt_adapters),
                skipped_cache_writes=tuple(self.skipped_cache_writes),
                workspace_partitions=tuple(
                    item.id for item in self.workspace.boundaries
                    if item.kind in {"project", "package"}
                ) if self.workspace is not None else (),
                workspace_diagnostics=tuple(
                    item.code for item in self.workspace.diagnostics
                ) if self.workspace is not None else (),
                reused_partitions=tuple(self.reused_partitions),
                rebuilt_partitions=tuple(self.rebuilt_partitions),
            ),
        )

    def _scan(self, cache: AdapterFragmentCache | None) -> AtlasGraph:
        self._discover_files()
        self._check_graph_budget()
        self._scan_workspace()
        self._check_graph_budget()
        self._scan_language_adapters(cache)
        self._check_graph_budget()
        self._scan_evidence_reports()
        self._check_graph_budget()
        self._scan_git_history()
        self._check_graph_budget()
        self._scan_user_vault()
        self._scan_delivery_reports()
        self._resolve_pending_links()
        self._check_graph_budget()
        return self.graph

    def _discover_files(self) -> None:
        for path in self._walk_files():
            relative_path = path.relative_to(self.root)
            if (
                path.suffix.casefold() not in SUPPORTED_SUFFIXES
                and path.name.casefold() not in WORKSPACE_METADATA_NAMES
            ):
                continue
            relative = relative_path.as_posix()
            kind = _file_kind(relative_path)
            try:
                size = path.stat().st_size
            except OSError:
                continue
            if len(self.files) + 1 > MAX_REPOSITORY_FILES:
                raise ValueError(
                    f"Repository exceeds the {MAX_REPOSITORY_FILES}-file scan budget"
                )
            self.discovered_bytes += size
            if self.discovered_bytes > MAX_REPOSITORY_BYTES:
                raise ValueError(
                    f"Repository exceeds the {MAX_REPOSITORY_BYTES}-byte scan budget"
                )
            node_id = f"file:{relative}"
            self.files[relative] = path
            metadata: dict[str, object] = {
                "language": _language(path.suffix.casefold()),
                "size_bytes": size,
                "owner": "scanner",
            }
            if kind == "test" and path.suffix.casefold() == ".py":
                metadata.update(
                    classify_python_test(relative_path, self.python_test_policy).metadata()
                )
            self.graph.add_node(
                Node(
                    id=node_id,
                    kind=kind,
                    label=relative,
                    path=relative,
                    metadata=metadata,
                )
            )

    def _scan_workspace(self) -> None:
        self.workspace = discover_workspace(self.root, self.files)
        nodes, edges = self.workspace.graph_fragment(self.files)
        for relative in sorted(self.files):
            node = self.graph.nodes[f"file:{relative}"]
            candidates = self.workspace.candidates(relative)
            owners = self.workspace.owners(relative)
            self.graph.add_node(
                Node(
                    node.id,
                    node.kind,
                    node.label,
                    node.path,
                    {
                        **node.metadata,
                        "workspace_schema_version": self.workspace.schema_version,
                        "workspace_candidates": list(candidates),
                        "workspace_owners": list(owners),
                        "workspace_state": "aligned" if len(owners) == 1 else "ambiguous",
                    },
                )
            )
        self.graph.extend(nodes, edges)

    def _walk_files(self) -> Iterable[Path]:
        """Yield files without descending into excluded or linked directories."""

        for current, directories, filenames in os.walk(
            self.root,
            topdown=True,
            onerror=lambda _error: None,
            followlinks=False,
        ):
            current_path = Path(current)
            current_relative = current_path.relative_to(self.root)
            allowed_directories: list[str] = []
            for name in sorted(directories, key=str.casefold):
                relative = current_relative / name
                if self._is_excluded(relative):
                    continue
                candidate = current_path / name
                if _is_directory_link(candidate):
                    continue
                allowed_directories.append(name)
            directories[:] = allowed_directories

            for name in sorted(filenames, key=str.casefold):
                relative = current_relative / name
                if self._is_excluded(relative):
                    continue
                candidate = current_path / name
                try:
                    if candidate.is_symlink() or not candidate.is_file():
                        continue
                except OSError:
                    continue
                yield candidate

    def _is_excluded(self, relative: Path) -> bool:
        parts = tuple(part.casefold() for part in relative.parts)
        if parts[: len(PRIVATE_PARTS)] == PRIVATE_PARTS:
            return True
        if self.vault_parts and parts[: len(self.vault_parts)] == self.vault_parts:
            return True
        for pattern in self.exclude_patterns:
            if len(pattern) == 1 and pattern[0] in parts:
                return True
            if len(pattern) > 1 and parts[: len(pattern)] == pattern:
                return True
        return False

    def _scan_language_adapters(self, cache: AdapterFragmentCache | None) -> None:
        kinds = {
            relative: self.graph.nodes[f"file:{relative}"].kind for relative in self.files
        }
        context = AdapterContext(
            files=MappingProxyType(dict(self.files)),
            kinds=MappingProxyType(kinds),
            max_parse_bytes=MAX_PARSE_BYTES,
            workspace_owners=self.workspace.aligned_owners if self.workspace is not None else {},
            source_roots=MappingProxyType(_workspace_source_roots(self.workspace)),
            module_aliases=tuple(
                (item.owner, item.pattern, item.targets)
                for item in self.workspace.aliases
            ) if self.workspace is not None else (),
            workspace_dependencies=frozenset(
                self.workspace.dependencies if self.workspace is not None else ()
            ),
        )
        for adapter in sorted(BUILTIN_ADAPTERS, key=lambda item: item.name):
            validate_adapter_definition(adapter)
            adapter_rebuilt = False
            adapter_reused = True
            for partition, partition_context in _adapter_partitions(adapter, context):
                cache_miss = False
                fingerprint = _adapter_fingerprint(adapter, partition_context)
                if cache is None:
                    fragment = adapter.scan(partition_context)
                else:
                    cached = cache.load(
                        adapter,
                        fingerprint,
                        frozenset(self.graph.nodes),
                        partition,
                    )
                    if cached.fragment is None:
                        fragment = adapter.scan(partition_context)
                        cache_miss = True
                        adapter_rebuilt = True
                        adapter_reused = False
                        self.rebuilt_partitions.append(f"{adapter.name}:{partition}")
                    else:
                        fragment = cached.fragment
                        self.reused_partitions.append(f"{adapter.name}:{partition}")

                    if _adapter_fingerprint(adapter, partition_context) != fingerprint:
                        raise ValueError(
                            f"{adapter.name} inputs changed during scan; "
                            "retry with a stable worktree"
                        )
                fragment = self._scope_adapter_fragment(fragment)
                validate_adapter_fragment(adapter, fragment, frozenset(self.graph.nodes))
                if (
                    cache is not None
                    and cache_miss
                    and not cache.store(adapter, fingerprint, fragment, partition)
                ):
                    self.skipped_cache_writes.append(adapter.name)
                for node in sorted(fragment.nodes, key=lambda item: item.id):
                    self.graph.add_node(node)
                for edge in sorted(
                    fragment.edges,
                    key=lambda item: (
                        item.source,
                        item.target,
                        item.relation,
                        item.evidence,
                    ),
                ):
                    if not self.graph.add_edge(edge):
                        raise ValueError(
                            f"Adapter {adapter.name!r} emitted invalid edge: "
                            f"{edge.source} -> {edge.target}"
                        )
            if cache is not None and adapter_rebuilt:
                self.rebuilt_adapters.append(adapter.name)
            elif cache is not None and adapter_reused:
                self.reused_adapters.append(adapter.name)

    def _scope_adapter_fragment(self, fragment: GraphFragment) -> GraphFragment:
        if self.workspace is None:
            return fragment
        nodes = []
        node_paths: dict[str, str] = {}
        for node in fragment.nodes:
            if node.path is None:
                nodes.append(node)
                continue
            node_paths[node.id] = node.path
            owners = self.workspace.owners(node.path)
            nodes.append(
                Node(
                    node.id,
                    node.kind,
                    node.label,
                    node.path,
                    {
                        **node.metadata,
                        "workspace_candidates": list(self.workspace.candidates(node.path)),
                        "workspace_owners": list(owners),
                        "workspace_state": "aligned" if len(owners) == 1 else "ambiguous",
                    },
                )
            )
        edges = []
        for edge in fragment.edges:
            source = _endpoint_path(edge.source, node_paths, self.graph)
            target = _endpoint_path(edge.target, node_paths, self.graph)
            if source is None or target is None or self.workspace.allows(source, target):
                edges.append(edge)
        return GraphFragment(nodes=tuple(nodes), edges=tuple(edges))

    def _scan_git_history(self) -> None:
        symbols_by_path = _symbols_by_path(self.graph.nodes.values())
        for commit in collect_git_history(
            self.root,
            self.config.git_history_limit,
            symbol_paths=symbols_by_path,
            excluded_paths=(*self.config.exclude, self.vault_relative),
        ):
            node_id = f"commit:{commit.sha}"
            self.graph.add_node(
                Node(
                    id=node_id,
                    kind="commit",
                    label=commit.subject or commit.short,
                    metadata={
                        "short": commit.short,
                        "date": commit.date,
                        "owner": "scanner",
                    },
                )
            )
            for relative in commit.paths:
                target = f"file:{relative}"
                if target in self.graph.nodes:
                    self.graph.add_edge(Edge(node_id, target, "changes", "git-log"))
            for symbol_id in _modified_symbols(commit.hunks, symbols_by_path):
                self.graph.add_edge(Edge(node_id, symbol_id, "modifies", "git-diff-hunk"))

    def _check_graph_budget(self) -> None:
        if len(self.graph.nodes) > MAX_GRAPH_NODES:
            raise ValueError(f"Graph exceeds the {MAX_GRAPH_NODES}-node scan budget")
        if self.graph.edge_count > MAX_GRAPH_EDGES:
            raise ValueError(f"Graph exceeds the {MAX_GRAPH_EDGES}-edge scan budget")

    def _scan_evidence_reports(self) -> None:
        kinds = {
            relative: self.graph.nodes[f"file:{relative}"].kind for relative in self.files
        }
        fragment = import_evidence(
            self.root,
            files=dict(self.files),
            kinds=kinds,
            vault=self.config.vault_path(self.root),
            coverage_reports=self.config.coverage_reports,
            test_reports=self.config.test_reports,
            scip_reports=self.config.scip_reports,
            sarif_reports=self.config.sarif_reports,
            test_execution_reports=self.config.test_execution_reports,
            head_revision=resolve_git_head(self.root),
            workspace_owners=dict(
                self.workspace.aligned_owners if self.workspace is not None else {}
            ),
            graph_nodes=dict(self.graph.nodes),
        )
        for node in fragment.nodes:
            self.graph.add_node(node)
        for edge in fragment.edges:
            if not self.graph.add_edge(edge):
                raise ValueError(
                    f"Evidence importer emitted invalid edge: {edge.source} -> {edge.target}"
                )

    def _scan_user_vault(self) -> None:
        vault = self.config.vault_path(self.root)
        for area, kind in USER_VAULT_AREAS.items():
            area_path = vault / area
            if not area_path.is_dir():
                continue
            for path in sorted(area_path.rglob("*.md")):
                if path.is_symlink():
                    continue
                try:
                    if path.stat().st_size > MAX_PARSE_BYTES:
                        continue
                    content = path.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                relative = path.relative_to(vault).as_posix()
                explicit_id = _frontmatter_id(content)
                node_id = (
                    _validate_user_id(explicit_id, relative)
                    if explicit_id is not None
                    else f"note:{relative.removesuffix('.md')}"
                )
                # Record where the identity came from. A note without frontmatter still
                # receives a stable ID derived from its path, and downstream evidence must
                # not describe that as a declared identity.
                identity = FRONTMATTER_IDENTITY if explicit_id is not None else PATH_IDENTITY
                node = Node(
                    id=node_id,
                    kind=kind,
                    label=path.stem,
                    path=relative,
                    metadata={"owner": "user", "area": area, "identity": identity},
                )
                self.graph.add_node(node)
                for target, relation in _wikilinks(content):
                    self.pending_links.append(
                        PendingLink(node_id, target, relation, "wikilink")
                    )

    def _scan_delivery_reports(self) -> None:
        fragment = import_delivery(
            self.root,
            files=dict(self.files),
            graph_nodes=dict(self.graph.nodes),
            vault=self.config.vault_path(self.root),
            reports=self.config.delivery_reports,
        )
        for node in fragment.nodes:
            self.graph.add_node(node)
        for edge in fragment.edges:
            if not self.graph.add_edge(edge):
                raise ValueError(
                    f"Delivery importer emitted invalid edge: {edge.source} -> {edge.target}"
                )

    def _resolve_pending_links(self) -> None:
        aliases: dict[str, set[str]] = defaultdict(set)
        locations = ProjectVault.note_locations(self.graph)
        for node in self.graph.nodes.values():
            location = locations[node.id]
            candidates = {
                node.id,
                node.label,
                note_title(node),
                Path(safe_filename(note_title(node))).stem,
                location.as_posix(),
                location.with_suffix("").as_posix(),
            }
            if node.path:
                candidates.update(
                    {
                        node.path,
                        Path(node.path).stem,
                        Path(node.path).with_suffix("").as_posix(),
                    }
                )
            for candidate in candidates:
                aliases[candidate.casefold()].add(node.id)

        for pending in self.pending_links:
            matches = aliases.get(pending.target.casefold(), set())
            if len(matches) == 1:
                self.graph.add_edge(
                    Edge(
                        pending.source,
                        next(iter(matches)),
                        pending.relation,
                        pending.evidence,
                    )
                )


def _adapter_fingerprint(adapter: LanguageAdapter, context: AdapterContext) -> str:
    digest = hashlib.sha256()
    _hash_part(digest, b"intentatlas-adapter-fragment-v1")
    _hash_part(digest, adapter.name.encode("utf-8"))
    _hash_part(digest, str(adapter.cache_version).encode("ascii"))
    _hash_part(digest, str(context.max_parse_bytes).encode("ascii"))
    for owner, roots in sorted(context.source_roots.items()):
        _hash_part(digest, owner.encode("utf-8"))
        for root in roots:
            _hash_part(digest, root.encode("utf-8"))
    for owner, pattern, targets in context.module_aliases:
        _hash_part(digest, owner.encode("utf-8"))
        _hash_part(digest, pattern.encode("utf-8"))
        for target in targets:
            _hash_part(digest, target.encode("utf-8"))
    for source, target in sorted(context.workspace_dependencies):
        _hash_part(digest, source.encode("utf-8"))
        _hash_part(digest, target.encode("utf-8"))
    for relative in sorted(context.files):
        suffix = PurePosixPath(relative).suffix.casefold()
        if suffix not in adapter.cache_input_suffixes:
            continue
        _hash_part(digest, relative.encode("utf-8"))
        _hash_part(digest, context.kinds[relative].encode("utf-8"))
        for owner in context.workspace_owners.get(relative, ()):
            _hash_part(digest, owner.encode("utf-8"))
        path = context.files[relative]
        try:
            size = path.stat().st_size
            if size > context.max_parse_bytes:
                _hash_part(digest, f"oversized:{size}".encode("ascii"))
                continue
            with path.open("rb") as stream:
                while chunk := stream.read(1024 * 1024):
                    _hash_part(digest, chunk)
        except OSError:
            _hash_part(digest, b"unreadable")
    return digest.hexdigest()


def _adapter_partitions(
    adapter: LanguageAdapter, context: AdapterContext
) -> tuple[tuple[str, AdapterContext], ...]:
    owners = {
        owner
        for relative in context.files
        if PurePosixPath(relative).suffix.casefold() in adapter.cache_input_suffixes
        for owner in context.workspace_owners.get(relative, ())
    }
    if not owners:
        owners = {"workspace:repository:."}
    partitions: list[tuple[str, AdapterContext]] = []
    for owner in sorted(owners):
        closure = {owner}
        while True:
            additions = {
                target
                for source, target in context.workspace_dependencies
                if source in closure
            }
            if additions <= closure:
                break
            closure.update(additions)
        selected = {
            relative: path
            for relative, path in context.files.items()
            if set(context.workspace_owners.get(relative, ())) & closure
        }
        partitions.append(
            (
                owner,
                AdapterContext(
                    files=MappingProxyType(selected),
                    kinds=MappingProxyType(
                        {relative: context.kinds[relative] for relative in selected}
                    ),
                    max_parse_bytes=context.max_parse_bytes,
                    workspace_owners=MappingProxyType(
                        {
                            relative: context.workspace_owners.get(relative, ())
                            for relative in selected
                        }
                    ),
                    source_roots=MappingProxyType(
                        {
                            key: value
                            for key, value in context.source_roots.items()
                            if key in closure
                        }
                    ),
                    module_aliases=tuple(
                        value for value in context.module_aliases if value[0] in closure
                    ),
                    workspace_dependencies=frozenset(
                        (source, target)
                        for source, target in context.workspace_dependencies
                        if source in closure and target in closure
                    ),
                ),
            )
        )
    return tuple(partitions)


def _workspace_source_roots(model: WorkspaceModel | None) -> dict[str, tuple[str, ...]]:
    if model is None:
        return {}
    grouped: dict[str, list[str]] = defaultdict(list)
    for source_root in model.source_roots:
        grouped[owner_id(source_root)].append(source_root.path)
    return {
        owner: tuple(sorted(set(roots)))
        for owner, roots in sorted(grouped.items())
    }


def _endpoint_path(
    node_id: str,
    fragment_paths: dict[str, str],
    graph: AtlasGraph,
) -> str | None:
    path = fragment_paths.get(node_id)
    if path is not None:
        return path
    node = graph.nodes.get(node_id)
    return node.path if node is not None else None


def _hash_part(digest: _HashWriter, value: bytes) -> None:
    digest.update(len(value).to_bytes(8, "big"))
    digest.update(value)


def _file_kind(path: Path) -> str:
    lowered_parts = {part.casefold() for part in path.parts}
    stem = path.stem.casefold()
    if (
        "tests" in lowered_parts
        or "test" in lowered_parts
        or "__tests__" in lowered_parts
        or stem in {"test", "tests"}
        or stem.startswith("test_")
        or stem.endswith("_test")
        or stem.endswith(".test")
        or stem.endswith(".spec")
    ):
        return "test"
    if path.suffix.casefold() in DOCUMENT_SUFFIXES:
        return "document"
    if path.suffix.casefold() in CONFIG_SUFFIXES:
        return "config"
    return "file"


def _language(suffix: str) -> str:
    return {
        ".c": "C",
        ".cc": "C++",
        ".cpp": "C++",
        ".cs": "C#",
        ".go": "Go",
        ".h": "C",
        ".hpp": "C++",
        ".java": "Java",
        ".js": "JavaScript",
        ".jsx": "JavaScript",
        ".md": "Markdown",
        ".mod": "Go Modules",
        ".php": "PHP",
        ".py": "Python",
        ".rb": "Ruby",
        ".rs": "Rust",
        ".rst": "reStructuredText",
        ".swift": "Swift",
        ".toml": "TOML",
        ".ts": "TypeScript",
        ".tsx": "TypeScript",
        ".yaml": "YAML",
        ".yml": "YAML",
    }.get(suffix, suffix.lstrip(".").upper())


def _exclude_patterns(values: Iterable[str]) -> tuple[tuple[str, ...], ...]:
    patterns: set[tuple[str, ...]] = set()
    for value in values:
        normalized = value.strip().replace("\\", "/").strip("/")
        if not normalized:
            continue
        parts = tuple(
            part.casefold()
            for part in PurePosixPath(normalized).parts
            if part not in {"", "."}
        )
        if ".." in parts:
            raise ValueError(f"Exclude path may not contain '..': {value}")
        if parts:
            patterns.add(parts)
    return tuple(sorted(patterns))


def _is_directory_link(path: Path) -> bool:
    try:
        if path.is_symlink():
            return True
        is_junction = getattr(path, "is_junction", None)
        return bool(is_junction and is_junction())
    except OSError:
        return True


def _wikilinks(content: str) -> Iterable[tuple[str, str]]:
    """Yield links with an allowlisted typed relation when explicitly annotated."""

    for match in WIKILINK.finditer(content):
        line_start = content.rfind("\n", 0, match.start()) + 1
        prefix = content[line_start : match.start()]
        typed = TYPED_RELATION_PREFIX.fullmatch(prefix)
        relation = (
            typed.group(1) if typed and typed.group(1) in USER_RELATIONS else "references"
        )
        yield match.group(1).strip(), relation


def _frontmatter_id(content: str) -> str | None:
    lines = content.lstrip("\ufeff \t\r\n").splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    candidate: str | None = None
    for line in lines[1:]:
        if line.strip() == "---":
            return candidate
        match = FRONTMATTER_ID_LINE.fullmatch(line.strip())
        if match is None:
            continue
        value = match.group(1).strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1].strip()
        candidate = value
    return None


def _validate_user_id(value: str, relative: str) -> str:
    if not value or len(value) > 240 or UNSAFE_USER_ID.search(value):
        raise ValueError(f"Invalid user note ID in {relative}: {value!r}")
    if value.casefold().startswith(RESERVED_USER_ID_PREFIXES):
        raise ValueError(f"Reserved graph node ID in {relative}: {value!r}")
    return value


def _symbols_by_path(nodes: Iterable[Node]) -> dict[str, tuple[Node, ...]]:
    return symbol_spans_by_path(nodes)


def _modified_symbols(
    hunks: tuple[DiffHunk, ...], symbols_by_path: dict[str, tuple[Node, ...]]
) -> tuple[str, ...]:
    return map_hunks_to_most_specific_symbols(hunks, symbols_by_path).symbol_ids
