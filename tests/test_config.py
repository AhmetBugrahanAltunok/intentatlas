from __future__ import annotations

import json

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
