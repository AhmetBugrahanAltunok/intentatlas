from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from intentatlas.cli import main

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout


def _project_snapshot(root: Path) -> dict[str, tuple[int, int, str]]:
    snapshot: dict[str, tuple[int, int, str]] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if ".git" in relative.parts or not path.is_file():
            continue
        data = path.read_bytes()
        snapshot[relative.as_posix()] = (
            len(data),
            path.stat().st_mtime_ns,
            hashlib.sha256(data).hexdigest(),
        )
    return snapshot


def _git_snapshot(root: Path) -> tuple[str, str, str, str]:
    return (
        _git(root, "rev-parse", "HEAD"),
        _git(root, "status", "--porcelain=v1", "--untracked-files=all"),
        _git(root, "diff", "--binary"),
        _git(root, "diff", "--cached", "--binary"),
    )


@pytest.mark.skipif(shutil.which("git") is None, reason="Git is required")
def test_diagnostic_and_real_repository_preview_are_no_write(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    project = tmp_path / "trusted checkout"
    project.mkdir()
    _git(project, "init", "-q")
    _git(project, "config", "user.name", "Trust First Test")
    _git(project, "config", "user.email", "trust-first@example.invalid")
    (project / "app.py").write_text("def answer():\n    return 42\n", encoding="utf-8")
    (project / "test_app.py").write_text(
        "from app import answer\n\ndef test_answer():\n    assert answer() == 42\n",
        encoding="utf-8",
    )
    _git(project, "add", ".")
    _git(project, "commit", "-qm", "baseline")

    before_files = _project_snapshot(project)
    before_git = _git_snapshot(project)

    assert main(["diagnose", str(project)]) == 0
    diagnostic_text = capsys.readouterr().out
    assert "Read only: yes" in diagnostic_text
    assert "network required: no" in diagnostic_text
    assert "intentatlas changes --commit HEAD --report" in diagnostic_text

    assert main(["diagnose", str(project), "--format", "json"]) == 0
    diagnostic_json = json.loads(capsys.readouterr().out)
    assert diagnostic_json["read_only"] is True
    assert diagnostic_json["network_required"] is False

    assert main(["changes", str(project), "--commit", "HEAD", "--report"]) == 0
    report_text = capsys.readouterr().out
    assert "Change report: commit" in report_text
    assert "Test strategy:" in report_text
    assert "Advisory:" in report_text

    assert main(
        ["changes", str(project), "--commit", "HEAD", "--report", "--format", "json"]
    ) == 0
    report_json = json.loads(capsys.readouterr().out)
    assert report_json["scope"] == "commit"
    assert report_json["analysis_state"] in {"analyzed", "fallback", "unknown"}
    assert "requirement_selection" in report_json
    assert "test_selection" in report_json

    assert _project_snapshot(project) == before_files
    assert _git_snapshot(project) == before_git
    assert not (project / "intentatlas.json").exists()
    assert not (project / "atlas").exists()
    assert not (project / ".intentatlas").exists()


def test_trust_first_documentation_sequence_and_artifacts_are_frozen() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    readme_tr = (PROJECT_ROOT / "README.tr.md").read_text(encoding="utf-8")
    docs_index = (PROJECT_ROOT / "docs" / "index.md").read_text(encoding="utf-8")
    preview = (PROJECT_ROOT / "docs" / "trust-first-preview.md").read_text(encoding="utf-8")
    guided = (PROJECT_ROOT / "docs" / "guided-cli.md").read_text(encoding="utf-8")
    observations = (PROJECT_ROOT / "docs" / "first-run-observation-guide.md").read_text(
        encoding="utf-8"
    )

    quick_starts = (
        readme.split("## Quick start", maxsplit=1)[1],
        readme_tr.split("## Hızlı başlangıç", maxsplit=1)[1],
        preview,
    )
    for document in quick_starts:
        assert document.index("demo --report text") < document.index("diagnose")
        assert document.index("diagnose") < document.index("changes")
        assert document.index("changes") < document.index(" init ")
    assert "guided-demo.md" in docs_index
    assert "guided-cli.md" in docs_index
    assert "trust-first-preview.md" in docs_index
    assert "onboarding-walkthroughs.md" in docs_index
    assert "first-run-observation-guide.md" in docs_index
    assert "both stdin and stdout are TTYs" in guided
    assert "Tests executed: 0" in guided
    assert "five independent" in guided
    assert "not independent observations" in observations

    report_path = PROJECT_ROOT / "docs" / "examples" / "trust-first-report.json"
    image_path = PROJECT_ROOT / "docs" / "assets" / "trust-first-preview.svg"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["schema_version"] == 1
    assert report["scope"] == "range"
    assert report["freshness"] == "aligned"
    assert report["requirements"][0]["path"]["relations"] == [
        "drives",
        "tracked-by",
        "implemented-by",
    ]
    assert report["omitted_requirements"][0]["reason"] == "below-minimum-confidence"
    assert report["test_strategy"] == "targeted"
    assert hashlib.sha256(report_path.read_bytes()).hexdigest() == (
        "7bd2ab8495f033d4e4833022fb9ec866f78066ae3e83d87c451cfad61f7238c1"
    )
    assert hashlib.sha256(image_path.read_bytes()).hexdigest() == (
        "c4a44299686c84478478a6db127b5caa033af24ca4872a1c14758c87283c6809"
    )
