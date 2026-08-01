from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


def _cli(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "utf-8"
    environment["PYTHONUTF8"] = "1"
    return subprocess.run(
        [sys.executable, "-m", "intentatlas", *args],
        cwd=cwd,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )


def _free_loopback_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def test_installed_cli_scan_recommend_and_viewer_workflow(tmp_path) -> None:
    project = tmp_path / "project with spaces"
    project.mkdir()

    initialized = _cli("init", str(project), cwd=tmp_path)
    assert initialized.returncode == 0, initialized.stderr
    assert (project / "atlas" / "Home.md").is_file()

    (project / "app.py").write_text(
        "def authenticate(token: str) -> bool:\n    return token == 'valid'\n",
        encoding="utf-8",
    )
    (project / "test_app.py").write_text(
        "from app import authenticate\n\ndef test_authenticate():\n"
        "    assert authenticate('valid')\n",
        encoding="utf-8",
    )
    (project / "must_not_execute.py").write_text(
        "raise RuntimeError('scanning executed project code')\n",
        encoding="utf-8",
    )

    scanned = _cli("scan", str(project), cwd=tmp_path)
    assert scanned.returncode == 0, scanned.stderr
    assert "relationships" in scanned.stdout
    assert (project / ".intentatlas" / "graph.json").is_file()

    status = _cli("status", str(project), cwd=tmp_path)
    assert status.returncode == 0, status.stderr
    assert "durable orphans 0" in status.stdout

    impact = _cli("impact", "app.py", str(project), "--depth", "2", cwd=tmp_path)
    assert impact.returncode == 0, impact.stderr
    assert "test_app.py" in impact.stdout

    recommendation = _cli(
        "recommend-tests",
        "app.py",
        str(project),
        "--minimum-confidence",
        "low",
        "--format",
        "json",
        cwd=tmp_path,
    )
    assert recommendation.returncode == 0, recommendation.stderr
    payload = json.loads(recommendation.stdout)
    assert [item["test"]["path"] for item in payload["recommendations"]] == ["test_app.py"]

    port = _free_loopback_port()
    loopback = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "utf-8"
    environment["PYTHONUTF8"] = "1"
    server = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "intentatlas",
            "open",
            str(project),
            "--port",
            str(port),
            "--no-browser",
        ],
        cwd=tmp_path,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    try:
        deadline = time.monotonic() + 10
        viewer_html = ""
        last_error: OSError | None = None
        while time.monotonic() < deadline:
            if server.poll() is not None:
                break
            try:
                with loopback.open(f"http://127.0.0.1:{port}/", timeout=1) as response:
                    viewer_html = response.read().decode("utf-8")
                break
            except OSError as exc:
                last_error = exc
                time.sleep(0.05)
        if not viewer_html:
            stdout, stderr = (
                server.communicate(timeout=2) if server.poll() is not None else ("", "")
            )
            raise AssertionError(
                f"viewer did not start: {last_error}; stdout={stdout!r}; stderr={stderr!r}"
            )
        assert "IntentAtlas" in viewer_html
        with loopback.open(f"http://127.0.0.1:{port}/graph.json", timeout=2) as response:
            graph = json.loads(response.read().decode("utf-8"))
        assert any(node["path"] == "app.py" for node in graph["nodes"])
    finally:
        if server.poll() is None:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=5)
