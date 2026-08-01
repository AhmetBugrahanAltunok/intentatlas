from __future__ import annotations

import socket
from importlib.resources import files

import pytest

import intentatlas.viewer as viewer


def test_viewer_assets_are_packaged() -> None:
    web = files("intentatlas.web")
    assert "IntentAtlas" in web.joinpath("index.html").read_text(encoding="utf-8")
    assert "--accent" in web.joinpath("styles.css").read_text(encoding="utf-8")
    app = web.joinpath("app.js").read_text(encoding="utf-8")
    assert 'fetch("/graph.json"' in app
    assert 'fetch("/review.json"' in app
    assert 'fetch("/change-report.json"' in app
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
    assert "findEvidencePaths(node.id)" in app
    assert 'const pathLimits = { depth: 6, visited: 800, results: 6 };' in app
    assert "edge.inverse || edge.relation" in app
    assert "No bounded evidence path found." in app
    assert "function bindFocusButton(button)" in app
    assert "state.pathAdjacency = buildPathAdjacency();" in app
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
    assert 'id="overview"' in index
    assert 'id="window-status"' in index
    assert 'id="focus-neighborhood"' in index


def test_serve_graph_rejects_missing_graph(tmp_path) -> None:
    with pytest.raises(ValueError, match="Graph not found"):
        viewer.serve_graph(tmp_path / "missing.json", open_browser=False)


def test_serve_graph_rejects_non_loopback_and_invalid_ports(tmp_path) -> None:
    graph = tmp_path / "graph.json"
    graph.write_text("{}", encoding="utf-8")
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
    graph.write_text("{}", encoding="utf-8")

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
