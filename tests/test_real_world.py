from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

import intentatlas.real_world as real_world_module
from intentatlas.cli import main
from intentatlas.real_world import (
    GENERATED_OUTPUT_POLICY,
    evaluate_real_world,
    load_real_world_manifest,
    render_real_world,
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


def build_real_world_fixture(tmp_path: Path) -> tuple[Path, Path, str, str]:
    project_root = tmp_path / "intentatlas-project"
    checkout = project_root / ".intentatlas" / "real-world" / "sources" / "sample"
    labels = project_root / "benchmarks" / "real-world" / "sample.labels.json"
    checkout.mkdir(parents=True)
    labels.parent.mkdir(parents=True)
    (checkout / "src").mkdir()
    (checkout / "tests").mkdir()
    (checkout / "src" / "value.py").write_text(
        "def value():\n    return 1\n", encoding="utf-8"
    )
    (checkout / "tests" / "test_value.py").write_text(
        "from src.value import value\n\ndef test_value():\n    assert value() == 1\n",
        encoding="utf-8",
    )
    license_bytes = b"MIT fixture license\n"
    (checkout / "LICENSE").write_bytes(license_bytes)
    _git(checkout, "init")
    # Extracted release tests can place this nested synthetic checkout beyond MAX_PATH on Windows.
    _git(checkout, "config", "core.longpaths", "true")
    _git(checkout, "config", "user.name", "Fixture")
    _git(checkout, "config", "user.email", "fixture@example.invalid")
    _git(checkout, "remote", "add", "origin", "https://github.com/example/sample.git")
    _git(checkout, "add", ".")
    _git(checkout, "commit", "-m", "Add value behavior")
    commit = _git(checkout, "rev-parse", "HEAD")
    license_hash = hashlib.sha256(license_bytes).hexdigest()
    labels.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "name": "Fixture labels",
                "label_policy": "complete-test-set",
                "cases": [
                    {
                        "id": "value",
                        "target": f"commit:{commit}",
                        "expected_tests": ["tests/test_value.py"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    manifest = project_root / "benchmarks" / "real-world" / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "name": "Fixture benchmark",
                "generated_output_policy": GENERATED_OUTPUT_POLICY,
                "projects": [
                    {
                        "id": "sample",
                        "name": "Sample",
                        "language": "Python",
                        "repository": "https://github.com/example/sample",
                        "commit": commit,
                        "license": {
                            "spdx": "MIT",
                            "path": "LICENSE",
                            "sha256": license_hash,
                        },
                        "labels": "benchmarks/real-world/sample.labels.json",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return project_root, manifest, commit, license_hash


def test_real_world_evaluation_scans_clean_pinned_checkout_in_memory(tmp_path) -> None:
    root, manifest_path, commit, _ = build_real_world_fixture(tmp_path)
    manifest = load_real_world_manifest(manifest_path)
    checkouts = root / ".intentatlas" / "real-world" / "sources"

    result = evaluate_real_world(root, checkouts, manifest)

    assert result.evaluation.project_count == 1
    assert result.evaluation.case_count == 1
    assert [threshold.totals.to_dict() for threshold in result.evaluation.thresholds] == [
        {
            "case_count": 1,
            "expected_count": 1,
            "recommendation_count": 1,
            "true_positive_count": 1,
            "false_positive_count": 0,
            "false_negative_count": 0,
            "precision": 1.0,
            "recall": 1.0,
        },
        {
            "case_count": 1,
            "expected_count": 1,
            "recommendation_count": 1,
            "true_positive_count": 1,
            "false_positive_count": 0,
            "false_negative_count": 0,
            "precision": 1.0,
            "recall": 1.0,
        },
        {
            "case_count": 1,
            "expected_count": 1,
            "recommendation_count": 1,
            "true_positive_count": 1,
            "false_positive_count": 0,
            "false_negative_count": 0,
            "precision": 1.0,
            "recall": 1.0,
        },
    ]
    assert result.projects[0].commit == commit
    assert not (checkouts / "sample" / "atlas").exists()
    assert not (checkouts / "sample" / ".intentatlas").exists()
    rendered = render_real_world(result, "json")
    assert rendered == render_real_world(result, "json")
    document = json.loads(rendered)
    assert document["generated_output_policy"] == "ephemeral-only"
    assert document["projects"][0]["license"]["spdx"] == "MIT"

    text = render_real_world(result)
    assert "Real-world recommendation benchmark: Fixture benchmark" in text
    assert "https://github.com/example/sample" in text
    assert "LOW confidence" in text
    with pytest.raises(ValueError, match="Unknown real-world output format"):
        render_real_world(result, "yaml")


def test_real_world_cli_runs_offline_fixture(tmp_path, capsys) -> None:
    root, _, _, _ = build_real_world_fixture(tmp_path)
    assert (
        main(
            [
                "evaluate-real-world",
                "benchmarks/real-world/manifest.json",
                ".intentatlas/real-world/sources",
                str(root),
                "--format",
                "json",
            ]
        )
        == 0
    )
    assert json.loads(capsys.readouterr().out)["evaluation"]["case_count"] == 1


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda document: document.update(schema_version=True), "Unsupported"),
        (lambda document: document.update(schema_version=2), "Unsupported"),
        (lambda document: document.update(generated_output_policy="committed"), "ephemeral-only"),
        (
            lambda document: document["projects"][0].update(repository="http://example.com/x"),
            "Invalid GitHub",
        ),
        (lambda document: document["projects"][0].update(commit="abc"), "pinned commit"),
        (
            lambda document: document["projects"][0]["license"].update(path="../LICENSE"),
            "Unsafe real-world license",
        ),
        (
            lambda document: document["projects"][0]["license"].update(sha256="bad"),
            "license SHA-256",
        ),
    ],
)
def test_real_world_manifest_rejects_invalid_metadata(tmp_path, mutate, message) -> None:
    _, manifest_path, _, _ = build_real_world_fixture(tmp_path)
    document = json.loads(manifest_path.read_text(encoding="utf-8"))
    mutate(document)
    manifest_path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        load_real_world_manifest(manifest_path)


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda document: document.update(extra=True), "Unknown real-world manifest"),
        (lambda document: document.update(projects=[]), "non-empty list"),
        (lambda document: document.update(projects=["bad"]), "project must be an object"),
        (lambda document: document["projects"][0].update(id="bad id"), "project ID"),
        (lambda document: document["projects"][0].update(license=[]), "must be an object"),
        (
            lambda document: document["projects"][0]["license"].update(spdx="bad id"),
            "Invalid SPDX",
        ),
    ],
)
def test_real_world_manifest_rejects_invalid_shapes(tmp_path, mutate, message) -> None:
    _, manifest_path, _, _ = build_real_world_fixture(tmp_path)
    document = json.loads(manifest_path.read_text(encoding="utf-8"))
    mutate(document)
    manifest_path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        load_real_world_manifest(manifest_path)


@pytest.mark.parametrize(
    ("field", "message"),
    [
        ("id", "Duplicate real-world project ID"),
        ("repository", "Duplicate real-world repository"),
        ("labels", "Duplicate real-world label path"),
    ],
)
def test_real_world_manifest_rejects_duplicate_projects(tmp_path, field, message) -> None:
    _, manifest_path, _, _ = build_real_world_fixture(tmp_path)
    document = json.loads(manifest_path.read_text(encoding="utf-8"))
    duplicate = json.loads(json.dumps(document["projects"][0]))
    duplicate.update(id="second", repository="https://github.com/example/second")
    duplicate["labels"] = "benchmarks/real-world/second.labels.json"
    duplicate[field] = document["projects"][0][field]
    document["projects"].append(duplicate)
    manifest_path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        load_real_world_manifest(manifest_path)


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ("dirty", "must be clean"),
        ("license", "license hash does not match"),
        ("origin", "unexpected origin"),
    ],
)
def test_real_world_evaluation_rejects_unverified_checkout(
    tmp_path, change, message
) -> None:
    root, manifest_path, _, _ = build_real_world_fixture(tmp_path)
    manifest = load_real_world_manifest(manifest_path)
    checkout = root / ".intentatlas" / "real-world" / "sources" / "sample"
    if change == "dirty":
        (checkout / "unexpected.py").write_text("value = 1\n", encoding="utf-8")
    elif change == "license":
        (checkout / "LICENSE").write_text("changed\n", encoding="utf-8")
    else:
        _git(checkout, "remote", "set-url", "origin", "https://github.com/example/other.git")

    with pytest.raises(ValueError, match=message):
        evaluate_real_world(root, checkout.parent, manifest)


def test_real_world_rejects_labels_for_another_target(tmp_path) -> None:
    root, manifest_path, _, _ = build_real_world_fixture(tmp_path)
    manifest = load_real_world_manifest(manifest_path)
    labels_path = root / manifest.projects[0].labels
    document = json.loads(labels_path.read_text(encoding="utf-8"))
    document["cases"][0]["target"] = "commit:" + "0" * 40
    labels_path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(ValueError, match="must include"):
        evaluate_real_world(
            root,
            root / ".intentatlas" / "real-world" / "sources",
            manifest,
        )


def test_real_world_rejects_missing_root_checkout_license_and_git(tmp_path, monkeypatch) -> None:
    root, manifest_path, _, _ = build_real_world_fixture(tmp_path)
    manifest = load_real_world_manifest(manifest_path)
    checkouts = root / ".intentatlas" / "real-world" / "sources"

    with pytest.raises(ValueError, match="checkout root does not exist"):
        evaluate_real_world(root, root / "missing", manifest)

    checkout = checkouts / "sample"
    (checkout / "LICENSE").unlink()
    with pytest.raises(ValueError, match="license file is missing"):
        evaluate_real_world(root, checkouts, manifest)

    (checkout / "LICENSE").write_text("MIT fixture license\n", encoding="utf-8")
    monkeypatch.setattr(real_world_module.shutil, "which", lambda _name: None)
    with pytest.raises(ValueError, match="Git is required"):
        evaluate_real_world(root, checkouts, manifest)


def test_real_world_rejects_wrong_commit(tmp_path) -> None:
    root, manifest_path, _, _ = build_real_world_fixture(tmp_path)
    manifest = load_real_world_manifest(manifest_path)
    checkout = root / ".intentatlas" / "real-world" / "sources" / "sample"
    (checkout / "src" / "value.py").write_text(
        "def value():\n    return 2\n", encoding="utf-8"
    )
    _git(checkout, "add", ".")
    _git(checkout, "commit", "-m", "Change value")

    with pytest.raises(ValueError, match="expected"):
        evaluate_real_world(root, checkout.parent, manifest)


def test_real_world_rejects_license_path_resolving_outside_checkout(
    tmp_path, monkeypatch
) -> None:
    root, manifest_path, _, _ = build_real_world_fixture(tmp_path)
    manifest = load_real_world_manifest(manifest_path)
    checkout = root / ".intentatlas" / "real-world" / "sources" / "sample"
    license_path = checkout / "LICENSE"
    outside = tmp_path / "outside-license"
    outside.write_text("MIT fixture license\n", encoding="utf-8")
    original_resolve = Path.resolve

    def redirected_resolve(self, *args, **kwargs):
        if self == license_path:
            return outside
        return original_resolve(self, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", redirected_resolve)
    with pytest.raises(ValueError, match="license file is missing"):
        evaluate_real_world(root, checkout.parent, manifest)


def test_real_world_manifest_is_bounded_and_symlink_safe(tmp_path, monkeypatch) -> None:
    _, manifest_path, _, _ = build_real_world_fixture(tmp_path)
    original_is_symlink = Path.is_symlink
    monkeypatch.setattr(
        Path,
        "is_symlink",
        lambda self: self == manifest_path or original_is_symlink(self),
    )
    with pytest.raises(ValueError, match="symbolic link"):
        load_real_world_manifest(manifest_path)

    monkeypatch.setattr(Path, "is_symlink", original_is_symlink)
    monkeypatch.setattr(real_world_module, "MAX_MANIFEST_BYTES", 1)
    with pytest.raises(ValueError, match="1-byte limit"):
        load_real_world_manifest(manifest_path)


def test_real_world_manifest_rejects_missing_and_malformed_files(tmp_path) -> None:
    missing = tmp_path / "missing.json"
    with pytest.raises(ValueError, match="does not exist"):
        load_real_world_manifest(missing)

    malformed = tmp_path / "malformed.json"
    malformed.write_text('{"schema_version": 1, "schema_version": 1}', encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate JSON key"):
        load_real_world_manifest(malformed)

    malformed.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="must be a JSON object"):
        load_real_world_manifest(malformed)
