from __future__ import annotations

import json
from pathlib import Path

import pytest

import intentatlas.cli as cli_module
import intentatlas.corpus as corpus_module
from intentatlas.cli import main
from intentatlas.corpus import (
    CorpusManifestProject,
    CorpusProject,
    evaluate_corpus,
    load_corpus_manifest,
    render_corpus,
    validate_corpus_graph_size,
)
from intentatlas.evaluation import EvaluationCase, EvaluationLabels, load_evaluation_labels
from intentatlas.graph import AtlasGraph

ROOT = Path(__file__).parents[1]
CORPUS_PATH = ROOT / "benchmarks" / "recommendation-corpus.json"


def write_manifest(
    path: Path,
    *,
    projects: list[dict[str, object]] | None = None,
) -> None:
    document = {
        "schema_version": 1,
        "name": "Test corpus",
        "projects": projects
        or [
            {
                "id": "sample",
                "name": "Sample project",
                "graph": "benchmarks/sample.graph.json",
                "labels": "benchmarks/sample.labels.json",
            }
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document), encoding="utf-8")


def load_original_projects() -> tuple[CorpusProject, ...]:
    manifest = load_corpus_manifest(CORPUS_PATH)
    return tuple(
        CorpusProject(
            entry.id,
            entry.name,
            AtlasGraph.load(ROOT / entry.graph),
            load_evaluation_labels(ROOT / entry.labels),
        )
        for entry in manifest.projects
    )


def test_original_corpus_compares_all_thresholds_deterministically(capsys) -> None:
    manifest = load_corpus_manifest(CORPUS_PATH)
    assert [project.id for project in manifest.projects] == [
        "go-package",
        "python-auth",
        "typescript-checkout",
    ]
    result = evaluate_corpus(manifest.name, load_original_projects())

    assert result.project_count == 3
    assert result.case_count == 3
    assert [threshold.minimum_confidence for threshold in result.thresholds] == [
        "low",
        "medium",
        "high",
    ]
    assert [threshold.totals.to_dict() for threshold in result.thresholds] == [
        {
            "case_count": 3,
            "expected_count": 4,
            "recommendation_count": 6,
            "true_positive_count": 4,
            "false_positive_count": 2,
            "false_negative_count": 0,
            "precision": 0.666667,
            "recall": 1.0,
        },
        {
            "case_count": 3,
            "expected_count": 4,
            "recommendation_count": 5,
            "true_positive_count": 4,
            "false_positive_count": 1,
            "false_negative_count": 0,
            "precision": 0.8,
            "recall": 1.0,
        },
        {
            "case_count": 3,
            "expected_count": 4,
            "recommendation_count": 2,
            "true_positive_count": 2,
            "false_positive_count": 0,
            "false_negative_count": 2,
            "precision": 1.0,
            "recall": 0.5,
        },
    ]
    typescript_high = result.thresholds[2].projects[2]
    assert typescript_high.precision is None
    assert typescript_high.recall == 0.0

    rendered = render_corpus(result, "json")
    assert rendered == render_corpus(result, "json")
    assert json.loads(rendered)["schema_version"] == 1
    text = render_corpus(result)
    assert "precision n/a, recall 0.00%" in text
    assert "do not prove accuracy" in text

    assert main(["evaluate-corpus", "benchmarks/recommendation-corpus.json", str(ROOT)]) == 0
    assert capsys.readouterr().out == text
    assert (
        main(
            [
                "evaluate-corpus",
                "benchmarks/recommendation-corpus.json",
                str(ROOT),
                "--format",
                "json",
            ]
        )
        == 0
    )
    assert json.loads(capsys.readouterr().out)["thresholds"][1]["totals"]["precision"] == 0.8


@pytest.mark.parametrize(
    ("update", "message"),
    [
        ({"schema_version": True}, "Unsupported corpus manifest schema"),
        ({"schema_version": 2}, "Unsupported corpus manifest schema"),
        ({"extra": True}, "Unknown corpus manifest field"),
        ({"projects": []}, "non-empty list"),
        ({"projects": ["bad"]}, "project must be an object"),
        (
            {
                "projects": [
                    {
                        "id": "unsafe",
                        "name": "Unsafe",
                        "graph": "../graph.json",
                        "labels": "labels.json",
                    }
                ]
            },
            "Unsafe corpus graph path",
        ),
    ],
)
def test_manifest_parser_rejects_invalid_documents(tmp_path, update, message) -> None:
    path = tmp_path / "corpus.json"
    write_manifest(path)
    document = json.loads(path.read_text(encoding="utf-8"))
    document.update(update)
    path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        load_corpus_manifest(path)


@pytest.mark.parametrize(
    ("projects", "message"),
    [
        (
            [
                {"id": "same", "name": "One", "graph": "one.json", "labels": "a.json"},
                {"id": "same", "name": "Two", "graph": "two.json", "labels": "b.json"},
            ],
            "Duplicate corpus project ID",
        ),
        (
            [
                {"id": "one", "name": "One", "graph": "same.json", "labels": "a.json"},
                {"id": "two", "name": "Two", "graph": "same.json", "labels": "b.json"},
            ],
            "Duplicate corpus graph path",
        ),
        (
            [
                {"id": "one", "name": "One", "graph": "one.json", "labels": "same.json"},
                {"id": "two", "name": "Two", "graph": "two.json", "labels": "same.json"},
            ],
            "Duplicate corpus label path",
        ),
        (
            [
                {"id": "same", "name": "Same", "graph": "same.json", "labels": "same.json"}
            ],
            "graph and labels must differ",
        ),
    ],
)
def test_manifest_parser_rejects_duplicate_identity_paths(tmp_path, projects, message) -> None:
    path = tmp_path / "corpus.json"
    write_manifest(path, projects=projects)
    with pytest.raises(ValueError, match=message):
        load_corpus_manifest(path)


def test_manifest_and_graph_files_are_bounded_and_symlink_safe(tmp_path, monkeypatch) -> None:
    manifest_path = tmp_path / "corpus.json"
    write_manifest(manifest_path)
    original_is_symlink = Path.is_symlink
    monkeypatch.setattr(
        Path,
        "is_symlink",
        lambda self: self == manifest_path or original_is_symlink(self),
    )
    with pytest.raises(ValueError, match="symbolic link"):
        load_corpus_manifest(manifest_path)

    monkeypatch.setattr(Path, "is_symlink", original_is_symlink)
    monkeypatch.setattr(corpus_module, "MAX_CORPUS_BYTES", 1)
    with pytest.raises(ValueError, match="1-byte limit"):
        load_corpus_manifest(manifest_path)

    graph_path = ROOT / "benchmarks" / "corpus" / "go-package.graph.json"
    monkeypatch.setattr(corpus_module, "MAX_CORPUS_GRAPH_BYTES", 1)
    with pytest.raises(ValueError, match="1-byte limit"):
        validate_corpus_graph_size(graph_path)


def test_corpus_engine_rejects_bounds_duplicates_and_stale_projects(monkeypatch) -> None:
    project = load_original_projects()[0]
    with pytest.raises(ValueError, match="at least one project"):
        evaluate_corpus("Empty", ())
    with pytest.raises(ValueError, match="between 1 and 100"):
        evaluate_corpus("Invalid limit", (project,), limit=0)
    with pytest.raises(ValueError, match="project IDs must be unique"):
        evaluate_corpus("Duplicate", (project, project))

    empty = CorpusProject(project.id, project.name, project.graph, EvaluationLabels("Empty", ()))
    with pytest.raises(ValueError, match="at least one evaluation case"):
        evaluate_corpus("Empty cases", (empty,))

    monkeypatch.setattr(corpus_module, "MAX_CORPUS_CASES", 0)
    with pytest.raises(ValueError, match="0-case limit"):
        evaluate_corpus("Too many cases", (project,))

    stale = CorpusProject(
        "stale",
        "Stale",
        project.graph,
        EvaluationLabels("Stale", (EvaluationCase("missing", "commit:missing", ()),)),
    )
    monkeypatch.setattr(corpus_module, "MAX_CORPUS_CASES", 2_000)
    with pytest.raises(ValueError, match="Corpus project stale failed"):
        evaluate_corpus("Stale", (stale,))

    result = evaluate_corpus("Valid", (project,))
    with pytest.raises(ValueError, match="Unknown corpus output format"):
        render_corpus(result, "yaml")


def test_corpus_cli_rejects_unsafe_and_private_paths(tmp_path, capsys) -> None:
    assert main(["init", str(tmp_path)]) == 0
    assert main(["evaluate-corpus", "../corpus.json", str(tmp_path)]) == 2
    assert "below the project root" in capsys.readouterr().err

    private = tmp_path / "atlas" / "Private" / "corpus.json"
    write_manifest(private)
    assert main(["evaluate-corpus", "atlas/Private/corpus.json", str(tmp_path)]) == 2
    assert "may not be inside atlas/Private" in capsys.readouterr().err


def test_corpus_cli_enforces_aggregate_graph_size(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli_module, "MAX_CORPUS_GRAPH_BYTES_TOTAL", 1)
    assert main(["evaluate-corpus", "benchmarks/recommendation-corpus.json", str(ROOT)]) == 2
    assert "1-byte aggregate limit" in capsys.readouterr().err


def test_manifest_project_dataclass_is_stable() -> None:
    project = CorpusManifestProject("id", "Name", "graph.json", "labels.json")
    assert (project.id, project.name, project.graph, project.labels) == (
        "id",
        "Name",
        "graph.json",
        "labels.json",
    )
