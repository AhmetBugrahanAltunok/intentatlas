from __future__ import annotations

import json
import os
import queue
import re
import shutil
import socket
import struct
import subprocess
import sys
import threading
import time
import urllib.request
from base64 import b64encode
from contextlib import suppress
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

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


class _CdpChrome:
    def __init__(self, browser: str, url: str, profile: Path) -> None:
        self._next_id = 1
        self.process = subprocess.Popen(
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
                "--remote-allow-origins=*",
                "--remote-debugging-port=0",
                f"--user-data-dir={profile}",
                url,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self.socket: socket.socket | None = None
        try:
            websocket_url = self._page_websocket(profile, url)
            parsed = urlparse(websocket_url)
            self.socket = socket.create_connection((parsed.hostname, parsed.port), timeout=10)
            self.socket.settimeout(10)
            key = b64encode(os.urandom(16)).decode("ascii")
            request_target = parsed.path + (f"?{parsed.query}" if parsed.query else "")
            request = (
                f"GET {request_target} HTTP/1.1\r\n"
                f"Host: {parsed.hostname}:{parsed.port}\r\n"
                "Upgrade: websocket\r\n"
                "Connection: Upgrade\r\n"
                f"Sec-WebSocket-Key: {key}\r\n"
                "Sec-WebSocket-Version: 13\r\n\r\n"
            )
            self.socket.sendall(request.encode("ascii"))
            response = bytearray()
            while not response.endswith(b"\r\n\r\n"):
                response.extend(self._receive_exact(1))
            assert response.startswith(b"HTTP/1.1 101 "), response.decode(
                "ascii", "replace"
            )
        except BaseException:
            self.close()
            raise

    def _page_websocket(self, profile: Path, url: str) -> str:
        port_file = profile / "DevToolsActivePort"
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if not port_file.is_file():
                time.sleep(0.05)
                continue
            port = port_file.read_text(encoding="utf-8").splitlines()[0]
            try:
                with urllib.request.urlopen(  # noqa: S310
                    f"http://127.0.0.1:{port}/json/list",
                    timeout=1,
                ) as response:
                    targets = json.load(response)
            except OSError:
                time.sleep(0.05)
                continue
            target = next(
                (
                    item
                    for item in targets
                    if item["type"] == "page" and item["url"].startswith(url)
                ),
                None,
            )
            if target is not None:
                return target["webSocketDebuggerUrl"]
            time.sleep(0.05)
        raise AssertionError("Chrome did not expose the viewer page")

    def _receive_exact(self, size: int) -> bytes:
        assert self.socket is not None
        chunks = bytearray()
        while len(chunks) < size:
            chunk = self.socket.recv(size - len(chunks))
            if not chunk:
                raise AssertionError("Chrome closed its debugging WebSocket")
            chunks.extend(chunk)
        return bytes(chunks)

    def _send_frame(self, payload: bytes, opcode: int = 1) -> None:
        assert self.socket is not None
        mask = os.urandom(4)
        length = len(payload)
        header = bytearray([0x80 | opcode])
        if length < 126:
            header.append(0x80 | length)
        elif length < 65_536:
            header.append(0x80 | 126)
            header.extend(struct.pack("!H", length))
        else:
            header.append(0x80 | 127)
            header.extend(struct.pack("!Q", length))
        header.extend(mask)
        masked = bytes(value ^ mask[index % 4] for index, value in enumerate(payload))
        self.socket.sendall(bytes(header) + masked)

    def _receive_message(self) -> dict[str, Any]:
        payload = bytearray()
        while True:
            first, second = self._receive_exact(2)
            final = bool(first & 0x80)
            opcode = first & 0x0F
            length = second & 0x7F
            if length == 126:
                length = struct.unpack("!H", self._receive_exact(2))[0]
            elif length == 127:
                length = struct.unpack("!Q", self._receive_exact(8))[0]
            mask = self._receive_exact(4) if second & 0x80 else b""
            fragment = self._receive_exact(length)
            if mask:
                fragment = bytes(
                    value ^ mask[index % 4] for index, value in enumerate(fragment)
                )
            if opcode == 8:
                raise AssertionError("Chrome closed its debugging WebSocket")
            if opcode == 9:
                self._send_frame(fragment, opcode=10)
                continue
            if opcode in {0, 1}:
                payload.extend(fragment)
            if final and payload:
                return json.loads(payload.decode("utf-8"))

    def command(
        self,
        method: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        command_id = self._next_id
        self._next_id += 1
        payload: dict[str, Any] = {"id": command_id, "method": method}
        if params is not None:
            payload["params"] = params
        self._send_frame(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            message = self._receive_message()
            if message.get("id") != command_id:
                continue
            if "error" in message:
                raise AssertionError(f"Chrome rejected {method}: {message['error']}")
            return message.get("result", {})
        raise AssertionError(f"Chrome did not answer {method}")

    def close(self) -> None:
        if self.socket is not None:
            with suppress(OSError):
                self.socket.close()
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)


def _keyboard_accessibility_probe(browser: str, url: str, profile: Path) -> None:
    chrome = _CdpChrome(browser, url, profile)
    try:
        def evaluate(expression: str) -> Any:
            result = chrome.command(
                "Runtime.evaluate",
                {"expression": expression, "returnByValue": True},
            )
            return result["result"].get("value")

        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if evaluate(
                "document.readyState === 'complete' && "
                "document.querySelector('#change-report')?.classList.contains('open')"
            ):
                break
            time.sleep(0.05)
        else:
            raise AssertionError("Change report did not auto-open in Chrome")

        chrome.command("Accessibility.enable")
        accessibility = chrome.command("Accessibility.getFullAXTree")
        assert any(
            node.get("role", {}).get("value") == "dialog"
            and node.get("name", {}).get("value") == "Change report"
            for node in accessibility["nodes"]
        )

        chrome.command(
            "Input.dispatchKeyEvent",
            {"type": "keyDown", "key": "Escape", "code": "Escape"},
        )
        chrome.command(
            "Input.dispatchKeyEvent",
            {"type": "keyUp", "key": "Escape", "code": "Escape"},
        )
        assert evaluate("document.querySelector('#change-report').getAttribute('aria-hidden')") == (
            "true"
        )

        assert evaluate("document.querySelector('#report-toggle').focus(); true") is True
        for event_type in ("rawKeyDown", "char", "keyUp"):
            key_text = "\r" if event_type in {"rawKeyDown", "char"} else ""
            chrome.command(
                "Input.dispatchKeyEvent",
                {
                    "type": event_type,
                    "key": "Enter",
                    "code": "Enter",
                    "text": key_text,
                    "unmodifiedText": key_text,
                    "windowsVirtualKeyCode": 13,
                    "nativeVirtualKeyCode": 13,
                },
            )
        keyboard_state = evaluate(
            "({hidden: document.querySelector('#change-report').getAttribute('aria-hidden'), "
            "active: document.activeElement?.id})"
        )
        assert keyboard_state == {"hidden": "false", "active": "close-report"}
    finally:
        chrome.close()


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
        _keyboard_accessibility_probe(
            browser,
            url,
            tmp_path / "demo-keyboard-browser-profile",
        )
    finally:
        _stop_server(server)
