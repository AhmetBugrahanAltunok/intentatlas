from __future__ import annotations

import json

import pytest

import intentatlas.recommendations as recommendations_module
from intentatlas.cli import main
from intentatlas.config import ProjectConfig
from intentatlas.graph import AtlasGraph
from intentatlas.models import Edge, Node
from intentatlas.recommendations import recommend_tests, render_recommendations


def recommendation_graph() -> AtlasGraph:
    graph = AtlasGraph()
    graph.extend(
        [
            Node("commit:abc", "commit", "change authentication", metadata={"owner": "scanner"}),
            Node("file:src/auth.py", "file", "src/auth.py", path="src/auth.py"),
            Node("file:src/billing.py", "file", "src/billing.py", path="src/billing.py"),
            Node("file:src/util.py", "file", "src/util.py", path="src/util.py"),
            Node(
                "symbol:src/auth.py::login",
                "symbol",
                "login",
                path="src/auth.py",
                metadata={"line": 1, "end_line": 2, "owner": "scanner"},
            ),
            Node(
                "file:tests/test_auth.py",
                "test",
                "tests/test_auth.py",
                path="tests/test_auth.py",
            ),
            Node(
                "file:tests/auth_test.py",
                "test",
                "tests/auth_test.py",
                path="tests/auth_test.py",
            ),
            Node(
                "file:tests/test_billing.py",
                "test",
                "tests/test_billing.py",
                path="tests/test_billing.py",
            ),
            Node(
                "file:tests/test_util.py",
                "test",
                "tests/test_util.py",
                path="tests/test_util.py",
            ),
            Node(
                "file:tests/test_changed.py",
                "test",
                "tests/test_changed.py",
                path="tests/test_changed.py",
            ),
            Node(
                "test-result:report:auth",
                "test-result",
                "Test results auth",
                metadata={
                    "report": "reports/junit.xml",
                    "total": 3,
                    "passed": 2,
                    "failed": 1,
                    "errors": 0,
                    "skipped": 0,
                    "duration_seconds": 0.25,
                    "owner": "scanner",
                },
            ),
            Node("REQ-X", "requirement", "Unsupported target"),
        ],
        [
            Edge(
                "commit:abc",
                "symbol:src/auth.py::login",
                "modifies",
                "git-diff-hunk",
            ),
            Edge("commit:abc", "file:src/auth.py", "changes", "git-log"),
            Edge("commit:abc", "file:src/billing.py", "changes", "git-log"),
            Edge("commit:abc", "file:src/util.py", "changes", "git-log"),
            Edge("commit:abc", "file:tests/test_changed.py", "changes", "git-log"),
            Edge(
                "file:src/auth.py",
                "symbol:src/auth.py::login",
                "defines",
                "python-ast",
            ),
            Edge("file:tests/test_auth.py", "file:src/auth.py", "tests", "python-ast"),
            Edge(
                "file:tests/test_auth.py",
                "symbol:src/auth.py::login",
                "tests",
                "python-ast",
            ),
            Edge(
                "file:tests/auth_test.py",
                "file:src/auth.py",
                "tests",
                "filename-convention",
            ),
            Edge(
                "file:tests/test_billing.py",
                "file:src/billing.py",
                "tests",
                "filename-convention",
            ),
            Edge("file:tests/test_util.py", "file:src/util.py", "tests", "python-ast"),
            Edge(
                "test-result:report:auth",
                "file:tests/test_auth.py",
                "proves",
                "junit-xml",
            ),
        ],
    )
    return graph


def test_recommendations_rank_deduplicate_filter_and_explain() -> None:
    result = recommend_tests(recommendation_graph(), "commit:abc")

    assert result.candidate_count == 4
    assert [(item.test.id, item.score, item.confidence) for item in result.recommendations] == [
        ("file:tests/test_changed.py", 100, "high"),
        ("file:tests/test_auth.py", 80, "medium"),
        ("file:tests/test_util.py", 65, "medium"),
    ]
    auth = result.recommendations[1]
    assert auth.reason_count == 1
    assert auth.reasons_truncated is False
    assert [reason.score for reason in auth.reasons] == [80]
    assert auth.reasons[0].path.nodes == (
        "commit:abc",
        "symbol:src/auth.py::login",
        "file:tests/test_auth.py",
    )
    assert auth.reasons[0].path.relations == ("modifies", "tested-by")
    assert auth.reasons[0].evidence == ("git-diff-hunk", "python-ast")
    assert auth.observations[0].report == "reports/junit.xml"
    assert auth.observation_count == 1
    assert auth.observations_truncated is False
    assert auth.observations[0].passed == 2


def test_recommendations_support_low_limit_file_symbol_and_no_results() -> None:
    graph = recommendation_graph()
    low = recommend_tests(graph, "file:src/billing.py", minimum_confidence="low")
    assert [(item.test.id, item.score) for item in low.recommendations] == [
        ("file:tests/test_billing.py", 45)
    ]

    symbol = recommend_tests(graph, "symbol:src/auth.py::login", limit=1)
    assert [(item.test.id, item.score) for item in symbol.recommendations] == [
        ("file:tests/test_auth.py", 80)
    ]

    empty = recommend_tests(graph, "file:src/billing.py", minimum_confidence="high")
    rendered = render_recommendations(empty)
    assert empty.candidate_count == 1
    assert empty.recommendations == ()
    assert "No test recommendations" in rendered
    assert "Lower-confidence candidates available: 1" in rendered


def test_recommendations_focus_nested_symbols_and_latest_file_change() -> None:
    graph = AtlasGraph()
    graph.extend(
        [
            Node(
                "commit:latest",
                "commit",
                "latest",
                metadata={"date": "2026-01-02", "owner": "scanner"},
            ),
            Node("file:src/core.py", "file", "src/core.py", path="src/core.py"),
            Node(
                "symbol:src/core.py::Context",
                "symbol",
                "Context",
                path="src/core.py",
            ),
            Node(
                "symbol:src/core.py::Context.close",
                "symbol",
                "Context.close",
                path="src/core.py",
            ),
            Node(
                "file:tests/test_context.py",
                "test",
                "tests/test_context.py",
                path="tests/test_context.py",
            ),
            Node(
                "file:tests/test_other.py",
                "test",
                "tests/test_other.py",
                path="tests/test_other.py",
            ),
        ],
        [
            Edge("commit:latest", "file:src/core.py", "changes", "git-log"),
            Edge(
                "commit:latest",
                "symbol:src/core.py::Context.close",
                "modifies",
                "git-diff-hunk",
            ),
            Edge(
                "file:src/core.py",
                "symbol:src/core.py::Context",
                "defines",
                "python-ast",
            ),
            Edge(
                "file:src/core.py",
                "symbol:src/core.py::Context.close",
                "defines",
                "python-ast",
            ),
            Edge(
                "file:tests/test_context.py",
                "symbol:src/core.py::Context",
                "tests",
                "python-symbol-reference",
            ),
            Edge(
                "file:tests/test_other.py",
                "symbol:src/core.py::Context",
                "tests",
                "python-symbol-reference",
            ),
        ],
    )

    result = recommend_tests(graph, "file:src/core.py")

    assert [item.test.id for item in result.recommendations] == [
        "file:tests/test_context.py"
    ]
    reason = result.recommendations[0].reasons[0]
    assert reason.signal == "symbol-structural-test"
    assert "owned-by" in reason.path.relations
    assert "owner-name-convention" in reason.evidence


def test_recommendations_use_exact_direct_dependents_and_recent_cochange(monkeypatch) -> None:
    graph = AtlasGraph()
    graph.extend(
        [
            Node(
                "commit:latest",
                "commit",
                "latest",
                metadata={"date": "2026-01-02", "owner": "scanner"},
            ),
            Node("file:src/helper.js", "file", "src/helper.js", path="src/helper.js"),
            Node("file:src/core.js", "file", "src/core.js", path="src/core.js"),
            Node(
                "symbol:src/helper.js::normalize",
                "symbol",
                "normalize",
                path="src/helper.js",
            ),
            Node(
                "file:tests/core.test.js",
                "test",
                "tests/core.test.js",
                path="tests/core.test.js",
            ),
            Node(
                "file:tests/integration.test.js",
                "test",
                "tests/integration.test.js",
                path="tests/integration.test.js",
            ),
        ],
        [
            Edge("commit:latest", "file:src/helper.js", "changes", "git-log"),
            Edge("commit:latest", "file:tests/integration.test.js", "changes", "git-log"),
            Edge(
                "file:src/helper.js",
                "symbol:src/helper.js::normalize",
                "defines",
                "javascript-structural",
            ),
            Edge(
                "file:src/core.js",
                "symbol:src/helper.js::normalize",
                "imports",
                "javascript-symbol-reference",
            ),
            Edge(
                "file:tests/core.test.js",
                "file:src/core.js",
                "tests",
                "javascript-structural",
            ),
        ],
    )

    result = recommend_tests(graph, "symbol:src/helper.js::normalize")

    assert [(item.test.id, item.score) for item in result.recommendations] == [
        ("file:tests/core.test.js", 65),
    ]
    dependent = result.recommendations[0].reasons[0]
    assert dependent.signal == "direct-symbol-dependent-test"
    assert dependent.path.relations[-2:] == ("imported-by", "tested-by")

    low = recommend_tests(
        graph,
        "symbol:src/helper.js::normalize",
        minimum_confidence="low",
    )
    assert [(item.test.id, item.score, item.confidence) for item in low.recommendations] == [
        ("file:tests/core.test.js", 65, "medium"),
        ("file:tests/integration.test.js", 60, "low"),
    ]

    monkeypatch.setattr(recommendations_module, "MAX_DIRECT_SYMBOL_DEPENDENTS", 0)
    with pytest.raises(ValueError, match="0-direct-dependent limit"):
        recommend_tests(graph, "symbol:src/helper.js::normalize")


def test_recommendations_reject_unsupported_targets_and_bounds() -> None:
    graph = recommendation_graph()
    with pytest.raises(ValueError, match="support commit, file, symbol, or test"):
        recommend_tests(graph, "REQ-X")
    with pytest.raises(ValueError, match="between 1 and 100"):
        recommend_tests(graph, "commit:abc", limit=0)
    with pytest.raises(ValueError, match="Unknown minimum confidence"):
        recommend_tests(graph, "commit:abc", minimum_confidence="certain")


def test_recommendations_bound_input_and_explanation_output(monkeypatch) -> None:
    graph = recommendation_graph()
    monkeypatch.setattr(recommendations_module, "MAX_ARTIFACT_SIGNALS", 1)
    with pytest.raises(ValueError, match="1-artifact signal limit"):
        recommend_tests(graph, "commit:abc")

    monkeypatch.setattr(recommendations_module, "MAX_ARTIFACT_SIGNALS", 1_000)
    monkeypatch.setattr(recommendations_module, "MAX_CANDIDATE_TESTS", 1)
    with pytest.raises(ValueError, match="1-test candidate limit"):
        recommend_tests(graph, "commit:abc")

    monkeypatch.setattr(recommendations_module, "MAX_CANDIDATE_TESTS", 10_000)
    monkeypatch.setattr(recommendations_module, "MAX_REASONS_PER_TEST", 0)
    monkeypatch.setattr(recommendations_module, "MAX_OBSERVATIONS_PER_TEST", 0)
    result = recommend_tests(graph, "commit:abc")
    auth = next(item for item in result.recommendations if item.test.id.endswith("test_auth.py"))
    assert auth.reason_count == 1
    assert auth.reasons_truncated is True
    assert auth.observation_count == 1
    assert auth.observations_truncated is True
    rendered = render_recommendations(result)
    assert "Additional reasons omitted: 1" in rendered
    assert "Additional observations omitted: 1" in rendered


def test_recommendation_json_and_cli_are_deterministic(tmp_path, capsys) -> None:
    graph = recommendation_graph()
    result = recommend_tests(graph, "commit:abc", minimum_confidence="low")
    first = render_recommendations(result, "json")
    second = render_recommendations(result, "json")
    assert first == second
    value = json.loads(first)
    assert value["schema_version"] == 1
    assert value["candidate_count"] == 4
    assert "not proof" in value["advisory"]

    ProjectConfig().save_if_missing(tmp_path)
    graph.save(tmp_path / ".intentatlas" / "graph.json")
    assert (
        main(
            [
                "recommend-tests",
                "commit:abc",
                str(tmp_path),
                "--minimum-confidence",
                "high",
                "--limit",
                "1",
                "--format",
                "json",
            ]
        )
        == 0
    )
    cli_value = json.loads(capsys.readouterr().out)
    assert cli_value["minimum_confidence"] == "high"
    assert [item["test"]["id"] for item in cli_value["recommendations"]] == [
        "file:tests/test_changed.py"
    ]

    assert (
        main(["recommend-tests", "commit:abc", str(tmp_path), "--limit", "0"])
        == 2
    )
    assert "between 1 and 100" in capsys.readouterr().err
    assert main(["recommend-tests", "REQ-X", str(tmp_path)]) == 2
    assert "support commit, file, symbol, or test" in capsys.readouterr().err
