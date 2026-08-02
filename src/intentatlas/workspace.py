from __future__ import annotations

import json
import re
import tomllib
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import Any

from .models import Edge, Node
from .safe_io import read_bounded_regular_file

WORKSPACE_SCHEMA_VERSION = 1
MAX_METADATA_BYTES = 1_000_000
MAX_BOUNDARIES = 1_024
MAX_ALIASES = 256
MAX_WORKSPACE_MEMBERS = 512
SAFE_PACKAGE_NAME = re.compile(r"[A-Za-z0-9@._/-]{1,240}")
JS_SUFFIXES = frozenset({".js", ".jsx", ".ts", ".tsx"})


@dataclass(frozen=True, slots=True)
class WorkspaceBoundary:
    id: str
    kind: str
    path: str
    language: str
    declaration: str
    name: str

    def to_node(self, candidates: tuple[str, ...] = ()) -> Node:
        metadata: dict[str, Any] = {
            "workspace_schema_version": WORKSPACE_SCHEMA_VERSION,
            "language": self.language,
            "declaration": self.declaration,
            "owner": "scanner",
        }
        if candidates:
            metadata["candidates"] = list(candidates)
        return Node(self.id, self.kind, self.name, self.path or None, metadata)


@dataclass(frozen=True, slots=True)
class WorkspaceDiagnostic:
    code: str
    path: str
    candidates: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "path": self.path, "candidates": list(self.candidates)}


@dataclass(frozen=True, slots=True)
class AliasRule:
    owner: str
    pattern: str
    targets: tuple[str, ...]
    declaration: str


@dataclass(frozen=True, slots=True)
class WorkspaceModel:
    boundaries: tuple[WorkspaceBoundary, ...]
    source_roots: tuple[WorkspaceBoundary, ...]
    owner_candidates: MappingProxyType[str, tuple[str, ...]]
    aligned_owners: MappingProxyType[str, tuple[str, ...]]
    aliases: tuple[AliasRule, ...]
    dependencies: tuple[tuple[str, str], ...]
    diagnostics: tuple[WorkspaceDiagnostic, ...]

    @property
    def schema_version(self) -> int:
        return WORKSPACE_SCHEMA_VERSION

    def candidates(self, path: str) -> tuple[str, ...]:
        return self.owner_candidates.get(path, ())

    def owners(self, path: str) -> tuple[str, ...]:
        return self.aligned_owners.get(path, ())

    def unique_owner(self, path: str) -> str | None:
        owners = self.owners(path)
        return owners[0] if len(owners) == 1 else None

    def allows(self, source: str, target: str) -> bool:
        source_owner = self.unique_owner(source)
        target_owner = self.unique_owner(target)
        if source_owner is None or target_owner is None:
            return False
        return source_owner == target_owner or (source_owner, target_owner) in self.dependencies

    def graph_fragment(self, files: dict[str, Path]) -> tuple[tuple[Node, ...], tuple[Edge, ...]]:
        nodes = [boundary.to_node() for boundary in (*self.boundaries, *self.source_roots)]
        edges: list[Edge] = []
        repository = "workspace:repository:."
        for boundary in self.boundaries:
            if boundary.id != repository:
                edges.append(Edge(repository, boundary.id, "contains", boundary.declaration))
        for root in self.source_roots:
            owner = root.id.split("::", maxsplit=1)[0].removeprefix("source-root:")
            edges.append(Edge(owner, root.id, "declares", root.declaration))
        for relative in sorted(files):
            unique_owner = self.unique_owner(relative)
            if unique_owner is not None:
                edges.append(
                    Edge(unique_owner, f"file:{relative}", "owns", "workspace-boundary")
                )
        return tuple(sorted(nodes, key=lambda item: item.id)), tuple(
            sorted(edges, key=lambda item: (item.source, item.target, item.relation, item.evidence))
        )


def discover_workspace(root: Path, files: dict[str, Path]) -> WorkspaceModel:
    root = root.resolve()
    repository = WorkspaceBoundary(
        "workspace:repository:.", "repository", "", "mixed", "repository-root", root.name
    )
    boundaries: list[WorkspaceBoundary] = [repository]
    source_roots: list[WorkspaceBoundary] = []
    aliases: list[AliasRule] = []
    dependency_names: list[tuple[str, str, str]] = []
    names: dict[tuple[str, str], set[str]] = defaultdict(set)

    for relative in sorted(files):
        path = PurePosixPath(relative)
        if path.name == "pyproject.toml":
            parsed = _toml(files[relative], relative)
            project = parsed.get("project", {})
            if not isinstance(project, dict):
                project = {}
            name = _safe_name(project.get("name"), f"python:{path.parent.as_posix()}")
            owner = _boundary("python-project", path.parent, "python", relative, name)
            boundaries.append(owner)
            names[("python", _python_distribution_name(name))].add(owner.id)
            for dependency in _python_dependency_names(project):
                dependency_names.append((owner.id, "python", dependency))
            where = _python_source_roots(parsed)
            for source in where or (".",):
                source_roots.append(_source_root(owner, path.parent, source, relative))
        elif path.name == "package.json":
            parsed = _json(files[relative], relative)
            name = _safe_name(parsed.get("name"), f"javascript:{path.parent.as_posix()}")
            owner = _boundary("javascript-package", path.parent, "javascript", relative, name)
            boundaries.append(owner)
            source_roots.append(_source_root(owner, path.parent, ".", relative))
            names[("javascript", name)].add(owner.id)
            for dependency in _dependency_names(parsed):
                dependency_names.append((owner.id, "javascript", dependency))
        elif path.name == "go.mod":
            module = _go_module(files[relative], relative)
            if module is not None:
                owner = _boundary("go-module", path.parent, "go", relative, module)
                boundaries.append(owner)
                source_roots.append(_source_root(owner, path.parent, ".", relative))
                names[("go", module)].add(owner.id)
                for dependency in _go_dependencies(files[relative], relative):
                    dependency_names.append((owner.id, "go", dependency))

    aliases.extend(_javascript_aliases(files, boundaries))
    if len(boundaries) + len(source_roots) > MAX_BOUNDARIES:
        raise ValueError(f"Workspace declarations exceed the {MAX_BOUNDARIES}-boundary limit")
    if len(aliases) > MAX_ALIASES:
        raise ValueError(f"Workspace aliases exceed the {MAX_ALIASES}-alias limit")

    dependencies = {
        (owner, target)
        for owner, language, name in dependency_names
        for target in names.get((language, name), ())
        if target != owner
    }
    candidates: dict[str, tuple[str, ...]] = {}
    aligned: dict[str, tuple[str, ...]] = {}
    diagnostics: list[WorkspaceDiagnostic] = []
    for relative in sorted(files):
        declared_by = tuple(
            sorted(
                item.id
                for item in boundaries
                if item.id != repository.id and item.declaration == relative
            )
        )
        if declared_by:
            candidates[relative] = declared_by
            aligned[relative] = declared_by
            if len(declared_by) != 1:
                diagnostics.append(
                    WorkspaceDiagnostic("ambiguous-owner", relative, declared_by)
                )
            continue
        language = _path_language(relative)
        matches = [
            item
            for item in boundaries
            if item.id != repository.id
            and item.language == language
            and _inside(relative, item.path)
        ]
        all_candidates: tuple[str, ...]
        selected: tuple[str, ...]
        if not matches:
            all_candidates = (repository.id,)
            selected = all_candidates
        else:
            all_candidates = tuple(sorted({item.id for item in matches}))
            longest = max(_path_depth(item.path) for item in matches)
            selected = tuple(
                sorted({item.id for item in matches if _path_depth(item.path) == longest})
            )
        candidates[relative] = all_candidates
        aligned[relative] = selected
        if len(selected) != 1:
            diagnostics.append(
                WorkspaceDiagnostic("ambiguous-owner", relative, selected)
            )

    duplicate_names = [
        WorkspaceDiagnostic("duplicate-package-name", name, tuple(sorted(owners)))
        for (_language, name), owners in sorted(names.items())
        if len(owners) > 1
    ]
    diagnostics.extend(duplicate_names)
    return WorkspaceModel(
        tuple(sorted(_deduplicate_boundaries(boundaries), key=lambda item: item.id)),
        tuple(sorted(_deduplicate_boundaries(source_roots), key=lambda item: item.id)),
        MappingProxyType(candidates),
        MappingProxyType(aligned),
        tuple(sorted(aliases, key=lambda item: (item.owner, item.pattern, item.targets))),
        tuple(sorted(dependencies)),
        tuple(sorted(diagnostics, key=lambda item: (item.code, item.path, item.candidates))),
    )


def owner_id(source_root: WorkspaceBoundary) -> str:
    return source_root.id.removeprefix("source-root:").split("::", maxsplit=1)[0]


def _boundary(
    kind: str,
    path: PurePosixPath,
    language: str,
    declaration: str,
    name: str,
) -> WorkspaceBoundary:
    normalized = "" if path.as_posix() == "." else path.as_posix()
    return WorkspaceBoundary(
        f"workspace:{kind}:{normalized or '.'}",
        "project" if kind != "javascript-package" else "package",
        normalized,
        language,
        declaration,
        name,
    )


def _source_root(
    owner: WorkspaceBoundary,
    base: PurePosixPath,
    configured: str,
    declaration: str,
) -> WorkspaceBoundary:
    target = PurePosixPath(configured)
    if target.is_absolute() or ".." in target.parts:
        raise ValueError(f"Workspace source root is unsafe in {declaration}: {configured}")
    combined = PurePosixPath(base, target)
    normalized = "" if combined.as_posix() == "." else combined.as_posix().removeprefix("./")
    return WorkspaceBoundary(
        f"source-root:{owner.id}::{normalized or '.'}", "source-root", normalized,
        owner.language, declaration, normalized or ".",
    )


def _python_source_roots(document: dict[str, Any]) -> tuple[str, ...]:
    tool = document.get("tool", {})
    if not isinstance(tool, dict):
        return ()
    setuptools = tool.get("setuptools", {})
    if not isinstance(setuptools, dict):
        return ()
    roots: list[str] = []
    package_dir = setuptools.get("package-dir", {})
    if isinstance(package_dir, dict):
        value = package_dir.get("")
        if isinstance(value, str):
            roots.append(value)
    packages = setuptools.get("packages", {})
    if isinstance(packages, dict):
        find = packages.get("find", {})
        if isinstance(find, dict):
            where = find.get("where", [])
            if isinstance(where, list):
                roots.extend(item for item in where if isinstance(item, str))
    return tuple(dict.fromkeys(root.strip() for root in roots if root.strip()))


def _javascript_aliases(
    files: dict[str, Path], boundaries: list[WorkspaceBoundary]
) -> list[AliasRule]:
    rules: list[AliasRule] = []
    for relative in sorted(files):
        path = PurePosixPath(relative)
        if path.name not in {"tsconfig.json", "jsconfig.json"}:
            continue
        document = _json(files[relative], relative, allow_comments=True)
        compiler = document.get("compilerOptions", {})
        if not isinstance(compiler, dict):
            continue
        paths = compiler.get("paths", {})
        if not isinstance(paths, dict):
            continue
        base_url = compiler.get("baseUrl", ".")
        if not isinstance(base_url, str):
            continue
        config_root = "" if path.parent.as_posix() == "." else path.parent.as_posix()
        owner_candidates = [
            item for item in boundaries
            if item.language == "javascript" and _inside(relative, item.path)
        ]
        owner_candidates.sort(key=lambda item: (-_path_depth(item.path), item.id))
        if not owner_candidates:
            continue
        longest = _path_depth(owner_candidates[0].path)
        owners = [item for item in owner_candidates if _path_depth(item.path) == longest]
        if len(owners) != 1:
            continue
        for pattern, targets in sorted(paths.items()):
            if not isinstance(pattern, str) or not isinstance(targets, list):
                continue
            normalized: list[str] = []
            for target in targets:
                if not isinstance(target, str):
                    continue
                pure = PurePosixPath(config_root, base_url, target)
                if pure.is_absolute() or ".." in pure.parts:
                    continue
                normalized.append(pure.as_posix().removeprefix("./"))
            if normalized:
                rules.append(
                    AliasRule(
                        owners[0].id,
                        pattern,
                        tuple(sorted(set(normalized))),
                        relative,
                    )
                )
    return rules


def _dependency_names(document: dict[str, Any]) -> tuple[str, ...]:
    names: set[str] = set()
    for key in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        value = document.get(key, {})
        if isinstance(value, dict):
            names.update(name for name in value if isinstance(name, str))
    return tuple(sorted(names))


def _python_dependency_names(project: dict[str, Any]) -> tuple[str, ...]:
    dependencies = project.get("dependencies", [])
    if not isinstance(dependencies, list):
        return ()
    names: set[str] = set()
    for value in dependencies:
        if not isinstance(value, str):
            continue
        match = re.match(r"[A-Za-z0-9][A-Za-z0-9._-]*", value.strip())
        if match is not None:
            names.add(_python_distribution_name(match.group(0)))
    return tuple(sorted(names))


def _python_distribution_name(value: str) -> str:
    return re.sub(r"[-_.]+", "-", value).casefold()


def _go_module(path: Path, relative: str) -> str | None:
    data = read_bounded_regular_file(path, MAX_METADATA_BYTES)
    if data is None:
        raise ValueError(f"Workspace metadata is not a bounded regular file: {relative}")
    for line in data.decode("utf-8", errors="replace").splitlines():
        stripped = line.split("//", maxsplit=1)[0].strip()
        if stripped.startswith("module "):
            return _safe_name(stripped.removeprefix("module ").strip(), f"go:{relative}")
    return None


def _go_dependencies(path: Path, relative: str) -> tuple[str, ...]:
    data = read_bounded_regular_file(path, MAX_METADATA_BYTES)
    if data is None:
        raise ValueError(f"Workspace metadata is not a bounded regular file: {relative}")
    dependencies: set[str] = set()
    in_require = False
    for line in data.decode("utf-8", errors="replace").splitlines():
        stripped = line.split("//", maxsplit=1)[0].strip()
        if stripped == "require (":
            in_require = True
            continue
        if in_require and stripped == ")":
            in_require = False
            continue
        if stripped.startswith("require "):
            candidate = stripped.removeprefix("require ").split(maxsplit=1)[0]
        elif in_require and stripped:
            candidate = stripped.split(maxsplit=1)[0]
        else:
            continue
        if SAFE_PACKAGE_NAME.fullmatch(candidate):
            dependencies.add(candidate)
    return tuple(sorted(dependencies))


def _json(
    path: Path, relative: str, *, allow_comments: bool = False
) -> dict[str, Any]:
    data = read_bounded_regular_file(path, MAX_METADATA_BYTES)
    if data is None:
        raise ValueError(f"Workspace metadata is not a bounded regular file: {relative}")
    try:
        source = data.decode("utf-8")
        if allow_comments:
            source = _strip_json_comments(source)
            source = re.sub(r",(?=\s*[}\]])", "", source)
        value = json.loads(source, object_pairs_hook=_unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"Cannot parse workspace metadata {relative}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"Workspace metadata must be an object: {relative}")
    return value


def _strip_json_comments(source: str) -> str:
    result = list(source)
    index = 0
    state = "code"
    quote = ""
    while index < len(source):
        current = source[index]
        following = source[index + 1] if index + 1 < len(source) else ""
        if state == "code":
            if current in {'"', "'"}:
                quote = current
                state = "string"
            elif current == "/" and following == "/":
                result[index] = result[index + 1] = " "
                index += 1
                state = "line-comment"
            elif current == "/" and following == "*":
                result[index] = result[index + 1] = " "
                index += 1
                state = "block-comment"
        elif state == "string":
            if current == "\\":
                index += 1
            elif current == quote:
                state = "code"
        elif state == "line-comment":
            if current == "\n":
                state = "code"
            else:
                result[index] = " "
        elif state == "block-comment":
            if current == "*" and following == "/":
                result[index] = result[index + 1] = " "
                index += 1
                state = "code"
            elif current != "\n":
                result[index] = " "
        index += 1
    if state == "block-comment":
        raise ValueError("Unterminated JSON block comment")
    return "".join(result)


def _toml(path: Path, relative: str) -> dict[str, Any]:
    data = read_bounded_regular_file(path, MAX_METADATA_BYTES)
    if data is None:
        raise ValueError(f"Workspace metadata is not a bounded regular file: {relative}")
    try:
        return tomllib.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise ValueError(f"Cannot parse workspace metadata {relative}: {exc}") from exc


def _safe_name(value: Any, fallback: str) -> str:
    return value if isinstance(value, str) and SAFE_PACKAGE_NAME.fullmatch(value) else fallback


def _path_language(relative: str) -> str:
    suffix = PurePosixPath(relative).suffix.casefold()
    if suffix == ".py":
        return "python"
    if suffix in JS_SUFFIXES:
        return "javascript"
    if suffix == ".go":
        return "go"
    return "mixed"


def _inside(relative: str, root: str) -> bool:
    if not root:
        return True
    return relative == root or relative.startswith(f"{root}/")


def _path_depth(path: str) -> int:
    return len(PurePosixPath(path).parts) if path else 0


def _deduplicate_boundaries(values: list[WorkspaceBoundary]) -> list[WorkspaceBoundary]:
    result: dict[str, WorkspaceBoundary] = {}
    for value in values:
        existing = result.get(value.id)
        if existing is not None and existing != value:
            raise ValueError(f"Conflicting workspace boundary: {value.id}")
        result[value.id] = value
    return list(result.values())


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"Duplicate JSON key in workspace metadata: {key}")
        value[key] = item
    return value
