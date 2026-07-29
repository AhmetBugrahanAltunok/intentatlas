from __future__ import annotations

from intentatlas.config import ProjectConfig
from intentatlas.scanner import scan_repository
from intentatlas.vault import ProjectVault


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


def test_scanner_connects_python_symbols_imports_and_tests(tmp_path) -> None:
    build_python_project(tmp_path)
    graph = scan_repository(tmp_path, ProjectConfig(git_history_limit=0))
    assert "file:src/demo/core.py" in graph.nodes
    assert "symbol:src/demo/core.py::Greeter" in graph.nodes
    assert "symbol:src/demo/core.py::Greeter.hello" in graph.nodes
    assert "file:.venv/ignored.py" not in graph.nodes

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


def test_scanner_reads_user_vault_links_but_skips_private(tmp_path) -> None:
    build_python_project(tmp_path)
    config = ProjectConfig(git_history_limit=0)
    vault = ProjectVault(config.vault_path(tmp_path))
    vault.initialize()
    private = config.vault_path(tmp_path) / "Private" / "secret.md"
    private.write_text("password=hunter2", encoding="utf-8")

    graph = scan_repository(tmp_path, config)
    assert "REQ-001" in graph.nodes
    assert "ADR-001" in graph.nodes
    assert all("secret" not in node.id.casefold() for node in graph.nodes.values())
    assert any(
        edge.source == "REQ-001" and edge.target == "ADR-001" and edge.relation == "references"
        for edge in graph.edges
    )
