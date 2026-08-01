from __future__ import annotations

import json
import shutil
import subprocess

import pytest

from intentatlas.cli import main


def git(root, *arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


@pytest.mark.skipif(shutil.which("git") is None, reason="Git is required")
def test_review_pilots_cover_aligned_stale_and_fallback_ranges(tmp_path, capsys) -> None:
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "review-pilots@example.invalid")
    git(tmp_path, "config", "user.name", "Review Pilots")
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    app = tmp_path / "app.py"
    test_app = tmp_path / "test_app.py"
    settings = tmp_path / "settings.toml"
    outcomes = tmp_path / "outcomes.json"
    app.write_text("def run():\n    return 1\n", encoding="utf-8")
    test_app.write_text(
        "from app import run\n\ndef test_run():\n    assert run() == 1\n",
        encoding="utf-8",
    )
    settings.write_text("enabled = true\n", encoding="utf-8")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-qm", "baseline")
    baseline = git(tmp_path, "rev-parse", "HEAD")

    app.write_text("def run():\n    return 2\n", encoding="utf-8")
    git(tmp_path, "add", "app.py")
    git(tmp_path, "commit", "-qm", "change exact symbol")
    exact_head = git(tmp_path, "rev-parse", "HEAD")
    outcome_document = {
        "schema_version": 1,
        "commit": exact_head,
        "test_set_policy": "complete-executed-set",
        "tests": [{"path": "test_app.py", "status": "passed"}],
    }
    outcomes.write_text(json.dumps(outcome_document), encoding="utf-8")
    exact_arguments = [
        "review",
        str(tmp_path),
        "--base",
        baseline,
        "--head",
        exact_head,
        "--test-outcomes",
        "outcomes.json",
        "--format",
        "json",
    ]
    assert main(exact_arguments) == 0
    exact = json.loads(capsys.readouterr().out)
    assert exact["change_report"]["analysis_state"] == "analyzed"
    assert exact["change_report"]["test_strategy"] == "targeted"
    assert [item["test"]["path"] for item in exact["change_report"]["tests"]] == [
        "test_app.py"
    ]
    assert exact["test_outcomes"]["freshness"] == "aligned"
    assert exact["test_outcomes"]["predicted_and_executed"] == ["test_app.py"]

    outcome_document["commit"] = baseline
    outcomes.write_text(json.dumps(outcome_document), encoding="utf-8")
    assert main(exact_arguments) == 0
    stale = json.loads(capsys.readouterr().out)["test_outcomes"]
    assert stale["freshness"] == "stale"
    assert stale["predicted_and_executed"] == []
    assert stale["predicted_not_executed"] == []
    assert stale["executed_not_predicted"] == []

    settings.write_text("enabled = false\n", encoding="utf-8")
    git(tmp_path, "add", "settings.toml")
    git(tmp_path, "commit", "-qm", "change unsupported configuration")
    fallback_head = git(tmp_path, "rev-parse", "HEAD")
    outcome_document["commit"] = fallback_head
    outcome_document["tests"] = []
    outcomes.write_text(json.dumps(outcome_document), encoding="utf-8")
    fallback_arguments = [
        "review",
        str(tmp_path),
        "--base",
        exact_head,
        "--head",
        fallback_head,
        "--test-outcomes",
        "outcomes.json",
        "--format",
        "sarif",
    ]
    assert main(fallback_arguments) == 0
    fallback = json.loads(capsys.readouterr().out)
    properties = fallback["runs"][0]["properties"]
    assert properties["analysis_state"] == "fallback"
    assert properties["test_strategy"] == "full-suite-fallback"
    assert properties["test_outcomes"]["freshness"] == "aligned"
    assert {item["ruleId"] for item in fallback["runs"][0]["results"]} == {
        "IA101",
        "IA300",
    }
