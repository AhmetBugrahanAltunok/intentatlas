from __future__ import annotations

from pathlib import Path

from intentatlas.change_analysis import CHANGE_ANALYSIS_SCHEMA_VERSION
from intentatlas.change_report import CHANGE_REPORT_SCHEMA_VERSION
from intentatlas.change_set import CHANGE_SET_SCHEMA_VERSION
from intentatlas.graph import AtlasGraph
from intentatlas.longitudinal import (
    PILOT_CLASSIFICATION_SCHEMA_VERSION,
    PILOT_LABEL_SCHEMA_VERSION,
    PILOT_SCHEMA_VERSION,
)


def test_compatibility_policy_covers_every_declared_contract() -> None:
    project_root = Path(__file__).resolve().parents[1]
    policy = (project_root / "docs" / "compatibility-policy.md").read_text(encoding="utf-8")
    normalized = " ".join(policy.split())

    for contract in (
        "Vault Markdown",
        "Saved graph JSON",
        "Supported CLI text",
        "Supported CLI JSON",
        "Change set, change analysis, change report, and review output",
        "Repository diagnostic output",
        "Longitudinal pilot manifest, labels, classifications, and result JSON",
        "Evidence import formats and external report adapters",
        "Language adapters and adapter conformance protocol",
        "Incremental scan cache",
        "Viewer bundles, in-memory indexes, and implementation helpers",
    ):
        assert contract in normalized

    assert policy.count("| stable |") == 7
    assert policy.count("| experimental |") == 4
    assert policy.count("| internal |") == 2
    assert "at least one minor release" in normalized
    assert "Warnings go to stderr and do not corrupt JSON stdout" in normalized
    assert "moving it to a weaker class is a breaking change" in normalized


def test_stable_schema_versions_remain_explicit() -> None:
    assert AtlasGraph.schema_version == 4
    assert AtlasGraph.supported_schema_versions == {1, 2, 3, 4}
    assert CHANGE_SET_SCHEMA_VERSION == 1
    assert CHANGE_ANALYSIS_SCHEMA_VERSION == 1
    assert CHANGE_REPORT_SCHEMA_VERSION == 1
    assert PILOT_SCHEMA_VERSION == 1
    assert PILOT_LABEL_SCHEMA_VERSION == 1
    assert PILOT_CLASSIFICATION_SCHEMA_VERSION == 1
