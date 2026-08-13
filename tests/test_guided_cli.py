from __future__ import annotations

import hashlib
import io
import os
import shutil
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest

from intentatlas import cli, onboarding
from intentatlas.change_analysis import ChangeAnalysis, ChangeAnalysisFile
from intentatlas.change_report import build_change_report
from intentatlas.change_set import ChangeFile, ChangeSet, DiffHunk
from intentatlas.graph import AtlasGraph
from intentatlas.models import Edge, Node
from intentatlas.onboarding import (
    GuideSnapshot,
    TerminalIO,
    resolve_git_root,
    run_guide,
    select_default_scope,
)

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="Git is required")


class TTYBuffer(io.StringIO):
    def isatty(self) -> bool:
        return True


class InterruptingInput(TTYBuffer):
    def readline(self, *args, **kwargs):  # noqa: ANN002, ANN003, ANN201
        raise KeyboardInterrupt


class ASCIIOutput(io.TextIOBase):
    def __init__(self) -> None:
        self.values: list[str] = []

    @property
    def encoding(self) -> str:
        return "ascii"

    def isatty(self) -> bool:
        return True

    def write(self, value: str) -> int:
        value.encode("ascii")
        self.values.append(value)
        return len(value)

    def flush(self) -> None:
        return None


def terminal_input(value: str) -> tuple[TerminalIO, TTYBuffer]:
    output = TTYBuffer()
    return TerminalIO(TTYBuffer(value), output), output


def git(root: Path, *arguments: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def repository(root: Path, *, commit: bool = True) -> str | None:
    root.mkdir(parents=True, exist_ok=True)
    git(root, "init", "-q")
    git(root, "config", "user.email", "intentatlas@example.invalid")
    git(root, "config", "user.name", "IntentAtlas Test")
    (root / "app.py").write_text("def run():\n    return 1\n", encoding="utf-8")
    (root / "test_app.py").write_text(
        "from app import run\n\ndef test_run():\n    assert run() == 1\n",
        encoding="utf-8",
    )
    if not commit:
        return None
    git(root, "add", "app.py", "test_app.py")
    git(root, "commit", "-qm", "baseline")
    return git(root, "rev-parse", "HEAD")


def project_snapshot(root: Path) -> tuple[str, ...]:
    values: list[str] = []
    for current, directories, files in os.walk(root):
        directories[:] = sorted(name for name in directories if name != ".git")
        for name in sorted(files):
            path = Path(current) / name
            relative = path.relative_to(root).as_posix()
            data = path.read_bytes()
            stat = path.stat()
            values.append(
                f"{relative}|{stat.st_size}|{stat.st_mtime_ns}|{hashlib.sha256(data).hexdigest()}"
            )
    return tuple(values)


def git_snapshot(root: Path) -> tuple[str, str, str, str]:
    return (
        git(root, "rev-parse", "HEAD"),
        git(root, "status", "--porcelain=v1", "--untracked-files=all"),
        git(root, "diff", "--binary"),
        git(root, "diff", "--cached", "--binary"),
    )


def semantic_graph(*, include_test: bool = True, second_test: bool = False) -> AtlasGraph:
    graph = AtlasGraph()
    nodes = [
        Node("REQ-GUIDE", "requirement", "Guide requirement"),
        Node("ADR-GUIDE", "decision", "Guide decision"),
        Node("ISSUE-GUIDE", "issue", "Guide issue"),
        Node("file:app.py", "file", "app.py", path="app.py"),
        Node(
            "symbol:app.py::run",
            "symbol",
            "run",
            path="app.py",
            metadata={"line": 1, "end_line": 2},
        ),
    ]
    edges = [
        Edge("REQ-GUIDE", "ADR-GUIDE", "drives", "wikilink"),
        Edge("ADR-GUIDE", "ISSUE-GUIDE", "tracked-by", "wikilink"),
        Edge("ISSUE-GUIDE", "symbol:app.py::run", "implemented-by", "wikilink"),
        Edge("file:app.py", "symbol:app.py::run", "defines", "python-ast"),
    ]
    if include_test:
        nodes.append(Node("file:test_app.py", "test", "test_app.py", path="test_app.py"))
        edges.append(
            Edge(
                "file:test_app.py",
                "symbol:app.py::run",
                "tests",
                "python-symbol-reference",
            )
        )
    if second_test:
        nodes.append(
            Node("file:test_app_alt.py", "test", "test_app_alt.py", path="test_app_alt.py")
        )
        edges.append(
            Edge(
                "file:test_app_alt.py",
                "symbol:app.py::run",
                "tests",
                "python-symbol-reference",
            )
        )
    graph.extend(nodes, edges)
    return graph


def semantic_analysis(
    state: str,
    *,
    freshness: str = "aligned",
    empty: bool = False,
) -> ChangeAnalysis:
    change_set = ChangeSet(
        "commit",
        "a" * 40,
        "b" * 40,
        ()
        if empty
        else (ChangeFile("modified", "app.py", hunks=(DiffHunk("app.py", 1, 1),)),),
    )
    if empty:
        return ChangeAnalysis(change_set, "unknown", ())
    if state == "analyzed":
        artifacts = ("symbol:app.py::run",)
        confidence = "high"
        evidence = ("validated-symbol-span",)
    elif state == "fallback":
        artifacts = ("file:app.py",)
        confidence = "low"
        evidence = ("file-level-fallback",)
    else:
        artifacts = ()
        confidence = "none"
        evidence = ("revision-worktree-mismatch",)
    return ChangeAnalysis(
        change_set,
        state,
        (
            ChangeAnalysisFile(
                "app.py",
                "modified",
                state,
                freshness,
                confidence,
                artifacts,
                evidence,
            ),
        ),
    )


def test_default_scope_order_covers_clean_staged_unstaged_untracked_and_unborn(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo"
    head = repository(root)
    clean = select_default_scope(root)
    assert clean.scope == "commit"
    assert clean.revision == head

    (root / "staged.py").write_text("value = 1\n", encoding="utf-8")
    git(root, "add", "staged.py")
    assert select_default_scope(root).scope == "staged"

    (root / "app.py").write_text("def run():\n    return 2\n", encoding="utf-8")
    assert select_default_scope(root).scope == "worktree"

    git(root, "restore", "app.py")
    git(root, "restore", "--staged", "staged.py")
    (root / "staged.py").unlink()
    (root / "untracked.py").write_text("value = 2\n", encoding="utf-8")
    assert select_default_scope(root).scope == "worktree"

    unborn = tmp_path / "unborn"
    repository(unborn, commit=False)
    assert select_default_scope(unborn).scope == "worktree"


def test_conflict_selects_worktree_and_detached_head_is_exact(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    head = repository(root)
    assert head is not None
    git(root, "checkout", "-qb", "other")
    (root / "app.py").write_text("def run():\n    return 2\n", encoding="utf-8")
    git(root, "commit", "-qam", "other change")
    git(root, "checkout", "-q", "master")
    (root / "app.py").write_text("def run():\n    return 3\n", encoding="utf-8")
    git(root, "commit", "-qam", "main change")
    git(root, "merge", "other", check=False)
    assert select_default_scope(root).scope == "worktree"
    git(root, "merge", "--abort")
    git(root, "checkout", "-q", "--detach", "HEAD")
    selected = select_default_scope(root)
    assert selected.scope == "commit"
    assert selected.revision == git(root, "rev-parse", "HEAD")


def test_root_resolution_is_nearest_explicit_quoted_and_private_safe(tmp_path: Path) -> None:
    outer = tmp_path / "outer repo"
    repository(outer)
    nested = outer / "nested" / "deeper"
    nested.mkdir(parents=True)
    inner = outer / "nested" / "inner"
    repository(inner)
    leaf = inner / "src"
    leaf.mkdir()

    assert resolve_git_root(f'"{leaf}"') == inner.resolve()
    assert resolve_git_root(nested) == outer.resolve()
    with pytest.raises(ValueError, match="atlas/Private"):
        resolve_git_root(outer / "atlas" / "Private" / "missing")
    with pytest.raises(ValueError, match="not a directory"):
        resolve_git_root(outer / "app.py")
    with pytest.raises(ValueError, match="does not exist"):
        resolve_git_root(tmp_path / "missing")


def test_root_resolution_rejects_symlink_or_junction_escape(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    repository(root)
    link = tmp_path / "linked-repo"
    try:
        link.symlink_to(root, target_is_directory=True)
    except OSError:
        pytest.skip("Directory links are unavailable")
    with pytest.raises(ValueError, match="symbolic-link|unsafe"):
        resolve_git_root(link)


def test_common_guide_path_reaches_production_report_with_one_enter_and_no_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "repo"
    head = repository(root)
    before = project_snapshot(root)
    before_git = git_snapshot(root)
    observed: list[list[str]] = []
    original_run = subprocess.run

    def guarded_run(command, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202
        rendered = [str(item) for item in command]
        observed.append(rendered)
        assert Path(rendered[0]).name.casefold() in {"git", "git.exe"}
        return original_run(command, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", guarded_run)
    terminal, output = terminal_input("\n\n")
    assert run_guide(root, language="en", terminal=terminal) == 0
    transcript = output.getvalue()
    assert transcript.startswith("=" * 68 + "\n  I N T E N T A T L A S\n")
    assert "--- SOURCE AND SCOPE ---" in transcript
    assert "--- SAFETY BOUNDARY ---" in transcript
    assert "--- ANALYSIS RESULT ---" in transcript
    assert "--- RECOMMENDATIONS ---" in transcript
    assert "--- ATLAS SNAPSHOT ---" in transcript
    assert "--- NEXT ACTION ---" in transcript
    assert "\n  [1] Show selection reasons\n" in transcript
    assert "\n  [4] Open this exact snapshot in the interactive Atlas\n" in transcript
    assert "1 reasons | 2 omissions" not in transcript
    assert f"Recommended scope: commit {head}" in transcript
    assert "Analysis state:" in transcript
    assert "Minimum confidence: medium" in transcript
    assert "Requirements:" in transcript
    assert "Tests:" in transcript
    assert "Test strategy:" in transcript
    assert "Tests executed: 0" in transcript
    assert "Not selected never means unaffected or unnecessary" in transcript
    assert project_snapshot(root) == before
    assert git_snapshot(root) == before_git
    assert observed


def test_guided_confirmation_exposes_bounded_diagnostic_limitations(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "repo"
    repository(root)
    diagnostic = onboarding.diagnose_repository(root)
    diagnostic = replace(
        diagnostic,
        unsupported_languages=("rust",),
        oversized_supported_file_count=2,
        discovery_truncated=True,
        ambiguity_state="detected",
        ambiguity_reasons=("multiple-project-roots", "discovery-limit-reached"),
    )
    monkeypatch.setattr(onboarding, "diagnose_repository", lambda _root: diagnostic)
    terminal, output = terminal_input("q\n")
    assert run_guide(root, language="en", terminal=terminal) == 0
    transcript = output.getvalue()
    assert "unsupported languages rust" in transcript
    assert "oversized supported files 2" in transcript
    assert "discovery truncated yes" in transcript
    assert "multiple-project-roots, discovery-limit-reached" in transcript


def test_invalid_config_and_collection_failure_are_actionable_without_traceback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = tmp_path / "repo"
    repository(root)
    (root / "intentatlas.json").write_text(
        '{"schema_version": 1, "vault": "atlas/Private"}',
        encoding="utf-8",
    )
    monkeypatch.setattr(sys, "stdin", TTYBuffer("\n"))
    monkeypatch.setattr(sys, "stdout", TTYBuffer())
    assert cli.main(["guide", str(root), "--language", "en"]) == 2
    assert "error:" in capsys.readouterr().err

    (root / "intentatlas.json").unlink()
    monkeypatch.setattr(
        onboarding,
        "collect_change_report_context",
        lambda *args, **kwargs: (_ for _ in ()).throw(ValueError("analysis budget exceeded")),
    )
    monkeypatch.setattr(cli, "run_guide", onboarding.run_guide)
    monkeypatch.setattr(sys, "stdin", TTYBuffer("\n"))
    monkeypatch.setattr(sys, "stdout", TTYBuffer())
    assert cli.main(["guide", str(root), "--language", "en"]) == 2
    error = capsys.readouterr().err
    assert "analysis budget exceeded" in error
    assert "Traceback" not in error


def test_git_absence_and_locale_selection_have_bounded_fallbacks(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "repo"
    repository(root)
    monkeypatch.setattr(onboarding.shutil, "which", lambda _name: None)
    with pytest.raises(ValueError, match="Git is required"):
        select_default_scope(root)

    monkeypatch.setattr(onboarding.locale, "getlocale", lambda: ("tr_TR", "UTF-8"))
    assert onboarding._language(None) == "tr"
    monkeypatch.setattr(onboarding.locale, "getlocale", lambda: ("de_DE", "UTF-8"))
    assert onboarding._language(None) == "en"
    assert onboarding._language("en") == "en"


def test_explicit_scope_change_and_unborn_empty_report_are_truthful(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    repository(root)
    (root / "app.py").write_text("def run():\n    return 4\n", encoding="utf-8")
    terminal, output = terminal_input("s\nw\n\n\n")
    assert run_guide(root, language="en", terminal=terminal) == 0
    assert "Recommended scope: worktree" in output.getvalue()

    unborn = tmp_path / "unborn"
    unborn.mkdir()
    git(unborn, "init", "-q")
    terminal, output = terminal_input("\n\n")
    assert run_guide(unborn, language="en", terminal=terminal) == 0
    assert "Test strategy: no-changes" in output.getvalue()
    assert "Tests executed: 0" in output.getvalue()


def test_explicit_commit_and_range_are_resolved_to_exact_revisions(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    first = repository(root)
    assert first is not None
    (root / "app.py").write_text("def run():\n    return 2\n", encoding="utf-8")
    git(root, "add", "app.py")
    git(root, "commit", "-qm", "second")
    second = git(root, "rev-parse", "HEAD")

    terminal, output = terminal_input("s\nc\nHEAD\n\n\n")
    assert run_guide(root, language="en", terminal=terminal) == 0
    assert f"Recommended scope: commit {second}" in output.getvalue()

    terminal, output = terminal_input("s\nr\nHEAD~1\nHEAD\n\n\n")
    assert run_guide(root, language="en", terminal=terminal) == 0
    transcript = output.getvalue()
    assert f"Recommended scope: range {first}..{second}" in transcript
    assert f"Revision: base {first}; head {second}" in transcript


def test_browser_receives_the_exact_snapshot_without_a_second_scan(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "repo"
    repository(root)
    collected = 0
    original_collect = onboarding.collect_change_report_context
    served: dict[str, object] = {}

    def counted_collect(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
        nonlocal collected
        collected += 1
        return original_collect(*args, **kwargs)

    def fake_serve(graph_path, **kwargs) -> None:  # noqa: ANN001
        served["graph_path"] = graph_path
        served.update(kwargs)

    monkeypatch.setattr(onboarding, "collect_change_report_context", counted_collect)
    monkeypatch.setattr(onboarding, "serve_graph", fake_serve)
    terminal, _output = terminal_input("\n4\n\n")
    assert run_guide(root, language="en", terminal=terminal) == 0
    assert collected == 1
    assert served["graph_path"] is None
    assert served["host"] == "127.0.0.1"
    assert served["port"] == 0
    assert served["open_browser"] is True
    graph = served["graph_document"]
    report = served["change_report_document"]
    assert isinstance(graph, bytes) and isinstance(report, bytes)
    assert b'"schema_version": 4' in graph
    assert b'"schema_version": 1' in report


def test_browser_failure_keeps_terminal_result_valid(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "repo"
    repository(root)

    def unavailable(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
        raise OSError("browser unavailable\nforged")

    monkeypatch.setattr(onboarding, "serve_graph", unavailable)
    terminal, output = terminal_input("\n4\n\n")
    assert run_guide(root, language="en", terminal=terminal) == 0
    transcript = output.getvalue()
    assert "terminal result remains valid" in transcript
    assert "browser unavailable\\nforged" in transcript
    assert "Tests executed: 0" in transcript


def test_refusing_browser_never_starts_a_listener(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "repo"
    repository(root)

    def forbidden(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
        raise AssertionError("viewer started without explicit selection")

    monkeypatch.setattr(onboarding, "serve_graph", forbidden)
    terminal, _output = terminal_input("\n\n")
    assert run_guide(root, language="en", terminal=terminal) == 0


def test_language_catalogs_preserve_canonical_values_and_safety_meaning(tmp_path: Path) -> None:
    assert set(onboarding.MESSAGES["en"]) == set(onboarding.MESSAGES["tr"])
    for language in ("en", "tr"):
        combined = "\n".join(onboarding.MESSAGES[language].values())
        assert "atlas/Private" in combined
        assert "Tests executed: 0" in combined
        assert "worktree" in combined
        assert "staged" in combined

    root = tmp_path / "repo"
    repository(root)
    terminal, output = terminal_input("\n\n")
    assert run_guide(root, language="tr", terminal=terminal) == 0
    transcript = output.getvalue()
    assert "I N T E N T A T L A S" in transcript
    assert "--- ANALİZ SONUCU ---" in transcript
    assert "--- SONRAKİ EYLEM ---" in transcript
    assert "[4] Bu exact snapshot'ı interaktif Atlas'ta aç" in transcript
    assert "Analysis state:" in transcript
    assert "freshness:" in transcript
    assert "Minimum confidence: medium" in transcript
    assert "Tests executed: 0" in transcript


def test_language_toggle_rerenders_the_same_snapshot_without_rescanning(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "repo"
    repository(root)
    calls = 0
    original_collect = onboarding.collect_change_report_context

    def counted_collect(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
        nonlocal calls
        calls += 1
        return original_collect(*args, **kwargs)

    monkeypatch.setattr(onboarding, "collect_change_report_context", counted_collect)
    terminal, output = terminal_input("\nl\n\n")
    assert run_guide(root, language="en", terminal=terminal) == 0
    assert calls == 1
    transcript = output.getvalue()
    assert "Project:" in transcript
    assert "Proje:" in transcript
    assert transcript.count("Stage: building local evidence") == 1


def test_details_reasons_omissions_commands_and_language_are_all_no_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "repo"
    repository(root)
    before_files = project_snapshot(root)
    before_git = git_snapshot(root)
    invoked: list[str] = []
    original_run = subprocess.run

    def git_only(command, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202
        invoked.append(Path(str(command[0])).name.casefold())
        assert invoked[-1] in {"git", "git.exe"}
        return original_run(command, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", git_only)
    terminal, output = terminal_input("\n6\n1\n2\n3\nl\n\n")
    assert run_guide(root, language="en", terminal=terminal) == 0
    transcript = output.getvalue()
    assert "Commands shown only; none were executed" in transcript
    assert '"schema_version": 1' in transcript
    assert "Selection reasons from this snapshot" in transcript
    assert "Omitted candidates from this snapshot" in transcript
    assert "Proje:" in transcript
    assert project_snapshot(root) == before_files
    assert git_snapshot(root) == before_git
    assert invoked


def test_guided_projection_preserves_production_report_semantics_for_all_strategies() -> None:
    reports = (
        build_change_report(semantic_graph(), semantic_analysis("analyzed")),
        build_change_report(semantic_graph(), semantic_analysis("fallback")),
        build_change_report(
            semantic_graph(include_test=False),
            semantic_analysis("fallback"),
        ),
        build_change_report(
            semantic_graph(),
            semantic_analysis("unknown", freshness="stale"),
        ),
        build_change_report(
            semantic_graph(include_test=False),
            semantic_analysis("analyzed"),
        ),
        build_change_report(semantic_graph(), semantic_analysis("unknown", empty=True)),
    )
    assert [report.test_strategy for report in reports] == [
        "targeted",
        "targeted-plus-full-suite",
        "full-suite-fallback",
        "abstain-and-full-suite",
        "no-targets-found",
        "no-changes",
    ]
    for report in reports:
        snapshot = GuideSnapshot(
            Path("safe-repository"),
            object(),  # type: ignore[arg-type]
            report.analysis.change_set,
            semantic_graph(),
            report,
            b"{}",
            b"{}",
        )
        terminal, output = terminal_input("")
        onboarding._render_summary(snapshot, terminal, "en")
        transcript = output.getvalue()
        payload = report.to_dict()
        assert f"Analysis state: {payload['analysis_state']}" in transcript
        assert f"freshness: {payload['freshness']}" in transcript
        assert f"Minimum confidence: {payload['minimum_confidence']}" in transcript
        assert f"Test strategy: {payload['test_strategy']}" in transcript
        assert f"Changed files: {len(report.analysis.change_set.files)}" in transcript
        assert "Tests executed: 0" in transcript
        assert "unaffected or unnecessary" in transcript
        if payload["revision_action"] is not None:
            assert "Revision action: use a clean checkout" in transcript
            turkish_terminal, turkish_output = terminal_input("")
            onboarding._render_summary(snapshot, turkish_terminal, "tr")
            assert "temiz bir checkout" in turkish_output.getvalue()
            assert "intentatlas changes --commit HEAD --report" in turkish_output.getvalue()


def test_guided_projection_distinguishes_threshold_and_limit_omissions() -> None:
    graph = semantic_graph(second_test=True)
    graph.add_node(Node("REQ-FILE", "requirement", "File-level requirement"))
    graph.add_edge(Edge("REQ-FILE", "file:app.py", "implemented-by", "wikilink"))
    report = build_change_report(graph, semantic_analysis("analyzed"), limit=1)
    snapshot = GuideSnapshot(
        Path("safe-repository"),
        object(),  # type: ignore[arg-type]
        report.analysis.change_set,
        graph,
        report,
        b"{}",
        b"{}",
    )
    terminal, output = terminal_input("")
    onboarding._render_summary(snapshot, terminal, "en")
    onboarding._render_omissions(report, terminal, "en")
    transcript = output.getvalue()
    assert "below threshold" in transcript
    assert "omitted by result limit" in transcript
    assert "reason=below-minimum-confidence" in transcript
    assert "reason=result-limit" in transcript


def test_terminal_sanitizer_escapes_control_ansi_bidi_and_newlines() -> None:
    hostile = "safe\x1b[31m\nforged\u202eright"
    rendered = onboarding._terminal_text(hostile)
    assert "\x1b" not in rendered
    assert "\n" not in rendered
    assert "\u202e" not in rendered
    assert "\\x1b" in rendered
    assert "\\n" in rendered
    assert "\\u202e" in rendered


def test_terminal_output_has_ascii_fallback_and_never_depends_on_color(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = ASCIIOutput()
    terminal = TerminalIO(TTYBuffer(), output)
    monkeypatch.setenv("NO_COLOR", "1")
    monkeypatch.setenv("TERM", "dumb")
    terminal.write("Türkçe \x1b[31m")
    rendered = "".join(output.values)
    assert "\\xfc" in rendered
    assert "\\x1b" in rendered
    assert "\x1b" not in rendered


def test_unc_confirmation_does_not_claim_operating_system_access_is_network_free() -> None:
    terminal, output = terminal_input("")
    onboarding._render_confirmation(
        terminal,
        "en",
        Path(r"\\server\share\repository"),
        onboarding.GuideScope("worktree"),
    )
    transcript = output.getvalue()
    assert "operating-system access to this path may be network-backed" in transcript
    assert "Local and no external request" not in transcript


def test_ctrl_c_eof_and_q_exit_without_traceback_or_analysis(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "repo"
    repository(root)
    output = TTYBuffer()
    assert run_guide(root, terminal=TerminalIO(InterruptingInput(), output)) == 130
    assert "no persistent output" in output.getvalue()

    calls = 0

    def forbidden(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
        nonlocal calls
        calls += 1
        raise AssertionError("analysis started after exit")

    monkeypatch.setattr(onboarding, "collect_change_report_context", forbidden)
    terminal, output = terminal_input("q\n")
    assert run_guide(root, terminal=terminal) == 0
    assert calls == 0
    assert "without persistent output" in output.getvalue()
    terminal, _output = terminal_input("")
    assert run_guide(root, terminal=terminal) == 0
    assert calls == 0


def test_cli_empty_argv_tty_gate_and_explicit_non_tty_refusal(monkeypatch, capsys) -> None:
    stdin = TTYBuffer("")
    stdout = TTYBuffer()
    monkeypatch.setattr(sys, "stdin", stdin)
    monkeypatch.setattr(sys, "stdout", stdout)
    monkeypatch.setattr(cli, "run_guide", lambda: 23)
    assert cli.main([]) == 23

    monkeypatch.undo()
    called = False

    def forbidden():  # noqa: ANN202
        nonlocal called
        called = True

    monkeypatch.setattr(cli, "run_guide", forbidden)
    with pytest.raises(SystemExit) as exc:
        cli.main([])
    assert exc.value.code == 2
    assert called is False
    assert "required" in capsys.readouterr().err

    monkeypatch.setattr(cli, "run_guide", onboarding.run_guide)
    assert cli.main(["guide"]) == 2
    error = capsys.readouterr().err
    assert "requires interactive stdin and stdout" in error
    assert "intentatlas diagnose PATH" in error
    assert "--worktree --report" in error


def test_non_tty_subprocess_preserves_argparse_exit_2_without_prompt(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    repository(root)
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(Path(__file__).parents[1] / "src")
    result = subprocess.run(
        [sys.executable, "-m", "intentatlas"],
        cwd=root,
        input="must-not-be-consumed",
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=environment,
        timeout=10,
        check=False,
    )
    assert result.returncode == 2
    assert "the following arguments are required: command" in result.stderr
    assert "guided" not in result.stdout.casefold()


def test_help_exposes_additive_guide_without_runtime_dependencies(capsys) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["--help"])
    assert exc.value.code == 0
    assert "guide" in capsys.readouterr().out
