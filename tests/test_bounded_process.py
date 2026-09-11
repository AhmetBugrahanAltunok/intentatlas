from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

import pytest

import intentatlas.bounded_process as bounded_process_module
from intentatlas.bounded_process import (
    ProcessCollectionError,
    ProcessOutputLimitError,
    run_bounded_process,
)


def test_bounded_process_accepts_stdout_at_exact_limit() -> None:
    result = run_bounded_process(
        [sys.executable, "-c", "import sys; sys.stdout.buffer.write(b'x' * 32)"],
        max_stdout_bytes=32,
        timeout=5,
    )

    assert result.returncode == 0
    assert result.stdout == b"x" * 32


def test_bounded_process_stops_stdout_overflow_during_collection() -> None:
    started = time.monotonic()
    with pytest.raises(ProcessOutputLimitError):
        run_bounded_process(
            [
                sys.executable,
                "-c",
                "import sys,time; sys.stdout.buffer.write(b'x' * 4096); "
                "sys.stdout.flush(); time.sleep(5)",
            ],
            max_stdout_bytes=64,
            timeout=4,
        )

    assert time.monotonic() - started < 3


def test_bounded_process_stops_on_timeout() -> None:
    started = time.monotonic()
    with pytest.raises(ProcessCollectionError):
        run_bounded_process(
            [sys.executable, "-c", "import time; time.sleep(5)"],
            max_stdout_bytes=64,
            timeout=0.1,
        )

    assert time.monotonic() - started < 3


def test_bounded_process_timeout_does_not_wait_for_descendant_pipe_writer(
    tmp_path: Path,
) -> None:
    marker = tmp_path / "descendant-survived"
    child = tmp_path / "child.py"
    child.write_text(
        "import pathlib,sys,time\n"
        "time.sleep(1)\n"
        "pathlib.Path(sys.argv[1]).write_text('survived', encoding='utf-8')\n",
        encoding="utf-8",
    )
    parent = tmp_path / "parent.py"
    parent.write_text(
        "import subprocess,sys,time\n"
        "subprocess.Popen([sys.executable, sys.argv[1], sys.argv[2]], stdout=sys.stdout)\n"
        "time.sleep(5)\n",
        encoding="utf-8",
    )

    started = time.monotonic()
    with pytest.raises(ProcessCollectionError):
        run_bounded_process(
            [sys.executable, str(parent), str(child), str(marker)],
            max_stdout_bytes=64,
            timeout=0.1,
        )

    assert time.monotonic() - started < 3
    time.sleep(1.2)
    assert not marker.exists()


def test_bounded_process_setup_failure_terminates_the_started_child(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    parent_marker = tmp_path / "parent-started"
    marker = tmp_path / "descendant-survived"
    child = tmp_path / "setup-child.py"
    child.write_text(
        "import pathlib,sys,time\n"
        "time.sleep(1)\n"
        "pathlib.Path(sys.argv[1]).write_text('survived', encoding='utf-8')\n",
        encoding="utf-8",
    )
    parent = tmp_path / "setup-parent.py"
    parent.write_text(
        "import pathlib,subprocess,sys,time\n"
        "pathlib.Path(sys.argv[1]).write_text('started', encoding='utf-8')\n"
        "subprocess.Popen([sys.executable, sys.argv[2], sys.argv[3]])\n"
        "time.sleep(5)\n",
        encoding="utf-8",
    )

    class FailingJob:
        def __init__(self, _process) -> None:  # noqa: ANN001
            time.sleep(0.2)
            raise OSError("simulated containment failure")

    monkeypatch.setattr(bounded_process_module, "_WindowsJob", FailingJob)
    with pytest.raises(ProcessCollectionError):
        run_bounded_process(
            [
                sys.executable,
                str(parent),
                str(parent_marker),
                str(child),
                str(marker),
            ],
            max_stdout_bytes=64,
            timeout=2,
        )

    time.sleep(1.2)
    if sys.platform == "win32":
        assert not parent_marker.exists()
    assert not marker.exists()


@pytest.mark.skipif(sys.platform != "win32", reason="Windows Job Object contract")
def test_windows_process_tree_uses_a_kill_on_close_job() -> None:
    process = subprocess.Popen(  # noqa: S603  # nosec B603
        [sys.executable, "-c", "import time; time.sleep(5)"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        shell=False,
    )
    container = bounded_process_module.contain_process_tree(process)

    bounded_process_module.terminate_process_tree(process, container)

    assert process.poll() is not None


def test_negative_stdout_allowance_is_refused_before_starting_anything(monkeypatch) -> None:
    started: list[object] = []
    monkeypatch.setattr(
        bounded_process_module.subprocess,
        "Popen",
        lambda *args, **kwargs: started.append(args) or pytest.fail("must not start"),
    )
    with pytest.raises(ProcessOutputLimitError):
        run_bounded_process([sys.executable, "-c", ""], max_stdout_bytes=-1, timeout=5)
    assert started == []


def test_unstartable_command_fails_closed() -> None:
    with pytest.raises(ProcessCollectionError):
        run_bounded_process(
            [str(Path("intentatlas-command-that-does-not-exist"))],
            max_stdout_bytes=16,
            timeout=5,
        )


def test_containment_failure_terminates_the_child_and_fails_closed(monkeypatch) -> None:
    observed: dict[str, subprocess.Popen[bytes]] = {}
    original = bounded_process_module.subprocess.Popen

    def record(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
        process = original(*args, **kwargs)
        observed["process"] = process
        return process

    monkeypatch.setattr(bounded_process_module.subprocess, "Popen", record)

    def refuse(process, *, resume=False):  # noqa: ANN001, ANN202
        raise OSError("containment unavailable")

    monkeypatch.setattr(bounded_process_module, "contain_process_tree", refuse)

    with pytest.raises(ProcessCollectionError):
        run_bounded_process(
            [sys.executable, "-c", "import time; time.sleep(30)"],
            max_stdout_bytes=64,
            timeout=10,
        )

    process = observed["process"]
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline and process.poll() is None:
        time.sleep(0.05)
    assert process.poll() is not None, "the started child outlived a containment failure"


def test_missing_stdout_pipe_fails_closed(monkeypatch) -> None:
    original = bounded_process_module.subprocess.Popen

    class _NoPipe:
        def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
            self._process = original(*args, **kwargs)
            self._process.stdout.close()
            self.stdout = None

        def __getattr__(self, name: str):  # noqa: ANN204
            return getattr(self._process, name)

    monkeypatch.setattr(bounded_process_module.subprocess, "Popen", _NoPipe)
    with pytest.raises(ProcessCollectionError):
        run_bounded_process(
            [sys.executable, "-c", "import time; time.sleep(30)"],
            max_stdout_bytes=64,
            timeout=10,
        )


def test_unreadable_stdout_fails_closed(monkeypatch) -> None:
    original = bounded_process_module.subprocess.Popen

    class _BrokenPipe:
        def __init__(self, stream) -> None:  # noqa: ANN001
            self._stream = stream

        def read(self, *args) -> bytes:  # noqa: ANN002
            raise OSError("pipe torn down")

        def close(self) -> None:
            self._stream.close()

    class _BrokenStdout:
        def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
            self._process = original(*args, **kwargs)
            self.stdout = _BrokenPipe(self._process.stdout)

        def __getattr__(self, name: str):  # noqa: ANN204
            return getattr(self._process, name)

    monkeypatch.setattr(bounded_process_module.subprocess, "Popen", _BrokenStdout)
    with pytest.raises(ProcessCollectionError):
        run_bounded_process(
            [sys.executable, "-c", "print('unreachable')"],
            max_stdout_bytes=64,
            timeout=10,
        )


def test_uncollectable_child_fails_closed(monkeypatch) -> None:
    original = bounded_process_module.subprocess.Popen

    class _UnwaitableProcess:
        def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
            self._process = original(*args, **kwargs)
            self.stdout = self._process.stdout
            self._refused = False

        def wait(self, timeout=None):  # noqa: ANN001, ANN202
            if not self._refused:
                self._refused = True
                raise subprocess.SubprocessError("cannot reap")
            return self._process.wait(timeout=timeout)

        def __getattr__(self, name: str):  # noqa: ANN204
            return getattr(self._process, name)

    monkeypatch.setattr(bounded_process_module.subprocess, "Popen", _UnwaitableProcess)
    with pytest.raises(ProcessCollectionError):
        run_bounded_process(
            [sys.executable, "-c", "import time; time.sleep(30)"],
            max_stdout_bytes=64,
            timeout=10,
        )


def test_zero_allowance_refuses_any_output() -> None:
    with pytest.raises(ProcessOutputLimitError):
        run_bounded_process(
            [sys.executable, "-c", "import sys; sys.stdout.buffer.write(b'x')"],
            max_stdout_bytes=0,
            timeout=10,
        )
    result = run_bounded_process(
        [sys.executable, "-c", ""], max_stdout_bytes=0, timeout=10
    )
    assert (result.returncode, result.stdout) == (0, b"")


def test_surviving_pipe_holder_after_a_clean_exit_fails_closed(tmp_path: Path) -> None:
    """The parent exits promptly, but a descendant keeps the stdout pipe open.

    Collection must fail closed instead of blocking on a reader that can never
    reach end of file, and must not return a partial result as if it were whole.
    """

    holder = tmp_path / "holder.py"
    holder.write_text(
        "import sys,time\ntime.sleep(6)\nsys.stdout.write('late')\n",
        encoding="utf-8",
    )
    parent = tmp_path / "quick-parent.py"
    parent.write_text(
        "import subprocess,sys\n"
        "subprocess.Popen([sys.executable, sys.argv[1]], stdout=sys.stdout)\n",
        encoding="utf-8",
    )

    started = time.monotonic()
    with pytest.raises(ProcessCollectionError):
        run_bounded_process(
            [sys.executable, str(parent), str(holder)],
            max_stdout_bytes=64,
            timeout=10,
        )
    elapsed = time.monotonic() - started
    assert elapsed < 6, "collection waited for the descendant instead of failing closed"
