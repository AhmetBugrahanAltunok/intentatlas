from __future__ import annotations

import re
import shutil
import subprocess  # nosec B404
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from .security import redact

MAX_DIFF_BYTES = 10_000_000
MAX_DIFF_FILES = 1_000
MAX_DIFF_HUNKS = 50_000
MAX_DIFF_LINE = 1_000_000_000
MAX_SYMBOL_SOURCE_BYTES = 1_000_000
MAX_SYMBOL_COMMITS = 25
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
    except (OSError, subprocess.SubprocessError):
        return None
    value = result.stdout.strip()
    return value if result.returncode == 0 and FULL_SHA.fullmatch(value) else None


def git_paths_match_head(root: Path, paths: tuple[str, ...]) -> bool | None:
    """Return whether every mapped artifact is tracked and byte-equivalent to HEAD."""

    if not paths:
        return True
    if not (root / ".git").exists():
        return None
    executable = shutil.which("git")
    if executable is None:
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
            [*prefix, "ls-files", "--error-unmatch", "--", *paths],
            check=False,
            capture_output=True,
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
                *paths,
            ],
            check=False,
            capture_output=True,
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
) -> list[CommitRecord]:
    """Read bounded commit metadata without executing repository-controlled code."""

    if limit <= 0 or not (root / ".git").exists():
        return []
    executable = shutil.which("git")
    if executable is None:
        return []

    command = [
        executable,
        "-c",
        f"safe.directory={root.resolve().as_posix()}",
        "-C",
        str(root.resolve()),
        "log",
        "--no-renames",
        "--name-only",
        f"-n{limit}",
        "--format=%x1e%H%x1f%h%x1f%cs%x1f%s",
    ]
    try:
        # Git is resolved with shutil.which and invoked with fixed read-only arguments.
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
    except (OSError, subprocess.SubprocessError):
        return []
    if result.returncode != 0:
        return []
    commits = parse_git_log(result.stdout)
    hunks = _collect_git_diffs(
        root,
        executable,
        commits[:MAX_SYMBOL_COMMITS],
        frozenset(symbol_paths),
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
) -> dict[str, tuple[DiffHunk, ...]]:
    shas = [commit.sha for commit in commits if FULL_SHA.fullmatch(commit.sha)]
    if not shas or not symbol_paths:
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
    except (OSError, subprocess.SubprocessError):
        return {}
    if result.returncode != 0:
        return {}
    parsed = parse_git_diffs(result.stdout)
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
    current = root.joinpath(*PurePosixPath(relative).parts)
    try:
        if current.is_symlink() or not current.is_file():
            return False
        if current.stat().st_size > MAX_SYMBOL_SOURCE_BYTES:
            return False
        current_bytes = current.read_bytes()
    except OSError:
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
        result = subprocess.run(  # noqa: S603  # nosec B603
            command,
            check=False,
            capture_output=True,
            timeout=5,
            shell=False,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    if result.returncode != 0 or len(result.stdout) > MAX_SYMBOL_SOURCE_BYTES:
        return False
    return _normalized_lines(current_bytes) == _normalized_lines(result.stdout)


def _normalized_lines(value: bytes) -> bytes:
    return value.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def parse_git_diffs(output: str) -> dict[str, tuple[DiffHunk, ...]]:
    """Parse bounded zero-context patches into current-side line ranges."""

    if len(output.encode("utf-8")) > MAX_DIFF_BYTES:
        return {}
    parsed: dict[str, list[DiffHunk]] = {}
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
                continue
            match = HUNK_HEADER.match(line)
            if match is None or current_path is None:
                continue
            start = int(match.group(1))
            count = int(match.group(2) or "1")
            if (
                start < 1
                or count <= 0
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
    pure = PurePosixPath(candidate)
    if (
        not candidate
        or pure.is_absolute()
        or ".." in pure.parts
        or any(ord(character) < 32 for character in candidate)
    ):
        return None
    return pure.as_posix()


def parse_git_log(output: str) -> list[CommitRecord]:
    commits: list[CommitRecord] = []
    for block in output.split("\x1e"):
        block = block.strip()
        if not block:
            continue
        header, *path_lines = block.splitlines()
        fields = header.split("\x1f", maxsplit=3)
        if len(fields) != 4:
            continue
        sha, short, date, subject = fields
        paths = tuple(
            sorted(
                {
                    line.strip().replace("\\", "/")
                    for line in path_lines
                    if line.strip() and "\x00" not in line
                }
            )
        )
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
