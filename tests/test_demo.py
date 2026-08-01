from __future__ import annotations

import json
from pathlib import Path

import pytest

import intentatlas.cli as cli
import intentatlas.demo as demo
from intentatlas.recommendations import recommend_tests


def test_demo_graph_is_deterministic_and_covers_intent_to_proof() -> None:
    first = demo.build_demo_graph()
    second = demo.build_demo_graph()

    assert list(first.nodes) == list(second.nodes)
    assert first.edges == second.edges
    assert len(first.nodes) == 9
    assert len(first.edges) == 13
    assert first.summary() == {
        "commit": 1,
        "decision": 1,
        "delivery-issue": 1,
        "evidence": 1,
        "file": 1,
        "pull-request": 1,
        "requirement": 1,
        "symbol": 1,
        "test": 1,
    }
    assert not first.orphans({"requirement", "decision", "evidence"})

    recommendation = recommend_tests(first, f"commit:{demo.DEMO_COMMIT_SHA}")
    assert [item.test.path for item in recommendation.recommendations] == ["tests/test_auth.py"]
    assert recommendation.recommendations[0].confidence == "medium"


def test_demo_uses_temporary_graph_and_cleans_it(monkeypatch) -> None:
    observed: dict[str, object] = {}

    def fake_serve(graph_path: Path, *, host: str, port: int, open_browser: bool) -> None:
        observed["path"] = graph_path
        observed["document"] = json.loads(graph_path.read_text(encoding="utf-8"))
        observed["options"] = (host, port, open_browser)

    monkeypatch.setattr(demo, "serve_graph", fake_serve)
    demo.serve_demo(host="localhost", port=0, open_browser=False)

    assert observed["options"] == ("localhost", 0, False)
    assert len(observed["document"]["edges"]) == 13
    assert not observed["path"].exists()


def test_demo_cli_and_viewer_boundaries(monkeypatch, capsys, tmp_path) -> None:
    calls: list[tuple[str, int, bool]] = []
    monkeypatch.setattr(
        cli,
        "serve_demo",
        lambda *, host, port, open_browser: calls.append((host, port, open_browser)),
    )
    assert cli.main(["demo", "--host", "localhost", "--port", "0", "--no-browser"]) == 0
    assert calls == [("localhost", 0, False)]

    graph = tmp_path / "graph.json"
    graph.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="loopback"):
        demo.serve_graph(graph, host="0.0.0.0", open_browser=False)
    with pytest.raises(ValueError, match="between 0 and 65535"):
        demo.serve_graph(graph, port=-1, open_browser=False)
    assert not capsys.readouterr().err
