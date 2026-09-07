from __future__ import annotations

import json
import shutil
import subprocess

import pytest

from intentatlas.cli import main


@pytest.mark.skipif(shutil.which("git") is None, reason="Git is required")
@pytest.mark.parametrize("scope", ["worktree", "staged", "commit", "range"])
@pytest.mark.parametrize(
    ("before", "after", "state", "artifacts"),
    [
        (
            "setting = 1\ndef selected():\n    return 1\n",
            "setting = 2\ndef selected(value=2):\n    return 1\n",
            "fallback", ("file:app.py",),
        ),
        (
            "def selected():\n    return 1\n\ndef removed():\n    return 10\n",
            "def selected():\n    return 2\n\n",
            "fallback", ("file:app.py",),
        ),
        (
            "def selected():\n    value = 1\n    def child():\n        return 1\n"
            "    return child()\n",
            "def selected():\n    value = 2\n    def child(value=2):\n        return 1\n"
            "    return child()\n",
            "analyzed", ("symbol:app.py::selected", "symbol:app.py::selected.child"),
        ),
        (
            "def selected():\n    def child():\n        return 1\n    return child()\n",
            "def selected():\n    def child():\n        return 2\n    return child()\n",
            "analyzed", ("symbol:app.py::selected.child",),
        ),
    ],
    ids=["partial", "mixed-deletion", "parent-and-child", "child-only"],
)
def test_git_to_cli_preserves_change_coverage(
    tmp_path, capsys, scope, before, after, state, artifacts
) -> None:
    def git(*arguments: str) -> None:
        subprocess.run(["git", *arguments], cwd=tmp_path, check=True, capture_output=True)

    git("init", "-q")
    git("config", "user.name", "Coverage Test")
    git("config", "user.email", "coverage@example.invalid")
    app = tmp_path / "app.py"
    app.write_text(before, encoding="utf-8")
    (tmp_path / "test_app.py").write_text(
        "from app import selected\n\ndef test_selected():\n    assert selected()\n",
        encoding="utf-8",
    )
    git("add", "app.py", "test_app.py")
    git("commit", "-qm", "initial")
    app.write_text(after, encoding="utf-8")
    if scope != "worktree":
        git("add", "app.py")
    if scope in {"commit", "range"}:
        git("commit", "-qm", "change behavior")
    selectors = {
        "worktree": ["--worktree"],
        "staged": ["--staged"],
        "commit": ["--commit", "HEAD"],
        "range": ["--base", "HEAD^", "--head", "HEAD"],
    }
    command = ["changes", str(tmp_path), *selectors[scope], "--report"]
    assert main([*command, "--format", "json"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["analysis"]["state"] == state
    assert report["analysis"]["files"][0]["artifact_ids"] == list(artifacts)
    assert report["analysis_coverage_complete"] is (state == "analyzed")
    strategy = "targeted-plus-full-suite" if state == "fallback" else "targeted"
    assert report["test_strategy"] == strategy
    assert main(command) == 0
    text = capsys.readouterr().out
    assert f"Test strategy: {strategy}" in text
    assert not (tmp_path / "intentatlas.json").exists()
    assert not (tmp_path / "atlas").exists()
    assert not (tmp_path / ".intentatlas").exists()
