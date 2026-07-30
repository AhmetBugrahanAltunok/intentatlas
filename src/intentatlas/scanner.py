from __future__ import annotations

import ast
import os
import re
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from .config import ProjectConfig
from .git_history import collect_git_history
from .graph import AtlasGraph
from .models import Edge, Node
from .naming import note_title, safe_filename

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
CONFIG_SUFFIXES = {".toml", ".yaml", ".yml"}
DOCUMENT_SUFFIXES = {".md", ".rst"}
MAX_PARSE_BYTES = 1_000_000
USER_VAULT_AREAS = {
    "Brain": "memory",
    "Requirements": "requirement",
    "Decisions": "decision",
    "Evidence": "evidence",
    "Reviews": "review",
    "Sessions": "session",
}
WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
FRONTMATTER_ID_LINE = re.compile(r"^id:\s*(.+?)\s*$")
UNSAFE_USER_ID = re.compile(r"[\x00-\x20\x7f\[\]|]")
RESERVED_USER_ID_PREFIXES = ("commit:", "file:", "symbol:")


@dataclass(slots=True)
class PendingLink:
    source: str
    target: str
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
        self.module_to_node: dict[str, str] = {}
        self.path_to_module: dict[str, str] = {}
        self.pending_links: list[PendingLink] = []
        self.exclude_patterns = _exclude_patterns(config.exclude)
        self.vault_parts = tuple(
            part.casefold()
            for part in config.vault_path(self.root).relative_to(self.root).parts
        )

    def scan(self) -> AtlasGraph:
        self._discover_files()
        self._build_module_map()
        self._scan_python_files()
        self._link_test_conventions()
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

    def _build_module_map(self) -> None:
        for relative in sorted(self.files):
            path = Path(relative)
            if path.suffix.casefold() != ".py":
                continue
            parts = list(path.with_suffix("").parts)
            if parts and parts[0] == "src":
                parts = parts[1:]
            if parts and parts[-1] == "__init__":
                parts = parts[:-1]
            if not parts:
                continue
            module = ".".join(parts)
            self.module_to_node[module] = f"file:{relative}"
            self.path_to_module[relative] = module

    def _scan_python_files(self) -> None:
        for relative, path in sorted(self.files.items()):
            if path.suffix.casefold() != ".py":
                continue
            try:
                if path.stat().st_size > MAX_PARSE_BYTES:
                    continue
                source = path.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(source, filename=relative)
            except (OSError, SyntaxError, ValueError):
                continue

            file_node = f"file:{relative}"
            visitor = _SymbolVisitor(relative)
            visitor.visit(tree)
            for node in visitor.nodes:
                self.graph.add_node(node)
                self.graph.add_edge(Edge(file_node, node.id, "defines", "python-ast"))

            relation = "tests" if self.graph.nodes[file_node].kind == "test" else "imports"
            for imported_module in sorted(_python_imports(tree, relative, self.path_to_module)):
                target = self._resolve_module(imported_module)
                if target is not None and target != file_node:
                    self.graph.add_edge(Edge(file_node, target, relation, "python-ast"))

    def _resolve_module(self, module: str) -> str | None:
        candidate = module
        while candidate:
            target = self.module_to_node.get(candidate)
            if target is not None:
                return target
            candidate = candidate.rpartition(".")[0]
        return None

    def _link_test_conventions(self) -> None:
        sources_by_stem: dict[str, list[str]] = defaultdict(list)
        for relative in self.files:
            node_id = f"file:{relative}"
            if self.graph.nodes[node_id].kind != "test" and relative.endswith(".py"):
                sources_by_stem[Path(relative).stem].append(node_id)

        for relative in self.files:
            node_id = f"file:{relative}"
            if self.graph.nodes[node_id].kind != "test":
                continue
            stem = Path(relative).stem
            candidate_stem = stem.removeprefix("test_").removesuffix("_test")
            candidates = sources_by_stem.get(candidate_stem, [])
            if len(candidates) == 1:
                self.graph.add_edge(Edge(node_id, candidates[0], "tests", "filename-convention"))

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
                for target in WIKILINK.findall(content):
                    self.pending_links.append(PendingLink(node_id, target.strip(), "wikilink"))

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
                    Edge(pending.source, next(iter(matches)), "references", pending.evidence)
                )


class _SymbolVisitor(ast.NodeVisitor):
    def __init__(self, relative: str):
        self.relative = relative
        self.stack: list[str] = []
        self.nodes: list[Node] = []

    def _visit_symbol(self, node: ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        qualname = ".".join([*self.stack, node.name])
        kind = "class" if isinstance(node, ast.ClassDef) else "function"
        symbol_id = f"symbol:{self.relative}::{qualname}"
        self.nodes.append(
            Node(
                id=symbol_id,
                kind="symbol",
                label=qualname,
                path=self.relative,
                metadata={"symbol_kind": kind, "line": node.lineno, "owner": "scanner"},
            )
        )
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
        self._visit_symbol(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
        self._visit_symbol(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # noqa: N802
        self._visit_symbol(node)


def _python_imports(tree: ast.AST, relative: str, path_to_module: dict[str, str]) -> Iterable[str]:
    current = path_to_module.get(relative, "")
    is_package = Path(relative).name == "__init__.py"
    package = current.split(".") if is_package else current.split(".")[:-1]

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            yield from (alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base_parts = list(package)
            if node.level:
                remove = max(0, node.level - 1)
                base_parts = base_parts[: len(base_parts) - remove] if remove else base_parts
            elif node.module:
                base_parts = []
            module_parts = node.module.split(".") if node.module else []
            base = ".".join([*base_parts, *module_parts])
            if base:
                yield base
            for alias in node.names:
                if alias.name != "*":
                    yield ".".join(part for part in (base, alias.name) if part)


def _file_kind(path: Path) -> str:
    lowered_parts = {part.casefold() for part in path.parts}
    stem = path.stem.casefold()
    if (
        "tests" in lowered_parts
        or "test" in lowered_parts
        or stem.startswith("test_")
        or stem.endswith("_test")
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
