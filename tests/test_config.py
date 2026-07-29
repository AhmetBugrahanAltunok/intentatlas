from __future__ import annotations

import json

import pytest

from intentatlas.config import ProjectConfig


def test_config_round_trip_and_bounds(tmp_path) -> None:
    config = ProjectConfig(git_history_limit=15)
    path = config.save_if_missing(tmp_path)
    assert path.exists()
    loaded = ProjectConfig.load(tmp_path)
    assert loaded.git_history_limit == 15
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
