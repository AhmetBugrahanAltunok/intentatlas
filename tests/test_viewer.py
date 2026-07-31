from __future__ import annotations

from importlib.resources import files

import pytest

import intentatlas.viewer as viewer


def test_viewer_assets_are_packaged() -> None:
    web = files("intentatlas.web")
    assert "IntentAtlas" in web.joinpath("index.html").read_text(encoding="utf-8")
    assert "--accent" in web.joinpath("styles.css").read_text(encoding="utf-8")
    app = web.joinpath("app.js").read_text(encoding="utf-8")
    assert 'fetch("/graph.json"' in app
    pointerup = app.split('group.addEventListener("pointerup"', maxsplit=1)[1].split(
        'group.addEventListener("pointercancel"', maxsplit=1
    )[0]
    assert "if (!moved) selectNode(node.id);" in pointerup
    assert 'group.addEventListener("click", () => { if (!moved) selectNode(node.id); });' in app
    assert "edge.inverse || edge.relation" in app
    assert 'issue: "#f97316"' in app
    assert '"delivery-issue": "#fb923c"' in app
    assert '"pull-request": "#facc15"' in app


def test_serve_graph_rejects_missing_graph(tmp_path) -> None:
    with pytest.raises(ValueError, match="Graph not found"):
        viewer.serve_graph(tmp_path / "missing.json", open_browser=False)


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

    fake = FakeServer(("127.0.0.1", 0), object)
    monkeypatch.setattr(viewer, "ThreadingHTTPServer", lambda address, handler: fake)
    viewer.serve_graph(graph, port=0, open_browser=False)
    assert fake.closed
    assert "http://127.0.0.1:1234" in capsys.readouterr().out
