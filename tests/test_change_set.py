from __future__ import annotations

import io
import json
import shutil
import subprocess
from pathlib import Path

import pytest

import intentatlas.bounded_process as bounded_process_module
import intentatlas.change_set as change_set_module
from intentatlas.change_set import (
    ChangeFile,
    collect_change_set,
    parse_name_status,
    render_change_set,
)


def test_parse_name_status_handles_bounded_paths_and_renames() -> None:
    parsed = parse_name_status(
        "M\0src/app.py\0A\0tests/test_app.py\0R100\0src/old.py\0src/new.py\0"
    )

    assert parsed == (
        ChangeFile("modified", "src/app.py"),
        ChangeFile("renamed", "src/new.py", previous_path="src/old.py"),
        ChangeFile("added", "tests/test_app.py"),
    )

    with pytest.raises(ValueError, match="unsafe path"):
        parse_name_status("M\0../outside.py\0")
    with pytest.raises(ValueError, match="malformed"):
        parse_name_status("R100\0only-old.py\0")


def test_parse_name_status_fails_closed_on_over_limit_output(monkeypatch) -> None:
    monkeypatch.setattr(change_set_module, "MAX_DIFF_BYTES", 4)

    with pytest.raises(ValueError, match="exceeds"):
        parse_name_status("M\0app.py\0")


def test_git_output_is_bounded_while_the_process_is_drained(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    read_sizes: list[int] = []

    class ProbedOutput(io.BytesIO):
        def read(self, size: int = -1) -> bytes:
            read_sizes.append(size)
            return super().read(size)

    class OutputProcess:
        def __init__(self, _command, **kwargs) -> None:  # noqa: ANN001, ANN003
            assert kwargs["stdout"] is subprocess.PIPE
            assert kwargs["stderr"] is subprocess.DEVNULL
            self.pid = 123_456
            self.stdout = ProbedOutput(b"12345")
            self.returncode = 0

        def wait(self, timeout: float | None = None) -> int:
            return self.returncode

        def poll(self) -> int:
            return self.returncode

        def kill(self) -> None:
            self.returncode = -9

    class NoopJob:
        def __init__(self, _process) -> None:  # noqa: ANN001
            pass

        def close(self) -> None:
            pass

    original_popen = change_set_module.subprocess.Popen

    def output_or_system_process(command, **kwargs):  # noqa: ANN001, ANN003, ANN202
        if Path(str(command[0])).name.casefold() == "taskkill.exe":
            return original_popen(command, **kwargs)
        return OutputProcess(command, **kwargs)

    monkeypatch.setattr(change_set_module, "MAX_DIFF_BYTES", 4)
    monkeypatch.setattr(change_set_module.subprocess, "Popen", output_or_system_process)
    monkeypatch.setattr(bounded_process_module, "_WindowsJob", NoopJob)
    monkeypatch.setattr(bounded_process_module, "_resume_windows_process", lambda _pid: None)

    with pytest.raises(ValueError, match="exceeds the 4-byte limit"):
        change_set_module._git_output(tmp_path, "git", "status")

    assert read_sizes == [5]


@pytest.mark.skipif(shutil.which("git") is None, reason="Git is required")
def test_collect_change_set_unifies_commit_range_staged_and_worktree(tmp_path) -> None:
    def git(*arguments: str) -> str:
        result = subprocess.run(
            ["git", *arguments],
            cwd=tmp_path,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return result.stdout.strip()

    git("init", "-q")
    git("config", "user.name", "Change Set Test")
    git("config", "user.email", "change-set@example.invalid")
    app = tmp_path / "app.py"
    app.write_text("def value():\n    return 1\n", encoding="utf-8")
    git("add", "app.py")
    git("commit", "-qm", "initial")
    base = git("rev-parse", "HEAD")
    root_commit = collect_change_set(tmp_path, scope="commit", revision=base)
    assert root_commit.base_revision is None
    assert [(item.status, item.path) for item in root_commit.files] == [
        ("added", "app.py")
    ]

    app.write_text("def value():\n    return 2\n", encoding="utf-8")
    git("add", "app.py")
    staged = collect_change_set(tmp_path, scope="staged")
    assert staged.base_revision == base
    assert [(item.status, item.path) for item in staged.files] == [
        ("modified", "app.py")
    ]
    assert staged.files[0].hunks[0].start == 2

    git("commit", "-qm", "change value")
    head = git("rev-parse", "HEAD")
    commit = collect_change_set(tmp_path, scope="commit", revision=head[:12])
    revision_range = collect_change_set(
        tmp_path,
        scope="range",
        base=base,
        head=head,
    )
    assert commit.head_revision == head
    assert commit.base_revision == base
    assert commit.files == revision_range.files

    app.write_text("def value():\n    return 3\n", encoding="utf-8")
    (tmp_path / "new.py").write_text("enabled = True\n", encoding="utf-8")
    worktree = collect_change_set(tmp_path, scope="worktree")
    assert [(item.status, item.path) for item in worktree.files] == [
        ("modified", "app.py"),
        ("untracked", "new.py"),
    ]

    git("add", "app.py", "new.py")
    staged = collect_change_set(tmp_path, scope="staged")
    assert [(item.status, item.path) for item in staged.files] == [
        ("modified", "app.py"),
        ("added", "new.py"),
    ]

    first = render_change_set(staged, "json")
    assert first == render_change_set(staged, "json")
    payload = json.loads(first)
    assert payload["schema_version"] == 1
    assert payload["scope"] == "staged"
    assert payload["file_count"] == 2
    assert "return 3" not in first


@pytest.mark.skipif(shutil.which("git") is None, reason="Git is required")
def test_worktree_collapses_staged_delete_and_same_path_recreation_to_modified(
    tmp_path,
) -> None:
    def git(*arguments: str) -> None:
        subprocess.run(
            ["git", *arguments],
            cwd=tmp_path,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    git("init", "-q")
    git("config", "user.name", "Change Set Test")
    git("config", "user.email", "change-set@example.invalid")
    app = tmp_path / "app.py"
    app.write_text("value = 1\n", encoding="utf-8")
    git("add", "app.py")
    git("commit", "-qm", "baseline")

    app.unlink()
    git("add", "-u", "app.py")
    app.write_text("value = 2\n", encoding="utf-8")

    staged = collect_change_set(tmp_path, scope="staged")
    worktree = collect_change_set(tmp_path, scope="worktree")

    assert [(item.status, item.path) for item in staged.files] == [("deleted", "app.py")]
    assert [(item.status, item.path) for item in worktree.files] == [("modified", "app.py")]


@pytest.mark.skipif(shutil.which("git") is None, reason="Git is required")
def test_collect_change_set_rejects_invalid_scope_and_revision(tmp_path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)

    with pytest.raises(ValueError, match="Unknown change scope"):
        collect_change_set(tmp_path, scope="everything")
    with pytest.raises(ValueError, match="Unsafe Git revision"):
        collect_change_set(tmp_path, scope="commit", revision="--output=/tmp/x")
    with pytest.raises(ValueError, match="requires both base and head"):
        collect_change_set(tmp_path, scope="range", base="HEAD")
