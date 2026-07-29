from __future__ import annotations

import shutil
import subprocess  # nosec B404
from dataclasses import dataclass
from pathlib import Path

from .security import redact


@dataclass(frozen=True, slots=True)
class CommitRecord:
    sha: str
    short: str
    date: str
    subject: str
    paths: tuple[str, ...]


def collect_git_history(root: Path, limit: int = 25) -> list[CommitRecord]:
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
    return parse_git_log(result.stdout)


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
