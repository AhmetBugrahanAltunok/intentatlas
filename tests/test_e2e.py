from __future__ import annotations

import http.client
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest


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


def _http_response(
    port: int, path: str, *, host_header: str | None = None
) -> tuple[int, dict[str, str], bytes]:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
    try:
        headers = {"Host": host_header} if host_header is not None else {}
        connection.request("GET", path, headers=headers)
        response = connection.getresponse()
        return response.status, dict(response.getheaders()), response.read()
    finally:
        connection.close()


def _http_get(port: int, path: str) -> bytes:
    status, _, body = _http_response(port, path)
    assert status == 200
    return body


def test_installed_cli_scan_recommend_and_viewer_workflow(tmp_path) -> None:
    version = _cli("--version", cwd=tmp_path)
    assert version.returncode == 0, version.stderr
    assert version.stdout.strip() == "IntentAtlas 0.3.0rc1"

    demo_report = _cli("demo", "--report", "json", cwd=tmp_path)
    assert demo_report.returncode == 0, demo_report.stderr
    demo_payload = json.loads(demo_report.stdout)
    assert demo_payload["schema_version"] == 1
    assert [
        item["test"]["path"]
        for item in demo_payload["test_recommendations"]["recommendations"]
    ] == ["tests/test_auth_rotation.py"]
    assert demo_payload["same_file_tests_not_recommended"][0]["path"] == (
        "tests/test_auth_audit.py"
    )

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

    git = shutil.which("git")
    if git is not None:
        subprocess.run([git, "init", "-q"], cwd=project, check=True)
        changes = _cli(
            "changes",
            str(project),
            "--worktree",
            "--format",
            "json",
            cwd=tmp_path,
        )
        assert changes.returncode == 0, changes.stderr
        change_payload = json.loads(changes.stdout)
        assert change_payload["scope"] == "worktree"
        assert "app.py" in {item["path"] for item in change_payload["files"]}

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

    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "utf-8"
    environment["PYTHONUTF8"] = "1"
    server = subprocess.Popen(
        [
            sys.executable,
            "-u",
            "-m",
            "intentatlas",
            "changes",
            str(project),
            "--worktree",
            "--report",
            "--open",
            "--port",
            "0",
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
        assert server.stdout is not None
        ready_lines: queue.Queue[str] = queue.Queue()
        threading.Thread(
            target=lambda: ready_lines.put(server.stdout.readline()), daemon=True
        ).start()
        try:
            ready_line = ready_lines.get(timeout=10)
        except queue.Empty as exc:
            raise AssertionError("viewer did not report its loopback address") from exc
        match = re.fullmatch(r"IntentAtlas viewer: http://127\.0\.0\.1:(\d+)\s*", ready_line)
        assert match is not None, ready_line
        port = int(match.group(1))

        deadline = time.monotonic() + 5
        viewer_html = ""
        last_error: OSError | None = None
        while time.monotonic() < deadline:
            if server.poll() is not None:
                break
            try:
                viewer_html = _http_get(port, "/").decode("utf-8")
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
        status, headers, _ = _http_response(port, "/")
        assert status == 200
        assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]
        assert headers["Cross-Origin-Resource-Policy"] == "same-origin"
        assert headers["Referrer-Policy"] == "no-referrer"
        assert headers["X-Content-Type-Options"] == "nosniff"
        assert headers["X-Frame-Options"] == "DENY"
        foreign_status, _, foreign_body = _http_response(
            port, "/graph.json", host_header="attacker.invalid"
        )
        assert foreign_status == 421
        assert b"app.py" not in foreign_body
        graph = json.loads(_http_get(port, "/graph.json").decode("utf-8"))
        assert any(node["path"] == "app.py" for node in graph["nodes"])
        report = json.loads(_http_get(port, "/change-report.json").decode("utf-8"))
        assert report["schema_version"] == 1
        assert report["analysis_state"] == "fallback"
        assert report["test_strategy"] in {
            "full-suite-fallback",
            "targeted-plus-full-suite",
        }
    finally:
        if server.poll() is None:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=5)


def test_installed_revision_review_viewer_serves_commit_keyed_outcomes(tmp_path) -> None:
    git = shutil.which("git")
    if git is None:
        pytest.skip("Git is required")
    project = tmp_path / "review project"
    project.mkdir()
    initialized = _cli("init", str(project), cwd=tmp_path)
    assert initialized.returncode == 0, initialized.stderr
    subprocess.run([git, "init", "-q"], cwd=project, check=True)
    subprocess.run(
        [git, "config", "user.email", "review-viewer@example.invalid"],
        cwd=project,
        check=True,
    )
    subprocess.run(
        [git, "config", "user.name", "Review Viewer Test"], cwd=project, check=True
    )
    app = project / "app.py"
    test_app = project / "test_app.py"
    app.write_text("def run():\n    return 1\n", encoding="utf-8")
    test_app.write_text(
        "from app import run\n\ndef test_run():\n    assert run() == 1\n",
        encoding="utf-8",
    )
    subprocess.run([git, "add", "."], cwd=project, check=True)
    subprocess.run([git, "commit", "-qm", "baseline"], cwd=project, check=True)
    base = subprocess.run(
        [git, "rev-parse", "HEAD"],
        cwd=project,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    app.write_text("def run():\n    return 2\n", encoding="utf-8")
    subprocess.run([git, "add", "app.py"], cwd=project, check=True)
    subprocess.run([git, "commit", "-qm", "change app"], cwd=project, check=True)
    head = subprocess.run(
        [git, "rev-parse", "HEAD"],
        cwd=project,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    (project / "test-outcomes.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "commit": head,
                "test_set_policy": "complete-executed-set",
                "tests": [{"path": "test_app.py", "status": "failed"}],
            }
        ),
        encoding="utf-8",
    )

    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "utf-8"
    environment["PYTHONUTF8"] = "1"
    server = subprocess.Popen(
        [
            sys.executable,
            "-u",
            "-m",
            "intentatlas",
            "review",
            str(project),
            "--base",
            base,
            "--head",
            head,
            "--test-outcomes",
            "test-outcomes.json",
            "--open",
            "--port",
            "0",
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
        assert server.stdout is not None
        ready_lines: queue.Queue[str] = queue.Queue()
        threading.Thread(
            target=lambda: ready_lines.put(server.stdout.readline()), daemon=True
        ).start()
        try:
            ready_line = ready_lines.get(timeout=10)
        except queue.Empty as exc:
            raise AssertionError("review viewer did not report its loopback address") from exc
        match = re.fullmatch(r"IntentAtlas viewer: http://127\.0\.0\.1:(\d+)\s*", ready_line)
        assert match is not None, ready_line
        port = int(match.group(1))

        deadline = time.monotonic() + 5
        review: dict[str, object] | None = None
        while time.monotonic() < deadline and server.poll() is None:
            try:
                review = json.loads(_http_get(port, "/review.json").decode("utf-8"))
                break
            except OSError:
                time.sleep(0.05)
        assert review is not None
        assert review["mode"] == "shadow"
        outcomes = review["test_outcomes"]
        assert outcomes["freshness"] == "aligned"
        assert outcomes["tests"] == [{"path": "test_app.py", "status": "failed"}]
        assert "report-outcomes" in _http_get(port, "/").decode("utf-8")
        assert 'fetch("/review.json"' in _http_get(port, "/app.js").decode("utf-8")
    finally:
        if server.poll() is None:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=5)
