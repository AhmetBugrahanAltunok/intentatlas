from __future__ import annotations

import http.client
import json
import socket
import threading
from importlib.resources import files

import pytest

import intentatlas.viewer as viewer
from intentatlas.graph import AtlasGraph
from intentatlas.models import Edge, Node


def _graph_document() -> str:
    return json.dumps(AtlasGraph().to_dict())


def test_viewer_assets_are_packaged() -> None:
    web = files("intentatlas.web")
    assert "IntentAtlas" in web.joinpath("index.html").read_text(encoding="utf-8")
    assert "--accent" in web.joinpath("styles.css").read_text(encoding="utf-8")
    app = web.joinpath("app.js").read_text(encoding="utf-8")
    assert 'fetch("/api/graph/overview?node_limit=240&edge_limit=900"' in app
    assert 'fetch("/api/report/review"' in app
    assert 'fetch("/api/report/change"' in app
    assert 'fetch("/graph.json"' not in app
    assert "/api/graph/search" in app
    assert "/api/graph/neighborhood" in app
    assert "renderChangeReport" in app
    pointerup = app.split('group.addEventListener("pointerup"', maxsplit=1)[1].split(
        'group.addEventListener("pointercancel"', maxsplit=1
    )[0]
    assert "if (!moved) selectNode(node.id);" in pointerup
    assert 'group.addEventListener("click", () => { if (!moved) selectNode(node.id); });' in app
    assert "edge.inverse || edge.relation" in app
    assert 'issue: "#f97316"' in app
    assert '"delivery-issue": "#fb923c"' in app
    assert '"pull-request": "#facc15"' in app
    assert "/api/graph/paths?${query}" in app
    assert "result.paths.map" in app
    assert "formatRecordedPath" in app
    assert "Primary ranking path:" in app
    assert "Primary reason:" in app
    assert "Primary evidence:" in app
    assert "omission details shown" in app
    assert "renderOmittedItems" in app
    assert "if (state.report) openChangeReport(false);" in app
    assert 'const pathLimits = { depth: 6, visited: 800, results: 6 };' in app
    assert "edge.inverse || edge.relation" in app
    assert "No bounded evidence path found." in app
    assert "function bindFocusButton(button)" in app
    assert "function findEvidencePaths" not in app
    assert "function buildPathAdjacency" not in app
    assert (
        "const renderLimits = { nodes: 240, edges: 900, focusDepth: 2, relationships: 80 };"
        in app
    )
    assert "function buildGraphIndexes()" in app
    assert "function overviewNodes()" in app
    assert "function focusedNodes()" in app
    assert "function windowEdges(ids)" in app
    assert "function compareWindowEdges(a, b)" in app
    assert "function bestSearchMatch(value)" in app
    assert "state.edgeByNode.get(id) || []" in app
    assert "state.visibleNodeById.get(group.dataset.id)" in app
    assert "state.data.edges.filter" not in app
    assert "state.nodes.find" not in app
    assert "state.edges.reduce" not in app
    index = web.joinpath("index.html").read_text(encoding="utf-8")
    assert 'id="detail-paths"' in index
    assert 'id="report-toggle"' in index
    assert 'id="change-report"' in index
    assert 'id="report-outcomes"' in index
    assert 'id="report-title"' in index
    assert 'id="report-omitted-requirements"' in index
    assert 'id="report-omitted-tests"' in index
    assert 'role="dialog"' in index
    assert 'aria-controls="change-report"' in index
    assert 'id="overview"' in index
    assert 'id="window-status"' in index
    assert 'id="focus-neighborhood"' in index


def test_serve_graph_rejects_missing_graph(tmp_path) -> None:
    with pytest.raises(ValueError, match="Graph not found"):
        viewer.serve_graph(tmp_path / "missing.json", open_browser=False)


def test_serve_graph_rejects_oversized_file_and_in_memory_documents(
    tmp_path, monkeypatch
) -> None:
    graph = tmp_path / "graph.json"
    graph.write_text(_graph_document(), encoding="utf-8")
    monkeypatch.setattr(viewer, "MAX_GRAPH_DOCUMENT_BYTES", 1)
    with pytest.raises(ValueError, match="byte limit"):
        viewer.serve_graph(graph, open_browser=False)
    with pytest.raises(ValueError, match="byte limit"):
        viewer.serve_graph(None, graph_document=b"{}", open_browser=False)


def test_serve_graph_rejects_non_loopback_and_invalid_ports(tmp_path) -> None:
    graph = tmp_path / "graph.json"
    graph.write_text(_graph_document(), encoding="utf-8")
    with pytest.raises(ValueError, match="loopback"):
        viewer.serve_graph(graph, host="0.0.0.0", open_browser=False)
    with pytest.raises(ValueError, match="IPv4 loopback"):
        viewer.serve_graph(graph, host="::1", open_browser=False)
    with pytest.raises(ValueError, match="between 0 and 65535"):
        viewer.serve_graph(graph, port=65536, open_browser=False)
    with pytest.raises(ValueError, match="between 0 and 65535"):
        viewer.serve_graph(graph, port=True, open_browser=False)


def test_serve_graph_starts_and_closes_server(tmp_path, monkeypatch, capsys) -> None:
    graph = tmp_path / "graph.json"
    graph.write_text(_graph_document(), encoding="utf-8")

    class FakeServer:
        server_address = ("127.0.0.1", 1234)
        closed = False

        def __init__(self, address, handler):
            self.address = address
            self.handler = handler

        def serve_forever(self):
            raise KeyboardInterrupt

        def server_close(self):
            self.closed = True

    observed: dict[str, object] = {}
    fake = FakeServer(("127.0.0.1", 0), object)

    def fake_server(address, handler):
        observed["address"] = address
        observed["handler"] = handler
        return fake

    monkeypatch.setattr(viewer, "LoopbackHTTPServer", fake_server)
    viewer.serve_graph(graph, host="localhost", port=0, open_browser=False)
    assert fake.closed
    assert observed["address"] == ("127.0.0.1", 0)
    assert "http://127.0.0.1:1234" in capsys.readouterr().out


def test_localhost_alias_accepts_localhost_host_headers_and_rejects_foreign(
    monkeypatch,
) -> None:
    original_server = viewer.LoopbackHTTPServer
    ready = threading.Event()
    captured: dict[str, viewer.LoopbackHTTPServer] = {}

    class CapturingServer(original_server):
        def __init__(self, *args, **kwargs):  # noqa: ANN002, ANN003
            super().__init__(*args, **kwargs)
            captured["server"] = self
            ready.set()

    monkeypatch.setattr(viewer, "LoopbackHTTPServer", CapturingServer)
    thread = threading.Thread(
        target=lambda: viewer.serve_graph(
            None,
            host="localhost",
            port=0,
            open_browser=False,
            graph_document=_graph_document().encode("utf-8"),
        ),
        daemon=True,
    )
    thread.start()
    assert ready.wait(timeout=5)
    server = captured["server"]
    port = server.server_address[1]

    def response_status(host_header: str) -> int:
        connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
        try:
            connection.putrequest("GET", "/", skip_host=True)
            connection.putheader("Host", host_header)
            connection.endheaders()
            response = connection.getresponse()
            response.read()
            return response.status
        finally:
            connection.close()

    try:
        assert response_status("localhost") == 200
        assert response_status(f"LOCALHOST:{port}") == 200
        assert response_status(f"127.0.0.1:{port}") == 200
        assert response_status(f"localhost.invalid:{port}") == 421
    finally:
        server.shutdown()
        thread.join(timeout=5)
    assert not thread.is_alive()


def test_serve_graph_flushes_url_for_redirected_output(tmp_path, monkeypatch) -> None:
    graph = tmp_path / "graph.json"
    graph.write_text(_graph_document(), encoding="utf-8")

    class FakeServer:
        server_address = ("127.0.0.1", 4317)

        def __init__(self, address, handler):
            pass

        def serve_forever(self):
            raise KeyboardInterrupt

        def server_close(self):
            pass

    printed: list[tuple[str, bool]] = []

    def capture_print(value: str, *, flush: bool = False) -> None:
        printed.append((value, flush))

    monkeypatch.setattr(viewer, "LoopbackHTTPServer", FakeServer)
    monkeypatch.setattr(viewer, "print", capture_print, raising=False)

    viewer.serve_graph(graph, open_browser=False)

    assert printed == [
        ("IntentAtlas viewer: http://127.0.0.1:4317", True),
        ("Press Ctrl+C to stop.", True),
    ]


def test_loopback_server_binding_does_not_require_reverse_dns(monkeypatch) -> None:
    def reject_reverse_dns(host: str) -> str:
        raise AssertionError(f"unexpected reverse DNS lookup for {host}")

    monkeypatch.setattr(socket, "getfqdn", reject_reverse_dns)
    server = viewer.LoopbackHTTPServer(("127.0.0.1", 0), object)
    try:
        assert server.server_name == "127.0.0.1"
        assert server.server_port == server.server_address[1]
    finally:
        server.server_close()


def _connected_graph_document() -> bytes:
    graph = AtlasGraph()
    graph.add_node(Node(id="REQ-1", kind="requirement", label="Explain impact", path=None))
    graph.add_node(Node(id="file:src/app.py", kind="file", label="app.py", path="src/app.py"))
    graph.add_node(
        Node(
            id="file:tests/test_app.py",
            kind="test",
            label="test_app.py",
            path="tests/test_app.py",
        )
    )
    graph.add_edge(
        Edge(
            source="REQ-1",
            target="file:src/app.py",
            relation="implemented-by",
            evidence="wikilink",
        )
    )
    graph.add_edge(
        Edge(
            source="file:tests/test_app.py",
            target="file:src/app.py",
            relation="tests",
            evidence="python-ast",
        )
    )
    return json.dumps(graph.to_dict()).encode("utf-8")


class _RunningViewer:
    """Serve one in-memory graph on loopback for the duration of a test."""

    def __init__(self, monkeypatch, **options) -> None:  # noqa: ANN001, ANN003
        original = viewer.LoopbackHTTPServer
        ready = threading.Event()
        captured: dict[str, viewer.LoopbackHTTPServer] = {}

        class CapturingServer(original):
            def __init__(self, *args, **kwargs):  # noqa: ANN002, ANN003
                super().__init__(*args, **kwargs)
                captured["server"] = self
                ready.set()

        monkeypatch.setattr(viewer, "LoopbackHTTPServer", CapturingServer)
        self._thread = threading.Thread(
            target=lambda: viewer.serve_graph(None, port=0, open_browser=False, **options),
            daemon=True,
        )
        self._thread.start()
        assert ready.wait(timeout=5)
        self._server = captured["server"]
        self.port = self._server.server_address[1]

    def get(self, path: str) -> tuple[int, bytes]:
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        try:
            connection.request("GET", path)
            response = connection.getresponse()
            return response.status, response.read()
        finally:
            connection.close()

    def json(self, path: str) -> tuple[int, object]:
        status, body = self.get(path)
        return status, json.loads(body.decode("utf-8"))

    def close(self) -> None:
        self._server.shutdown()
        self._thread.join(timeout=5)


@pytest.fixture
def running_viewer(monkeypatch):  # noqa: ANN001, ANN201
    servers: list[_RunningViewer] = []

    def start(**options):  # noqa: ANN003, ANN202
        server = _RunningViewer(monkeypatch, **options)
        servers.append(server)
        return server

    yield start
    for server in servers:
        server.close()


def test_graph_query_routes_serve_the_served_snapshot(running_viewer) -> None:  # noqa: ANN001
    document = _connected_graph_document()
    server = running_viewer(graph_document=document)

    status, overview = server.json("/api/graph/overview")
    assert status == 200
    assert {node["id"] for node in overview["nodes"]} == {
        "REQ-1",
        "file:src/app.py",
        "file:tests/test_app.py",
    }

    status, search = server.json("/api/graph/search?q=test_app")
    assert status == 200
    assert any(node["id"] == "file:tests/test_app.py" for node in search["nodes"])

    status, neighborhood = server.json("/api/graph/neighborhood?id=file:src/app.py&depth=1")
    assert status == 200
    assert "file:src/app.py" in {node["id"] for node in neighborhood["nodes"]}

    status, paths = server.json("/api/graph/paths?start=REQ-1")
    assert status == 200
    assert any(
        path["destination"]["id"] == "file:tests/test_app.py" for path in paths["paths"]
    )

    status, raw = server.json("/graph.json")
    assert status == 200
    assert raw == json.loads(document.decode("utf-8"))


def test_unparsable_graph_document_fails_closed() -> None:
    with pytest.raises(ValueError, match="Cannot parse viewer graph"):
        viewer.serve_graph(None, graph_document=b"{not json", open_browser=False)
    with pytest.raises(ValueError, match="Cannot parse viewer graph"):
        viewer.serve_graph(None, graph_document=b"\xff\xfe", open_browser=False)


def test_malformed_graph_query_returns_a_bounded_error_not_a_traceback(
    running_viewer,
) -> None:  # noqa: ANN001
    server = running_viewer(graph_document=_connected_graph_document())

    for path in (
        "/api/graph/overview?node_limit=many",
        "/api/graph/overview?node_limit=-1",
        "/api/graph/overview?node_limit=1&node_limit=2",
        "/api/graph/search",
        "/api/graph/search?q=a&q=b",
        "/api/graph/neighborhood?id=file:src/app.py&depth=deep",
        "/api/graph/paths?start=REQ-1&visited_limit=%D9%A3",  # Arabic-Indic digit three
    ):
        status, payload = server.json(path)
        assert status == 400, path
        assert payload["schema_version"] == 1
        assert payload["error"]
        assert "Traceback" not in payload["error"]


def test_unknown_routes_are_refused(running_viewer) -> None:  # noqa: ANN001
    server = running_viewer(graph_document=_connected_graph_document())
    for path in ("/api/graph/unknown", "/nope", "/api/report/change", "/review.json"):
        status, _ = server.get(path)
        assert status == 404, path


def test_optional_report_endpoints_appear_only_when_supplied(running_viewer) -> None:  # noqa: ANN001
    change = json.dumps({"schema_version": 1, "kind": "change"}).encode("utf-8")
    review = json.dumps({"schema_version": 1, "kind": "review"}).encode("utf-8")
    server = running_viewer(
        graph_document=_connected_graph_document(),
        change_report_document=change,
        review_document=review,
    )
    for path in ("/api/report/change", "/change-report.json"):
        status, payload = server.json(path)
        assert (status, payload["kind"]) == (200, "change")
    for path in ("/api/report/review", "/review.json"):
        status, payload = server.json(path)
        assert (status, payload["kind"]) == (200, "review")


def test_packaged_assets_are_served_with_their_content_types(running_viewer) -> None:  # noqa: ANN001
    server = running_viewer(graph_document=_connected_graph_document())
    status, body = server.get("/")
    assert status == 200
    assert b"IntentAtlas" in body
    for route in ("/app.js", "/styles.css"):
        status, body = server.get(route)
        assert (status, bool(body)) == (200, True), route
