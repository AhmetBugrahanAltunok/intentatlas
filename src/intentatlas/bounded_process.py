from __future__ import annotations

import os
import subprocess  # nosec B404
import threading
from collections.abc import Mapping, Sequence
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

if os.name == "nt":
    import ctypes
    from ctypes import wintypes

_CREATE_SUSPENDED = 0x00000004


class _WindowsJob:
    """Own a Windows kill-on-close job for one bounded process tree."""

    def __init__(self, process: subprocess.Popen[bytes]) -> None:
        self.handle: int | None = None
        if os.name != "nt":
            return

        class _BasicLimitInformation(ctypes.Structure):
            _fields_ = [
                ("PerProcessUserTimeLimit", ctypes.c_longlong),
                ("PerJobUserTimeLimit", ctypes.c_longlong),
                ("LimitFlags", wintypes.DWORD),
                ("MinimumWorkingSetSize", ctypes.c_size_t),
                ("MaximumWorkingSetSize", ctypes.c_size_t),
                ("ActiveProcessLimit", wintypes.DWORD),
                ("Affinity", ctypes.c_size_t),
                ("PriorityClass", wintypes.DWORD),
                ("SchedulingClass", wintypes.DWORD),
            ]

        class _IoCounters(ctypes.Structure):
            _fields_ = [
                ("ReadOperationCount", ctypes.c_ulonglong),
                ("WriteOperationCount", ctypes.c_ulonglong),
                ("OtherOperationCount", ctypes.c_ulonglong),
                ("ReadTransferCount", ctypes.c_ulonglong),
                ("WriteTransferCount", ctypes.c_ulonglong),
                ("OtherTransferCount", ctypes.c_ulonglong),
            ]

        class _ExtendedLimitInformation(ctypes.Structure):
            _fields_ = [
                ("BasicLimitInformation", _BasicLimitInformation),
                ("IoInfo", _IoCounters),
                ("ProcessMemoryLimit", ctypes.c_size_t),
                ("JobMemoryLimit", ctypes.c_size_t),
                ("PeakProcessMemoryUsed", ctypes.c_size_t),
                ("PeakJobMemoryUsed", ctypes.c_size_t),
            ]

        kernel32 = cast(Any, ctypes).WinDLL("kernel32", use_last_error=True)
        create_job = kernel32.CreateJobObjectW
        create_job.argtypes = (ctypes.c_void_p, wintypes.LPCWSTR)
        create_job.restype = wintypes.HANDLE
        set_information = kernel32.SetInformationJobObject
        set_information.argtypes = (
            wintypes.HANDLE,
            ctypes.c_int,
            ctypes.c_void_p,
            wintypes.DWORD,
        )
        set_information.restype = wintypes.BOOL
        assign_process = kernel32.AssignProcessToJobObject
        assign_process.argtypes = (wintypes.HANDLE, wintypes.HANDLE)
        assign_process.restype = wintypes.BOOL
        close_handle = kernel32.CloseHandle
        close_handle.argtypes = (wintypes.HANDLE,)
        close_handle.restype = wintypes.BOOL
        handle = create_job(None, None)
        if not handle:
            raise OSError(
                int(cast(Any, ctypes).get_last_error()), "cannot create process job"
            )
        information = _ExtendedLimitInformation()
        information.BasicLimitInformation.LimitFlags = 0x00002000
        configured = set_information(
            handle,
            9,
            ctypes.byref(information),
            ctypes.sizeof(information),
        )
        assigned = configured and assign_process(
            handle, wintypes.HANDLE(process._handle)  # type: ignore[attr-defined]
        )
        if not assigned:
            error = int(cast(Any, ctypes).get_last_error())
            close_handle(handle)
            raise OSError(error, "cannot contain process tree")
        self.handle = int(handle)

    def close(self) -> None:
        if self.handle is None:
            return
        kernel32 = cast(Any, ctypes).WinDLL("kernel32", use_last_error=True)
        close_handle = kernel32.CloseHandle
        close_handle.argtypes = (wintypes.HANDLE,)
        close_handle.restype = wintypes.BOOL
        close_handle(wintypes.HANDLE(self.handle))
        self.handle = None


def contained_process_creation_flags() -> int:
    """Return flags that prevent Windows child code running before containment."""

    if os.name != "nt":
        return 0
    return getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | _CREATE_SUSPENDED


def contain_process_tree(
    process: subprocess.Popen[bytes], *, resume: bool = False
) -> _WindowsJob:
    """Attach a started process to the platform process-tree container."""

    job = _WindowsJob(process)
    if resume and os.name == "nt":
        try:
            _resume_windows_process(process.pid)
        except OSError:
            job.close()
            raise
    return job


def terminate_process_tree(
    process: subprocess.Popen[bytes], container: _WindowsJob | None
) -> None:
    """Terminate a contained process tree and reap its leader."""

    _terminate_process_tree(process, container)
    with suppress(OSError, subprocess.SubprocessError):
        process.wait(timeout=1)


class ProcessCollectionError(Exception):
    """A bounded child process could not be collected safely."""


class ProcessOutputLimitError(ProcessCollectionError):
    """A child process exceeded its declared stdout allowance."""


@dataclass(frozen=True, slots=True)
class BoundedProcessResult:
    returncode: int
    stdout: bytes


def run_bounded_process(
    command: Sequence[str],
    *,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
    max_stdout_bytes: int,
    timeout: float,
) -> BoundedProcessResult:
    """Run a fixed command while enforcing its stdout bound during collection."""

    if max_stdout_bytes < 0:
        raise ProcessOutputLimitError
    try:
        process = subprocess.Popen(  # noqa: S603  # nosec B603
            list(command),
            cwd=cwd,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            shell=False,
            start_new_session=os.name != "nt",
            creationflags=contained_process_creation_flags(),
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ProcessCollectionError from exc
    try:
        job = contain_process_tree(process, resume=os.name == "nt")
    except OSError as exc:
        with suppress(OSError, subprocess.SubprocessError):
            _terminate_process_tree(process, None)
        with suppress(OSError, subprocess.SubprocessError):
            process.wait(timeout=1)
        if process.stdout is not None:
            with suppress(OSError):
                process.stdout.close()
        raise ProcessCollectionError from exc
    if process.stdout is None:
        with suppress(OSError, subprocess.SubprocessError):
            _terminate_process_tree(process, job)
        job.close()
        raise ProcessCollectionError

    stdout = process.stdout
    chunks: list[bytes] = []
    size = 0
    exceeded = False
    read_failed = False

    def drain() -> None:
        nonlocal exceeded, read_failed, size
        try:
            while True:
                # Keep at most the declared allowance and read one sentinel byte
                # when the producer reaches it, so overflow is detected promptly.
                chunk = stdout.read(min(65_536, max_stdout_bytes - size + 1))
                if not chunk:
                    return
                if size + len(chunk) > max_stdout_bytes:
                    exceeded = True
                    with suppress(OSError, subprocess.SubprocessError):
                        _terminate_process_tree(process, job)
                    return
                chunks.append(chunk)
                size += len(chunk)
        except (OSError, ValueError):
            read_failed = True
            with suppress(OSError, subprocess.SubprocessError):
                _terminate_process_tree(process, job)

    reader = threading.Thread(target=drain, daemon=True)
    reader.start()
    try:
        returncode = process.wait(timeout=timeout)
    except (OSError, subprocess.SubprocessError) as exc:
        with suppress(OSError, subprocess.SubprocessError):
            _terminate_process_tree(process, job)
        with suppress(OSError, subprocess.SubprocessError):
            process.wait(timeout=1)
        reader.join(timeout=1)
        if not reader.is_alive():
            with suppress(OSError):
                stdout.close()
        job.close()
        raise ProcessCollectionError from exc

    reader.join(timeout=1)
    if reader.is_alive():
        with suppress(OSError, subprocess.SubprocessError):
            _terminate_process_tree(process, job)
        with suppress(OSError, subprocess.SubprocessError):
            process.wait(timeout=1)
        # Do not synchronously close a pipe while the reader may be blocked in
        # it. The daemon reader owns that descriptor until the process tree
        # releases every inherited writer.
        job.close()
        raise ProcessCollectionError
    with suppress(OSError):
        stdout.close()
    job.close()
    if exceeded:
        raise ProcessOutputLimitError
    if read_failed:
        raise ProcessCollectionError
    return BoundedProcessResult(returncode, b"".join(chunks))


def _terminate_process_tree(
    process: subprocess.Popen[bytes], job: _WindowsJob | None
) -> None:
    if os.name == "nt":
        if job is not None:
            job.close()
        if process.poll() is None:
            process.kill()
        return
    with suppress(OSError):
        os.kill(-process.pid, 9)
    if process.poll() is None:
        process.kill()


def _resume_windows_process(process_id: int) -> None:
    if os.name != "nt":
        return

    class _ThreadEntry32(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD),
            ("cntUsage", wintypes.DWORD),
            ("th32ThreadID", wintypes.DWORD),
            ("th32OwnerProcessID", wintypes.DWORD),
            ("tpBasePri", wintypes.LONG),
            ("tpDeltaPri", wintypes.LONG),
            ("dwFlags", wintypes.DWORD),
        ]

    kernel32 = cast(Any, ctypes).WinDLL("kernel32", use_last_error=True)
    create_snapshot = kernel32.CreateToolhelp32Snapshot
    create_snapshot.argtypes = (wintypes.DWORD, wintypes.DWORD)
    create_snapshot.restype = wintypes.HANDLE
    thread_first = kernel32.Thread32First
    thread_first.argtypes = (wintypes.HANDLE, ctypes.POINTER(_ThreadEntry32))
    thread_first.restype = wintypes.BOOL
    thread_next = kernel32.Thread32Next
    thread_next.argtypes = (wintypes.HANDLE, ctypes.POINTER(_ThreadEntry32))
    thread_next.restype = wintypes.BOOL
    open_thread = kernel32.OpenThread
    open_thread.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    open_thread.restype = wintypes.HANDLE
    resume_thread = kernel32.ResumeThread
    resume_thread.argtypes = (wintypes.HANDLE,)
    resume_thread.restype = wintypes.DWORD
    close_handle = kernel32.CloseHandle
    close_handle.argtypes = (wintypes.HANDLE,)
    close_handle.restype = wintypes.BOOL

    snapshot = create_snapshot(0x00000004, 0)
    invalid_handle = ctypes.c_void_p(-1).value
    if snapshot in (None, invalid_handle):
        error = int(cast(Any, ctypes).get_last_error())
        raise OSError(error, "cannot enumerate suspended process threads")

    entry = _ThreadEntry32()
    entry.dwSize = ctypes.sizeof(entry)
    last_error = 0
    try:
        has_entry = bool(thread_first(snapshot, ctypes.byref(entry)))
        if not has_entry:
            last_error = int(cast(Any, ctypes).get_last_error())
        while has_entry:
            if entry.th32OwnerProcessID == process_id:
                thread = open_thread(0x0002, False, entry.th32ThreadID)
                if thread:
                    try:
                        previous_count = resume_thread(thread)
                        if previous_count != 0xFFFFFFFF:
                            return
                        last_error = int(cast(Any, ctypes).get_last_error())
                    finally:
                        close_handle(thread)
                else:
                    last_error = int(cast(Any, ctypes).get_last_error())
            has_entry = bool(thread_next(snapshot, ctypes.byref(entry)))
    finally:
        close_handle(snapshot)
    raise OSError(last_error, "cannot resume contained process")
