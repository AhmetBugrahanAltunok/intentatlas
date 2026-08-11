from __future__ import annotations

import json
from pathlib import Path

import pytest

import intentatlas.evaluation as evaluation_module
from intentatlas.cli import main
from intentatlas.config import ProjectConfig
from intentatlas.evaluation import (
    EvaluationCase,
    EvaluationLabels,
    evaluate_recommendations,
    load_evaluation_labels,
    render_evaluation,
)
from intentatlas.graph import AtlasGraph
from intentatlas.models import Edge, Node


def evaluation_graph() -> AtlasGraph:
    graph = AtlasGraph()
    graph.extend(
        [
            Node("commit:change", "commit", "Change login"),
            Node("file:src/auth.py", "file", "src/auth.py", path="src/auth.py"),
            Node("file:src/empty.py", "file", "src/empty.py", path="src/empty.py"),
            Node(
                "file:tests/test_changed.py",
                "test",
                "tests/test_changed.py",
                path="tests/test_changed.py",
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
            Node("REQ-X", "requirement", "Unsupported"),
        ],
        [
            Edge("commit:change", "file:src/auth.py", "changes", "git-log"),
            Edge("commit:change", "file:tests/test_changed.py", "changes", "git-log"),
            Edge("file:tests/test_auth.py", "file:src/auth.py", "tests", "python-ast"),
            Edge(
                "file:tests/auth_test.py",
                "file:src/auth.py",
                "tests",
                "filename-convention",
            ),
        ],
    )
    return graph


def write_labels(path: Path, *, cases: list[dict[str, object]] | None = None) -> None:
    document = {
        "schema_version": 1,
        "name": "Reviewed baseline",
        "label_policy": "complete-test-set",
        "cases": cases
        or [
            {
                "id": "change",
                "target": "commit:change",
                "expected_tests": ["tests/auth_test.py", "tests/test_changed.py"],
            }
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document), encoding="utf-8")


def test_load_evaluate_and_render_deterministically(tmp_path) -> None:
    labels_path = tmp_path / "labels.json"
    write_labels(labels_path)
    labels = load_evaluation_labels(labels_path)

    assert labels.cases[0].expected_tests == (
        "tests/auth_test.py",
        "tests/test_changed.py",
    )
    result = evaluate_recommendations(evaluation_graph(), labels)
    case = result.cases[0]
    assert case.recommended_tests == ("tests/test_changed.py", "tests/test_auth.py")
    assert case.true_positives == ("tests/test_changed.py",)
    assert case.false_positives == ("tests/test_auth.py",)
    assert case.false_negatives == ("tests/auth_test.py",)
    assert (case.precision, case.recall) == (0.5, 0.5)
    assert result.totals.to_dict() == {
        "case_count": 1,
        "expected_count": 2,
        "recommendation_count": 2,
        "true_positive_count": 1,
        "false_positive_count": 1,
        "false_negative_count": 1,
        "precision": 0.5,
        "recall": 0.5,
    }

    first = render_evaluation(result, "json")
    assert first == render_evaluation(result, "json")
    value = json.loads(first)
    assert value["schema_version"] == 1
    assert value["cases"][0]["false_positives"] == ["tests/test_auth.py"]
    text = render_evaluation(result)
    assert "Micro precision: 50.00%" in text
    assert "False negatives: tests/auth_test.py" in text
    assert "does not prove accuracy" in text


def test_evaluation_preserves_undefined_metrics() -> None:
    labels = EvaluationLabels(
        name="Empty baseline",
        cases=(EvaluationCase("empty", "file:src/empty.py", ()),),
    )
    result = evaluate_recommendations(evaluation_graph(), labels)

    assert result.cases[0].precision is None
    assert result.cases[0].recall is None
    assert result.totals.precision is None
    assert result.totals.recall is None
    assert json.loads(render_evaluation(result, "json"))["totals"]["precision"] is None
    assert "Micro precision: n/a" in render_evaluation(result)


@pytest.mark.parametrize(
    ("update", "message"),
    [
        ({"schema_version": True}, "Unsupported evaluation label schema"),
        ({"schema_version": 2}, "Unsupported evaluation label schema"),
        ({"label_policy": "known-positives"}, "label_policy"),
        ({"extra": True}, "Unknown evaluation labels field"),
        ({"cases": []}, "non-empty list"),
        ({"cases": ["bad"]}, "case must be an object"),
        (
            {
                "cases": [
                    {
                        "id": "unsafe",
                        "target": "commit:change",
                        "expected_tests": ["../test_auth.py"],
                    }
                ]
            },
            "Unsafe expected test path",
        ),
    ],
)
def test_label_parser_rejects_invalid_documents(tmp_path, update, message) -> None:
    path = tmp_path / "labels.json"
    write_labels(path)
    document = json.loads(path.read_text(encoding="utf-8"))
    document.update(update)
    path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        load_evaluation_labels(path)


def test_label_parser_rejects_duplicates_symlinks_and_bounds(tmp_path, monkeypatch) -> None:
    duplicate_key = tmp_path / "duplicate-key.json"
    duplicate_key.write_text(
        '{"schema_version":1,"schema_version":1,"name":"x",'
        '"label_policy":"complete-test-set","cases":[]}',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Duplicate JSON key"):
        load_evaluation_labels(duplicate_key)

    duplicate_case = tmp_path / "duplicate-case.json"
    record = {"id": "same", "target": "commit:change", "expected_tests": []}
    write_labels(duplicate_case, cases=[record, record])
    with pytest.raises(ValueError, match="Duplicate evaluation case ID"):
        load_evaluation_labels(duplicate_case)

    duplicate_target = tmp_path / "duplicate-target.json"
    write_labels(
        duplicate_target,
        cases=[
            {"id": "one", "target": "commit:change", "expected_tests": []},
            {"id": "two", "target": "commit:change", "expected_tests": []},
        ],
    )
    with pytest.raises(ValueError, match="Duplicate evaluation target"):
        load_evaluation_labels(duplicate_target)

    duplicate_test = tmp_path / "duplicate-test.json"
    write_labels(
        duplicate_test,
        cases=[
            {
                "id": "duplicate-test",
                "target": "commit:change",
                "expected_tests": ["tests/test_auth.py", "tests/test_auth.py"],
            }
        ],
    )
    with pytest.raises(ValueError, match="Duplicate expected test"):
        load_evaluation_labels(duplicate_test)

    bounded = tmp_path / "bounded.json"
    write_labels(bounded)
    monkeypatch.setattr(evaluation_module, "MAX_EVALUATION_CASES", 0)
    with pytest.raises(ValueError, match="0-case limit"):
        load_evaluation_labels(bounded)
    monkeypatch.setattr(evaluation_module, "MAX_EVALUATION_CASES", 500)
    monkeypatch.setattr(evaluation_module, "MAX_EXPECTED_TESTS_PER_CASE", 0)
    with pytest.raises(ValueError, match="0-test limit"):
        load_evaluation_labels(bounded)

    labels_path = tmp_path / "labels.json"
    write_labels(labels_path)
    original_is_symlink = Path.is_symlink
    monkeypatch.setattr(
        Path,
        "is_symlink",
        lambda self: self == labels_path or original_is_symlink(self),
    )
    with pytest.raises(ValueError, match="symbolic link"):
        load_evaluation_labels(labels_path)

    monkeypatch.setattr(Path, "is_symlink", original_is_symlink)
    monkeypatch.setattr(evaluation_module, "MAX_EXPECTED_TESTS_PER_CASE", 1_000)
    monkeypatch.setattr(evaluation_module, "MAX_LABEL_BYTES", 1)
    with pytest.raises(ValueError, match="1-byte limit"):
        load_evaluation_labels(labels_path)


def test_evaluation_rejects_stale_or_invalid_graph_labels() -> None:
    graph = evaluation_graph()
    with pytest.raises(ValueError, match="Run `scan` first.*git_history_limit"):
        evaluate_recommendations(
            graph,
            EvaluationLabels("x", (EvaluationCase("missing", "commit:missing", ()),)),
        )
    with pytest.raises(ValueError, match="Unsupported evaluation target kind"):
        evaluate_recommendations(
            graph,
            EvaluationLabels("x", (EvaluationCase("requirement", "REQ-X", ()),)),
        )
    with pytest.raises(ValueError, match="Run `scan` first.*refresh the reviewed labels"):
        evaluate_recommendations(
            graph,
            EvaluationLabels(
                "x",
                (EvaluationCase("test", "commit:change", ("tests/missing.py",)),),
            ),
        )
    with pytest.raises(ValueError, match="between 1 and 100"):
        evaluate_recommendations(
            graph,
            EvaluationLabels("x", (EvaluationCase("change", "commit:change", ()),)),
            limit=0,
        )
    with pytest.raises(ValueError, match="Unknown minimum confidence"):
        evaluate_recommendations(
            graph,
            EvaluationLabels("x", (EvaluationCase("change", "commit:change", ()),)),
            minimum_confidence="certain",
        )
    result = evaluate_recommendations(
        graph,
        EvaluationLabels("x", (EvaluationCase("change", "commit:change", ()),)),
    )
    with pytest.raises(ValueError, match="Unknown evaluation output format"):
        render_evaluation(result, "yaml")


def test_evaluation_cli_json_and_path_boundaries(tmp_path, capsys) -> None:
    ProjectConfig().save_if_missing(tmp_path)
    evaluation_graph().save(tmp_path / ".intentatlas" / "graph.json")
    labels_path = tmp_path / "benchmarks" / "labels.json"
    write_labels(labels_path)

    args = [
        "evaluate-recommendations",
        "benchmarks/labels.json",
        str(tmp_path),
        "--minimum-confidence",
        "high",
        "--limit",
        "1",
        "--format",
        "json",
    ]
    assert main(args) == 0
    output = capsys.readouterr().out
    assert output == render_evaluation(
        evaluate_recommendations(
            evaluation_graph(),
            load_evaluation_labels(labels_path),
            minimum_confidence="high",
            limit=1,
        ),
        "json",
    )
    assert json.loads(output)["totals"]["recall"] == 0.5

    assert main(["evaluate-recommendations", "../labels.json", str(tmp_path)]) == 2
    assert "below the project root" in capsys.readouterr().err

    private = tmp_path / "atlas" / "Private" / "labels.json"
    write_labels(private)
    assert (
        main(
            [
                "evaluate-recommendations",
                "atlas/Private/labels.json",
                str(tmp_path),
            ]
        )
        == 2
    )
    assert "may not be inside atlas/Private" in capsys.readouterr().err
