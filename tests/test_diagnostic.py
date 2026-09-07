from __future__ import annotations

import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import intentatlas.diagnostic as diagnostic_module
from intentatlas.cli import main
from intentatlas.config import ProjectConfig
from intentatlas.diagnostic import diagnose_repository, render_diagnostic
from intentatlas.scanner import scan_repository


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


def _quoted_command_path(path: Path) -> str:
    value = str(path.resolve())
    if os.name == "nt":
        return subprocess.list2cmdline([value])
    return shlex.quote(value)


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
    assert payload["project_root"] == str(tmp_path.resolve())
    assert payload["config"]["state"] == "missing"
    assert payload["repository"]["git_state"] == "ready"
    assert payload["artifacts"]["change_report_state"] == "available-unassessed"
    assert payload["recommended_change_scope"]["scope"] == "commit"
    assert payload["symbol_test_links"]["state"] == "not-assessed"
    assert payload["next_safe_command"] == (
        f"intentatlas changes {_quoted_command_path(tmp_path)} "
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
    assert f"Project: {tmp_path.resolve()}" in rendered
    assert "Evidence: not-configured; freshness not-assessed" in rendered
    assert "Next safe command: intentatlas demo --report text" in rendered
    assert "absence is not proof of no impact" in rendered
    assert "Ambiguity guidance:" in rendered
    assert "No action is required for this heuristic alone" in rendered
    assert "not proof that symbol resolution abstained" in rendered
    assert "Exact Python symbol-test links: not-assessed" in rendered


def test_diagnostic_git_runner_bounds_stdout_during_collection_and_times_out(
    tmp_path: Path,
) -> None:
    overflow = [
        sys.executable,
        "-c",
        "import sys; sys.stdout.buffer.write(b'x' * 4097)",
    ]
    delayed = [sys.executable, "-c", "import time; time.sleep(60)"]

    assert diagnostic_module._run_git_bounded(
        overflow,
        cwd=tmp_path,
        max_bytes=4096,
        timeout=5,
    ) is None
    assert diagnostic_module._run_git_bounded(
        delayed,
        cwd=tmp_path,
        max_bytes=4096,
        timeout=0.05,
    ) is None


def test_diagnostic_cli_contains_git_timeout_and_process_errors(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    (tmp_path / ".git").mkdir()
    monkeypatch.setattr(diagnostic_module.shutil, "which", lambda _name: "git")

    def timeout(*_args, **_kwargs):
        raise subprocess.TimeoutExpired(["git"], 10)

    monkeypatch.setattr(diagnostic_module, "_run_git_bounded", timeout)
    assert main(["diagnose", str(tmp_path), "--format", "json"]) == 0
    captured = capsys.readouterr()
    assert json.loads(captured.out)["repository"]["git_state"] == "not-a-repository"
    assert "Traceback" not in captured.err

    monkeypatch.setattr(
        diagnostic_module,
        "_git_readiness",
        lambda _root: ("ready", "a" * 40),
    )

    def process_error(*_args, **_kwargs):
        raise subprocess.SubprocessError("simulated process failure")

    monkeypatch.setattr(diagnostic_module, "_run_git_bounded", process_error)
    result = diagnose_repository(tmp_path)
    assert result.recommended_scope == "worktree"
    assert result.scope_detail.startswith("Git change state could not be fully inspected")


def test_diagnostic_reports_missing_and_ready_exact_python_test_links(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "src" / "auth.py").write_text(
        "def rotate_session(value: str) -> str:\n    return value[::-1]\n",
        encoding="utf-8",
    )
    test = tmp_path / "tests" / "test_auth_rotation.py"
    test.write_text("def test_placeholder():\n    assert True\n", encoding="utf-8")
    graph_path = tmp_path / ".intentatlas" / "graph.json"
    scan_repository(tmp_path, ProjectConfig(git_history_limit=0)).save(graph_path)

    missing = diagnose_repository(tmp_path).to_dict()["symbol_test_links"]

    assert missing["state"] == "missing-exact-links"
    assert missing["python_test_count"] == 1
    assert missing["exact_link_count"] == 0

    test.write_text(
        "from src.auth import rotate_session\n\n"
        "def test_rotate_session():\n    assert rotate_session('abc') == 'cba'\n",
        encoding="utf-8",
    )
    scan_repository(tmp_path, ProjectConfig(git_history_limit=0)).save(graph_path)

    ready = diagnose_repository(tmp_path).to_dict()["symbol_test_links"]

    assert ready["state"] == "ready"
    assert ready["python_test_count"] == 1
    assert ready["exact_link_count"] == 1


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

    quoted = _quoted_command_path(project)
    assert result.next_safe_command == (
        f"intentatlas changes {quoted} --commit HEAD --report"
    )


@pytest.mark.skipif(shutil.which("git") is None, reason="Git is required")
def test_diagnostic_selects_worktree_staged_and_clean_scopes(tmp_path: Path) -> None:
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.name", "Diagnostic Test")
    _git(tmp_path, "config", "user.email", "diagnostic@example.invalid")
    tracked = tmp_path / "app.py"
    tracked.write_text("value = 1\n", encoding="utf-8")
    _git(tmp_path, "add", "app.py")
    _git(tmp_path, "commit", "-qm", "baseline")

    clean = diagnose_repository(tmp_path)
    assert clean.recommended_scope == "commit"
    assert clean.next_safe_command.endswith("--commit HEAD --report")

    tracked.write_text("value = 2\n", encoding="utf-8")
    dirty = diagnose_repository(tmp_path)
    assert dirty.recommended_scope == "worktree"
    assert dirty.next_safe_command.endswith("--worktree --report")

    _git(tmp_path, "add", "app.py")
    staged = diagnose_repository(tmp_path)
    assert staged.recommended_scope == "staged"
    assert staged.next_safe_command.endswith("--staged --report")


@pytest.mark.skipif(shutil.which("git") is None, reason="Git is required")
def test_diagnostic_scope_ignores_private_and_generated_paths(tmp_path: Path) -> None:
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.name", "Diagnostic Test")
    _git(tmp_path, "config", "user.email", "diagnostic@example.invalid")
    (tmp_path / "app.py").write_text("value = 1\n", encoding="utf-8")
    _git(tmp_path, "add", "app.py")
    _git(tmp_path, "commit", "-qm", "baseline")
    private = tmp_path / "atlas" / "Private"
    private.mkdir(parents=True)
    (private / "secret.py").write_text("must not affect scope\n", encoding="utf-8")
    generated = tmp_path / ".intentatlas"
    generated.mkdir()
    (generated / "cache.json").write_text("{}\n", encoding="utf-8")

    result = diagnose_repository(tmp_path)

    assert result.recommended_scope == "commit"
