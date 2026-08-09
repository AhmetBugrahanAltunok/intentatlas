from __future__ import annotations

import json
import shutil
import subprocess

import pytest

import intentatlas.change_set as change_set_module
from intentatlas.change_analysis import analyze_change_set, render_change_analysis
from intentatlas.change_set import collect_change_set
from intentatlas.config import ProjectConfig


@pytest.mark.skipif(shutil.which("git") is None, reason="Git is required")
def test_change_analysis_distinguishes_exact_fallback_and_stale_files(tmp_path) -> None:
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
    git("config", "user.name", "Change Analysis Test")
    git("config", "user.email", "change-analysis@example.invalid")
    app = tmp_path / "app.py"
    config_file = tmp_path / "settings.toml"
    data_file = tmp_path / "labels.json"
    app.write_text(
        "def selected():\n    return 1\n\ndef untouched():\n    return 10\n",
        encoding="utf-8",
    )
    config_file.write_text("enabled = false\n", encoding="utf-8")
    data_file.write_text('{"enabled": false}\n', encoding="utf-8")
    git("add", "app.py", "settings.toml", "labels.json")
    git("commit", "-qm", "initial")

    app.write_text(
        "def selected():\n    return 2\n\ndef untouched():\n    return 10\n",
        encoding="utf-8",
    )
    config_file.write_text("enabled = true\n", encoding="utf-8")
    data_file.write_text('{"enabled": true}\n', encoding="utf-8")
    git("add", "app.py", "settings.toml", "labels.json")

    change_set = collect_change_set(tmp_path, scope="staged")
    config = ProjectConfig(git_history_limit=0)
    result = analyze_change_set(tmp_path, change_set, config)

    assert result.state == "fallback"
    exact = next(item for item in result.files if item.path == "app.py")
    assert (exact.state, exact.freshness, exact.confidence) == (
        "analyzed",
        "aligned",
        "high",
    )
    assert exact.artifact_ids == ("symbol:app.py::selected",)
    fallback = next(item for item in result.files if item.path == "settings.toml")
    assert (fallback.state, fallback.freshness, fallback.confidence) == (
        "fallback",
        "aligned",
        "low",
    )
    unscanned = next(item for item in result.files if item.path == "labels.json")
    assert (unscanned.state, unscanned.confidence) == ("fallback", "low")
    assert "unscanned-file-fallback" in unscanned.evidence

    app.write_text(
        "def selected():\n    return 3\n\ndef untouched():\n    return 10\n",
        encoding="utf-8",
    )
    stale = analyze_change_set(tmp_path, change_set, config)
    stale_app = next(item for item in stale.files if item.path == "app.py")
    assert (stale_app.state, stale_app.freshness, stale_app.confidence) == (
        "unknown",
        "stale",
        "none",
    )
    assert stale_app.artifact_ids == ()

    rendered = render_change_analysis(result, "json")
    assert rendered == render_change_analysis(result, "json")
    payload = json.loads(rendered)
    assert payload["schema_version"] == 1
    assert payload["change_set"]["scope"] == "staged"
    assert "return 2" not in rendered


@pytest.mark.skipif(shutil.which("git") is None, reason="Git is required")
def test_worktree_analysis_marks_untracked_source_as_file_fallback(tmp_path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "new.py").write_text("def created():\n    return True\n", encoding="utf-8")

    change_set = collect_change_set(tmp_path, scope="worktree")
    result = analyze_change_set(
        tmp_path, change_set, ProjectConfig(git_history_limit=0)
    )

    assert len(result.files) == 1
    item = result.files[0]
    assert (item.state, item.freshness, item.confidence) == (
        "fallback",
        "aligned",
        "low",
    )
    assert item.artifact_ids == ("file:new.py",)
    assert "untracked-content-not-read" in item.evidence


@pytest.mark.skipif(shutil.which("git") is None, reason="Git is required")
def test_oversized_unscanned_commit_file_uses_safe_file_fallback(
    tmp_path, monkeypatch
) -> None:
    def git(*arguments: str) -> None:
        subprocess.run(
            ["git", *arguments],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

    git("init", "-q")
    git("config", "user.name", "Change Analysis Test")
    git("config", "user.email", "change-analysis@example.invalid")
    asset = tmp_path / "demo.gif"
    asset.write_bytes(b"GIF89a" + (b"x" * 64))
    git("add", "demo.gif")
    git("commit", "-qm", "add demo")
    monkeypatch.setattr(change_set_module, "MAX_SYMBOL_SOURCE_BYTES", 16)

    change_set = collect_change_set(tmp_path, scope="commit", revision="HEAD")
    result = analyze_change_set(
        tmp_path, change_set, ProjectConfig(git_history_limit=0)
    )

    assert result.state == "fallback"
    assert len(result.files) == 1
    item = result.files[0]
    assert (item.state, item.freshness, item.confidence) == (
        "fallback",
        "aligned",
        "low",
    )
    assert "unscanned-file-fallback" in item.evidence
