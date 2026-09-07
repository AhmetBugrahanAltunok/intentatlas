from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import subprocess  # nosec B404
import sys
import tempfile
import time
import uuid
from collections.abc import Callable
from contextlib import suppress
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol, cast
from urllib.parse import urlsplit, urlunsplit

from .bounded_process import (
    ProcessCollectionError,
    ProcessOutputLimitError,
    contain_process_tree,
    contained_process_creation_flags,
    run_bounded_process,
    terminate_process_tree,
)

CACHE_SCHEMA_VERSION = 1
GITHUB_HOST = "github.com"
FULL_REVISION = re.compile(r"[0-9a-f]{40}")
CACHE_ID = re.compile(r"[a-z0-9][a-z0-9-]{0,79}-[0-9a-f]{16}")
OWNER = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?")
REPOSITORY = re.compile(r"[A-Za-z0-9_.-]{1,100}")
MAX_METADATA_BYTES = 32_768
GIT_METADATA_TIMEOUT_SECONDS = 15
LOCK_SCHEMA_VERSION = 1
MAX_LOCK_METADATA_BYTES = 4_096
LOCK_TOKEN = re.compile(r"[0-9a-f]{32}")
_RMTREE_ERROR_CALLBACK = "onexc" if sys.version_info >= (3, 12) else "onerror"


@dataclass(frozen=True, slots=True)
class AcquisitionLimits:
    history_depth: int = 50
    timeout_seconds: int = 120
    lock_timeout_seconds: int = 30
    max_git_output_bytes: int = 1_000_000
    max_checkout_files: int = 20_000
    max_checkout_bytes: int = 256 * 1024 * 1024
    max_cache_bytes: int = 512 * 1024 * 1024


DEFAULT_LIMITS = AcquisitionLimits()


@dataclass(frozen=True, slots=True)
class CacheEntry:
    cache_id: str
    url: str
    revision: str
    repository_root: Path
    acquired_at: str
    history_depth: int
    history_commit_count: int
    checkout_file_count: int
    checkout_bytes: int
    cache_state: str

    def public_dict(self) -> dict[str, object]:
        return {
            "schema_version": CACHE_SCHEMA_VERSION,
            "cache_id": self.cache_id,
            "url": self.url,
            "revision": self.revision,
            "acquired_at": self.acquired_at,
            "history_depth": self.history_depth,
            "history_commit_count": self.history_commit_count,
            "history_is_bounded": True,
            "checkout_file_count": self.checkout_file_count,
            "checkout_bytes": self.checkout_bytes,
            "cache_state": self.cache_state,
        }


class AcquisitionTransport(Protocol):
    def clone(self, url: str, destination: Path, limits: AcquisitionLimits) -> None: ...


class GitTransport:
    """Acquire an inert shallow checkout without inheriting Git execution/auth behavior."""

    def __init__(self, executable: str | None = None) -> None:
        self.executable = executable or shutil.which("git") or ""

    def clone(self, url: str, destination: Path, limits: AcquisitionLimits) -> None:
        if not self.executable:
            raise ValueError("Git is required to acquire a public repository")
        destination.parent.mkdir(parents=True, exist_ok=True)
        self._run(
            destination.parent,
            limits,
            "clone",
            "--quiet",
            "--depth",
            str(limits.history_depth),
            "--no-tags",
            "--no-recurse-submodules",
            "--no-checkout",
            "--config",
            f"core.hooksPath={os.devnull}",
            "--config",
            "credential.helper=",
            "--config",
            "filter.lfs.smudge=",
            "--config",
            "filter.lfs.required=false",
            "--config",
            "submodule.recurse=false",
            url,
            str(destination),
            monitor_root=destination.parent,
        )
        git_dir = destination / ".git"
        if not git_dir.is_dir() or git_dir.is_symlink():
            raise ValueError("acquired repository has an unsafe Git directory")
        self._run(destination, limits, "sparse-checkout", "init", "--no-cone")
        sparse_file = git_dir / "info" / "sparse-checkout"
        sparse_file.parent.mkdir(parents=True, exist_ok=True)
        sparse_file.write_text("/*\n!/atlas/Private/\n", encoding="utf-8", newline="\n")
        self._run(destination, limits, "checkout", "--quiet", "--detach", "--force", "HEAD")

    def _run(
        self,
        cwd: Path,
        limits: AcquisitionLimits,
        *arguments: str,
        monitor_root: Path | None = None,
    ) -> None:
        command = _safe_git_command(self.executable, cwd, *arguments)
        environment = _safe_git_environment()
        creation_flags = contained_process_creation_flags()
        with tempfile.TemporaryFile() as output:
            try:
                process = subprocess.Popen(  # noqa: S603  # nosec B603
                    command,
                    cwd=cwd,
                    env=environment,
                    stdin=subprocess.DEVNULL,
                    stdout=output,
                    stderr=output,
                    shell=False,
                    creationflags=creation_flags,
                    start_new_session=os.name != "nt",
                )
            except OSError as exc:
                raise ValueError("cannot start bounded Git acquisition") from exc
            try:
                process_container = contain_process_tree(
                    process, resume=os.name == "nt"
                )
            except OSError as exc:
                terminate_process_tree(process, None)
                raise ValueError("cannot contain bounded Git acquisition") from exc
            deadline = time.monotonic() + limits.timeout_seconds
            try:
                while process.poll() is None:
                    if time.monotonic() >= deadline:
                        terminate_process_tree(process, process_container)
                        raise ValueError(
                            f"Git acquisition exceeded the {limits.timeout_seconds}-second limit"
                        )
                    if output.tell() > limits.max_git_output_bytes:
                        terminate_process_tree(process, process_container)
                        raise ValueError("Git acquisition output exceeded its bounded limit")
                    if (
                        monitor_root is not None
                        and _tree_size(monitor_root) > limits.max_cache_bytes
                    ):
                        terminate_process_tree(process, process_container)
                        raise ValueError(
                            f"Git acquisition exceeded the {limits.max_cache_bytes}-byte disk limit"
                        )
                    time.sleep(0.05)
            except BaseException:
                terminate_process_tree(process, process_container)
                raise
            if output.tell() > limits.max_git_output_bytes:
                process_container.close()
                raise ValueError("Git acquisition output exceeded its bounded limit")
            if (
                monitor_root is not None
                and _tree_size(monitor_root) > limits.max_cache_bytes
            ):
                process_container.close()
                raise ValueError(
                    f"Git acquisition exceeded the {limits.max_cache_bytes}-byte disk limit"
                )
            process_container.close()
            if process.returncode != 0:
                raise ValueError(
                    "public GitHub acquisition failed; private/authenticated repositories and "
                    "interactive credentials are unsupported"
                )


class ManagedRepositoryCache:
    def __init__(
        self,
        root: Path | None = None,
        *,
        transport: AcquisitionTransport | None = None,
        limits: AcquisitionLimits = DEFAULT_LIMITS,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.root = (root or default_cache_root()).absolute()
        self.transport = transport or GitTransport()
        self.limits = limits
        self.clock = clock or (lambda: datetime.now(UTC))

    def acquire(self, source: str, *, refresh: bool = False) -> CacheEntry:
        url = normalize_github_url(source)
        cache_id = cache_identity(url)
        self._ensure_root()
        with _CacheLock(
            self.root,
            cache_id,
            self.limits.lock_timeout_seconds,
            stale_after_seconds=_stale_lock_seconds(self.limits),
        ):
            target = self._target(cache_id)
            existing = self._load_entry(target, cache_state="hit")
            if existing is not None and not refresh:
                return existing
            stage = self.root / f".{cache_id}.staging-{uuid.uuid4().hex}"
            backup = self.root / f".{cache_id}.backup-{uuid.uuid4().hex}"
            try:
                stage.mkdir(parents=False)
                repository = stage / "repository"
                self.transport.clone(url, repository, self.limits)
                entry = self._validate_checkout(
                    cache_id,
                    url,
                    repository,
                    cache_state="refreshed" if existing is not None else "created",
                )
                _write_metadata(stage / "metadata.json", entry)
                (stage / ".complete").write_text("1\n", encoding="ascii", newline="\n")
                if target.exists():
                    _reject_link(target, "managed cache entry")
                    target.rename(backup)
                try:
                    stage.rename(target)
                except OSError:
                    if backup.exists() and not target.exists():
                        backup.rename(target)
                    raise
                if backup.exists():
                    _remove_tree(backup)
                loaded = self._load_entry(target, cache_state=entry.cache_state)
                if loaded is None:
                    raise ValueError("completed managed cache entry failed validation")
                return loaded
            except KeyboardInterrupt:
                raise
            except OSError as exc:
                raise ValueError("cannot atomically update the managed repository cache") from exc
            finally:
                if stage.exists():
                    _remove_tree(stage)
                if backup.exists() and target.exists():
                    _remove_tree(backup)

    def list(self) -> tuple[CacheEntry, ...]:
        if not self.root.exists():
            return ()
        self._ensure_root()
        entries: list[CacheEntry] = []
        for candidate in sorted(self.root.iterdir(), key=lambda item: item.name):
            if not CACHE_ID.fullmatch(candidate.name):
                continue
            entry = self._load_entry(candidate, cache_state="cached")
            if entry is not None:
                entries.append(entry)
        return tuple(entries)

    def info(self, cache_id: str) -> CacheEntry:
        target = self._target(cache_id)
        entry = self._load_entry(target, cache_state="cached")
        if entry is None:
            raise ValueError(f"managed cache entry is missing or invalid: {cache_id}")
        return entry

    def clear(self, cache_id: str) -> None:
        self._ensure_root()
        target = self._target(cache_id)
        if not target.exists():
            raise ValueError(f"managed cache entry does not exist: {cache_id}")
        _reject_link(target, "managed cache entry")
        with _CacheLock(
            self.root,
            cache_id,
            self.limits.lock_timeout_seconds,
            stale_after_seconds=_stale_lock_seconds(self.limits),
        ):
            _remove_tree(target)

    def _ensure_root(self) -> None:
        if self.root.exists():
            _reject_link(self.root, "managed cache root")
            if not self.root.is_dir():
                raise ValueError("managed cache root is not a directory")
        else:
            self.root.mkdir(parents=True)
        if self.root.resolve() != self.root:
            raise ValueError("managed cache root crosses a link or canonical boundary")

    def _target(self, cache_id: str) -> Path:
        if not CACHE_ID.fullmatch(cache_id):
            raise ValueError(f"invalid managed cache identity: {cache_id!r}")
        target = self.root / cache_id
        if target.parent != self.root:
            raise ValueError("managed cache target escapes its root")
        return target

    def _load_entry(self, target: Path, *, cache_state: str) -> CacheEntry | None:
        try:
            if not target.is_dir() or target.is_symlink():
                return None
            _reject_link(target, "managed cache entry")
            if not (target / ".complete").is_file():
                return None
            raw = _load_metadata(target / "metadata.json")
            repository = target / "repository"
            entry = _entry_from_metadata(raw, repository, cache_state)
            self._validate_repository_identity(entry)
            return entry
        except (OSError, ValueError):
            return None

    def _validate_checkout(
        self,
        cache_id: str,
        url: str,
        repository: Path,
        *,
        cache_state: str,
    ) -> CacheEntry:
        _reject_link(repository, "acquired repository")
        revision = _git_capture(repository, "rev-parse", "--verify", "HEAD^{commit}").strip()
        if not FULL_REVISION.fullmatch(revision):
            raise ValueError("acquired repository HEAD is not a full commit revision")
        origin = normalize_github_url(
            _git_capture(repository, "remote", "get-url", "origin").strip()
        )
        if origin != url:
            raise ValueError("acquired repository origin differs from the approved URL")
        commit_count_text = _git_capture(repository, "rev-list", "--count", "HEAD").strip()
        if not commit_count_text.isdigit():
            raise ValueError("acquired repository history count is invalid")
        commit_count = int(commit_count_text)
        shallow = _git_capture(repository, "rev-parse", "--is-shallow-repository").strip()
        if commit_count < 1 or shallow not in {"true", "false"}:
            raise ValueError("acquired repository history boundary is invalid")
        if commit_count > self.limits.history_depth and shallow != "true":
            raise ValueError("acquired repository history is not shallow-bounded")
        files, checkout_bytes = _checkout_size(repository, self.limits)
        return CacheEntry(
            cache_id=cache_id,
            url=url,
            revision=revision,
            repository_root=repository,
            acquired_at=self.clock().astimezone(UTC).isoformat().replace("+00:00", "Z"),
            history_depth=self.limits.history_depth,
            history_commit_count=commit_count,
            checkout_file_count=files,
            checkout_bytes=checkout_bytes,
            cache_state=cache_state,
        )

    def _validate_repository_identity(self, entry: CacheEntry) -> None:
        target = self._target(entry.cache_id)
        if entry.repository_root != target / "repository":
            raise ValueError("managed repository path does not match its cache identity")
        _reject_link(entry.repository_root, "managed repository")
        revision = _git_capture(
            entry.repository_root, "rev-parse", "--verify", "HEAD^{commit}"
        ).strip()
        if revision != entry.revision:
            raise ValueError("managed repository revision differs from cache metadata")
        origin = normalize_github_url(
            _git_capture(entry.repository_root, "remote", "get-url", "origin").strip()
        )
        if origin != entry.url or cache_identity(origin) != entry.cache_id:
            raise ValueError("managed repository origin differs from cache metadata")


class _CacheLock:
    def __init__(
        self,
        root: Path,
        cache_id: str,
        timeout_seconds: int,
        *,
        stale_after_seconds: int | None = None,
    ) -> None:
        self.root = root
        self.cache_id = cache_id
        self.path = root / f".{cache_id}.lock"
        self.owner_path = self.path / "owner.json"
        self.timeout_seconds = timeout_seconds
        self.stale_after_seconds = max(
            1,
            stale_after_seconds
            if stale_after_seconds is not None
            else max(60, timeout_seconds * 2),
        )
        self.token = uuid.uuid4().hex

    def __enter__(self) -> _CacheLock:
        deadline = time.monotonic() + self.timeout_seconds
        while True:
            try:
                self.path.mkdir()
                try:
                    self._write_owner()
                except OSError as exc:
                    with suppress(OSError):
                        self.path.rmdir()
                    raise ValueError("cannot create managed cache lock metadata") from exc
                return self
            except FileExistsError:
                try:
                    _reject_link(self.path, "managed cache lock")
                except ValueError:
                    # The owner may have released the exact lock between
                    # mkdir's collision and this validation. Retry that race;
                    # unsafe links and other extant shapes still fail closed.
                    if not self.path.exists():
                        continue
                    raise
                if self._reap_stale():
                    continue
                if time.monotonic() >= deadline:
                    raise ValueError(
                        f"managed cache lock exceeded the {self.timeout_seconds}-second limit"
                    ) from None
                time.sleep(0.05)

    def __exit__(self, _type: object, _value: object, _traceback: object) -> None:
        try:
            owner = _read_lock_owner(self.path)
        except (OSError, ValueError):
            return
        if owner.get("token") != self.token:
            return
        with suppress(FileNotFoundError):
            self.owner_path.unlink()
        with suppress(FileNotFoundError, OSError):
            self.path.rmdir()

    def _write_owner(self) -> None:
        payload = {
            "schema_version": LOCK_SCHEMA_VERSION,
            "pid": os.getpid(),
            "created_unix": time.time(),
            "token": self.token,
        }
        self.owner_path.write_text(
            json.dumps(payload, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    def _reap_stale(self) -> bool:
        try:
            if not self.path.is_dir():
                return False
            entries = tuple(self.path.iterdir())
            if any(entry.name != self.owner_path.name for entry in entries):
                return False
            now = time.time()
            if entries:
                try:
                    owner = _read_lock_owner(self.path)
                    created = owner["created_unix"]
                    if not isinstance(created, (int, float)) or isinstance(created, bool):
                        raise ValueError("managed cache lock creation time is invalid")
                    if created < 0 or created > now + 60:
                        raise ValueError("managed cache lock creation time is invalid")
                    pid = owner["pid"]
                    if not isinstance(pid, int) or isinstance(pid, bool):
                        raise ValueError("managed cache lock owner PID is invalid")
                    if _process_is_alive(pid):
                        return False
                    timestamp = float(created)
                except ValueError:
                    # A crash may interrupt the small owner-metadata write. Only
                    # a lone, old, regular, bounded file is eligible for cleanup.
                    _reject_link(self.owner_path, "managed cache lock owner")
                    details = self.owner_path.stat()
                    if (
                        not stat.S_ISREG(details.st_mode)
                        or details.st_size > MAX_LOCK_METADATA_BYTES
                    ):
                        return False
                    timestamp = details.st_mtime
            else:
                timestamp = self.path.stat().st_mtime
            if now - timestamp <= self.stale_after_seconds:
                return False

            stale = self.root / f".{self.cache_id}.stale-lock-{uuid.uuid4().hex}"
            self.path.rename(stale)
        except (FileNotFoundError, OSError, ValueError):
            return False

        try:
            owner_path = stale / "owner.json"
            with suppress(FileNotFoundError):
                owner_path.unlink()
            stale.rmdir()
        except OSError:
            # The renamed directory is exact-target, contains no nested entries,
            # and can be safely retried or inspected on a later cache operation.
            return True
        return True


def _stale_lock_seconds(limits: AcquisitionLimits) -> int:
    """Keep a live lock longer than every bounded operation it can protect."""

    git_budget = 4 * max(10, limits.timeout_seconds)
    return max(60, git_budget + max(0, limits.lock_timeout_seconds) + 60)


def _process_is_alive(pid: int) -> bool:
    """Return whether a local PID is alive, failing closed on uncertain checks."""

    if pid < 1:
        return False
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        process_query_limited_information = 0x1000
        still_active = 259
        kernel32 = cast(Any, ctypes).WinDLL("kernel32", use_last_error=True)
        open_process = kernel32.OpenProcess
        open_process.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
        open_process.restype = wintypes.HANDLE
        get_exit_code = kernel32.GetExitCodeProcess
        get_exit_code.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD))
        get_exit_code.restype = wintypes.BOOL
        close_handle = kernel32.CloseHandle
        close_handle.argtypes = (wintypes.HANDLE,)
        close_handle.restype = wintypes.BOOL
        handle = open_process(process_query_limited_information, False, pid)
        if not handle:
            error = int(cast(Any, ctypes).get_last_error())
            # Access denied proves that an object with this PID exists. Unknown
            # failures fail closed and keep the lock.
            return error != 87
        exit_code = ctypes.c_ulong()
        try:
            if not get_exit_code(handle, ctypes.byref(exit_code)):
                return True
            return exit_code.value == still_active
        finally:
            close_handle(handle)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except (OSError, PermissionError):
        return True
    return True


def _read_lock_owner(path: Path) -> dict[str, object]:
    owner_path = path / "owner.json"
    _reject_link(owner_path, "managed cache lock owner")
    details = owner_path.stat()
    if not stat.S_ISREG(details.st_mode) or details.st_size > MAX_LOCK_METADATA_BYTES:
        raise ValueError("managed cache lock owner metadata is invalid")
    raw = json.loads(owner_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or set(raw) != {
        "schema_version",
        "pid",
        "created_unix",
        "token",
    }:
        raise ValueError("managed cache lock owner metadata is invalid")
    pid = raw.get("pid")
    token = raw.get("token")
    if (
        raw.get("schema_version") != LOCK_SCHEMA_VERSION
        or not isinstance(pid, int)
        or isinstance(pid, bool)
        or pid < 1
        or not isinstance(token, str)
        or LOCK_TOKEN.fullmatch(token) is None
    ):
        raise ValueError("managed cache lock owner metadata is invalid")
    return raw


def normalize_github_url(value: str) -> str:
    raw = value.strip()
    if len(raw) > 500 or any(ord(character) < 32 for character in raw):
        raise ValueError("GitHub repository URL is invalid")
    try:
        parsed = urlsplit(raw)
    except ValueError as exc:
        raise ValueError("GitHub repository URL is invalid") from exc
    if parsed.scheme.casefold() != "https":
        raise ValueError("only HTTPS public GitHub repository URLs are supported")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("credentials are forbidden in GitHub repository URLs")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("GitHub repository URL has an invalid port") from exc
    if port is not None:
        raise ValueError("custom ports are forbidden in GitHub repository URLs")
    if (parsed.hostname or "").casefold() != GITHUB_HOST:
        raise ValueError("only github.com public repository URLs are supported")
    if parsed.query or parsed.fragment:
        raise ValueError("query strings and fragments are forbidden in repository URLs")
    segments = parsed.path.split("/")
    if len(segments) != 3 or not segments[1] or not segments[2]:
        raise ValueError("URL must identify exactly one GitHub owner and repository")
    owner = segments[1]
    repository = segments[2]
    if repository.casefold().endswith(".git"):
        repository = repository[:-4]
    if not OWNER.fullmatch(owner) or not REPOSITORY.fullmatch(repository):
        raise ValueError("GitHub owner or repository name is invalid")
    if repository in {".", ".."} or repository.endswith("."):
        raise ValueError("GitHub repository name is invalid")
    return urlunsplit(("https", GITHUB_HOST, f"/{owner}/{repository}", "", ""))


def is_github_url(value: str | Path) -> bool:
    rendered = str(value).strip()
    return "://" in rendered or rendered.casefold().startswith(("git@", "ssh:"))


def cache_identity(url: str) -> str:
    normalized = normalize_github_url(url)
    repository = normalized.rsplit("/", maxsplit=1)[-1].casefold()
    slug = re.sub(r"[^a-z0-9]+", "-", repository).strip("-")[:48] or "repository"
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]
    return f"{slug}-{digest}"


def default_cache_root() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return base / "IntentAtlas" / "Cache" / "repositories"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Caches" / "IntentAtlas" / "repositories"
    base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    return base / "intentatlas" / "repositories"


def render_cache_entry(entry: CacheEntry, output_format: str = "text") -> str:
    payload = entry.public_dict()
    if output_format == "json":
        return json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if output_format != "text":
        raise ValueError(f"unknown cache output format: {output_format}")
    return (
        f"Cache ID: {entry.cache_id}\n"
        f"URL: {entry.url}\n"
        f"Revision: {entry.revision}\n"
        f"Cache state: {entry.cache_state}; acquired at {entry.acquired_at}\n"
        f"History: {entry.history_commit_count} commits available; shallow bound "
        f"{entry.history_depth}\n"
        f"Checkout: {entry.checkout_file_count} files; {entry.checkout_bytes} bytes\n"
    )


def _safe_git_command(executable: str, cwd: Path, *arguments: str) -> list[str]:
    return [
        executable,
        "-c",
        "alias.clone=",
        "-c",
        "credential.helper=",
        "-c",
        "core.askPass=",
        "-c",
        f"core.hooksPath={os.devnull}",
        "-c",
        f"core.attributesFile={os.devnull}",
        "-c",
        "filter.lfs.smudge=",
        "-c",
        "filter.lfs.required=false",
        "-c",
        "submodule.recurse=false",
        "-c",
        "protocol.file.allow=never",
        "-c",
        "protocol.ext.allow=never",
        "-c",
        "http.followRedirects=false",
        "-C",
        str(cwd),
        *arguments,
    ]


def _safe_git_environment() -> dict[str, str]:
    allowed = ("SYSTEMROOT", "WINDIR", "COMSPEC", "TMP", "TEMP", "LANG", "LC_ALL")
    environment = {key: os.environ[key] for key in allowed if key in os.environ}
    environment.update(
        {
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_ASKPASS": "",
            "GCM_INTERACTIVE": "Never",
            "GIT_LFS_SKIP_SMUDGE": "1",
            "GIT_OPTIONAL_LOCKS": "0",
        }
    )
    return environment


def _git_capture(root: Path, *arguments: str) -> str:
    executable = shutil.which("git")
    if executable is None:
        raise ValueError("Git is required to inspect the managed repository")
    try:
        result = run_bounded_process(
            _safe_git_command(executable, root, *arguments),
            cwd=root,
            env=_safe_git_environment(),
            max_stdout_bytes=MAX_METADATA_BYTES,
            timeout=GIT_METADATA_TIMEOUT_SECONDS,
        )
    except ProcessOutputLimitError as exc:
        raise ValueError("managed Git repository validation failed") from exc
    except ProcessCollectionError as exc:
        raise ValueError("cannot validate the managed Git repository") from exc
    if result.returncode != 0:
        raise ValueError("managed Git repository validation failed")
    return result.stdout.decode("utf-8", errors="replace")


def _checkout_size(root: Path, limits: AcquisitionLimits) -> tuple[int, int]:
    files = 0
    checkout_bytes = 0
    for current, directories, names in os.walk(root, followlinks=False):
        current_path = Path(current)
        for name in sorted(directories):
            if name != ".git":
                _reject_link(current_path / name, "remote checkout directory")
        directories[:] = [
            name
            for name in sorted(directories)
            if name != ".git"
            and not (
                current_path.relative_to(root).as_posix().casefold() == "atlas"
                and name.casefold() == "private"
            )
        ]
        for name in sorted(names):
            path = current_path / name
            _reject_link(path, "remote checkout file")
            details = path.stat()
            if not stat.S_ISREG(details.st_mode):
                raise ValueError("remote checkout contains a non-regular file")
            files += 1
            checkout_bytes += details.st_size
            if files > limits.max_checkout_files:
                raise ValueError(
                    f"remote checkout exceeds the {limits.max_checkout_files}-file limit"
                )
            if checkout_bytes > limits.max_checkout_bytes:
                raise ValueError(
                    f"remote checkout exceeds the {limits.max_checkout_bytes}-byte limit"
                )
    return files, checkout_bytes


def _entry_from_metadata(
    raw: dict[str, object], repository: Path, cache_state: str
) -> CacheEntry:
    required = {
        "schema_version",
        "cache_id",
        "url",
        "revision",
        "acquired_at",
        "history_depth",
        "history_commit_count",
        "checkout_file_count",
        "checkout_bytes",
    }
    if set(raw) != required or raw.get("schema_version") != CACHE_SCHEMA_VERSION:
        raise ValueError("invalid managed cache metadata")
    strings = ("cache_id", "url", "revision", "acquired_at")
    integers = ("history_depth", "history_commit_count", "checkout_file_count", "checkout_bytes")
    if any(not isinstance(raw[key], str) for key in strings) or any(
        type(raw[key]) is not int or cast(int, raw[key]) < 0 for key in integers
    ):
        raise ValueError("invalid managed cache metadata values")
    cache_id = cast(str, raw["cache_id"])
    url = normalize_github_url(cast(str, raw["url"]))
    revision = cast(str, raw["revision"])
    if not CACHE_ID.fullmatch(cache_id) or cache_identity(url) != cache_id:
        raise ValueError("managed cache identity mismatch")
    if not FULL_REVISION.fullmatch(revision):
        raise ValueError("managed cache revision is invalid")
    return CacheEntry(
        cache_id,
        url,
        revision,
        repository,
        cast(str, raw["acquired_at"]),
        cast(int, raw["history_depth"]),
        cast(int, raw["history_commit_count"]),
        cast(int, raw["checkout_file_count"]),
        cast(int, raw["checkout_bytes"]),
        cache_state,
    )


def _load_metadata(path: Path) -> dict[str, object]:
    _reject_link(path, "managed cache metadata")
    if not path.is_file() or path.stat().st_size > MAX_METADATA_BYTES:
        raise ValueError("managed cache metadata is missing or oversized")
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("managed cache metadata must be an object")
    return raw


def _write_metadata(path: Path, entry: CacheEntry) -> None:
    payload = entry.public_dict()
    payload.pop("history_is_bounded")
    payload.pop("cache_state")
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _tree_size(root: Path) -> int:
    total = 0
    try:
        for current, _directories, files in os.walk(root, followlinks=False):
            for name in files:
                try:
                    total += (Path(current) / name).stat().st_size
                except OSError:
                    continue
    except OSError:
        return 0
    return total


def _reject_link(path: Path, label: str) -> None:
    try:
        details = path.lstat()
    except FileNotFoundError:
        raise ValueError(f"{label} does not exist") from None
    attributes = getattr(details, "st_file_attributes", 0)
    reparse = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    if stat.S_ISLNK(details.st_mode) or (reparse and attributes & reparse):
        raise ValueError(f"{label} is a symbolic link, junction, or reparse point")


def _remove_tree(path: Path) -> None:
    _reject_link(path, "managed cache removal target")
    if not path.is_dir():
        raise ValueError("managed cache removal target is not a directory")
    def make_writable(function: object, target: str, _details: object) -> None:
        os.chmod(target, stat.S_IWRITE)
        cast(Callable[[str], object], function)(target)

    def on_error(function: object, target: str, _details: object) -> None:
        make_writable(function, target, _details)

    remove_tree = cast(Callable[..., None], shutil.rmtree)
    remove_tree(path, **{_RMTREE_ERROR_CALLBACK: on_error})
