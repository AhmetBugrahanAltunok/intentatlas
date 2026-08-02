from __future__ import annotations

import hashlib
import io
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from intentatlas import cli, onboarding
from intentatlas.acquisition import AcquisitionLimits, ManagedRepositoryCache
from intentatlas.onboarding import TerminalIO, run_guide


class TTYBuffer(io.StringIO):
    def isatty(self) -> bool:
        return True


class LocalTransport:
    def __init__(self) -> None:
        self.calls = 0

    def clone(self, url: str, destination: Path, limits: AcquisitionLimits) -> None:
        self.calls += 1
        destination.mkdir(parents=True)
        git(destination, "init", "-q")
        git(destination, "config", "user.email", "source-test@example.invalid")
        git(destination, "config", "user.name", "Source Test")
        (destination / "app.py").write_text("def run():\n    return 1\n", encoding="utf-8")
        (destination / "test_app.py").write_text(
            "from app import run\n\ndef test_run():\n    assert run() == 1\n",
            encoding="utf-8",
        )
        git(destination, "add", "app.py", "test_app.py")
        git(destination, "commit", "-qm", "baseline")
        git(destination, "remote", "add", "origin", url)


def git(root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def snapshot(root: Path) -> tuple[str, ...]:
    values: list[str] = []
    for current, directories, files in os.walk(root):
        directories[:] = sorted(name for name in directories if name != ".git")
        for name in sorted(files):
            path = Path(current) / name
            data = path.read_bytes()
            values.append(
                f"{path.relative_to(root).as_posix()}|{path.stat().st_mtime_ns}|"
                f"{hashlib.sha256(data).hexdigest()}"
            )
    return tuple(values)


def test_public_url_one_approval_reaches_ready_atlas_and_cache_hit_is_no_write(
    tmp_path: Path,
) -> None:
    transport = LocalTransport()
    cache = ManagedRepositoryCache(tmp_path / "cache", transport=transport)
    url = "https://github.com/owner/repo"
    entry = cache.acquire(url)
    before = snapshot(entry.repository_root)
    before_git = (
        git(entry.repository_root, "rev-parse", "HEAD"),
        git(entry.repository_root, "status", "--porcelain=v1"),
    )
    output = TTYBuffer()
    terminal = TerminalIO(TTYBuffer("\n\n"), output)

    assert run_guide(url, language="en", terminal=terminal, cache=cache) == 0

    transcript = output.getvalue()
    assert transcript.count("Approve bounded HTTPS acquisition") == 1
    assert "Managed cache: hit" in transcript
    assert f"exact revision {entry.revision}" in transcript
    assert "Recommended scope: commit" in transcript
    assert "Atlas ready:" in transcript
    assert "Layers: requirements 0; decisions 0; issues 0" in transcript
    assert "missing requirements, decisions, issues" in transcript
    assert "Tests executed: 0" in transcript
    assert transport.calls == 1
    assert snapshot(entry.repository_root) == before
    assert (
        git(entry.repository_root, "rev-parse", "HEAD"),
        git(entry.repository_root, "status", "--porcelain=v1"),
    ) == before_git


def test_remote_terminal_and_viewer_reuse_one_immutable_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cache = ManagedRepositoryCache(tmp_path / "cache", transport=LocalTransport())
    calls = 0
    served: dict[str, object] = {}
    original = onboarding.collect_change_report_context

    def collect(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
        nonlocal calls
        calls += 1
        return original(*args, **kwargs)

    def serve(_path, **kwargs):  # noqa: ANN001, ANN003, ANN202
        served.update(kwargs)

    monkeypatch.setattr(onboarding, "collect_change_report_context", collect)
    monkeypatch.setattr(onboarding, "serve_graph", serve)
    terminal = TerminalIO(TTYBuffer("\n4\n\n"), TTYBuffer())
    assert run_guide(
        "https://github.com/owner/repo", terminal=terminal, cache=cache
    ) == 0
    assert calls == 1
    assert json.loads(served["graph_document"])["schema_version"] == 4
    assert json.loads(served["change_report_document"])["schema_version"] == 1


def test_direct_url_shorthand_requires_real_tty_and_non_tty_never_calls_guide(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    observed: list[str] = []
    monkeypatch.setattr(sys, "stdin", TTYBuffer(""))
    monkeypatch.setattr(sys, "stdout", TTYBuffer())
    monkeypatch.setattr(cli, "run_guide", lambda source: observed.append(source) or 17)
    url = "https://github.com/owner/repo"
    assert cli.main([url]) == 17
    assert observed == [url]

    monkeypatch.undo()
    called = False

    def forbidden(_source: str) -> int:
        nonlocal called
        called = True
        return 1

    monkeypatch.setattr(cli, "run_guide", forbidden)
    with pytest.raises(SystemExit) as error:
        cli.main([url])
    assert error.value.code == 2
    assert called is False
    assert "invalid choice" in capsys.readouterr().err


def test_cache_cli_is_deterministic_offline_and_clears_only_exact_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    cache = ManagedRepositoryCache(tmp_path / "cache", transport=LocalTransport())
    entry = cache.acquire("https://github.com/owner/repo")
    monkeypatch.setattr(cli, "ManagedRepositoryCache", lambda: cache)

    assert cli.main(["cache", "list", "--format", "json"]) == 0
    listed = json.loads(capsys.readouterr().out)
    assert [item["cache_id"] for item in listed["entries"]] == [entry.cache_id]
    assert cli.main(["cache", "info", entry.cache_id, "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["revision"] == entry.revision
    assert cli.main(["cache", "info", "../escape"]) == 2
    assert "invalid managed cache identity" in capsys.readouterr().err
    assert cli.main(["cache", "clear", entry.cache_id]) == 0
    assert "Cleared managed cache entry" in capsys.readouterr().out
    assert cache.list() == ()
