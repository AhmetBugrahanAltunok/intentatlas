from __future__ import annotations

import tomllib
from importlib.metadata import version
from pathlib import Path

import intentatlas


def test_release_candidate_uses_one_canonical_version_source() -> None:
    project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

    assert "version" not in project["project"]
    assert project["project"]["dynamic"] == ["version"]
    assert project["tool"]["hatch"]["version"]["path"] == "src/intentatlas/__init__.py"
    assert intentatlas.__version__ == "0.3.0rc1"
    assert version("intentatlas") == intentatlas.__version__
