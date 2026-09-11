from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from intentatlas.cli import main
from intentatlas.longitudinal import (
    GENERATED_OUTPUT_POLICY,
    PilotCase,
    evaluate_longitudinal,
    load_pilot_labels,
    load_pilot_manifest,
    partition_hashes,
    render_longitudinal,
)


def _git(path: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(path), *arguments],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def _commit(path: Path, message: str) -> tuple[str, str]:
    _git(path, "add", ".")
    _git(path, "commit", "-m", message)
    revision = _git(path, "rev-parse", "HEAD")
    return revision, _git(path, "show", "-s", "--format=%cI", revision)


def build_pilot_fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    root = tmp_path / "project"
    checkout = root / ".intentatlas" / "longitudinal" / "checkouts" / "sample"
    metadata = root / "benchmarks" / "longitudinal"
    checkout.mkdir(parents=True)
    metadata.mkdir(parents=True)
    (checkout / "src").mkdir()
    (checkout / "tests").mkdir()
    license_bytes = b"MIT fixture license\n"
    (checkout / "LICENSE").write_bytes(license_bytes)
    (checkout / "src" / "value.py").write_text("def value():\n    return 1\n", encoding="utf-8")
    (checkout / "tests" / "test_value.py").write_text(
        "from src.value import value\n\ndef test_value():\n    assert value() == 1\n",
        encoding="utf-8",
    )
    _git(checkout, "init")
    _git(checkout, "config", "core.longpaths", "true")
    _git(checkout, "config", "user.name", "Fixture")
    _git(checkout, "config", "user.email", "fixture@example.invalid")
    _git(checkout, "remote", "add", "origin", "https://github.com/example/sample.git")
    first, first_time = _commit(checkout, "Add value")
    (checkout / "src" / "value.py").write_text("def value():\n    return 2\n", encoding="utf-8")
    (checkout / "tests" / "test_value.py").write_text(
        "from src.value import value\n\ndef test_value():\n    assert value() == 2\n",
        encoding="utf-8",
    )
    second, second_time = _commit(checkout, "Change value")
    (checkout / "README.md").write_text("Fixture\n", encoding="utf-8")
    third, third_time = _commit(checkout, "Document value")

    cases = [
        {
            "id": "sample-add-value",
            "sequence": 1,
            "revision": first,
            "committed_at": first_time,
            "partition": "calibration",
            "expected_tests": ["tests/test_value.py"],
        },
        {
            "id": "sample-change-value",
            "sequence": 2,
            "revision": second,
            "committed_at": second_time,
            "partition": "evaluation",
            "expected_tests": ["tests/test_value.py"],
        },
        {
            "id": "sample-docs-only",
            "sequence": 3,
            "revision": third,
            "committed_at": third_time,
            "partition": "evaluation",
            "expected_tests": [],
        },
    ]
    labels_path = metadata / "sample.labels.json"
    labels_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "project_id": "sample",
                "label_policy": "complete-test-set",
                "cases": cases,
            }
        ),
        encoding="utf-8",
    )
    classifications_path = metadata / "sample.classifications.json"
    classifications_path.write_text(
        json.dumps(
            {"schema_version": 1, "project_id": "sample", "observations": []}
        ),
        encoding="utf-8",
    )
    parsed_cases = tuple(
        (
            "sample",
            PilotCase(
                item["id"],
                item["sequence"],
                item["revision"],
                item["committed_at"],
                item["partition"],
                tuple(item["expected_tests"]),
            ),
        )
        for item in cases
    )
    hashes = partition_hashes(parsed_cases)
    manifest_path = metadata / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "name": "Fixture longitudinal pilot",
                "generated_output_policy": GENERATED_OUTPUT_POLICY,
                "thresholds": ["low", "medium", "high"],
                "partitions": {
                    "calibration": {"sha256": hashes["calibration"]},
                    "evaluation": {"sha256": hashes["evaluation"]},
                },
                "projects": [
                    {
                        "id": "sample",
                        "name": "Sample",
                        "language": "python",
                        "workspace_shape": "single-package",
                        "repository": "https://github.com/example/sample",
                        "revision": third,
                        "history_limit": 25,
                        "excluded_paths": [],
                        "license": {
                            "spdx": "MIT",
                            "path": "LICENSE",
                            "sha256": hashlib.sha256(license_bytes).hexdigest(),
                            "reviewed_at": "2026-08-02",
                        },
                        "labels": "benchmarks/longitudinal/sample.labels.json",
                        "classifications": (
                            "benchmarks/longitudinal/sample.classifications.json"
                        ),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return root, checkout.parent, manifest_path


def test_longitudinal_evaluation_is_deterministic_and_uncertainty_aware(tmp_path) -> None:
    root, checkouts, manifest_path = build_pilot_fixture(tmp_path)
    manifest = load_pilot_manifest(manifest_path)

    first = evaluate_longitudinal(root, checkouts, manifest_path, manifest)
    second = evaluate_longitudinal(root, checkouts, manifest_path, manifest)

    assert first.to_dict() == second.to_dict()
    assert len(first.cases) == 9
    assert {case.freshness for case in first.cases} >= {"aligned", "stale"}
    assert any(case.execution_strategy == "abstain-and-full-suite" for case in first.cases)
    assert first.to_dict()["duration_evidence"] is None
    evaluation_high = next(
        cohort
        for cohort in first.cohorts
        if cohort.cohort == "overall"
        and cohort.partition == "evaluation"
        and cohort.minimum_confidence == "high"
    )
    assert evaluation_high.case_count == 2
    assert evaluation_high.recall.denominator == 1
    assert evaluation_high.recommendation_coverage.denominator == 2
    assert render_longitudinal(first, "json") == render_longitudinal(second, "json")
    assert "Duration/savings: unknown" in render_longitudinal(first)
    with pytest.raises(ValueError, match="Unknown longitudinal output format"):
        render_longitudinal(first, "yaml")


def test_longitudinal_manifest_rejects_mutated_partition_hash(tmp_path) -> None:
    root, checkouts, manifest_path = build_pilot_fixture(tmp_path)
    document = json.loads(manifest_path.read_text(encoding="utf-8"))
    document["partitions"]["evaluation"]["sha256"] = "0" * 64
    manifest_path.write_text(json.dumps(document), encoding="utf-8")
    manifest = load_pilot_manifest(manifest_path)

    with pytest.raises(ValueError, match="partition hashes"):
        evaluate_longitudinal(root, checkouts, manifest_path, manifest)


def test_longitudinal_cli_runs_offline(tmp_path, capsys) -> None:
    root, _, _ = build_pilot_fixture(tmp_path)

    assert (
        main(
            [
                "evaluate-longitudinal",
                "benchmarks/longitudinal/manifest.json",
                ".intentatlas/longitudinal/checkouts",
                str(root),
                "--format",
                "json",
            ]
        )
        == 0
    )
    document = json.loads(capsys.readouterr().out)
    assert document["name"] == "Fixture longitudinal pilot"
    assert document["duration_evidence"] is None


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda document: document.update(extra=True), "Unknown longitudinal labels"),
        (
            lambda document: document["cases"][0].update(sequence=2),
            "sequence must be contiguous",
        ),
        (
            lambda document: document["cases"][0].update(partition="tuning"),
            "Invalid partition",
        ),
        (
            lambda document: document["cases"][0].update(expected_tests=["../test.py"]),
            "Unsafe pilot expected test",
        ),
        (
            lambda document: document.update(schema_version="1"),
            "Unsupported longitudinal pilot label schema",
        ),
        (
            lambda document: document.update(project_id="someone-else"),
            "do not belong to",
        ),
        (
            lambda document: document.update(label_policy="best-effort"),
            "label_policy must be",
        ),
        (lambda document: document.update(cases=[]), "non-empty case list"),
        (lambda document: document.update(cases={}), "non-empty case list"),
        (lambda document: document.update(cases=["case-1"]), "must be an object"),
        (
            lambda document: document["cases"][0].update(expected_tests="tests/a.py"),
            "Expected tests must be a list",
        ),
        (
            lambda document: document["cases"][0].update(
                expected_tests=["tests/a.py", "tests/a.py"]
            ),
            "Duplicate expected test",
        ),
    ],
)
def test_longitudinal_labels_are_strict(tmp_path, mutate, message) -> None:
    _, _, manifest_path = build_pilot_fixture(tmp_path)
    manifest = load_pilot_manifest(manifest_path)
    labels_path = manifest_path.parents[2] / manifest.projects[0].labels
    document = json.loads(labels_path.read_text(encoding="utf-8"))
    mutate(document)
    labels_path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        load_pilot_labels(labels_path, "sample")


def test_longitudinal_manifest_rejects_duplicate_keys_and_unbounded_history(tmp_path) -> None:
    _, _, manifest_path = build_pilot_fixture(tmp_path)
    document = json.loads(manifest_path.read_text(encoding="utf-8"))
    document["projects"][0]["history_limit"] = 251
    manifest_path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(ValueError, match="history_limit"):
        load_pilot_manifest(manifest_path)

    manifest_path.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate JSON key"):
        load_pilot_manifest(manifest_path)


def test_frozen_pilot_metadata_and_benchmark_card_match() -> None:
    project_root = Path(__file__).resolve().parents[1]
    manifest_path = project_root / "benchmarks" / "longitudinal" / "manifest.json"
    manifest = load_pilot_manifest(manifest_path)
    labels = [
        load_pilot_labels(project_root / project.labels, project.id)
        for project in manifest.projects
    ]

    assert len(manifest.projects) == 8
    assert sum(len(item.cases) for item in labels) == 64
    assert {project.language for project in manifest.projects} == {
        "python",
        "javascript-typescript",
        "go",
    }
    assert sum(project.workspace_shape == "workspace" for project in manifest.projects) == 2
    assert all(
        sum(case.partition == partition for case in item.cases) == 4
        for item in labels
        for partition in ("calibration", "evaluation")
    )

    protocol = (project_root / "docs" / "longitudinal-pilot.md").read_text(encoding="utf-8")
    readme = (project_root / "README.md").read_text(encoding="utf-8")
    normalized_readme = " ".join(readme.split())
    for value in (
        manifest.partition_hashes["calibration"],
        manifest.partition_hashes["evaluation"],
        "dd90bd22ceefba5321e1a0fb2a762adee15f8f943807718b1bcf0117923d3cdd",
        "0a0b9c530dcd57c9e6ca208e665c408da4d7376c0cc05c4463db8ccbf4aa887d",
    ):
        assert value in protocol
    assert "not general accuracy" in normalized_readme
    assert "duration/savings remain unknown" in normalized_readme
    assert "intentatlas evaluate-longitudinal" in normalized_readme


def _manifest_document() -> dict:
    return json.loads(
        Path("benchmarks/longitudinal/manifest.json").read_text(encoding="utf-8")
    )


def _drop_schema_version(document: dict) -> None:
    document["schema_version"] = "1"


def _unknown_top_level_key(document: dict) -> None:
    document["notes"] = "extra"


def _wrong_output_policy(document: dict) -> None:
    document["generated_output_policy"] = "persisted"


def _wrong_thresholds(document: dict) -> None:
    document["thresholds"] = ["low", "high"]


def _partitions_not_object(document: dict) -> None:
    document["partitions"] = []


def _unknown_partition(document: dict) -> None:
    document["partitions"]["holdout"] = {"sha256": "0" * 64}


def _partition_not_object(document: dict) -> None:
    document["partitions"]["evaluation"] = "0" * 64


def _partition_digest_not_hex(document: dict) -> None:
    document["partitions"]["evaluation"]["sha256"] = "z" * 64


def _projects_not_a_list(document: dict) -> None:
    document["projects"] = {}


def _projects_empty(document: dict) -> None:
    document["projects"] = []


def _project_not_an_object(document: dict) -> None:
    document["projects"][0] = "antfu-utils"


def _unknown_project_key(document: dict) -> None:
    document["projects"][0]["notes"] = "extra"


def _non_github_repository(document: dict) -> None:
    document["projects"][0]["repository"] = "https://example.invalid/owner/repo"


def _short_revision(document: dict) -> None:
    document["projects"][0]["revision"] = "91f8cf7"


def _unsupported_language(document: dict) -> None:
    document["projects"][0]["language"] = "cobol"


def _unsupported_workspace_shape(document: dict) -> None:
    document["projects"][0]["workspace_shape"] = "monorepo-of-monorepos"


def _history_limit_out_of_range(document: dict) -> None:
    document["projects"][0]["history_limit"] = 0


def _history_limit_not_an_int(document: dict) -> None:
    document["projects"][0]["history_limit"] = True


def _excluded_paths_unbounded(document: dict) -> None:
    document["projects"][0]["excluded_paths"] = [f"p{index}" for index in range(33)]


def _license_not_an_object(document: dict) -> None:
    document["projects"][0]["license"] = "MIT"


def _invalid_spdx(document: dict) -> None:
    document["projects"][0]["license"]["spdx"] = "MIT OR $$$"


def _invalid_license_digest(document: dict) -> None:
    document["projects"][0]["license"]["sha256"] = "0" * 63


def _labels_equal_classifications(document: dict) -> None:
    document["projects"][0]["classifications"] = document["projects"][0]["labels"]


def _duplicate_project_id(document: dict) -> None:
    document["projects"][1]["id"] = document["projects"][0]["id"]


def _duplicate_repository(document: dict) -> None:
    document["projects"][1]["repository"] = document["projects"][0]["repository"]


def _duplicate_metadata_path(document: dict) -> None:
    document["projects"][1]["labels"] = document["projects"][0]["labels"]


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (_drop_schema_version, "schema"),
        (_unknown_top_level_key, "manifest"),
        (_wrong_output_policy, "generated_output_policy"),
        (_wrong_thresholds, "thresholds"),
        (_partitions_not_object, "partitions must be an object"),
        (_unknown_partition, "partitions"),
        (_partition_not_object, "must be an object"),
        (_partition_digest_not_hex, "SHA-256"),
        (_projects_not_a_list, "non-empty list"),
        (_projects_empty, "non-empty list"),
        (_project_not_an_object, "must be an object"),
        (_unknown_project_key, "project"),
        (_non_github_repository, "GitHub repository URL"),
        (_short_revision, "revision"),
        (_unsupported_language, "Unsupported pilot language"),
        (_unsupported_workspace_shape, "Unsupported workspace shape"),
        (_history_limit_out_of_range, "history_limit"),
        (_history_limit_not_an_int, "history_limit"),
        (_excluded_paths_unbounded, "excluded_paths"),
        (_license_not_an_object, "License review"),
        (_invalid_spdx, "Invalid SPDX"),
        (_invalid_license_digest, "license SHA-256"),
        (_labels_equal_classifications, "must differ"),
        (_duplicate_project_id, "Duplicate pilot project ID"),
        (_duplicate_repository, "Duplicate pilot repository"),
        (_duplicate_metadata_path, "Duplicate pilot metadata path"),
    ],
)
def test_pilot_manifest_refuses_every_malformed_shape(tmp_path, mutate, message) -> None:
    document = _manifest_document()
    mutate(document)
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        load_pilot_manifest(path)


def test_the_frozen_pilot_manifest_is_accepted_unmutated(tmp_path) -> None:
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(_manifest_document()), encoding="utf-8")

    manifest = load_pilot_manifest(path)

    assert manifest.projects
    assert len(manifest.projects) == len({project.id for project in manifest.projects})
    assert set(manifest.partition_hashes) == {"calibration", "evaluation"}
