from __future__ import annotations

import json
from pathlib import Path

import pytest

import intentatlas.cli as cli
import intentatlas.demo as demo
from intentatlas.graph import AtlasGraph
from intentatlas.models import Edge
from intentatlas.recommendations import recommend_tests


def test_demo_graph_is_deterministic_and_covers_intent_to_proof() -> None:
    first = demo.build_demo_graph()
    second = demo.build_demo_graph()

    assert list(first.nodes) == list(second.nodes)
    assert first.edges == second.edges
    assert len(first.nodes) == 12
    assert len(first.edges) == 18
    assert first.summary() == {
        "commit": 1,
        "decision": 1,
        "delivery-issue": 1,
        "evidence": 1,
        "file": 1,
        "pull-request": 1,
        "requirement": 2,
        "symbol": 2,
        "test": 2,
    }
    assert not first.orphans({"requirement", "decision", "evidence"})

    recommendation = recommend_tests(first, f"commit:{demo.DEMO_COMMIT_SHA}")
    assert [item.test.path for item in recommendation.recommendations] == [
        "tests/test_auth_rotation.py"
    ]
    assert recommendation.recommendations[0].confidence == "medium"
    assert "tests/test_auth_audit.py" not in {
        item.test.path for item in recommendation.recommendations
    }
    assert demo.DEMO_CHANGED_SYMBOL_ID == "symbol:src/auth.py::rotate_session"
    assert demo.DEMO_UNRELATED_SYMBOL_ID == "symbol:src/auth.py::record_login_audit"

    low_confidence = recommend_tests(
        first,
        demo.DEMO_COMMIT_ID,
        minimum_confidence="low",
    )
    assert [item.test.path for item in low_confidence.recommendations] == [
        "tests/test_auth_rotation.py"
    ]
    assert low_confidence.candidate_count == 1

    file_only = AtlasGraph()
    file_only.extend(
        first.nodes.values(),
        [
            edge
            for edge in first.edges
            if not (edge.source == demo.DEMO_COMMIT_ID and edge.relation == "modifies")
        ],
    )
    fallback = recommend_tests(file_only, demo.DEMO_COMMIT_ID, minimum_confidence="low")
    assert [(item.test.path, item.score) for item in fallback.recommendations] == [
        ("tests/test_auth_audit.py", 65),
        ("tests/test_auth_rotation.py", 65),
    ]


def test_demo_report_is_deterministic_and_exposes_same_file_boundary() -> None:
    first = demo.build_demo_report()
    second = demo.build_demo_report()

    assert first == second
    assert [node.id for node in first.same_file_requirements] == [
        "REQ-DEMO-001",
        "REQ-DEMO-002",
    ]
    assert [node.id for node in first.exact_symbol_requirements] == ["REQ-DEMO-001"]
    assert [item.test.path for item in first.recommendations.recommendations] == [
        "tests/test_auth_rotation.py"
    ]
    assert [node.path for node in first.same_file_tests_not_recommended] == [
        "tests/test_auth_audit.py"
    ]

    text = demo.render_demo_report(first)
    assert text == demo.render_demo_report(second)
    assert "Preserve login audit events" in text
    assert "Why: The test directly references an exactly modified symbol." in text
    assert f"Path: {demo.DEMO_COMMIT_ID} --modifies-->" in text
    assert "not recommended from available exact-symbol evidence" in text
    assert "not proven unaffected or unnecessary" in text

    payload = json.loads(demo.render_demo_report(first, "json"))
    assert payload["schema_version"] == 1
    assert payload["scenario"] == "same-file-exact-symbol"
    assert payload["requirements_with_exact_changed_symbol_evidence"][0]["id"] == "REQ-DEMO-001"
    assert payload["same_file_requirements_without_exact_changed_symbol_evidence"][0]["id"] == (
        "REQ-DEMO-002"
    )
    assert payload["same_file_tests_not_recommended"][0]["path"] == (
        "tests/test_auth_audit.py"
    )

    with pytest.raises(ValueError, match="Unknown demo report format"):
        demo.render_demo_report(first, "yaml")


def test_demo_report_derives_the_changed_symbol_from_the_graph() -> None:
    original = demo.build_demo_graph()
    changed = AtlasGraph()
    changed.extend(
        original.nodes.values(),
        [
            edge
            for edge in original.edges
            if not (edge.source == demo.DEMO_COMMIT_ID and edge.relation == "modifies")
        ],
    )
    assert changed.add_edge(
        Edge(
            demo.DEMO_COMMIT_ID,
            demo.DEMO_UNRELATED_SYMBOL_ID,
            "modifies",
            "demo-diff-hunk",
        )
    )

    report = demo._build_demo_report(changed)

    assert report.changed_symbol.id == demo.DEMO_UNRELATED_SYMBOL_ID
    assert [node.id for node in report.exact_symbol_requirements] == ["REQ-DEMO-002"]
    assert [item.test.path for item in report.recommendations.recommendations] == [
        "tests/test_auth_audit.py"
    ]


def test_demo_change_report_matches_the_terminal_recommendation() -> None:
    report = demo.build_demo_change_report()

    assert report.analysis.state == "analyzed"
    assert report.test_strategy == "targeted"
    assert report.analysis_coverage_complete is True
    assert [(item.requirement.id, item.confidence) for item in report.requirements] == [
        ("REQ-DEMO-001", "high")
    ]
    assert [(item.test.path, item.score) for item in report.tests] == [
        ("tests/test_auth_rotation.py", 80)
    ]
    assert report.test_candidate_count == 1


def test_demo_uses_temporary_graph_and_cleans_it(monkeypatch) -> None:
    observed: dict[str, object] = {}

    def fake_serve(
        graph_path: Path,
        *,
        host: str,
        port: int,
        open_browser: bool,
        change_report_document: bytes,
    ) -> None:
        observed["path"] = graph_path
        observed["document"] = json.loads(graph_path.read_text(encoding="utf-8"))
        observed["report"] = json.loads(change_report_document)
        observed["options"] = (host, port, open_browser)

    monkeypatch.setattr(demo, "serve_graph", fake_serve)
    demo.serve_demo(host="localhost", port=0, open_browser=False)

    assert observed["options"] == ("localhost", 0, False)
    assert len(observed["document"]["edges"]) == 18
    assert [item["test"]["path"] for item in observed["report"]["tests"]] == [
        "tests/test_auth_rotation.py"
    ]
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

    assert cli.main(["demo", "--report", "json"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["schema_version"] == 1
    assert report["same_file_tests_not_recommended"][0]["path"] == "tests/test_auth_audit.py"
    assert calls == [("localhost", 0, False)]

    graph = tmp_path / "graph.json"
    graph.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="loopback"):
        demo.serve_graph(graph, host="0.0.0.0", open_browser=False)
    with pytest.raises(ValueError, match="between 0 and 65535"):
        demo.serve_graph(graph, port=-1, open_browser=False)
    assert not capsys.readouterr().err
