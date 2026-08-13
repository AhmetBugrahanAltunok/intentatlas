from __future__ import annotations

import json
import os

import pytest

from intentatlas.config import ProjectConfig


def test_config_round_trip_and_bounds(tmp_path) -> None:
    config = ProjectConfig(
        git_history_limit=15,
        coverage_reports=["reports/coverage.xml"],
        test_reports=["reports/junit.xml"],
        delivery_reports=["reports/delivery.json"],
        scip_reports=["reports/index.scip.json"],
        sarif_reports=["reports/results.sarif"],
        test_execution_reports=["reports/execution.json"],
    )
    path = config.save_if_missing(tmp_path)
    assert path.exists()
    loaded = ProjectConfig.load(tmp_path)
    assert loaded.git_history_limit == 15
    assert loaded.coverage_reports == ["reports/coverage.xml"]
    assert loaded.test_reports == ["reports/junit.xml"]
    assert loaded.delivery_reports == ["reports/delivery.json"]
    assert loaded.scip_reports == ["reports/index.scip.json"]
    assert loaded.sarif_reports == ["reports/results.sarif"]
    assert loaded.test_execution_reports == ["reports/execution.json"]
    assert ".obsidian" in loaded.exclude
    assert ".venv-intentatlas" in loaded.exclude
    assert loaded.vault_path(tmp_path) == (tmp_path / "atlas").resolve()


def test_config_rejects_escape_and_unknown_schema(tmp_path) -> None:
    (tmp_path / "intentatlas.json").write_text(
        json.dumps({"schema_version": 1, "vault": "../outside"}), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="escapes"):
        ProjectConfig.load(tmp_path).vault_path(tmp_path)

    (tmp_path / "intentatlas.json").write_text(json.dumps({"schema_version": 99}), encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported"):
        ProjectConfig.load(tmp_path)


def test_config_rejects_project_root_as_an_output_path(tmp_path) -> None:
    (tmp_path / "intentatlas.json").write_text(
        json.dumps({"schema_version": 1, "vault": "."}), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="vault path must be below"):
        ProjectConfig.load(tmp_path).vault_path(tmp_path)

    (tmp_path / "intentatlas.json").write_text(
        json.dumps({"schema_version": 1, "graph": "."}), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="graph path must be below"):
        ProjectConfig.load(tmp_path).graph_path(tmp_path)


def test_config_rejects_invalid_report_source_lists(tmp_path) -> None:
    (tmp_path / "intentatlas.json").write_text(
        json.dumps({"coverage_reports": "coverage.xml"}), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="must be a list"):
        ProjectConfig.load(tmp_path)

    (tmp_path / "intentatlas.json").write_text(
        json.dumps({"scip_reports": "index.scip.json"}), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="must be a list"):
        ProjectConfig.load(tmp_path)

    (tmp_path / "intentatlas.json").write_text(
        json.dumps({"test_reports": [""]}), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="empty path"):
        ProjectConfig.load(tmp_path)

    (tmp_path / "intentatlas.json").write_text(
        json.dumps({"test_reports": [{"path": "junit.xml"}]}), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="path strings"):
        ProjectConfig.load(tmp_path)

    (tmp_path / "intentatlas.json").write_text(
        json.dumps({"delivery_reports": "delivery.json"}), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="must be a list"):
        ProjectConfig.load(tmp_path)


@pytest.mark.parametrize(
    ("content", "message"),
    [
        ("[]", "JSON object"),
        ('{"exclude": "vendor"}', "exclude must be a list"),
        ('{"exclude": [1]}', "only path strings"),
        ('{"vault": 1}', "vault must be a non-empty string"),
        ('{"graph": []}', "graph must be a non-empty string"),
        ('{"git_history_limit": true}', "git_history_limit must be an integer"),
        ('{"unknown": 1}', "Unknown IntentAtlas config fields"),
        ('{"exclude": ["../private"]}', "unsafe path"),
    ],
)
def test_config_rejects_non_object_and_malformed_field_types(
    tmp_path, content, message
) -> None:
    (tmp_path / "intentatlas.json").write_text(content, encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        ProjectConfig.load(tmp_path)


def test_config_rejects_duplicate_keys_and_private_output_paths(
    tmp_path, monkeypatch
) -> None:
    config_path = tmp_path / "intentatlas.json"
    config_path.write_text('{"exclude": [], "exclude": ["vendor"]}', encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate JSON key"):
        ProjectConfig.load(tmp_path)

    original_resolve = type(tmp_path).resolve

    def guarded_resolve(path, *args, **kwargs):
        folded = tuple(part.casefold() for part in path.parts)
        if ("atlas", "private") in tuple(zip(folded, folded[1:], strict=False)):
            raise AssertionError("config resolution inspected atlas/Private")
        return original_resolve(path, *args, **kwargs)

    monkeypatch.setattr(type(tmp_path), "resolve", guarded_resolve)
    config_path.write_text('{"vault": "atlas/Private/nested"}', encoding="utf-8")
    with pytest.raises(ValueError, match="inside atlas/Private"):
        ProjectConfig.load(tmp_path).vault_path(tmp_path)

    config_path.write_text('{"graph": "atlas/Private/graph.json"}', encoding="utf-8")
    with pytest.raises(ValueError, match="inside atlas/Private"):
        ProjectConfig.load(tmp_path).graph_path(tmp_path)


def test_config_rejects_symbolic_link_input(tmp_path) -> None:
    target = tmp_path / "outside.json"
    target.write_text("{}", encoding="utf-8")
    config_path = tmp_path / "intentatlas.json"
    try:
        os.symlink(target, config_path)
    except OSError:
        pytest.skip("Symbolic links are unavailable")

    with pytest.raises(ValueError, match="symbolic link"):
        ProjectConfig.load(tmp_path)


def test_dangling_config_link_is_rejected_before_absence_or_write(
    tmp_path, monkeypatch
) -> None:
    config_path = tmp_path / "intentatlas.json"
    external = tmp_path.parent / f"{tmp_path.name}-must-not-be-created.json"
    original_is_symlink = type(config_path).is_symlink

    def simulated_link(path) -> bool:
        if path == config_path:
            return True
        return original_is_symlink(path)

    monkeypatch.setattr(type(config_path), "is_symlink", simulated_link)

    with pytest.raises(ValueError, match="symbolic link"):
        ProjectConfig.load(tmp_path)
    with pytest.raises(ValueError, match="symbolic link"):
        ProjectConfig().save_if_missing(tmp_path)
    assert not external.exists()
