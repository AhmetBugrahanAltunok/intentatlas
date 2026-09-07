from __future__ import annotations

import re
import shutil
import subprocess  # nosec B404
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from .bounded_process import ProcessCollectionError, run_bounded_process
from .safe_io import read_bounded_regular_file
from .security import redact

MAX_DIFF_BYTES = 10_000_000
MAX_DIFF_FILES = 1_000
MAX_DIFF_HUNKS = 50_000
MAX_DIFF_LINE = 1_000_000_000
MAX_GIT_ARGUMENT_BYTES = 100_000
MAX_GIT_PATH_BYTES = 4_096
MAX_LOG_BYTES = 10_000_000
MAX_LOG_PATHS = 50_000
MAX_SYMBOL_SOURCE_BYTES = 1_000_000
MAX_SYMBOL_COMMITS = 25
PRIVATE_EXCLUDE = "atlas/Private"
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
HUNK_HEADER = re.compile(
    r"^@@ -\d{1,10}(?:,\d{1,10})? \+(\d{1,10})(?:,(\d{1,10}))? @@(?: .*)?$"
)


@dataclass(frozen=True, slots=True)
class DiffHunk:
    path: str
    start: int
    count: int


@dataclass(frozen=True, slots=True)
class CommitRecord:
    sha: str
    short: str
    date: str
    subject: str
    paths: tuple[str, ...]
    hunks: tuple[DiffHunk, ...] = ()


def resolve_git_head(root: Path) -> str | None:
    """Resolve the current commit through a fixed read-only Git invocation."""

    if not (root / ".git").exists():
        return None
    executable = shutil.which("git")
    if executable is None:
        return None
    command = [
        executable,
        "-c",
        f"safe.directory={root.resolve().as_posix()}",
        "-C",
        str(root.resolve()),
        "rev-parse",
        "--verify",
        "--end-of-options",
        "HEAD^{commit}",
    ]
    try:
        output = _run_git_bounded(command, max_bytes=256, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    if output is None:
        return None
    value = output.decode("utf-8", errors="replace").strip()
    return value if FULL_SHA.fullmatch(value) else None


def git_paths_match_head(root: Path, paths: tuple[str, ...]) -> bool | None:
    """Return whether every mapped artifact is tracked and byte-equivalent to HEAD."""

    if not paths:
        return True
    if not (root / ".git").exists():
        return None
    executable = shutil.which("git")
    if executable is None:
        return None
    safe_paths = _literal_pathspecs(paths)
    if safe_paths is None:
        return None
    prefix = [
        executable,
        "-c",
        f"safe.directory={root.resolve().as_posix()}",
        "-c",
        "core.quotePath=false",
        "-C",
        str(root.resolve()),
    ]
    try:
        tracked = subprocess.run(  # noqa: S603  # nosec B603
            [*prefix, "ls-files", "--error-unmatch", "--", *safe_paths],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10,
            shell=False,
        )
        if tracked.returncode != 0:
            return False
        changed = subprocess.run(  # noqa: S603  # nosec B603
            [
                *prefix,
                "diff",
                "--quiet",
                "--no-ext-diff",
                "--ignore-submodules=all",
                "HEAD",
                "--",
                *safe_paths,
            ],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10,
            shell=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if changed.returncode == 0:
        return True
    if changed.returncode == 1:
        return False
    return None


def collect_git_history(
    root: Path,
    limit: int = 25,
    *,
    symbol_paths: Iterable[str] = (),
    excluded_paths: Iterable[str] = (),
) -> list[CommitRecord]:
    """Read bounded commit metadata without executing repository-controlled code."""

    if limit <= 0 or not (root / ".git").exists():
        return []
    limit = min(limit, 250)
    executable = shutil.which("git")
    if executable is None:
        return []
    exclusions = _normalized_excludes((*excluded_paths, PRIVATE_EXCLUDE))
    if exclusions is None:
        return []
    exclusion_pathspecs = _git_exclusion_pathspecs(exclusions)
    if exclusion_pathspecs is None:
        return []
    safe_symbol_paths = frozenset(
        path
        for path in symbol_paths
        if _safe_git_path(path) is not None and not _is_excluded(path, exclusions)
    )
    if len(safe_symbol_paths) > MAX_DIFF_FILES:
        safe_symbol_paths = frozenset()

    command = [
        executable,
        "-c",
        f"safe.directory={root.resolve().as_posix()}",
        "-c",
        "core.quotePath=false",
        "-C",
        str(root.resolve()),
        "log",
        "--no-renames",
        "--name-only",
        f"-n{limit}",
        "--format=%x1e%H%x1f%h%x1f%cs%x1f%s",
        "--",
        ".",
        *exclusion_pathspecs,
    ]
    try:
        # Git is resolved with shutil.which and invoked with fixed read-only arguments.
        output = _run_git_bounded(command, max_bytes=MAX_LOG_BYTES, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return []
    if output is None:
        return []
    commits = parse_git_log(output.decode("utf-8", errors="replace"))
    hunks = _collect_git_diffs(
        root,
        executable,
        commits[:MAX_SYMBOL_COMMITS],
        safe_symbol_paths,
        exclusion_pathspecs,
    )
    return [
        CommitRecord(
            sha=commit.sha,
            short=commit.short,
            date=commit.date,
            subject=commit.subject,
            paths=commit.paths,
            hunks=hunks.get(commit.sha, ()),
        )
        for commit in commits
    ]


def _collect_git_diffs(
    root: Path,
    executable: str,
    commits: list[CommitRecord],
    symbol_paths: frozenset[str],
    exclusion_pathspecs: tuple[str, ...],
) -> dict[str, tuple[DiffHunk, ...]]:
    shas = [commit.sha for commit in commits if FULL_SHA.fullmatch(commit.sha)]
    if not shas or not symbol_paths:
        return {}
    literal_paths = _literal_pathspecs(symbol_paths)
    if literal_paths is None:
        return {}
    command = [
        executable,
        "-c",
        f"safe.directory={root.resolve().as_posix()}",
        "-c",
        "core.quotePath=false",
        "-C",
        str(root.resolve()),
        "show",
        "--format=%x00%H",
        "--no-ext-diff",
        "--no-textconv",
        "--no-renames",
        "--no-color",
        "--unified=0",
        *shas,
        "--",
        *literal_paths,
        *exclusion_pathspecs,
    ]
    try:
        output = _run_git_bounded(command, max_bytes=MAX_DIFF_BYTES, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return {}
    if output is None:
        return {}
    parsed = parse_git_diffs(output.decode("utf-8", errors="replace"))
    return _aligned_git_diffs(root, executable, parsed, symbol_paths)


def _aligned_git_diffs(
    root: Path,
    executable: str,
    parsed: dict[str, tuple[DiffHunk, ...]],
    symbol_paths: frozenset[str],
) -> dict[str, tuple[DiffHunk, ...]]:
    pairs = {
        (sha, hunk.path)
        for sha, hunks in parsed.items()
        for hunk in hunks
        if hunk.path in symbol_paths
    }
    if len(pairs) > MAX_DIFF_FILES:
        return {}
    aligned: dict[str, list[DiffHunk]] = {}
    for sha, path in sorted(pairs):
        if not _matches_commit_blob(root, executable, sha, path):
            continue
        aligned.setdefault(sha, []).extend(
            hunk for hunk in parsed[sha] if hunk.path == path
        )
    return {sha: tuple(hunks) for sha, hunks in aligned.items()}


def _matches_commit_blob(root: Path, executable: str, sha: str, relative: str) -> bool:
    if FULL_SHA.fullmatch(sha) is None:
        return False
    safe_relative = _safe_git_path(relative)
    if safe_relative is None:
        return False
    current = root.joinpath(*PurePosixPath(safe_relative).parts)
    current_bytes = read_bounded_regular_file(current, MAX_SYMBOL_SOURCE_BYTES)
    if current_bytes is None:
        return False
    command = [
        executable,
        "-c",
        f"safe.directory={root.resolve().as_posix()}",
        "-C",
        str(root.resolve()),
        "cat-file",
        "blob",
        f"{sha}:{relative}",
    ]
    try:
        output = _run_git_bounded(
            command,
            max_bytes=MAX_SYMBOL_SOURCE_BYTES,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    if output is None:
        return False
    return _normalized_lines(current_bytes) == _normalized_lines(output)


def _normalized_lines(value: bytes) -> bytes:
    return value.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def parse_git_diffs(output: str) -> dict[str, tuple[DiffHunk, ...]]:
    """Parse bounded patches, retaining zero-count ranges as deletion uncertainty."""

    if len(output.encode("utf-8")) > MAX_DIFF_BYTES:
        return {}
    parsed: dict[str, list[DiffHunk]] = {}
    parsed_paths: set[str] = set()
    total = 0
    for block in output.split("\x00"):
        lines = block.splitlines()
        if not lines:
            continue
        sha = lines[0].strip()
        if FULL_SHA.fullmatch(sha) is None:
            continue
        current_path: str | None = None
        commit_hunks = parsed.setdefault(sha, [])
        for line in lines[1:]:
            if line.startswith("+++ "):
                current_path = _patch_path(line[4:])
                if current_path is not None:
                    parsed_paths.add(current_path)
                    if len(parsed_paths) > MAX_DIFF_FILES:
                        return {}
                continue
            match = HUNK_HEADER.match(line)
            if match is None or current_path is None:
                continue
            start = int(match.group(1))
            count = int(match.group(2) or "1")
            if (
                start < 0
                or count < 0
                or (start == 0 and count > 0)
                or start > MAX_DIFF_LINE
                or count > MAX_DIFF_LINE
            ):
                continue
            total += 1
            if total > MAX_DIFF_HUNKS:
                return {}
            commit_hunks.append(DiffHunk(current_path, start, count))
    return {
        sha: tuple(sorted(set(hunks), key=lambda item: (item.path, item.start, item.count)))
        for sha, hunks in parsed.items()
    }


def _patch_path(value: str) -> str | None:
    candidate = value.strip()
    if candidate == "/dev/null" or candidate.startswith('"'):
        return None
    candidate = candidate.removeprefix("b/").replace("\\", "/")
    return _safe_git_path(candidate)


def parse_git_log(output: str) -> list[CommitRecord]:
    if len(output.encode("utf-8")) > MAX_LOG_BYTES:
        return []
    commits: list[CommitRecord] = []
    total_paths = 0
    for block in output.split("\x1e"):
        block = block.strip()
        if not block:
            continue
        header, *path_lines = block.splitlines()
        fields = header.split("\x1f", maxsplit=3)
        if len(fields) != 4:
            continue
        sha, short, date, subject = fields
        paths_set: set[str] = set()
        for line in path_lines:
            if not line.strip() or "\x00" in line:
                continue
            path = _safe_git_path(line.strip().replace("\\", "/"))
            if path is None:
                return []
            paths_set.add(path)
        total_paths += len(paths_set)
        if total_paths > MAX_LOG_PATHS:
            return []
        paths = tuple(sorted(paths_set))
        commits.append(
            CommitRecord(
                sha=sha,
                short=short,
                date=date,
                subject=str(redact(subject.strip())),
                paths=paths,
            )
        )
    return commits


def _run_git_bounded(
    command: list[str],
    *,
    max_bytes: int,
    timeout: float,
) -> bytes | None:
    """Run fixed Git arguments while bounding stdout during collection."""

    try:
        result = run_bounded_process(
            command,
            max_stdout_bytes=max_bytes,
            timeout=timeout,
        )
    except ProcessCollectionError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout


def _safe_git_path(value: str) -> str | None:
    if value != value.strip():
        return None
    candidate = value.replace("\\", "/")
    pure = PurePosixPath(candidate)
    if (
        not candidate
        or candidate.startswith('"')
        or pure.is_absolute()
        or ".." in pure.parts
        or any(part in {"", "."} for part in pure.parts)
        or any(ord(character) < 32 for character in candidate)
        or len(candidate.encode("utf-8")) > MAX_GIT_PATH_BYTES
    ):
        return None
    return pure.as_posix()


def _literal_pathspecs(paths: Iterable[str]) -> tuple[str, ...] | None:
    values: list[str] = []
    for path in sorted(set(paths)):
        safe = _safe_git_path(path)
        if safe is None:
            return None
        values.append(f":(top,literal){safe}")
    if len(values) > MAX_DIFF_FILES:
        return None
    if sum(len(value.encode("utf-8")) + 1 for value in values) > MAX_GIT_ARGUMENT_BYTES:
        return None
    return tuple(values)


def _normalized_excludes(values: Iterable[str]) -> tuple[tuple[str, ...], ...] | None:
    patterns: set[tuple[str, ...]] = set()
    for value in values:
        safe = _safe_git_path(value.strip().strip("/"))
        if safe is None:
            return None
        patterns.add(tuple(PurePosixPath(safe).parts))
    return tuple(sorted(patterns, key=lambda item: tuple(part.casefold() for part in item)))


def _git_exclusion_pathspecs(
    exclusions: tuple[tuple[str, ...], ...],
) -> tuple[str, ...] | None:
    values: list[str] = []
    for parts in exclusions:
        joined = "/".join(parts)
        if len(parts) == 1:
            escaped = _escape_git_glob(parts[0])
            values.extend(
                (
                    f":(top,literal,icase,exclude){joined}",
                    f":(top,glob,icase,exclude)**/{escaped}",
                    f":(top,glob,icase,exclude)**/{escaped}/**",
                )
            )
        else:
            values.append(f":(top,literal,icase,exclude){joined}")
    unique = tuple(sorted(set(values)))
    if sum(len(value.encode("utf-8")) + 1 for value in unique) > MAX_GIT_ARGUMENT_BYTES:
        return None
    return unique


def _escape_git_glob(value: str) -> str:
    return "".join(f"\\{character}" if character in "*?[\\" else character for character in value)


def _is_excluded(relative: str, exclusions: tuple[tuple[str, ...], ...]) -> bool:
    safe = _safe_git_path(relative)
    if safe is None:
        return True
    parts = tuple(part.casefold() for part in PurePosixPath(safe).parts)
    for exclusion in exclusions:
        pattern = tuple(part.casefold() for part in exclusion)
        if len(pattern) == 1 and pattern[0] in parts:
            return True
        if len(pattern) > 1 and parts[: len(pattern)] == pattern:
            return True
    return False
