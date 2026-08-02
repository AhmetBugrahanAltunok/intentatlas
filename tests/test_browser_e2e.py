from __future__ import annotations

import json
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
from pathlib import Path

import pytest

from intentatlas.graph import AtlasGraph
from intentatlas.models import Edge, Node


def _browser() -> str | None:
    commands = ("google-chrome", "chrome", "chromium", "chromium-browser", "msedge")
    for command in commands:
        resolved = shutil.which(command)
        if resolved:
            return resolved
    candidates = (
        Path(os.environ.get("PROGRAMFILES", "")) / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("PROGRAMFILES", "")) / "Microsoft/Edge/Application/msedge.exe",
        Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Microsoft/Edge/Application/msedge.exe",
        Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
    )
    return next((str(path) for path in candidates if path.is_file()), None)


def _viewer_url(server: subprocess.Popen[str]) -> str:
    assert server.stdout is not None
    ready: queue.Queue[str] = queue.Queue()

    def read_ready() -> None:
        for _ in range(3):
            line = server.stdout.readline()
            match = re.fullmatch(r"IntentAtlas viewer: (http://127\.0\.0\.1:\d+)\s*", line)
            if match is not None:
                ready.put(match.group(1))
                return
        ready.put("")

    threading.Thread(target=read_ready, daemon=True).start()
    try:
        url = ready.get(timeout=10)
    except queue.Empty as exc:
        raise AssertionError("viewer did not report its loopback address") from exc
    assert url, "viewer did not emit a valid loopback address"
    return url


def _dump_dom(browser: str, url: str, profile: Path) -> str:
    completed = subprocess.run(
        [
            browser,
            "--headless=new",
            "--disable-background-networking",
            "--disable-default-apps",
            "--disable-extensions",
            "--disable-gpu",
            "--disable-sync",
            "--metrics-recording-only",
            "--no-first-run",
            "--no-sandbox",
            "--run-all-compositor-stages-before-draw",
            f"--user-data-dir={profile}",
            "--virtual-time-budget=5000",
            "--dump-dom",
            url,
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )
    assert completed.returncode == 0, completed.stderr
    return completed.stdout


def _stop_server(server: subprocess.Popen[str]) -> None:
    if server.poll() is None:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=5)


def test_real_browser_renders_bounded_large_graph_window(tmp_path: Path) -> None:
    browser = _browser()
    if browser is None:
        if os.environ.get("INTENTATLAS_REQUIRE_BROWSER") == "1":
            pytest.fail("A Chrome-family browser is required for the browser E2E gate")
        pytest.skip("No installed Chrome-family browser")

    project = tmp_path / "browser project"
    graph_path = project / ".intentatlas" / "graph.json"
    graph = AtlasGraph()
    nodes = [
        Node(
            f"file:src/module_{index:03}.py",
            "file",
            f"module_{index:03}.py",
            f"src/module_{index:03}.py",
            {"owner": "scanner"},
        )
        for index in range(320)
    ]
    graph.extend(nodes)
    for index in range(319):
        assert graph.add_edge(
            Edge(nodes[index].id, nodes[index + 1].id, "imports", "browser-fixture")
        )
    graph.save(graph_path)

    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "utf-8"
    environment["PYTHONUTF8"] = "1"
    server = subprocess.Popen(
        [
            sys.executable,
            "-u",
            "-m",
            "intentatlas",
            "open",
            str(project),
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
        url = _viewer_url(server)
        rendered = _dump_dom(browser, url, tmp_path / "browser-profile")
        assert "Could not load graph" not in rendered
        assert "<strong>320</strong><span>total nodes</span>" in rendered
        assert "<strong>319</strong><span>total links</span>" in rendered
        assert "<strong>240</strong><span>shown nodes</span>" in rendered
        assert "Ranked overview; 80 nodes remain available" in rendered
        assert rendered.count('class="node"') == 240
        assert json.loads(graph_path.read_text(encoding="utf-8"))["summary"] == {"file": 320}
    finally:
        _stop_server(server)


def test_real_browser_renders_same_file_demo_story(tmp_path: Path) -> None:
    browser = _browser()
    if browser is None:
        if os.environ.get("INTENTATLAS_REQUIRE_BROWSER") == "1":
            pytest.fail("A Chrome-family browser is required for the browser E2E gate")
        pytest.skip("No installed Chrome-family browser")

    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "utf-8"
    environment["PYTHONUTF8"] = "1"
    server = subprocess.Popen(
        [
            sys.executable,
            "-u",
            "-m",
            "intentatlas",
            "demo",
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
        url = _viewer_url(server)
        rendered = _dump_dom(browser, url, tmp_path / "demo-browser-profile")
        assert "Could not load graph" not in rendered
        assert "<strong>12</strong><span>total nodes</span>" in rendered
        assert "<strong>18</strong><span>total links</span>" in rendered
        assert "Keep customer sessions secure" in rendered
        assert "Preserve login audit events" in rendered
        assert "rotate_session" in rendered
        assert "record_login_audit" in rendered

        toggle = re.search(r'<button id="report-toggle"[^>]*>', rendered)
        assert toggle is not None
        assert "hidden" not in toggle.group(0)
        summary = re.search(
            r'<div id="report-summary"[^>]*>(.*?)</div>\s*<h3>',
            rendered,
            re.DOTALL,
        )
        assert summary is not None
        assert "<strong>targeted</strong>" in summary.group(1)
        assert "<strong>analyzed</strong>" in summary.group(1)
        assert "<span>freshness</span><strong>aligned</strong>" in summary.group(1)
        assert "<span>threshold</span><strong>medium</strong>" in summary.group(1)
        assert 'id="change-report" class="detail report-detail open"' in rendered
        assert 'role="dialog"' in rendered
        assert 'aria-hidden="false"' in rendered
        assert (
            "Impact and test recommendations are bounded structural evidence, not proof that an "
            "omitted requirement is unaffected or that a suggested test is sufficient."
            in rendered
        )
        report_tests = re.search(
            r'<div id="report-tests"[^>]*>(.*?)</div>',
            rendered,
            re.DOTALL,
        )
        assert report_tests is not None
        assert "tests/test_auth_rotation.py" in report_tests.group(1)
        assert "tests/test_auth_audit.py" not in report_tests.group(1)
        assert "Recorded ranking path:" in report_tests.group(1)
        assert "symbol:src/auth.py::rotate_session" in report_tests.group(1)
        assert "file:tests/test_auth_rotation.py" in report_tests.group(1)
    finally:
        _stop_server(server)
