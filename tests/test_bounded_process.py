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
