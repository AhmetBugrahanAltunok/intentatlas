from __future__ import annotations

import json
import subprocess

import pytest

import intentatlas.open_evidence as open_evidence_module
from intentatlas.config import ProjectConfig
from intentatlas.recommendations import recommend_tests
from intentatlas.scanner import scan_repository, scan_repository_incremental
from intentatlas.vault import ProjectVault


def git(root, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def build_open_evidence_project(tmp_path) -> tuple[ProjectConfig, str]:
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "reports").mkdir()
    (tmp_path / "src" / "app.py").write_text(
        "def run():\n    return True\n", encoding="utf-8"
    )
    (tmp_path / "tests" / "test_app.py").write_text(
        "def test_placeholder():\n    assert True\n", encoding="utf-8"
    )
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.name", "IntentAtlas Test")
    git(tmp_path, "config", "user.email", "intentatlas-test@example.invalid")
    git(tmp_path, "add", "src/app.py", "tests/test_app.py")
    git(tmp_path, "commit", "-q", "-m", "fixture")
    head = git(tmp_path, "rev-parse", "HEAD")

    (tmp_path / "reports" / "index.scip.json").write_text(
        json.dumps(
            {
                "metadata": {"projectRoot": "file:///not-retained"},
                "documents": [
                    {
                        "relativePath": "src/app.py",
                        "language": "python",
                        "occurrences": [
                            {
                                "range": [0, 0, 3],
                                "symbol": "scip-python python demo run().",
                                "symbolRoles": 1,
                            },
                            {
                                "range": [1, 0, 1, 4],
                                "symbol": "secret-external-symbol",
                                "symbolRoles": 0,
                                "diagnostics": [
                                    {"message": "password=do-not-retain", "severity": 2}
                                ],
                            },
                        ],
                    },
                    {
                        "relativePath": "../outside.py",
                        "occurrences": [],
                    },
                ],
                "externalSymbols": [],
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "reports" / "results.sarif").write_text(
        json.dumps(
            {
                "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
                "version": "2.1.0",
                "runs": [
                    {
                        "tool": {"driver": {"name": "fixture"}},
                        "results": [
                            {
                                "ruleId": "SEC001",
                                "level": "error",
                                "message": {"text": "token=do-not-retain"},
                                "locations": [
                                    {
                                        "physicalLocation": {
                                            "artifactLocation": {"uri": "src/app.py"},
                                            "region": {"snippet": {"text": "secret source"}},
                                        }
                                    }
                                ],
                            },
                            {
                                "ruleId": "STYLE002",
                                "level": "warning",
                                "locations": [
                                    {
                                        "physicalLocation": {
                                            "artifactLocation": {
                                                "uri": "src%2Fapp.py",
                                                "uriBaseId": "%SRCROOT%",
                                            }
                                        }
                                    }
                                ],
                            },
                            {
                                "ruleId": "UNSAFE",
                                "locations": [
                                    {
                                        "physicalLocation": {
                                            "artifactLocation": {"uri": "../outside.py"}
                                        }
                                    }
                                ],
                            },
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "reports" / "execution.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "commit": head,
                "completeness": "complete-observed-set",
                "tests": [{"test": "tests/test_app.py", "files": ["src/app.py"]}],
            }
        ),
        encoding="utf-8",
    )
    config = ProjectConfig(
        git_history_limit=0,
        scip_reports=["reports/index.scip.json"],
        sarif_reports=["reports/results.sarif"],
        test_execution_reports=["reports/execution.json"],
    )
    ProjectVault(config.vault_path(tmp_path)).initialize()
    return config, head


def test_imports_open_evidence_without_retaining_raw_content(tmp_path) -> None:
    config, head = build_open_evidence_project(tmp_path)

    first = scan_repository(tmp_path, config)
    second = scan_repository(tmp_path, config)
    incremental = scan_repository_incremental(tmp_path, config).graph

    scip_id = "code-index:reports/index.scip.json:src/app.py"
    sarif_id = "finding-summary:reports/results.sarif:src/app.py"
    execution_id = "test-execution:reports/execution.json:tests/test_app.py"
    assert first.nodes[scip_id].metadata == {
        "format": "scip-protobuf-json",
        "report": "reports/index.scip.json",
        "occurrences": 2,
        "definitions": 1,
        "references": 1,
        "diagnostics": 1,
        "owner": "scanner",
    }
    assert first.nodes[sarif_id].metadata == {
        "format": "sarif-2.1.0",
        "report": "reports/results.sarif",
        "results": 2,
        "none": 0,
        "notes": 0,
        "warnings": 1,
        "errors": 1,
        "rule_count": 2,
        "rules": ["SEC001", "STYLE002"],
        "rules_truncated": False,
        "owner": "scanner",
    }
    assert first.nodes[execution_id].metadata == {
        "format": "intentatlas-test-execution-map",
        "report": "reports/execution.json",
        "commit": head,
        "freshness": "aligned",
        "completeness": "complete-observed-set",
        "observed_files": 1,
        "owner": "scanner",
    }
    relationships = {
        (edge.source, edge.target, edge.relation, edge.evidence) for edge in first.edges
    }
    assert (scip_id, "file:src/app.py", "references", "scip-json") in relationships
    assert (sarif_id, "file:src/app.py", "references", "sarif-2.1.0") in relationships
    assert (
        "file:tests/test_app.py",
        "file:src/app.py",
        "tests",
        "test-execution-map",
    ) in relationships
    assert not any(
        source in {scip_id, sarif_id} and relation in {"proves", "tests", "changes"}
        for source, _target, relation, _evidence in relationships
    )
    recommendation = recommend_tests(first, "file:src/app.py")
    assert [item.test.id for item in recommendation.recommendations] == [
        "file:tests/test_app.py"
    ]
    assert "test-execution-map" in recommendation.recommendations[0].reasons[0].evidence
    assert first.nodes == second.nodes == incremental.nodes
    assert first.edges == second.edges == incremental.edges

    persisted = json.dumps(first.to_dict(), sort_keys=True)
    for forbidden in (
        "do-not-retain",
        "secret source",
        "secret-external-symbol",
        "file:///not-retained",
        str(tmp_path),
        "outside.py",
    ):
        assert forbidden not in persisted


def test_stale_and_unknown_execution_maps_withhold_runtime_test_edges(tmp_path) -> None:
    config, _head = build_open_evidence_project(tmp_path)
    report = tmp_path / "reports" / "execution.json"
    document = json.loads(report.read_text(encoding="utf-8"))
    document["commit"] = "0" * 40
    report.write_text(json.dumps(document), encoding="utf-8")

    stale = scan_repository(tmp_path, config)
    node_id = "test-execution:reports/execution.json:tests/test_app.py"
    assert stale.nodes[node_id].metadata["freshness"] == "stale"
    assert not any(
        edge.evidence == "test-execution-map" and edge.relation == "tests"
        for edge in stale.edges
    )
    assert recommend_tests(stale, "file:src/app.py").recommendations == ()

    (tmp_path / ".git").rename(tmp_path / "git-disabled")
    unknown = scan_repository(tmp_path, config)
    assert unknown.nodes[node_id].metadata["freshness"] == "unknown"
    assert not any(
        edge.evidence == "test-execution-map" and edge.relation == "tests"
        for edge in unknown.edges
    )


def test_dirty_mapped_paths_make_matching_commit_execution_stale(tmp_path) -> None:
    config, _head = build_open_evidence_project(tmp_path)
    (tmp_path / "src" / "app.py").write_text(
        "def run():\n    return False\n", encoding="utf-8"
    )

    graph = scan_repository(tmp_path, config)
    node_id = "test-execution:reports/execution.json:tests/test_app.py"

    assert graph.nodes[node_id].metadata["freshness"] == "stale"
    assert not any(
        edge.evidence == "test-execution-map" and edge.relation == "tests"
        for edge in graph.edges
    )


@pytest.mark.parametrize("field", ["scip_reports", "sarif_reports", "test_execution_reports"])
def test_open_evidence_uses_existing_safe_report_boundary(tmp_path, field) -> None:
    ProjectVault((tmp_path / "atlas").resolve()).initialize()
    config = ProjectConfig(git_history_limit=0, **{field: ["atlas/Private/secret.json"]})
    with pytest.raises(ValueError, match="atlas/Private"):
        scan_repository(tmp_path, config)


def test_rejects_malformed_duplicate_binary_and_unbounded_open_evidence(
    tmp_path, monkeypatch
) -> None:
    config, _head = build_open_evidence_project(tmp_path)
    scip = tmp_path / "reports" / "index.scip.json"

    scip.write_text('{"documents":[],"documents":[]}', encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate JSON key"):
        scan_repository(tmp_path, config)

    scip.write_bytes(b"\xff\x00protobuf")
    with pytest.raises(ValueError, match="Cannot parse JSON"):
        scan_repository(tmp_path, config)

    monkeypatch.setattr(open_evidence_module, "MAX_RECORDS", 1)
    scip.write_text(
        json.dumps(
            {
                "documents": [
                    {
                        "relativePath": "src/app.py",
                        "occurrences": [
                            {"range": [0, 0, 1], "symbolRoles": 1},
                            {"range": [1, 0, 1], "symbolRoles": 0},
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="record limit"):
        scan_repository(tmp_path, config)


def test_rejects_invalid_execution_map_contract_and_sarif_version(tmp_path) -> None:
    config, _head = build_open_evidence_project(tmp_path)
    execution = tmp_path / "reports" / "execution.json"
    document = json.loads(execution.read_text(encoding="utf-8"))
    document["unknown"] = True
    execution.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid test execution map"):
        scan_repository(tmp_path, config)

    config.test_execution_reports = []
    sarif = tmp_path / "reports" / "results.sarif"
    document = json.loads(sarif.read_text(encoding="utf-8"))
    document["version"] = "2.0.0"
    sarif.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(ValueError, match="not version 2.1.0"):
        scan_repository(tmp_path, config)
