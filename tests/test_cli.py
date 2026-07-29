from __future__ import annotations

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


def test_cli_reports_invalid_requests(tmp_path, capsys) -> None:
    assert main(["status", str(tmp_path)]) == 2
    assert "error:" in capsys.readouterr().err
    assert main(["init", str(tmp_path)]) == 0
    assert main(["scan", str(tmp_path)]) == 0
    assert main(["impact", "missing", str(tmp_path)]) == 2
    assert main(["impact", "Home", str(tmp_path), "--depth", "20"]) == 2
