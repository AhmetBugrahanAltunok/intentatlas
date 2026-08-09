from __future__ import annotations

import json
import re
import shutil
import subprocess  # nosec B404
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath

from .git_history import (
    MAX_DIFF_BYTES,
    MAX_DIFF_FILES,
    MAX_SYMBOL_SOURCE_BYTES,
    DiffHunk,
    parse_git_diffs,
)

CHANGE_SET_SCHEMA_VERSION = 1
MAX_REVISION_LENGTH = 200
_SYNTHETIC_SHA = "0" * 40
_REVISION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/@{}^~+\-]{0,199}$")
_STATUS = re.compile(r"^(?P<kind>[ACDMRTU])(?:\d{1,3})?$")
_STATUS_NAMES = {
    "A": "added",
    "C": "copied",
    "D": "deleted",
    "M": "modified",
    "R": "renamed",
    "T": "type-changed",
    "U": "unmerged",
}


@dataclass(frozen=True, slots=True)
class ChangeFile:
    status: str
    path: str
    previous_path: str | None = None
    hunks: tuple[DiffHunk, ...] = ()

    def to_dict(self) -> dict[str, object]:
        value: dict[str, object] = {
            "status": self.status,
            "path": self.path,
            "hunks": [
                {"start": hunk.start, "count": hunk.count} for hunk in self.hunks
            ],
        }
        if self.previous_path is not None:
            value["previous_path"] = self.previous_path
        return value


@dataclass(frozen=True, slots=True)
class ChangeSet:
    scope: str
    base_revision: str | None
    head_revision: str | None
    files: tuple[ChangeFile, ...]

    @property
    def hunk_count(self) -> int:
        return sum(len(item.hunks) for item in self.files)

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": CHANGE_SET_SCHEMA_VERSION,
            "scope": self.scope,
            "base_revision": self.base_revision,
            "head_revision": self.head_revision,
            "file_count": len(self.files),
            "hunk_count": self.hunk_count,
            "files": [item.to_dict() for item in self.files],
        }


def collect_change_set(
    root: Path,
    *,
    scope: str,
    revision: str | None = None,
    base: str | None = None,
    head: str | None = None,
    excluded_paths: tuple[str, ...] = (),
) -> ChangeSet:
    """Collect bounded Git metadata without retaining diff contents."""

    if scope not in {"commit", "range", "staged", "worktree"}:
        raise ValueError(f"Unknown change scope: {scope}")
    root = root.resolve()
    if not root.is_dir() or not (root / ".git").exists():
        raise ValueError(f"Project is not a Git repository: {root}")
    executable = shutil.which("git")
    if executable is None:
        raise ValueError("Git is required to collect a change set")
    excluded_paths = tuple(
        sorted({_safe_git_path(path.rstrip("/")) for path in excluded_paths})
    )

    base_revision: str | None
    head_revision: str | None
    status_arguments: tuple[str, ...]
    patch_arguments: tuple[str, ...]

    if scope == "commit":
        if revision is None or base is not None or head is not None:
            raise ValueError("Commit scope requires exactly one revision")
        head_revision = _resolve_revision(root, executable, revision)
        base_revision = _try_resolve_revision(root, executable, f"{head_revision}^")
        if base_revision is None:
            status_arguments = (
                "diff-tree",
                "--root",
                "--no-commit-id",
                "-r",
                "--find-renames=50%",
                "--name-status",
                "-z",
                head_revision,
                "--",
                *_pathspecs(excluded_paths),
            )
            patch_arguments = (
                "show",
                "--format=",
                "--root",
                "--find-renames=50%",
                "--no-ext-diff",
                "--no-textconv",
                "--no-color",
                "--unified=0",
                head_revision,
                "--",
                *_pathspecs(excluded_paths),
            )
        else:
            status_arguments = _diff_arguments(
                base_revision, head_revision, names=True, excluded_paths=excluded_paths
            )
            patch_arguments = _diff_arguments(
                base_revision, head_revision, names=False, excluded_paths=excluded_paths
            )
    elif scope == "range":
        if revision is not None or base is None or head is None:
            raise ValueError("Range scope requires both base and head revisions")
        base_revision = _resolve_revision(root, executable, base)
        head_revision = _resolve_revision(root, executable, head)
        status_arguments = _diff_arguments(
            base_revision, head_revision, names=True, excluded_paths=excluded_paths
        )
        patch_arguments = _diff_arguments(
            base_revision, head_revision, names=False, excluded_paths=excluded_paths
        )
    elif scope == "staged":
        if revision is not None or base is not None or head is not None:
            raise ValueError("Staged scope does not accept revisions")
        base_revision = _try_resolve_revision(root, executable, "HEAD")
        head_revision = None
        status_arguments = _diff_arguments(
            None, None, names=True, cached=True, excluded_paths=excluded_paths
        )
        patch_arguments = _diff_arguments(
            None, None, names=False, cached=True, excluded_paths=excluded_paths
        )
    else:
        if revision is not None or base is not None or head is not None:
            raise ValueError("Worktree scope does not accept revisions")
        base_revision = _try_resolve_revision(root, executable, "HEAD")
        head_revision = None
        if base_revision is None:
            staged_status = _git_output(
                root,
                executable,
                *_diff_arguments(
                    None,
                    None,
                    names=True,
                    cached=True,
                    excluded_paths=excluded_paths,
                ),
            )
            unstaged_status = _git_output(
                root,
                executable,
                *_diff_arguments(None, None, names=True, excluded_paths=excluded_paths),
            )
            staged_patch = _git_output(
                root,
                executable,
                *_diff_arguments(
                    None,
                    None,
                    names=False,
                    cached=True,
                    excluded_paths=excluded_paths,
                ),
            )
            unstaged_patch = _git_output(
                root,
                executable,
                *_diff_arguments(None, None, names=False, excluded_paths=excluded_paths),
            )
            files = _merge_files(
                (*parse_name_status(staged_status), *parse_name_status(unstaged_status))
            )
            patch = f"{staged_patch}\n{unstaged_patch}"
            return _finish_change_set(
                root,
                executable,
                scope,
                base_revision,
                head_revision,
                files,
                patch,
                include_untracked=True,
                excluded_paths=excluded_paths,
            )
        status_arguments = _diff_arguments(
            base_revision, None, names=True, excluded_paths=excluded_paths
        )
        patch_arguments = _diff_arguments(
            base_revision, None, names=False, excluded_paths=excluded_paths
        )

    status_output = _git_output(root, executable, *status_arguments)
    patch_output = _git_output(root, executable, *patch_arguments)
    return _finish_change_set(
        root,
        executable,
        scope,
        base_revision,
        head_revision,
        parse_name_status(status_output),
        patch_output,
        include_untracked=scope == "worktree",
        excluded_paths=excluded_paths,
    )


def parse_name_status(output: str) -> tuple[ChangeFile, ...]:
    if len(output.encode("utf-8")) > MAX_DIFF_BYTES:
        raise ValueError(f"Git change metadata exceeds the {MAX_DIFF_BYTES}-byte limit")
    tokens = output.split("\x00")
    if tokens and tokens[-1] == "":
        tokens.pop()
    files: list[ChangeFile] = []
    index = 0
    while index < len(tokens):
        match = _STATUS.fullmatch(tokens[index])
        if match is None:
            raise ValueError("Git change metadata is malformed")
        kind = match.group("kind")
        index += 1
        needs_previous = kind in {"C", "R"}
        required = 2 if needs_previous else 1
        if index + required > len(tokens):
            raise ValueError("Git change metadata is malformed")
        previous_path = _safe_git_path(tokens[index]) if needs_previous else None
        if needs_previous:
            index += 1
        path = _safe_git_path(tokens[index])
        index += 1
        files.append(ChangeFile(_STATUS_NAMES[kind], path, previous_path))
        if len(files) > MAX_DIFF_FILES:
            raise ValueError(f"Change set exceeds the {MAX_DIFF_FILES}-file limit")
    return tuple(sorted(files, key=lambda item: (item.path, item.status, item.previous_path or "")))


def render_change_set(change_set: ChangeSet, output_format: str = "text") -> str:
    if output_format == "json":
        return json.dumps(
            change_set.to_dict(), indent=2, ensure_ascii=False, sort_keys=True
        ) + "\n"
    if output_format != "text":
        raise ValueError(f"Unknown change-set output format: {output_format}")
    lines = [
        f"Change set: {change_set.scope}",
        f"Base revision: {change_set.base_revision or 'none'}",
        f"Head revision: {change_set.head_revision or 'none'}",
        f"Files: {len(change_set.files)}, hunks: {change_set.hunk_count}",
    ]
    for item in change_set.files:
        previous = f" (from {item.previous_path})" if item.previous_path else ""
        ranges = ", ".join(f"{hunk.start}+{hunk.count}" for hunk in item.hunks)
        suffix = f" — lines {ranges}" if ranges else ""
        lines.append(f"- {item.status}: {item.path}{previous}{suffix}")
    return "\n".join(lines) + "\n"


def change_file_freshness(root: Path, change_set: ChangeSet, item: ChangeFile) -> str:
    """Compare the scanned worktree artifact with the ChangeSet target without reading content."""

    if change_set.scope == "worktree":
        return "aligned"
    if item.status == "unmerged":
        return "unknown"
    current = root.resolve().joinpath(*PurePosixPath(item.path).parts)
    if item.status == "deleted":
        try:
            return "aligned" if not current.exists() else "stale"
        except OSError:
            return "unknown"
    try:
        if current.is_symlink() or not current.is_file():
            return "unknown"
    except OSError:
        return "unknown"
    executable = shutil.which("git")
    if executable is None:
        return "unknown"
    if change_set.scope == "staged":
        target = f":{item.path}"
    elif change_set.head_revision is not None:
        target = f"{change_set.head_revision}:{item.path}"
    else:
        return "unknown"
    try:
        if current.stat().st_size > MAX_SYMBOL_SOURCE_BYTES:
            return _oversized_file_freshness(
                root.resolve(), executable, change_set, item.path
            )
        current_bytes = current.read_bytes()
    except OSError:
        return "unknown"
    target_bytes = _try_git_blob(root.resolve(), executable, target)
    if target_bytes is None:
        return "unknown"
    return (
        "aligned"
        if _normalized_lines(target_bytes) == _normalized_lines(current_bytes)
        else "stale"
    )


def _oversized_file_freshness(
    root: Path,
    executable: str,
    change_set: ChangeSet,
    path: str,
) -> str:
    """Compare an oversized file through Git without loading its content into Python."""

    command = [
        executable,
        "-c",
        f"safe.directory={root.as_posix()}",
        "-c",
        "core.quotePath=false",
        "-C",
        str(root),
        "diff",
        "--quiet",
        "--no-ext-diff",
        "--no-textconv",
    ]
    if change_set.scope != "staged":
        if change_set.head_revision is None:
            return "unknown"
        command.append(change_set.head_revision)
    command.extend(("--", path))
    try:
        result = subprocess.run(  # noqa: S603  # nosec B603
            command,
            check=False,
            capture_output=True,
            timeout=10,
            shell=False,
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    if result.returncode == 0:
        return "aligned"
    if result.returncode == 1:
        return "stale"
    return "unknown"


def _finish_change_set(
    root: Path,
    executable: str,
    scope: str,
    base_revision: str | None,
    head_revision: str | None,
    files: tuple[ChangeFile, ...],
    patch_output: str,
    *,
    include_untracked: bool,
    excluded_paths: tuple[str, ...],
) -> ChangeSet:
    merged = _merge_files(files)
    if include_untracked:
        untracked = _git_output(
            root,
            executable,
            "ls-files",
            "--others",
            "--exclude-standard",
            "-z",
            "--",
            *_pathspecs(excluded_paths),
        )
        merged = _merge_files((*merged, *_parse_untracked(untracked)))
    hunks = _parse_patch_hunks(patch_output)
    by_path: dict[str, list[DiffHunk]] = {}
    for hunk in hunks:
        by_path.setdefault(hunk.path, []).append(hunk)
    attached = tuple(
        replace(
            item,
            hunks=tuple(
                sorted(
                    set(by_path.get(item.path, ())),
                    key=lambda hunk: (hunk.start, hunk.count),
                )
            ),
        )
        for item in merged
    )
    return ChangeSet(scope, base_revision, head_revision, attached)


def _diff_arguments(
    base: str | None,
    head: str | None,
    *,
    names: bool,
    cached: bool = False,
    excluded_paths: tuple[str, ...] = (),
) -> tuple[str, ...]:
    arguments = [
        "diff",
        "--find-renames=50%",
        "--no-ext-diff",
        "--no-textconv",
        "--no-color",
        "--ignore-submodules=all",
    ]
    if cached:
        arguments.append("--cached")
    if names:
        arguments.extend(("--name-status", "-z"))
    else:
        arguments.append("--unified=0")
    if base is not None:
        arguments.append(base)
    if head is not None:
        arguments.append(head)
    arguments.append("--")
    arguments.extend(_pathspecs(excluded_paths))
    return tuple(arguments)


def _resolve_revision(root: Path, executable: str, revision: str) -> str:
    if (
        len(revision) > MAX_REVISION_LENGTH
        or _REVISION.fullmatch(revision) is None
        or ".." in revision
    ):
        raise ValueError(f"Unsafe Git revision: {revision!r}")
    value = _git_output(
        root,
        executable,
        "rev-parse",
        "--verify",
        "--end-of-options",
        f"{revision}^{{commit}}",
    ).strip()
    if re.fullmatch(r"[0-9a-f]{40,64}", value) is None:
        raise ValueError(f"Git revision did not resolve to a commit: {revision}")
    return value


def _try_resolve_revision(root: Path, executable: str, revision: str) -> str | None:
    try:
        return _resolve_revision(root, executable, revision)
    except ValueError:
        return None


def _git_output(root: Path, executable: str, *arguments: str) -> str:
    command = [
        executable,
        "-c",
        f"safe.directory={root.as_posix()}",
        "-c",
        "core.quotePath=false",
        "-C",
        str(root),
        *arguments,
    ]
    try:
        result = subprocess.run(  # noqa: S603  # nosec B603
            command,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            shell=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError("Cannot inspect Git changes") from exc
    if result.returncode != 0:
        raise ValueError("Cannot inspect Git changes")
    if len(result.stdout.encode("utf-8")) > MAX_DIFF_BYTES:
        raise ValueError(f"Git change output exceeds the {MAX_DIFF_BYTES}-byte limit")
    return result.stdout


def _try_git_blob(root: Path, executable: str, target: str) -> bytes | None:
    command = [
        executable,
        "-c",
        f"safe.directory={root.as_posix()}",
        "-c",
        "core.quotePath=false",
        "-C",
        str(root),
        "cat-file",
        "blob",
        target,
    ]
    try:
        result = subprocess.run(  # noqa: S603  # nosec B603
            command,
            check=False,
            capture_output=True,
            timeout=5,
            shell=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0 or len(result.stdout) > MAX_SYMBOL_SOURCE_BYTES:
        return None
    return result.stdout


def _normalized_lines(value: bytes) -> bytes:
    return value.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def _safe_git_path(value: str) -> str:
    candidate = value.replace("\\", "/")
    pure = PurePosixPath(candidate)
    if (
        not candidate
        or pure.is_absolute()
        or ".." in pure.parts
        or any(ord(character) < 32 for character in candidate)
    ):
        raise ValueError(f"Git change contains an unsafe path: {value!r}")
    return pure.as_posix()


def _pathspecs(excluded_paths: tuple[str, ...]) -> tuple[str, ...]:
    if not excluded_paths:
        return ()
    return (".", *(f":(exclude,literal){path}" for path in excluded_paths))


def _parse_untracked(output: str) -> tuple[ChangeFile, ...]:
    if len(output.encode("utf-8")) > MAX_DIFF_BYTES:
        raise ValueError(f"Git change output exceeds the {MAX_DIFF_BYTES}-byte limit")
    paths = output.split("\x00")
    if paths and paths[-1] == "":
        paths.pop()
    if len(paths) > MAX_DIFF_FILES:
        raise ValueError(f"Change set exceeds the {MAX_DIFF_FILES}-file limit")
    return tuple(ChangeFile("untracked", _safe_git_path(path)) for path in paths)


def _parse_patch_hunks(output: str) -> tuple[DiffHunk, ...]:
    if len(output.encode("utf-8")) > MAX_DIFF_BYTES:
        raise ValueError(f"Git patch metadata exceeds the {MAX_DIFF_BYTES}-byte limit")
    parsed = parse_git_diffs(f"\x00{_SYNTHETIC_SHA}\n{output}")
    return parsed.get(_SYNTHETIC_SHA, ())


def _merge_files(files: tuple[ChangeFile, ...]) -> tuple[ChangeFile, ...]:
    merged: dict[str, ChangeFile] = {}
    for item in files:
        current = merged.get(item.path)
        if current is None:
            merged[item.path] = item
        elif current.status == "added" and item.status == "modified":
            continue
        elif current.status == "modified" and item.status == "added":
            merged[item.path] = item
        elif current != item:
            raise ValueError(f"Conflicting Git change metadata for path: {item.path}")
    if len(merged) > MAX_DIFF_FILES:
        raise ValueError(f"Change set exceeds the {MAX_DIFF_FILES}-file limit")
    return tuple(merged[path] for path in sorted(merged))
