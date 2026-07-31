from __future__ import annotations

import json
from pathlib import Path

import pytest

import intentatlas.delivery as delivery_module
from intentatlas.config import ProjectConfig
from intentatlas.delivery import import_delivery
from intentatlas.models import Node
from intentatlas.scanner import scan_repository
from intentatlas.vault import GENERATED_MARKER, ProjectVault

DELIVERY_FIXTURE = Path(__file__).parent / "fixtures" / "delivery_project"
ISSUE_ID = "delivery-issue:github-export:acme%2Fdemo:12"
PR_ID = "pull-request:github-export:acme%2Fdemo:45"


def test_imports_local_delivery_context_deterministically() -> None:
    config = ProjectConfig.load(DELIVERY_FIXTURE)
    first = scan_repository(DELIVERY_FIXTURE, config)
    second = scan_repository(DELIVERY_FIXTURE, config)

    assert first.nodes == second.nodes
    assert first.edges == second.edges
    assert first.nodes[ISSUE_ID].kind == "delivery-issue"
    assert first.nodes[ISSUE_ID].metadata == {
        "source": "github-export",
        "repository": "acme/demo",
        "external_id": "12",
        "state": "open",
        "url": "https://example.invalid/acme/demo/issues/12",
        "labels": ["enhancement", "intent"],
        "report": "reports/delivery.json",
        "owner": "scanner",
    }
    assert first.nodes[PR_ID].kind == "pull-request"
    relationships = {
        (edge.source, edge.target, edge.relation, edge.evidence) for edge in first.edges
    }
    assert ("REQ-DELIVERY", ISSUE_ID, "tracked-by", "delivery-json") in relationships
    assert (ISSUE_ID, PR_ID, "addressed-by", "delivery-json") in relationships
    assert (PR_ID, "file:src/app.py", "changes", "delivery-json") in relationships
    assert not any(
        "outside.py" in edge.target or "missing.py" in edge.target for edge in first.edges
    )
    assert not any("000000" in edge.target for edge in first.edges)


def test_delivery_nodes_sync_to_generated_commit_subfolders(tmp_path: Path) -> None:
    graph = scan_repository(DELIVERY_FIXTURE, ProjectConfig.load(DELIVERY_FIXTURE))
    vault = ProjectVault(tmp_path / "atlas")

    vault.sync(graph)
    issue_notes = list((vault.root / "Commits" / "Issues").glob("*.md"))
    pr_notes = list((vault.root / "Commits" / "Pull Requests").glob("*.md"))
    assert len(issue_notes) == 1
    assert len(pr_notes) == 1
    assert GENERATED_MARKER in issue_notes[0].read_text(encoding="utf-8")
    assert "addressed-by" in issue_notes[0].read_text(encoding="utf-8")
    vault.sync(graph)
    assert len(list((vault.root / "Commits" / "Issues").glob("*.md"))) == 1


def test_delivery_links_only_exact_known_commit_shas(tmp_path: Path) -> None:
    reports = tmp_path / "reports"
    reports.mkdir()
    report = reports / "delivery.json"
    report.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source": "fixture",
                "repository": "demo/repo",
                "pull_requests": [
                    {
                        "id": 7,
                        "title": "Known commit",
                        "state": "merged",
                        "commit_shas": ["abc123", "missing"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    fragment = import_delivery(
        tmp_path,
        files={},
        graph_nodes={"commit:abc123": Node("commit:abc123", "commit", "Known")},
        vault=tmp_path / "atlas",
        reports=["reports/delivery.json"],
    )
    pr_id = "pull-request:fixture:demo%2Frepo:7"
    assert (pr_id, "commit:abc123", "references") in {
        (edge.source, edge.target, edge.relation) for edge in fragment.edges
    }
    assert not any(edge.target == "commit:missing" for edge in fragment.edges)


@pytest.mark.parametrize(
    ("configured", "message"),
    [
        ("../outside.json", "project-relative"),
        ("atlas/Private/delivery.json", "atlas/Private"),
        ("missing.json", "does not exist"),
    ],
)
def test_rejects_unsafe_or_missing_delivery_paths(tmp_path, configured, message) -> None:
    config = ProjectConfig(git_history_limit=0, delivery_reports=[configured])
    ProjectVault(config.vault_path(tmp_path)).initialize()
    with pytest.raises(ValueError, match=message):
        scan_repository(tmp_path, config)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ({"schema_version": 99}, "Unsupported delivery report schema"),
        ({"body": "raw secret body"}, "Unknown delivery report field"),
        ({"issues": "not-a-list"}, "list of objects"),
    ],
)
def test_rejects_invalid_delivery_schema(tmp_path, mutation, message) -> None:
    reports = tmp_path / "reports"
    reports.mkdir()
    document = {
        "schema_version": 1,
        "source": "fixture",
        "repository": "demo/repo",
        "issues": [],
        "pull_requests": [],
    }
    document.update(mutation)
    (reports / "delivery.json").write_text(json.dumps(document), encoding="utf-8")
    config = ProjectConfig(git_history_limit=0, delivery_reports=["reports/delivery.json"])
    ProjectVault(config.vault_path(tmp_path)).initialize()
    with pytest.raises(ValueError, match=message):
        scan_repository(tmp_path, config)


def test_rejects_duplicate_keys_unsafe_urls_and_bounds(tmp_path, monkeypatch) -> None:
    reports = tmp_path / "reports"
    reports.mkdir()
    report = reports / "delivery.json"
    config = ProjectConfig(git_history_limit=0, delivery_reports=["reports/delivery.json"])
    ProjectVault(config.vault_path(tmp_path)).initialize()

    report.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate JSON key"):
        scan_repository(tmp_path, config)

    report.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source": "fixture",
                "repository": "demo/repo",
                "issues": [
                    {
                        "id": 1,
                        "title": "Unsafe URL",
                        "state": "open",
                        "url": "https://example.invalid/issues/1?token=secret",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Invalid delivery issue URL"):
        scan_repository(tmp_path, config)

    monkeypatch.setattr(delivery_module, "MAX_REPORT_BYTES", 8)
    with pytest.raises(ValueError, match="byte limit"):
        scan_repository(tmp_path, config)


def test_rejects_symbolic_link_delivery_report_before_reading(tmp_path, monkeypatch) -> None:
    reports = tmp_path / "reports"
    reports.mkdir()
    report = reports / "delivery.json"
    report.write_text("{}", encoding="utf-8")
    config = ProjectConfig(git_history_limit=0, delivery_reports=["reports/delivery.json"])
    ProjectVault(config.vault_path(tmp_path)).initialize()
    original_is_symlink = Path.is_symlink

    def guarded_is_symlink(path: Path) -> bool:
        return path == report or original_is_symlink(path)

    monkeypatch.setattr(Path, "is_symlink", guarded_is_symlink)
    with pytest.raises(ValueError, match="symbolic link"):
        scan_repository(tmp_path, config)
