from __future__ import annotations

import os
from pathlib import Path

import pytest

import intentatlas.scanner as scanner_module
from intentatlas.config import ProjectConfig
from intentatlas.scanner import scan_repository
from intentatlas.vault import ProjectVault

TYPESCRIPT_FIXTURE = Path(__file__).parent / "fixtures" / "typescript_project"
GO_FIXTURE = Path(__file__).parent / "fixtures" / "go_project"


def build_python_project(tmp_path) -> None:
    (tmp_path / "src" / "demo").mkdir(parents=True)
    (tmp_path / "tests").mkdir()
    (tmp_path / "src" / "demo" / "__init__.py").write_text(
        "from .core import Greeter\n", encoding="utf-8"
    )
    (tmp_path / "src" / "demo" / "core.py").write_text(
        "class Greeter:\n    def hello(self, name: str) -> str:\n        return f'Hello {name}'\n",
        encoding="utf-8",
    )
    (tmp_path / "src" / "demo" / "cli.py").write_text(
        "from .core import Greeter\n\ndef main():\n    return Greeter().hello('Atlas')\n",
        encoding="utf-8",
    )
    (tmp_path / "tests" / "test_core.py").write_text(
        "from demo.core import Greeter\n\ndef test_hello():\n    assert Greeter().hello('A')\n",
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "ignored.py").write_text("raise Exception\n", encoding="utf-8")
    (tmp_path / ".obsidian").mkdir()
    (tmp_path / ".obsidian" / "ignored.md").write_text("# Wrong vault\n", encoding="utf-8")


def test_scanner_connects_python_symbols_imports_and_tests(tmp_path) -> None:
    build_python_project(tmp_path)
    graph = scan_repository(tmp_path, ProjectConfig(git_history_limit=0))
    assert "file:src/demo/core.py" in graph.nodes
    assert "symbol:src/demo/core.py::Greeter" in graph.nodes
    assert "symbol:src/demo/core.py::Greeter.hello" in graph.nodes
    assert "file:.venv/ignored.py" not in graph.nodes
    assert "file:.obsidian/ignored.md" not in graph.nodes

    relationships = {(edge.source, edge.target, edge.relation) for edge in graph.edges}
    assert (
        "file:src/demo/cli.py",
        "file:src/demo/core.py",
        "imports",
    ) in relationships
    assert (
        "file:tests/test_core.py",
        "file:src/demo/core.py",
        "tests",
    ) in relationships


def test_scanner_connects_typescript_javascript_symbols_imports_and_tests() -> None:
    first = scan_repository(TYPESCRIPT_FIXTURE, ProjectConfig(git_history_limit=0))
    second = scan_repository(TYPESCRIPT_FIXTURE, ProjectConfig(git_history_limit=0))

    assert first.to_dict()["nodes"] == second.to_dict()["nodes"]
    assert first.to_dict()["edges"] == second.to_dict()["edges"]
    for node_id in (
        "symbol:src/math.ts::Calculator",
        "symbol:src/math.ts::Numeric",
        "symbol:src/math.ts::Operation",
        "symbol:src/math.ts::add",
        "symbol:src/components/index.ts::Card",
        "symbol:src/main.ts::boot",
        "symbol:src/card.tsx::CardView",
        "symbol:src/view.jsx::View",
        "symbol:src/comments.ts::VisibleShape",
        "symbol:src/multiline.ts::createCard",
        "symbol:src/dynamic.ts::loadMath",
    ):
        assert node_id in first.nodes
    assert "symbol:src/comments.ts::Phantom" not in first.nodes
    assert "symbol:src/comments.ts::TemplatePhantom" not in first.nodes
    assert "symbol:src/comments.ts::StringPhantom" not in first.nodes
    assert first.nodes["file:src/main.test.ts"].kind == "test"
    assert first.nodes["file:src/main.test.ts"].metadata["language"] == "TypeScript"
    assert first.nodes["file:src/view.jsx"].metadata["language"] == "JavaScript"

    relationships = {
        (edge.source, edge.target, edge.relation, edge.evidence) for edge in first.edges
    }
    assert (
        "file:src/main.ts",
        "file:src/math.ts",
        "imports",
        "javascript-structural",
    ) in relationships
    assert (
        "file:src/main.ts",
        "file:src/components/index.ts",
        "imports",
        "javascript-structural",
    ) in relationships
    assert (
        "file:src/legacy.js",
        "file:src/math.ts",
        "imports",
        "javascript-structural",
    ) in relationships
    assert (
        "file:src/multiline.ts",
        "file:src/components/index.ts",
        "imports",
        "javascript-structural",
    ) in relationships
    assert (
        "file:src/main.test.ts",
        "file:src/main.ts",
        "tests",
        "javascript-structural",
    ) in relationships
    assert (
        "file:src/math.test.ts",
        "file:src/math.ts",
        "tests",
        "filename-convention",
    ) in relationships
    assert not any(
        edge.source == "file:src/main.ts" and edge.target == "file:src/react.ts"
        for edge in first.edges
    )
    assert not any(
        edge.source == "file:src/escape.ts" and edge.target == "file:outside.ts"
        for edge in first.edges
    )
    assert not any(
        edge.source == "file:src/ambiguous.ts"
        and edge.target in {"file:src/dual.ts", "file:src/dual.js"}
        for edge in first.edges
    )
    assert not any(
        edge.source == "file:src/dynamic.ts" and edge.relation in {"imports", "tests"}
        for edge in first.edges
    )


def test_scanner_connects_go_symbols_local_imports_and_tests() -> None:
    first = scan_repository(GO_FIXTURE, ProjectConfig(git_history_limit=0))
    second = scan_repository(GO_FIXTURE, ProjectConfig(git_history_limit=0))

    assert first.to_dict()["nodes"] == second.to_dict()["nodes"]
    assert first.to_dict()["edges"] == second.to_dict()["edges"]
    for node_id in (
        "symbol:internal/math/add.go::Calculator",
        "symbol:internal/math/add.go::Calculator.Sum",
        "symbol:internal/math/add.go::Number",
        "symbol:internal/math/add.go::Operation",
        "symbol:internal/math/add.go::Add",
        "symbol:cmd/app/main.go::main",
        "symbol:internal/math/add_test.go::TestAdd",
    ):
        assert node_id in first.nodes
    assert "symbol:internal/math/comments.go::Phantom" not in first.nodes
    assert "symbol:internal/math/comments.go::RawPhantom" not in first.nodes
    assert first.nodes["file:go.mod"].kind == "config"
    assert first.nodes["file:go.mod"].metadata["language"] == "Go Modules"
    assert first.nodes["file:internal/math/add_test.go"].kind == "test"
    assert first.nodes["file:internal/math/add.go"].metadata["language"] == "Go"

    relationships = {
        (edge.source, edge.target, edge.relation, edge.evidence) for edge in first.edges
    }
    assert (
        "file:cmd/app/main.go",
        "file:internal/math/add.go",
        "imports",
        "go-structural",
    ) in relationships
    assert (
        "file:cmd/app/main.go",
        "file:internal/math/comments.go",
        "imports",
        "go-structural",
    ) in relationships
    assert (
        "file:internal/math/integration_test.go",
        "file:internal/math/add.go",
        "tests",
        "go-structural",
    ) in relationships
    assert (
        "file:internal/math/add_test.go",
        "file:internal/math/add.go",
        "tests",
        "filename-convention",
    ) in relationships
    assert not any(
        edge.source == "file:cmd/app/external_fixture.go"
        and edge.target == "file:third_party/external.go"
        for edge in first.edges
    )
    assert (
        "file:cmd/app/main.go",
        "file:submodule/worker/worker.go",
        "imports",
        "go-structural",
    ) in relationships
    assert not any(
        edge.source == "file:internal/math/comments.go"
        and edge.target == "file:submodule/worker/worker.go"
        for edge in first.edges
    )


def test_scanner_reads_user_vault_links_without_enumerating_private(
    tmp_path, monkeypatch
) -> None:
    build_python_project(tmp_path)
    config = ProjectConfig(git_history_limit=0)
    vault = ProjectVault(config.vault_path(tmp_path))
    vault.initialize()
    private = config.vault_path(tmp_path) / "Private" / "secret.md"
    private.write_text("password=hunter2", encoding="utf-8")

    original_scandir = os.scandir
    private_root = private.parent.resolve()

    def guarded_scandir(path):
        candidate = Path(path).resolve()
        if candidate == private_root or private_root in candidate.parents:
            raise AssertionError("scanner enumerated atlas/Private")
        return original_scandir(path)

    monkeypatch.setattr(scanner_module.os, "scandir", guarded_scandir)

    graph = scan_repository(tmp_path, config)
    assert "REQ-001" in graph.nodes
    assert "ADR-001" in graph.nodes
    assert all("secret" not in node.id.casefold() for node in graph.nodes.values())
    assert any(
        edge.source == "REQ-001" and edge.target == "ADR-001" and edge.relation == "references"
        for edge in graph.edges
    )


def test_scanner_prunes_configured_nested_excludes_before_descent(tmp_path, monkeypatch) -> None:
    (tmp_path / "vendor" / "generated").mkdir(parents=True)
    (tmp_path / "vendor" / "keep.py").write_text("value = 1\n", encoding="utf-8")
    (tmp_path / "vendor" / "generated" / "secret.py").write_text(
        "password = 'do-not-read'\n", encoding="utf-8"
    )
    blocked = (tmp_path / "vendor" / "generated").resolve()
    original_scandir = os.scandir

    def guarded_scandir(path):
        candidate = Path(path).resolve()
        if candidate == blocked or blocked in candidate.parents:
            raise AssertionError("scanner descended into configured exclude")
        return original_scandir(path)

    monkeypatch.setattr(scanner_module.os, "scandir", guarded_scandir)
    config = ProjectConfig(exclude=["vendor/generated"], git_history_limit=0)
    graph = scan_repository(tmp_path, config)

    assert "file:vendor/keep.py" in graph.nodes
    assert "file:vendor/generated/secret.py" not in graph.nodes


def test_scanner_rejects_reserved_user_note_ids(tmp_path) -> None:
    config = ProjectConfig(git_history_limit=0)
    vault = ProjectVault(config.vault_path(tmp_path))
    vault.initialize()
    (config.vault_path(tmp_path) / "Requirements" / "Collision.md").write_text(
        "---\nid: file:README.md\ntype: requirement\n---\n# Collision\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Reserved graph node ID"):
        scan_repository(tmp_path, config)


def test_scanner_only_reads_ids_from_frontmatter(tmp_path) -> None:
    config = ProjectConfig(git_history_limit=0)
    vault = ProjectVault(config.vault_path(tmp_path))
    vault.initialize()
    note = config.vault_path(tmp_path) / "Requirements" / "Body ID.md"
    note.write_text("# Body ID\n\nid: file:README.md\n", encoding="utf-8")
    malformed = config.vault_path(tmp_path) / "Requirements" / "Malformed frontmatter.md"
    malformed.write_text("---\n# Not closed\nid: file:README.md\n", encoding="utf-8")

    graph = scan_repository(tmp_path, config)

    assert "note:Requirements/Body ID" in graph.nodes
    assert "note:Requirements/Malformed frontmatter" in graph.nodes


def test_scanner_preserves_explicit_typed_intent_links(tmp_path) -> None:
    build_python_project(tmp_path)
    config = ProjectConfig(git_history_limit=0)
    vault = ProjectVault(config.vault_path(tmp_path))
    vault.initialize()
    (vault.root / "Requirements" / "REQ-Typed.md").write_text(
        "---\nid: REQ-TYPED\ntype: requirement\n---\n"
        "# Typed requirement\n\n- drives:: [[Decisions/ADR-Typed]]\n"
        "- unknown:: [[Evidence/EVD-Typed]]\n",
        encoding="utf-8",
    )
    (vault.root / "Decisions" / "ADR-Typed.md").write_text(
        "---\nid: ADR-TYPED\ntype: decision\n---\n"
        "# Typed decision\n\n- tracked-by:: [[Issues/ISSUE-Typed]]\n",
        encoding="utf-8",
    )
    (vault.root / "Issues" / "ISSUE-Typed.md").write_text(
        "---\nid: ISSUE-TYPED\ntype: issue\n---\n"
        "# Typed issue\n\n- implemented-by:: [[src - demo - core.py]]\n",
        encoding="utf-8",
    )
    (vault.root / "Evidence" / "EVD-Typed.md").write_text(
        "---\nid: EVD-TYPED\ntype: evidence\n---\n"
        "# Typed evidence\n\n- proves:: [[Requirements/REQ-Typed]]\n",
        encoding="utf-8",
    )

    graph = scan_repository(tmp_path, config)
    assert graph.nodes["ISSUE-TYPED"].kind == "issue"
    relationships = {(edge.source, edge.target, edge.relation) for edge in graph.edges}
    assert ("REQ-TYPED", "ADR-TYPED", "drives") in relationships
    assert ("ADR-TYPED", "ISSUE-TYPED", "tracked-by") in relationships
    assert ("ISSUE-TYPED", "file:src/demo/core.py", "implemented-by") in relationships
    assert ("EVD-TYPED", "REQ-TYPED", "proves") in relationships
    assert ("REQ-TYPED", "EVD-TYPED", "references") in relationships
