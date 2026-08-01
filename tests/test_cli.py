from __future__ import annotations

import json
import shutil
import subprocess

import pytest

from intentatlas.cli import main


def test_cli_init_scan_status_and_impact(tmp_path, capsys) -> None:
    assert main(["init", str(tmp_path)]) == 0
    assert (tmp_path / "intentatlas.json").exists()
    assert (tmp_path / "atlas" / "Home.md").exists()

    (tmp_path / "app.py").write_text("def run():\n    return True\n", encoding="utf-8")
    (tmp_path / "test_app.py").write_text(
        "from app import run\n\ndef test_run():\n    assert run()\n", encoding="utf-8"
    )
    assert main(["scan", str(tmp_path)]) == 0
    assert (tmp_path / ".intentatlas" / "graph.json").exists()
    assert main(["status", str(tmp_path)]) == 0
    assert main(["impact", "app.py", str(tmp_path), "--depth", "1"]) == 0
    output = capsys.readouterr().out
    assert "Scanned" in output
    assert "relationships" in output
    assert "app.py" in output
    assert "tested-by · verification" in output
    assert "via python-ast" in output


def test_cli_reports_invalid_requests(tmp_path, capsys) -> None:
    assert main(["status", str(tmp_path)]) == 2
    assert "error:" in capsys.readouterr().err
    assert main(["init", str(tmp_path)]) == 0
    assert main(["scan", str(tmp_path)]) == 0
    assert main(["impact", "missing", str(tmp_path)]) == 2
    assert main(["impact", "Home", str(tmp_path), "--depth", "20"]) == 2


def test_cli_writes_deterministic_graph_diff_and_supports_ci_check(tmp_path, capsys) -> None:
    assert main(["init", str(tmp_path)]) == 0
    app = tmp_path / "app.py"
    app.write_text("value = 1\n", encoding="utf-8")
    assert main(["scan", str(tmp_path)]) == 0
    baseline = tmp_path / ".intentatlas" / "baseline.json"
    shutil.copyfile(tmp_path / ".intentatlas" / "graph.json", baseline)

    app.write_text("value = 1\n\ndef added():\n    return value\n", encoding="utf-8")
    assert main(["scan", str(tmp_path)]) == 0
    output = ".intentatlas/diff.json"
    assert main(["diff", ".intentatlas/baseline.json", str(tmp_path), "--output", output]) == 0
    first = (tmp_path / output).read_text(encoding="utf-8")
    value = json.loads(first)
    assert value["schema_version"] == 1
    assert value["has_changes"] is True
    assert value["summary"]["nodes_added"] >= 1

    assert (
        main(
            [
                "diff",
                ".intentatlas/baseline.json",
                str(tmp_path),
                "--output",
                output,
                "--check",
            ]
        )
        == 1
    )
    assert (tmp_path / output).read_text(encoding="utf-8") == first
    capsys.readouterr()
    assert main(["diff", ".intentatlas/graph.json", str(tmp_path), "--check"]) == 0
    assert json.loads(capsys.readouterr().out)["has_changes"] is False


def test_cli_rejects_unsafe_graph_diff_paths(tmp_path, capsys) -> None:
    assert main(["init", str(tmp_path)]) == 0
    assert main(["scan", str(tmp_path)]) == 0
    assert main(["diff", "../outside.json", str(tmp_path)]) == 2
    assert "below the project root" in capsys.readouterr().err
    assert (
        main(
            [
                "diff",
                ".intentatlas/graph.json",
                str(tmp_path),
                "--output",
                ".intentatlas/graph.json",
            ]
        )
        == 2
    )
    assert "may not overwrite" in capsys.readouterr().err


@pytest.mark.skipif(shutil.which("git") is None, reason="Git is required")
def test_cli_renders_worktree_change_set_as_deterministic_json(tmp_path, capsys) -> None:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "new.py").write_text("value = 1\n", encoding="utf-8")
    (tmp_path / "atlas" / "Private").mkdir(parents=True)
    (tmp_path / "atlas" / "Private" / "secret.md").write_text(
        "must stay outside change metadata\n", encoding="utf-8"
    )

    arguments = ["changes", str(tmp_path), "--worktree", "--format", "json"]
    assert main(arguments) == 0
    first = capsys.readouterr().out
    assert main(arguments) == 0
    assert capsys.readouterr().out == first
    payload = json.loads(first)
    assert payload["scope"] == "worktree"
    assert payload["files"] == [
        {"hunks": [], "path": "new.py", "status": "untracked"}
    ]

    assert main([*arguments, "--analyze"]) == 0
    analyzed = json.loads(capsys.readouterr().out)
    assert analyzed["state"] == "fallback"
    assert analyzed["files"][0]["freshness"] == "aligned"

    assert main([*arguments, "--report"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["schema_version"] == 1
    assert report["analysis_state"] == "fallback"
    assert report["test_strategy"] == "full-suite-fallback"
    assert report["requirements"] == []
    assert report["tests"] == []

    assert main([*arguments, "--analyze", "--report"]) == 2
    assert "either --analyze or --report" in capsys.readouterr().err
    assert main([*arguments, "--open"]) == 2
    assert "--open requires --report" in capsys.readouterr().err

    assert main(["changes", str(tmp_path)]) == 2
    assert "Select exactly one change scope" in capsys.readouterr().err
    assert main(["changes", str(tmp_path), "--base", "HEAD"]) == 2
    assert "both --base and --head" in capsys.readouterr().err


@pytest.mark.skipif(shutil.which("git") is None, reason="Git is required")
def test_cli_reviews_revision_range_in_non_blocking_shadow_mode(
    tmp_path, capsys, monkeypatch
) -> None:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "config", "user.email", "intentatlas@example.invalid"],
        cwd=tmp_path,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "IntentAtlas Test"], cwd=tmp_path, check=True
    )
    assert main(["init", str(tmp_path)]) == 0
    capsys.readouterr()
    app = tmp_path / "app.py"
    test_app = tmp_path / "test_app.py"
    app.write_text("def run():\n    return 1\n", encoding="utf-8")
    test_app.write_text(
        "from app import run\n\ndef test_run():\n    assert run() == 1\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "baseline"], cwd=tmp_path, check=True)
    base = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    app.write_text("def run():\n    return 2\n", encoding="utf-8")
    subprocess.run(["git", "add", "app.py"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "change app"], cwd=tmp_path, check=True)
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    arguments = [
        "review",
        str(tmp_path),
        "--base",
        base,
        "--head",
        head,
        "--format",
        "json",
    ]
    assert main(arguments) == 0
    first = capsys.readouterr().out
    assert main(arguments) == 0
    assert capsys.readouterr().out == first
    payload = json.loads(first)
    assert payload["mode"] == "shadow"
    assert payload["base_revision"] == base
    assert payload["head_revision"] == head
    assert payload["change_report"]["analysis"]["change_set"]["scope"] == "range"

    outcomes_path = tmp_path / "test-outcomes.json"
    outcomes_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "commit": head,
                "test_set_policy": "complete-executed-set",
                "tests": [{"path": "test_app.py", "status": "passed"}],
            }
        ),
        encoding="utf-8",
    )
    outcome_arguments = [*arguments, "--test-outcomes", "test-outcomes.json"]
    assert main(outcome_arguments) == 0
    compared = json.loads(capsys.readouterr().out)
    assert compared["test_outcomes"]["freshness"] == "aligned"
    assert compared["test_outcomes"]["predicted_and_executed"] == ["test_app.py"]

    stale_document = json.loads(outcomes_path.read_text(encoding="utf-8"))
    stale_document["commit"] = base
    outcomes_path.write_text(json.dumps(stale_document), encoding="utf-8")
    assert main(outcome_arguments) == 0
    stale = json.loads(capsys.readouterr().out)["test_outcomes"]
    assert stale["freshness"] == "stale"
    assert stale["predicted_and_executed"] == []
    assert stale["predicted_not_executed"] == []
    assert stale["executed_not_predicted"] == []

    stale_document["commit"] = head
    outcomes_path.write_text(json.dumps(stale_document), encoding="utf-8")
    served: dict[str, object] = {}

    def fake_serve(
        graph_path,
        *,
        host,
        port,
        open_browser,
        graph_document,
        change_report_document=None,
        review_document=None,
    ) -> None:
        served.update(
            graph_path=graph_path,
            host=host,
            port=port,
            open_browser=open_browser,
            graph_document=graph_document,
            change_report_document=change_report_document,
            review_document=review_document,
        )

    monkeypatch.setattr("intentatlas.cli.serve_graph", fake_serve)
    assert main([*outcome_arguments, "--open", "--no-browser", "--port", "0"]) == 0
    assert served["graph_path"] is None
    assert served["open_browser"] is False
    assert served["change_report_document"] is None
    opened = json.loads(served["review_document"])
    assert opened["mode"] == "shadow"
    assert opened["test_outcomes"]["freshness"] == "aligned"
    opened_graph = json.loads(served["graph_document"])
    assert any(node.get("path") == "app.py" for node in opened_graph["nodes"])

    private = tmp_path / "atlas" / "Private"
    private.mkdir(exist_ok=True)
    (private / "outcomes.json").write_text(json.dumps(stale_document), encoding="utf-8")
    private_arguments = [*arguments, "--test-outcomes", "atlas/Private/outcomes.json"]
    assert main(private_arguments) == 2
    assert "may not be inside atlas/Private" in capsys.readouterr().err

    assert main([*arguments[:-1], "sarif"]) == 0
    sarif = json.loads(capsys.readouterr().out)
    assert sarif["version"] == "2.1.0"
    assert sarif["runs"][0]["invocations"][0]["executionSuccessful"] is True
    assert sarif["runs"][0]["invocations"][0]["properties"]["blocking"] is False
