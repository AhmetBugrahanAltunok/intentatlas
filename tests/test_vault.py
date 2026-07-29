from __future__ import annotations

from intentatlas.graph import AtlasGraph
from intentatlas.models import Edge, Node
from intentatlas.vault import GENERATED_MARKER, ProjectVault


def graph_fixture() -> AtlasGraph:
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
            Node("file:src/app.py", "file", "src/app.py", "src/app.py", {"language": "Python"}),
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
