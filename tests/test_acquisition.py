from __future__ import annotations

import json
import os
import shutil
import subprocess
import threading
import time
from datetime import UTC, datetime
from pathlib import Path

import pytest

from intentatlas import acquisition
from intentatlas.acquisition import (
    AcquisitionLimits,
    GitTransport,
    ManagedRepositoryCache,
    _safe_git_command,
    _safe_git_environment,
    cache_identity,
    is_github_url,
    normalize_github_url,
    render_cache_entry,
)

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="Git is required")


class LocalTransport:
    def __init__(self, *, delay: float = 0, fail: bool = False) -> None:
        self.calls = 0
        self.delay = delay
        self.fail = fail
        self.lock = threading.Lock()

    def clone(self, url: str, destination: Path, limits: AcquisitionLimits) -> None:
        with self.lock:
            self.calls += 1
        if self.delay:
            time.sleep(self.delay)
        if self.fail:
            raise ValueError("injected acquisition failure")
        destination.mkdir(parents=True)
        git(destination, "init", "-q")
        git(destination, "config", "user.email", "cache-test@example.invalid")
        git(destination, "config", "user.name", "Cache Test")
        (destination / "app.py").write_text("def run():\n    return 1\n", encoding="utf-8")
        (destination / "test_app.py").write_text(
            "from app import run\n\ndef test_run():\n    assert run() == 1\n",
            encoding="utf-8",
        )
        git(destination, "add", "app.py", "test_app.py")
        git(destination, "commit", "-qm", "baseline")
        git(destination, "remote", "add", "origin", url)


class InterruptingTransport:
    def clone(self, url: str, destination: Path, limits: AcquisitionLimits) -> None:
        destination.mkdir(parents=True)
        raise KeyboardInterrupt


class HangingProcess:
    def __init__(self, command, **kwargs) -> None:  # noqa: ANN001, ANN003
        self.pid = 123
        self.returncode: int | None = None
        output = kwargs["stdout"]
        if "emit-output" in command:
            output.write(b"too much")

    def poll(self) -> int | None:
        return self.returncode

    def kill(self) -> None:
        self.returncode = -9

    def wait(self, timeout: int | None = None) -> int:
        self.returncode = -9
        return -9


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


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("https://github.com/owner/repo", "https://github.com/owner/repo"),
        ("https://github.com/owner/repo.git", "https://github.com/owner/repo"),
        ("  https://GITHUB.com/Owner/Repo.git  ", "https://github.com/Owner/Repo"),
    ],
)
def test_strict_github_url_normalization(value: str, expected: str) -> None:
    assert normalize_github_url(value) == expected
    assert cache_identity(value) == cache_identity(expected)


@pytest.mark.parametrize(
    "value",
    [
        "http://github.com/owner/repo",
        "ssh://git@github.com/owner/repo",
        "git://github.com/owner/repo",
        "file:///tmp/repo",
        "git@github.com:owner/repo.git",
        "https://gitlab.com/owner/repo",
        "https://127.0.0.1/owner/repo",
        "https://localhost/owner/repo",
        "https://github.com:443/owner/repo",
        "https://user@github.com/owner/repo",
        "https://user:token@github.com/owner/repo",
        "https://github.com/owner/repo?token=secret",
        "https://github.com/owner/repo#readme",
        "https://github.com/owner/repo/tree/main",
        "https://github.com/owner/repo/issues",
        "https://github.com/owner",
        "https://github.com/-owner/repo",
        "https://github.com/owner/..",
    ],
)
def test_strict_github_url_rejection(value: str) -> None:
    with pytest.raises(ValueError):
        normalize_github_url(value)


def test_url_detection_keeps_quoted_windows_paths_local() -> None:
    assert is_github_url("https://github.com/owner/repo") is True
    assert is_github_url("file:///tmp/repo") is True
    assert is_github_url(r'"C:\Projects\repo"') is False
    assert is_github_url("relative/repo") is False


def test_cache_create_hit_refresh_list_info_and_clear(tmp_path: Path) -> None:
    transport = LocalTransport()

    def clock() -> datetime:
        return datetime(2026, 8, 3, 12, 0, tzinfo=UTC)

    cache = ManagedRepositoryCache(tmp_path / "cache", transport=transport, clock=clock)
    url = "https://github.com/owner/repo"

    created = cache.acquire(url)
    assert created.cache_state == "created"
    assert created.url == url
    assert len(created.revision) == 40
    assert created.history_commit_count == 1
    assert created.acquired_at == "2026-08-03T12:00:00Z"
    assert transport.calls == 1

    hit = cache.acquire(url)
    assert hit.cache_state == "hit"
    assert hit.revision == created.revision
    assert transport.calls == 1

    refreshed = cache.acquire(url, refresh=True)
    assert refreshed.cache_state == "refreshed"
    assert transport.calls == 2
    assert [entry.cache_id for entry in cache.list()] == [created.cache_id]
    assert cache.info(created.cache_id).revision == refreshed.revision
    assert '"history_is_bounded": true' in render_cache_entry(hit, "json")
    assert "shallow bound 50" in render_cache_entry(hit)

    cache.clear(created.cache_id)
    assert cache.list() == ()
    with pytest.raises(ValueError, match="does not exist"):
        cache.clear(created.cache_id)


def test_corruption_recovers_atomically_and_failure_preserves_prior_good_entry(
    tmp_path: Path,
) -> None:
    root = tmp_path / "cache"
    transport = LocalTransport()
    cache = ManagedRepositoryCache(root, transport=transport)
    entry = cache.acquire("https://github.com/owner/repo")
    metadata = root / entry.cache_id / "metadata.json"
    metadata.write_text("{}", encoding="utf-8")

    recovered = cache.acquire(entry.url)
    assert recovered.cache_state == "created"
    assert transport.calls == 2
    before = metadata.read_bytes()

    failing = ManagedRepositoryCache(root, transport=LocalTransport(fail=True))
    with pytest.raises(ValueError, match="injected acquisition failure"):
        failing.acquire(entry.url, refresh=True)
    assert metadata.read_bytes() == before
    assert failing.info(entry.cache_id).revision == recovered.revision
    assert not tuple(root.glob(".*.staging-*"))


def test_same_repository_concurrency_uses_one_atomic_acquisition(tmp_path: Path) -> None:
    root = tmp_path / "cache"
    root.mkdir()
    transport = LocalTransport(delay=0.2)
    cache = ManagedRepositoryCache(root, transport=transport)
    entries: list[str] = []
    failures: list[BaseException] = []

    def acquire() -> None:
        try:
            entries.append(cache.acquire("https://github.com/owner/repo").revision)
        except BaseException as exc:  # pragma: no cover - diagnostic path
            failures.append(exc)

    threads = [threading.Thread(target=acquire) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)
    assert failures == []
    assert len(entries) == 2 and len(set(entries)) == 1
    assert transport.calls == 1


def test_cache_identity_and_cleanup_reject_traversal_and_links(tmp_path: Path) -> None:
    cache = ManagedRepositoryCache(tmp_path / "cache", transport=LocalTransport())
    entry = cache.acquire("https://github.com/owner/repo")
    for invalid in ("../escape", "repo", entry.cache_id + "/child"):
        with pytest.raises(ValueError, match="invalid managed cache identity"):
            cache.info(invalid)

    link = tmp_path / "linked-cache"
    target = tmp_path / "target"
    target.mkdir()
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError:
        pytest.skip("directory links are unavailable")
    unsafe = ManagedRepositoryCache(link, transport=LocalTransport())
    with pytest.raises(ValueError, match="link|canonical"):
        unsafe.list()


def test_safe_git_contract_disables_external_execution_and_auth(tmp_path: Path) -> None:
    command = _safe_git_command("git", tmp_path, "status")
    rendered = " ".join(command)
    for contract in (
        "credential.helper=",
        "core.askPass=",
        "core.hooksPath=",
        "core.attributesFile=",
        "filter.lfs.smudge=",
        "submodule.recurse=false",
        "protocol.file.allow=never",
        "protocol.ext.allow=never",
        "http.followRedirects=false",
    ):
        assert contract in rendered
    environment = _safe_git_environment()
    assert environment["GIT_TERMINAL_PROMPT"] == "0"
    assert environment["GCM_INTERACTIVE"] == "Never"
    assert environment["GIT_LFS_SKIP_SMUDGE"] == "1"
    assert "SSH_AUTH_SOCK" not in environment


def test_metadata_contains_no_source_or_environment_content(tmp_path: Path) -> None:
    cache = ManagedRepositoryCache(tmp_path / "cache", transport=LocalTransport())
    entry = cache.acquire("https://github.com/owner/repo")
    metadata_path = tmp_path / "cache" / entry.cache_id / "metadata.json"
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert set(payload) == {
        "acquired_at",
        "cache_id",
        "checkout_bytes",
        "checkout_file_count",
        "history_commit_count",
        "history_depth",
        "revision",
        "schema_version",
        "url",
    }
    serialized = json.dumps(payload)
    assert "def run" not in serialized
    for key in os.environ:
        assert key not in payload


def test_interrupted_acquisition_removes_staging_and_lock(tmp_path: Path) -> None:
    root = tmp_path / "cache"
    cache = ManagedRepositoryCache(root, transport=InterruptingTransport())
    with pytest.raises(KeyboardInterrupt):
        cache.acquire("https://github.com/owner/repo")
    assert not tuple(root.iterdir())


@pytest.mark.parametrize(
    ("argument", "limits", "message", "monitor"),
    [
        (
            "emit-output",
            AcquisitionLimits(max_git_output_bytes=1),
            "output exceeded",
            False,
        ),
        ("wait", AcquisitionLimits(timeout_seconds=0), "0-second", False),
        ("wait", AcquisitionLimits(max_cache_bytes=0), "disk limit", True),
    ],
)
def test_git_transport_enforces_output_time_and_disk_bounds(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    argument: str,
    limits: AcquisitionLimits,
    message: str,
    monitor: bool,
) -> None:
    monkeypatch.setattr(acquisition.subprocess, "Popen", HangingProcess)
    monitored = tmp_path if monitor else None
    if monitor:
        (tmp_path / "existing").write_text("x", encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        GitTransport("git")._run(
            tmp_path,
            limits,
            argument,
            monitor_root=monitored,
        )
