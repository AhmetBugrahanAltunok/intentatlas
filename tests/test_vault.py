from __future__ import annotations

import errno
from pathlib import Path

import pytest

import intentatlas.vault as vault_module
from intentatlas.graph import AtlasGraph
from intentatlas.models import Edge, Node
from intentatlas.vault import FILE_LOCK_RETRY_DELAYS, GENERATED_MARKER, ProjectVault


def graph_fixture(*, language: str = "Python") -> AtlasGraph:
    graph = AtlasGraph()
    graph.extend(
        [
            Node(
                "REQ-1",
                "requirement",
                "Keep context",
                "Requirements/Keep context.md",
                {"owner": "user"},
            ),
            Node("file:src/app.py", "file", "src/app.py", "src/app.py", {"language": language}),
            Node("symbol:src/app.py::main", "symbol", "main", "src/app.py", {"line": 1}),
        ]
    )
    graph.add_edge(Edge("REQ-1", "file:src/app.py", "implemented-by", "wikilink"))
    graph.add_edge(Edge("file:src/app.py", "symbol:src/app.py::main", "defines", "python-ast"))
    return graph


def test_vault_initializes_obsidian_and_preserves_user_owned_notes(tmp_path) -> None:
    vault = ProjectVault(tmp_path / "atlas")
    vault.initialize()
    private = tmp_path / "atlas" / "Private" / "mine.md"
    private.write_text("never touch", encoding="utf-8")
    requirement = tmp_path / "atlas" / "Requirements" / "Keep context.md"
    requirement.write_text("# My requirement\n", encoding="utf-8")

    result = vault.sync(graph_fixture())
    assert result == {"generated_notes": 2, "dashboard": 1}
    assert private.read_text(encoding="utf-8") == "never touch"
    assert requirement.read_text(encoding="utf-8") == "# My requirement\n"
    assert (tmp_path / "atlas" / ".obsidian" / "graph.json").exists()

    generated = next((tmp_path / "atlas" / "Code").glob("*.md"))
    content = generated.read_text(encoding="utf-8")
    assert GENERATED_MARKER in content
    assert "[[Requirements/Keep context|Keep context]]" in content
    assert "[[Symbols/main - src - app.py|main]]" in content
    assert "<code>implements</code>" in content
    assert "implementation; evidence: wikilink" in content
    assert (tmp_path / "atlas" / "Issues").is_dir()
    assert (tmp_path / "atlas" / "Templates" / "Issue.md").exists()


def test_sync_removes_only_generated_notes(tmp_path) -> None:
    vault = ProjectVault(tmp_path / "atlas")
    vault.initialize()
    manual = tmp_path / "atlas" / "Code" / "manual.md"
    manual.write_text("# Keep me\n", encoding="utf-8")
    vault.sync(graph_fixture())
    first = sorted((tmp_path / "atlas" / "Code").glob("*.md"))
    vault.sync(graph_fixture())
    second = sorted((tmp_path / "atlas" / "Code").glob("*.md"))
    assert manual in second
    assert [path.name for path in first] == [path.name for path in second]


def test_sync_does_not_replace_byte_identical_generated_notes(tmp_path, monkeypatch) -> None:
    vault = ProjectVault(tmp_path / "atlas")
    vault.sync(graph_fixture())

    def unexpected_replace(source, target) -> None:
        raise AssertionError(f"Unexpected replacement: {source} -> {target}")

    monkeypatch.setattr(vault_module.os, "replace", unexpected_replace)

    assert vault.sync(graph_fixture()) == {"generated_notes": 2, "dashboard": 1}


def test_sync_replaces_text_equal_but_byte_different_generated_note(tmp_path, monkeypatch) -> None:
    vault = ProjectVault(tmp_path / "atlas")
    vault.sync(graph_fixture())
    generated = next((tmp_path / "atlas" / "Code").glob("*.md"))
    generated.write_bytes(generated.read_bytes().replace(b"\n", b"\r\n"))
    original_replace = vault_module.os.replace
    targets: list[Path] = []

    def record_replace(source, target) -> None:
        targets.append(Path(target))
        original_replace(source, target)

    monkeypatch.setattr(vault_module.os, "replace", record_replace)

    vault.sync(graph_fixture())

    assert targets == [generated]
    assert b"\r\n" not in generated.read_bytes()


def test_sync_retries_transient_atomic_replacement_and_cleans_temporary_file(
    tmp_path, monkeypatch
) -> None:
    vault = ProjectVault(tmp_path / "atlas")
    vault.sync(graph_fixture())
    generated = next((tmp_path / "atlas" / "Code").glob("*.md"))
    original_replace = vault_module.os.replace
    attempts: list[tuple[Path, Path]] = []
    delays: list[float] = []

    def transient_replace(source, target) -> None:
        attempts.append((Path(source), Path(target)))
        if len(attempts) < 3:
            raise PermissionError(errno.EACCES, "locked", str(target))
        original_replace(source, target)

    monkeypatch.setattr(vault_module.os, "replace", transient_replace)
    monkeypatch.setattr(vault_module.time, "sleep", delays.append)

    vault.sync(graph_fixture(language="Python 3"))

    assert len(attempts) == 3
    assert delays == list(FILE_LOCK_RETRY_DELAYS[:2])
    assert all(source.parent == target.parent for source, target in attempts)
    assert "Python 3" in generated.read_text(encoding="utf-8")
    assert list(generated.parent.glob("*.intentatlas.tmp")) == []


def test_missing_atomic_replace_source_is_not_treated_as_success(tmp_path, monkeypatch) -> None:
    vault = ProjectVault(tmp_path / "atlas")
    vault.sync(graph_fixture())
    generated = next((tmp_path / "atlas" / "Code").glob("*.md"))
    previous = generated.read_text(encoding="utf-8")
    stale = generated.parent / "stale.md"
    stale.write_text(f"{GENERATED_MARKER}\n# Stale\n", encoding="utf-8")
    attempts = 0

    def missing_replace(source, target) -> None:
        nonlocal attempts
        attempts += 1
        raise FileNotFoundError(errno.ENOENT, "missing", str(source))

    monkeypatch.setattr(vault_module.os, "replace", missing_replace)

    with pytest.raises(FileNotFoundError, match="missing"):
        vault.sync(graph_fixture(language="Python 3"))

    assert attempts == 1
    assert generated.read_text(encoding="utf-8") == previous
    assert stale.exists()
    assert list(generated.parent.glob("*.intentatlas.tmp")) == []


def test_non_transient_replace_failure_is_not_retried(tmp_path, monkeypatch) -> None:
    vault = ProjectVault(tmp_path / "atlas")
    vault.sync(graph_fixture())
    generated = next((tmp_path / "atlas" / "Code").glob("*.md"))
    previous = generated.read_text(encoding="utf-8")
    attempts = 0
    delays: list[float] = []

    def failed_replace(source, target) -> None:
        nonlocal attempts
        attempts += 1
        raise OSError(errno.EIO, "I/O failure", str(target))

    monkeypatch.setattr(vault_module.os, "replace", failed_replace)
    monkeypatch.setattr(vault_module.time, "sleep", delays.append)

    with pytest.raises(OSError, match="I/O failure"):
        vault.sync(graph_fixture(language="Python 3"))

    assert attempts == 1
    assert delays == []
    assert generated.read_text(encoding="utf-8") == previous
    assert list(generated.parent.glob("*.intentatlas.tmp")) == []


def test_temporary_file_is_cleaned_when_writing_it_fails(tmp_path, monkeypatch) -> None:
    vault = ProjectVault(tmp_path / "atlas")
    vault.sync(graph_fixture())
    generated = next((tmp_path / "atlas" / "Code").glob("*.md"))
    previous = generated.read_text(encoding="utf-8")
    original_named_temporary_file = vault_module.tempfile.NamedTemporaryFile

    class FailingTemporaryFile:
        def __init__(self, *args, **kwargs):
            self._context = original_named_temporary_file(*args, **kwargs)
            self._stream = None

        def __enter__(self):
            self._stream = self._context.__enter__()
            return self

        @property
        def name(self):
            return self._stream.name

        def write(self, content) -> None:
            raise OSError(errno.ENOSPC, "disk full")

        def __exit__(self, exc_type, exc, traceback):
            return self._context.__exit__(exc_type, exc, traceback)

    monkeypatch.setattr(
        vault_module.tempfile, "NamedTemporaryFile", FailingTemporaryFile
    )

    with pytest.raises(OSError, match="disk full"):
        vault.sync(graph_fixture(language="Python 3"))

    assert generated.read_text(encoding="utf-8") == previous
    assert list(generated.parent.glob("*.intentatlas.tmp")) == []


def test_persistent_replace_failure_preserves_previous_output_and_skips_stale_cleanup(
    tmp_path, monkeypatch
) -> None:
    vault = ProjectVault(tmp_path / "atlas")
    vault.sync(graph_fixture())
    generated = next((tmp_path / "atlas" / "Code").glob("*.md"))
    previous = generated.read_text(encoding="utf-8")
    stale = generated.parent / "stale.md"
    stale.write_text(f"{GENERATED_MARKER}\n# Stale\n", encoding="utf-8")
    attempts: list[Path] = []
    delays: list[float] = []

    def locked_replace(source, target) -> None:
        attempts.append(Path(target))
        raise PermissionError(errno.EACCES, "locked", str(target))

    monkeypatch.setattr(vault_module.os, "replace", locked_replace)
    monkeypatch.setattr(vault_module.time, "sleep", delays.append)

    with pytest.raises(PermissionError, match="locked"):
        vault.sync(graph_fixture(language="Python 3"))

    assert attempts == [generated] * (len(FILE_LOCK_RETRY_DELAYS) + 1)
    assert delays == list(FILE_LOCK_RETRY_DELAYS)
    assert generated.read_text(encoding="utf-8") == previous
    assert stale.exists()
    assert list(generated.parent.glob("*.intentatlas.tmp")) == []


def test_sync_retries_transient_stale_note_lock(tmp_path, monkeypatch) -> None:
    vault = ProjectVault(tmp_path / "atlas")
    vault.sync(graph_fixture())
    stale = tmp_path / "atlas" / "Code" / "stale.md"
    stale.write_text(f"{GENERATED_MARKER}\n# Stale\n", encoding="utf-8")
    original_unlink = Path.unlink
    attempts: list[Path] = []
    delays: list[float] = []

    def transient_unlink(path, *args, **kwargs) -> None:
        if path == stale:
            attempts.append(path)
            if len(attempts) < 3:
                raise PermissionError(errno.EACCES, "locked", str(path))
        original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", transient_unlink)
    monkeypatch.setattr(vault_module.time, "sleep", delays.append)

    vault.sync(graph_fixture())

    assert attempts == [stale, stale, stale]
    assert delays == list(FILE_LOCK_RETRY_DELAYS[:2])
    assert not stale.exists()


def test_sync_retries_transient_stale_note_read_lock(tmp_path, monkeypatch) -> None:
    vault = ProjectVault(tmp_path / "atlas")
    vault.sync(graph_fixture())
    stale = tmp_path / "atlas" / "Code" / "stale.md"
    stale.write_text(f"{GENERATED_MARKER}\n# Stale\n", encoding="utf-8")
    original_read_text = Path.read_text
    attempts: list[Path] = []
    delays: list[float] = []

    def transient_read_text(path, *args, **kwargs) -> str:
        if path == stale:
            attempts.append(path)
            if len(attempts) < 3:
                raise PermissionError(errno.EACCES, "locked", str(path))
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", transient_read_text)
    monkeypatch.setattr(vault_module.time, "sleep", delays.append)

    vault.sync(graph_fixture())

    assert attempts == [stale, stale, stale]
    assert delays == list(FILE_LOCK_RETRY_DELAYS[:2])
    assert not stale.exists()


def test_sync_does_not_follow_stale_generated_symlink(tmp_path, monkeypatch) -> None:
    vault = ProjectVault(tmp_path / "atlas")
    vault.sync(graph_fixture())
    stale = tmp_path / "atlas" / "Code" / "stale.md"
    stale.write_text(f"{GENERATED_MARKER}\n# Simulated symlink\n", encoding="utf-8")
    original_is_symlink = Path.is_symlink

    def simulated_symlink(path) -> bool:
        return path == stale or original_is_symlink(path)

    monkeypatch.setattr(Path, "is_symlink", simulated_symlink)

    vault.sync(graph_fixture())

    assert stale.exists()


def test_render_failure_occurs_before_generated_output_mutation(tmp_path, monkeypatch) -> None:
    vault = ProjectVault(tmp_path / "atlas")
    vault.sync(graph_fixture())
    generated = next((tmp_path / "atlas" / "Code").glob("*.md"))
    previous = generated.read_text(encoding="utf-8")
    stale = generated.parent / "stale.md"
    stale.write_text(f"{GENERATED_MARKER}\n# Stale\n", encoding="utf-8")

    def fail_render(*args, **kwargs) -> str:
        raise RuntimeError("render failed")

    monkeypatch.setattr(vault, "_render_node", fail_render)

    with pytest.raises(RuntimeError, match="render failed"):
        vault.sync(graph_fixture(language="Python 3"))

    assert generated.read_text(encoding="utf-8") == previous
    assert stale.exists()


def test_vault_escapes_untrusted_markdown_in_generated_notes(tmp_path) -> None:
    graph = AtlasGraph()
    graph.add_node(
        Node(
            "commit:abc",
            "commit",
            "fix ![load](https://example.invalid/x) <img src=x>",
            metadata={"detail": "</code><script>alert(1)</script>"},
        )
    )
    vault = ProjectVault(tmp_path / "atlas")

    vault.sync(graph)

    generated = next((tmp_path / "atlas" / "Commits").glob("*.md"))
    content = generated.read_text(encoding="utf-8")
    assert "<img" not in content
    assert "<script" not in content
    assert "![load](" not in content
    assert "&lt;img src=x&gt;" in content
    assert "&lt;/code&gt;&lt;script&gt;" in content
