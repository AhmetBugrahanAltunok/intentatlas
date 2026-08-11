from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from intentatlas.cli import main
from intentatlas.diagnostic import diagnose_repository, render_diagnostic


def _snapshot(root: Path) -> tuple[tuple[str, str, int, int, str], ...]:
    values: list[tuple[str, str, int, int, str]] = []
    for current, directories, filenames in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        directories[:] = sorted(
            (name for name in directories if name.casefold() != ".git"),
            key=str.casefold,
        )
        for name in directories:
            path = current_path / name
            stat = path.lstat()
            values.append(
                (path.relative_to(root).as_posix(), "directory", 0, stat.st_mtime_ns, "")
            )
        for name in sorted(filenames, key=str.casefold):
            path = current_path / name
            stat = path.lstat()
            digest = "link" if path.is_symlink() else hashlib.sha256(path.read_bytes()).hexdigest()
            values.append(
                (path.relative_to(root).as_posix(), "file", stat.st_size, stat.st_mtime_ns, digest)
            )
    return tuple(sorted(values))


def _git(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout.strip()


@pytest.mark.skipif(shutil.which("git") is None, reason="Git is required")
def test_diagnostic_is_deterministic_and_no_write_without_config_or_vault(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.name", "Diagnostic Test")
    _git(tmp_path, "config", "user.email", "diagnostic@example.invalid")
    (tmp_path / "app.py").write_text("def run():\n    return True\n", encoding="utf-8")
    _git(tmp_path, "add", "app.py")
    _git(tmp_path, "commit", "-qm", "baseline")
    before = _snapshot(tmp_path)
    git_before = _git(tmp_path, "status", "--porcelain=v1")

    first = diagnose_repository(tmp_path)
    second = diagnose_repository(tmp_path)

    assert render_diagnostic(first, "json") == render_diagnostic(second, "json")
    payload = json.loads(render_diagnostic(first, "json"))
    assert payload["schema_version"] == 1
    assert payload["read_only"] is True
    assert payload["network_required"] is False
    assert payload["config"]["state"] == "missing"
    assert payload["repository"]["git_state"] == "ready"
    assert payload["artifacts"]["change_report_state"] == "available-unassessed"
    assert payload["next_safe_command"] == (
        f"intentatlas changes {subprocess.list2cmdline([str(tmp_path.resolve())])} "
        "--commit HEAD --report"
    )
    assert main(["diagnose", str(tmp_path), "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out) == payload
    assert _snapshot(tmp_path) == before
    assert _git(tmp_path, "status", "--porcelain=v1") == git_before
    assert not (tmp_path / "intentatlas.json").exists()
    assert not (tmp_path / "atlas").exists()
    assert not (tmp_path / ".intentatlas").exists()


def test_diagnostic_reports_experimental_unsupported_oversize_and_ambiguity(
    tmp_path: Path,
) -> None:
    for relative in (
        "src/app.py",
        "packages/client/index.ts",
        "packages/server/index.ts",
        "native/lib.rs",
        "package.json",
        "packages/client/package.json",
    ):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}\n", encoding="utf-8")
    (tmp_path / "src/large.py").write_bytes(b"x" * 1_000_001)

    payload = diagnose_repository(tmp_path).to_dict()

    assert payload["ambiguity"] == {
        "state": "detected",
        "reasons": ["multiple-project-roots", "multiple-source-roots"],
        "detail": (
            "Detected roots are bounded readiness heuristics, not proof that symbol resolution "
            "abstained; the scanner independently requires unique declared workspace ownership, "
            "module identity, and symbol identity. No action is required for this heuristic "
            "alone. If an actual result reports ambiguous ownership, exclude unrelated nested "
            "fixtures/projects in intentatlas.json or correct the relevant project manifests, "
            "then run scan again."
        ),
    }
    assert payload["project_roots"] == [".", "packages/client"]
    assert payload["source_roots"] == ["packages/client", "packages/server", "src"]
    assert payload["unsupported_languages"] == ["rust"]
    assert payload["repository"]["oversized_supported_file_count"] == 1
    python = next(item for item in payload["capabilities"] if item["adapter"] == "python")
    assert python["support_level"] == "experimental"
    assert python["detected_file_count"] == 2


def test_diagnostic_rejects_private_config_without_reading_private(tmp_path: Path) -> None:
    private = tmp_path / "atlas" / "Private"
    private.mkdir(parents=True)
    sentinel = private / "secret.py"
    sentinel.write_text("raise RuntimeError('must not be read')\n", encoding="utf-8")
    (tmp_path / "intentatlas.json").write_text(
        json.dumps({"schema_version": 1, "vault": "atlas/Private"}),
        encoding="utf-8",
    )
    before = _snapshot(private)

    payload = diagnose_repository(tmp_path).to_dict()

    assert payload["config"]["state"] == "invalid"
    assert payload["artifacts"]["graph_state"] == "unavailable-invalid-config"
    assert "secret.py" not in json.dumps(payload)
    assert _snapshot(private) == before


def test_diagnostic_text_preserves_safe_next_action_and_advisory(tmp_path: Path) -> None:
    rendered = render_diagnostic(diagnose_repository(tmp_path), "text")

    assert "IntentAtlas read-only diagnostic" in rendered
    assert "Evidence: not-configured; freshness not-assessed" in rendered
    assert "Next safe command: intentatlas demo --report text" in rendered
    assert "absence is not proof of no impact" in rendered
    assert "Ambiguity guidance:" in rendered
    assert "No action is required for this heuristic alone" in rendered
    assert "not proof that symbol resolution abstained" in rendered


@pytest.mark.skipif(shutil.which("git") is None, reason="Git is required")
def test_diagnostic_next_command_quotes_the_project_path(tmp_path: Path) -> None:
    project = tmp_path / "project with spaces"
    project.mkdir()
    _git(project, "init", "-q")
    (project / "app.py").write_text("value = 1\n", encoding="utf-8")
    _git(project, "add", "app.py")
    _git(project, "config", "user.name", "Diagnostic Test")
    _git(project, "config", "user.email", "diagnostic@example.invalid")
    _git(project, "commit", "-qm", "baseline")

    result = diagnose_repository(project)

    quoted = subprocess.list2cmdline([str(project.resolve())])
    assert result.next_safe_command == (
        f"intentatlas changes {quoted} --commit HEAD --report"
    )
