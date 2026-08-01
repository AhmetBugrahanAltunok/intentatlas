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
        assert server.stdout is not None
        ready: queue.Queue[str] = queue.Queue()
        threading.Thread(target=lambda: ready.put(server.stdout.readline()), daemon=True).start()
        try:
            ready_line = ready.get(timeout=10)
        except queue.Empty as exc:
            raise AssertionError("viewer did not report its loopback address") from exc
        match = re.fullmatch(r"IntentAtlas viewer: (http://127\.0\.0\.1:\d+)\s*", ready_line)
        assert match is not None, ready_line
        url = match.group(1)

        profile = tmp_path / "browser-profile"
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
        rendered = completed.stdout
        assert "Could not load graph" not in rendered
        assert "<strong>320</strong><span>total nodes</span>" in rendered
        assert "<strong>319</strong><span>total links</span>" in rendered
        assert "<strong>240</strong><span>shown nodes</span>" in rendered
        assert "Ranked overview; 80 nodes remain available" in rendered
        assert rendered.count('class="node"') == 240
        assert json.loads(graph_path.read_text(encoding="utf-8"))["summary"] == {"file": 320}
    finally:
        if server.poll() is None:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=5)
