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
