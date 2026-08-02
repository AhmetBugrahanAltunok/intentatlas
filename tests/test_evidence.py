from __future__ import annotations

import json
from pathlib import Path

import pytest

import intentatlas.evidence as evidence_module
from intentatlas.config import ProjectConfig
from intentatlas.scanner import scan_repository
from intentatlas.vault import ProjectVault


def _evidence_project(tmp_path) -> ProjectConfig:
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "reports").mkdir()
    (tmp_path / "src" / "app.py").write_text("def run():\n    return True\n", encoding="utf-8")
    (tmp_path / "tests" / "test_app.py").write_text(
        "from src.app import run\n\ndef test_run():\n    assert run()\n", encoding="utf-8"
    )
    (tmp_path / "reports" / "coverage.xml").write_text(
        """<?xml version="1.0"?>
<coverage>
  <packages><package name="demo"><classes>
    <class name="app" filename="src/app.py"><lines>
      <line number="1" hits="1"/><line number="2" hits="0"/>
    </lines></class>
    <class name="outside" filename="../outside.py"><lines>
      <line number="1" hits="1"/>
    </lines></class>
  </classes></package></packages>
</coverage>
""",
        encoding="utf-8",
    )
    (tmp_path / "reports" / "junit.xml").write_text(
        """<?xml version="1.0"?>
<testsuite name="demo">
  <testcase classname="tests.test_app" name="test_run" time="0.1"/>
  <testcase classname="tests.test_app" name="test_failure[secret-value]" time="0.2">
    <failure message="password=do-not-persist">raw private failure output</failure>
  </testcase>
  <testcase file="tests/test_app.py" name="test_skip" time="-1"><skipped/></testcase>
  <testcase file="tests/test_app.py" name="test_error" time="1e10000"><error/></testcase>
  <testcase classname="external.package" name="ignored" time="9"/>
</testsuite>
""",
        encoding="utf-8",
    )
    config = ProjectConfig(
        git_history_limit=0,
        coverage_reports=["reports/coverage.xml"],
        test_reports=["reports/junit.xml"],
    )
    ProjectVault(config.vault_path(tmp_path)).initialize()
    return config


def test_imports_bounded_coverage_and_test_evidence_deterministically(tmp_path) -> None:
    config = _evidence_project(tmp_path)

    first = scan_repository(tmp_path, config)
    second = scan_repository(tmp_path, config)

    coverage_id = "coverage:reports/coverage.xml:src/app.py"
    result_id = "test-result:reports/junit.xml:tests/test_app.py"
    coverage = first.nodes[coverage_id]
    result = first.nodes[result_id]
    assert coverage.kind == "coverage"
    assert coverage.metadata["lines_covered"] == 1
    assert coverage.metadata["lines_valid"] == 2
    assert coverage.metadata["line_rate"] == 0.5
    assert result.kind == "test-result"
    assert result.metadata == {
        "format": "junit-xml",
        "report": "reports/junit.xml",
        "total": 4,
        "passed": 1,
        "failed": 1,
        "errors": 1,
        "skipped": 1,
        "duration_seconds": 0.3,
        "owner": "scanner",
    }
    relationships = {
        (edge.source, edge.target, edge.relation, edge.evidence) for edge in first.edges
    }
    assert (coverage_id, "file:src/app.py", "proves", "cobertura-xml") in relationships
    assert (result_id, "file:tests/test_app.py", "proves", "junit-xml") in relationships
    assert first.nodes == second.nodes
    assert first.edges == second.edges

    persisted = json.dumps(first.to_dict(), sort_keys=True)
    assert "do-not-persist" not in persisted
    assert "raw private failure" not in persisted
    assert str(tmp_path) not in persisted
    assert "outside.py" not in persisted

    vault = ProjectVault(config.vault_path(tmp_path))
    vault.sync(first)
    generated = [
        path.read_text(encoding="utf-8") for path in (vault.root / "Tests").glob("*.md")
    ]
    assert any(coverage_id in content for content in generated)
    assert any(result_id in content for content in generated)


@pytest.mark.parametrize(
    ("configured", "message"),
    [
        ("../outside.xml", "project-relative"),
        ("atlas/Private/secret.xml", "atlas/Private"),
        ("missing.xml", "does not exist"),
    ],
)
def test_rejects_unsafe_or_missing_report_paths(tmp_path, configured, message) -> None:
    config = ProjectConfig(git_history_limit=0, coverage_reports=[configured])
    ProjectVault(config.vault_path(tmp_path)).initialize()

    with pytest.raises(ValueError, match=message):
        scan_repository(tmp_path, config)


def test_literal_private_report_boundary_is_independent_of_custom_vault(tmp_path) -> None:
    config = ProjectConfig(
        vault="project-vault",
        git_history_limit=0,
        coverage_reports=["atlas/Private/secret.xml"],
    )

    with pytest.raises(ValueError, match="atlas/Private"):
        scan_repository(tmp_path, config)


def test_rejects_entity_malformed_oversized_and_excessive_reports(tmp_path, monkeypatch) -> None:
    reports = tmp_path / "reports"
    reports.mkdir()
    config = ProjectConfig(git_history_limit=0, coverage_reports=["reports/coverage.xml"])
    ProjectVault(config.vault_path(tmp_path)).initialize()
    report = reports / "coverage.xml"

    report.write_text(
        '<!DOCTYPE coverage [<!ENTITY x "unsafe">]><coverage>&x;</coverage>',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="forbidden XML declaration"):
        scan_repository(tmp_path, config)

    report.write_text("<coverage>", encoding="utf-8")
    with pytest.raises(ValueError, match="Cannot parse"):
        scan_repository(tmp_path, config)

    monkeypatch.setattr(evidence_module, "MAX_REPORT_BYTES", 8)
    report.write_text("<coverage></coverage>", encoding="utf-8")
    with pytest.raises(ValueError, match="byte limit"):
        scan_repository(tmp_path, config)

    monkeypatch.setattr(evidence_module, "MAX_REPORT_BYTES", 10_000)
    monkeypatch.setattr(evidence_module, "MAX_REPORT_RECORDS", 1)
    report.write_text(
        '<coverage><class filename="a.py"/><class filename="b.py"/></coverage>',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="record limit"):
        scan_repository(tmp_path, config)


def test_rejects_report_content_with_the_wrong_format(tmp_path) -> None:
    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "coverage.xml").write_text("<testsuite/>", encoding="utf-8")
    config = ProjectConfig(git_history_limit=0, coverage_reports=["reports/coverage.xml"])
    ProjectVault(config.vault_path(tmp_path)).initialize()

    with pytest.raises(ValueError, match="not Cobertura"):
        scan_repository(tmp_path, config)


def test_rejects_symbolic_link_report_before_reading(tmp_path, monkeypatch) -> None:
    reports = tmp_path / "reports"
    reports.mkdir()
    report = reports / "coverage.xml"
    report.write_text("<coverage/>", encoding="utf-8")
    config = ProjectConfig(git_history_limit=0, coverage_reports=["reports/coverage.xml"])
    ProjectVault(config.vault_path(tmp_path)).initialize()
    original_is_symlink = Path.is_symlink

    def guarded_is_symlink(path: Path) -> bool:
        return path == report or original_is_symlink(path)

    monkeypatch.setattr(Path, "is_symlink", guarded_is_symlink)

    with pytest.raises(ValueError, match="symbolic link"):
        scan_repository(tmp_path, config)
