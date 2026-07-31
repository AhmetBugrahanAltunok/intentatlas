from __future__ import annotations

import os
import re
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from types import MappingProxyType

from .adapters import BUILTIN_ADAPTERS, AdapterContext
from .config import ProjectConfig
from .evidence import import_evidence
from .git_history import collect_git_history
from .graph import AtlasGraph
from .models import Edge, Node
from .naming import note_title, safe_filename
from .relations import USER_RELATIONS

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
MAX_PARSE_BYTES = 1_000_000
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


@dataclass(slots=True)
class PendingLink:
    source: str
    target: str
    relation: str
    evidence: str


def scan_repository(root: Path, config: ProjectConfig | None = None) -> AtlasGraph:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"Project path is not a directory: {root}")
    config = config or ProjectConfig.load(root)
    scanner = RepositoryScanner(root, config)
    return scanner.scan()


class RepositoryScanner:
    def __init__(self, root: Path, config: ProjectConfig):
        self.root = root.resolve()
        self.config = config
        self.graph = AtlasGraph()
        self.files: dict[str, Path] = {}
        self.pending_links: list[PendingLink] = []
        self.exclude_patterns = _exclude_patterns(config.exclude)
        self.vault_parts = tuple(
            part.casefold()
            for part in config.vault_path(self.root).relative_to(self.root).parts
        )

    def scan(self) -> AtlasGraph:
        self._discover_files()
        self._scan_language_adapters()
        self._scan_evidence_reports()
        self._scan_git_history()
        self._scan_user_vault()
        self._resolve_pending_links()
        return self.graph

    def _discover_files(self) -> None:
        for path in self._walk_files():
            relative_path = path.relative_to(self.root)
            if path.suffix.casefold() not in SUPPORTED_SUFFIXES:
                continue
            relative = relative_path.as_posix()
            kind = _file_kind(relative_path)
            try:
                size = path.stat().st_size
            except OSError:
                continue
            node_id = f"file:{relative}"
            self.files[relative] = path
            self.graph.add_node(
                Node(
                    id=node_id,
                    kind=kind,
                    label=relative,
                    path=relative,
                    metadata={
                        "language": _language(path.suffix.casefold()),
                        "size_bytes": size,
                        "owner": "scanner",
                    },
                )
            )

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
        if self.vault_parts and parts[: len(self.vault_parts)] == self.vault_parts:
            return True
        for pattern in self.exclude_patterns:
            if len(pattern) == 1 and pattern[0] in parts:
                return True
            if len(pattern) > 1 and parts[: len(pattern)] == pattern:
                return True
        return False

    def _scan_language_adapters(self) -> None:
        kinds = {
            relative: self.graph.nodes[f"file:{relative}"].kind for relative in self.files
        }
        context = AdapterContext(
            files=MappingProxyType(dict(self.files)),
            kinds=MappingProxyType(kinds),
            max_parse_bytes=MAX_PARSE_BYTES,
        )
        for adapter in sorted(BUILTIN_ADAPTERS, key=lambda item: item.name):
            fragment = adapter.scan(context)
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

    def _scan_git_history(self) -> None:
        for commit in collect_git_history(self.root, self.config.git_history_limit):
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
                node = Node(
                    id=node_id,
                    kind=kind,
                    label=path.stem,
                    path=relative,
                    metadata={"owner": "user", "area": area},
                )
                self.graph.add_node(node)
                for target, relation in _wikilinks(content):
                    self.pending_links.append(
                        PendingLink(node_id, target, relation, "wikilink")
                    )

    def _resolve_pending_links(self) -> None:
        aliases: dict[str, set[str]] = defaultdict(set)
        for node in self.graph.nodes.values():
            candidates = {
                node.id,
                node.label,
                note_title(node),
                Path(safe_filename(note_title(node))).stem,
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


def _file_kind(path: Path) -> str:
    lowered_parts = {part.casefold() for part in path.parts}
    stem = path.stem.casefold()
    if (
        "tests" in lowered_parts
        or "test" in lowered_parts
        or "__tests__" in lowered_parts
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
