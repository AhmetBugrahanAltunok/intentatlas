from pathlib import Path

import intentatlas.git_history as git_history
from intentatlas.git_history import MAX_DIFF_BYTES, DiffHunk, parse_git_diffs, parse_git_log


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
