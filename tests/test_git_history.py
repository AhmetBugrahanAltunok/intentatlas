import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import intentatlas.git_history as git_history
from intentatlas.git_history import (
    MAX_DIFF_BYTES,
    DiffHunk,
    collect_git_history,
    parse_git_diffs,
    parse_git_log,
)


def test_parse_git_log_collects_paths_and_redacts_subjects() -> None:
    output = (
        "\x1eabc123\x1fabc123\x1f2026-07-30\x1ffeat: token=super-secret\n"
        "src/app.py\nREADME.md\n\n"
        "\x1edef456\x1fdef456\x1f2026-07-29\x1finitial commit\nREADME.md\n"
    )
    commits = parse_git_log(output)
    assert len(commits) == 2
    assert commits[0].subject == "feat: token=[REDACTED]"
    assert commits[0].paths == ("README.md", "src/app.py")
    assert commits[1].short == "def456"


def test_parse_git_log_ignores_malformed_blocks() -> None:
    assert parse_git_log("\x1enot-a-header\nfile.py") == []


def test_parse_git_diffs_collects_only_safe_current_side_ranges() -> None:
    sha = "a" * 40
    output = (
        f"\x00{sha}\n"
        "diff --git a/src/auth.py b/src/auth.py\n"
        "--- a/src/auth.py\n"
        "+++ b/src/auth.py\n"
        "@@ -2 +2 @@\n-old\n+new\n"
        "@@ -8,0 +9,2 @@\n+one\n+two\n"
        "diff --git a/src/old.py b/src/old.py\n"
        "--- a/src/old.py\n"
        "+++ /dev/null\n"
        "@@ -1 +0,0 @@\n-old\n"
    )

    assert parse_git_diffs(output) == {
        sha: (
            DiffHunk("src/auth.py", 2, 1),
            DiffHunk("src/auth.py", 9, 2),
        )
    }


def test_parse_git_diffs_rejects_malformed_paths_and_excessive_output() -> None:
    sha = "b" * 40
    unsafe = (
        f'\x00{sha}\n+++ "b/src/quoted.py"\n@@ -1 +1 @@\n'
        "+++ b/src/app.py\n"
        "@@ -1 +99999999999,99999999999 @@\n"
    )
    assert parse_git_diffs(unsafe) == {sha: ()}
    assert parse_git_diffs("x" * (MAX_DIFF_BYTES + 1)) == {}


def test_parse_git_diffs_preserves_deletion_uncertainty_in_surviving_files() -> None:
    sha = "d" * 40
    patch = (
        f"\x00{sha}\n+++ b/app.py\n"
        "@@ -1,2 +0,0 @@\n-old\n-old\n"
        "@@ -6 +4 @@\n-old\n+new\n"
        "@@ -12,2 +9,0 @@\n-old\n-old\n"
    )
    assert parse_git_diffs(patch) == {sha: (
        DiffHunk("app.py", 0, 0),
        DiffHunk("app.py", 4, 1),
        DiffHunk("app.py", 9, 0),
    )}


def test_alignment_checks_only_scanned_sources_with_trusted_symbol_spans(monkeypatch) -> None:
    sha = "c" * 40
    checked: list[str] = []

    def matches(_root: Path, _executable: str, _sha: str, path: str) -> bool:
        checked.append(path)
        return True

    monkeypatch.setattr(git_history, "_matches_commit_blob", matches)
    parsed = {
        sha: (
            DiffHunk("src/app.py", 2, 1),
            DiffHunk("web/app.js", 4, 1),
            DiffHunk("docs/design.md", 6, 1),
        )
    }

    assert git_history._aligned_git_diffs(
        Path("."), "git", parsed, frozenset({"src/app.py"})
    ) == {
        sha: (DiffHunk("src/app.py", 2, 1),)
    }
    assert checked == ["src/app.py"]


def test_bounded_runner_rejects_stdout_while_it_is_being_collected() -> None:
    command = [
        sys.executable,
        "-c",
        "import sys; sys.stdout.buffer.write(b'x' * 4097)",
    ]

    assert git_history._run_git_bounded(command, max_bytes=4096, timeout=5) is None


@pytest.mark.skipif(shutil.which("git") is None, reason="Git is required")
def test_history_excludes_private_and_configured_paths_at_git_boundary(
    tmp_path, monkeypatch
) -> None:
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

    public = tmp_path / "src" / "app.py"
    private = tmp_path / "atlas" / "pRIVATE" / "secret.py"
    configured = tmp_path / "vendor" / "generated" / "credential.py"
    named_exclude = tmp_path / "packages" / "cache" / "state.py"
    public.parent.mkdir(parents=True)
    private.parent.mkdir(parents=True)
    configured.parent.mkdir(parents=True)
    named_exclude.parent.mkdir(parents=True)
    public.write_text("def value():\n    return 'old'\n", encoding="utf-8")
    private.write_text("PRIVATE-HISTORY-MARKER = 'old'\n", encoding="utf-8")
    configured.write_text("CONFIGURED-EXCLUDE-MARKER = 'old'\n", encoding="utf-8")
    named_exclude.write_text("NAMED-EXCLUDE-MARKER = 'old'\n", encoding="utf-8")
    git("init", "-q")
    git("config", "user.name", "IntentAtlas Test")
    git("config", "user.email", "intentatlas-test@example.invalid")
    git(
        "add",
        "src/app.py",
        "atlas/pRIVATE/secret.py",
        "vendor/generated/credential.py",
        "packages/cache/state.py",
    )
    git("commit", "-q", "-m", "initial")

    public.write_text("def value():\n    return 'new'\n", encoding="utf-8")
    private.write_text("PRIVATE-HISTORY-MARKER = 'new'\n", encoding="utf-8")
    configured.write_text("CONFIGURED-EXCLUDE-MARKER = 'new'\n", encoding="utf-8")
    named_exclude.write_text("NAMED-EXCLUDE-MARKER = 'new'\n", encoding="utf-8")
    git(
        "add",
        "src/app.py",
        "atlas/pRIVATE/secret.py",
        "vendor/generated/credential.py",
        "packages/cache/state.py",
    )
    git("commit", "-q", "-m", "change public and excluded paths")

    commands: list[tuple[str, ...]] = []
    original_runner = git_history._run_git_bounded

    def guarded_runner(command, *, max_bytes, timeout):
        commands.append(tuple(command))
        output = original_runner(command, max_bytes=max_bytes, timeout=timeout)
        if output is not None:
            folded = output.lower()
            assert b"PRIVATE-HISTORY-MARKER" not in output
            assert b"CONFIGURED-EXCLUDE-MARKER" not in output
            assert b"NAMED-EXCLUDE-MARKER" not in output
            assert b"atlas/private" not in folded
            assert b"vendor/generated" not in output
            assert b"packages/cache" not in output
        return output

    monkeypatch.setattr(git_history, "_run_git_bounded", guarded_runner)

    commits = collect_git_history(
        tmp_path,
        2,
        symbol_paths=("src/app.py",),
        excluded_paths=("vendor/generated", "cache"),
    )

    assert commits
    assert all(commit.paths == ("src/app.py",) for commit in commits)
    log_command = next(command for command in commands if "log" in command)
    show_command = next(command for command in commands if "show" in command)
    assert ":(top,literal,icase,exclude)atlas/Private" in log_command
    assert ":(top,literal,icase,exclude)vendor/generated" in log_command
    assert ":(top,glob,icase,exclude)**/cache/**" in log_command
    assert ":(top,literal,icase,exclude)atlas/Private" in show_command
    assert ":(top,literal,icase,exclude)vendor/generated" in show_command
    assert ":(top,glob,icase,exclude)**/cache/**" in show_command
    assert ":(top,literal)src/app.py" in show_command
