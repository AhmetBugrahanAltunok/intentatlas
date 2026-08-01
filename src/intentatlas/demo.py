from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from .graph import AtlasGraph
from .models import Edge, Node
from .viewer import serve_graph

DEMO_COMMIT_SHA = "1111111111111111111111111111111111111111"


def build_demo_graph() -> AtlasGraph:
    """Build the original first-party intent-to-proof showcase graph."""
    graph = AtlasGraph()
    graph.extend(
        [
            Node(
                "REQ-DEMO-001",
                "requirement",
                "Keep customer sessions secure",
                "Requirements/REQ-DEMO-001 - Keep customer sessions secure.md",
                {"owner": "demo", "status": "accepted"},
            ),
            Node(
                "ADR-DEMO-001",
                "decision",
                "Rotate sessions after authentication",
                "Decisions/ADR-DEMO-001 - Rotate sessions after authentication.md",
                {"owner": "demo", "status": "accepted"},
            ),
            Node(
                "delivery-issue:demo:42",
                "delivery-issue",
                "Issue 42 — Rotate authenticated sessions",
                metadata={"owner": "demo", "state": "closed"},
            ),
            Node(
                "pull-request:demo:57",
                "pull-request",
                "PR 57 — Add session rotation",
                metadata={"owner": "demo", "state": "merged"},
            ),
            Node(
                "file:src/auth.py",
                "file",
                "src/auth.py",
                "src/auth.py",
                {"owner": "demo", "language": "python"},
            ),
            Node(
                "symbol:src/auth.py:rotate_session",
                "symbol",
                "rotate_session",
                "src/auth.py",
                {"owner": "demo", "qualified_name": "rotate_session", "symbol_kind": "function"},
            ),
            Node(
                "file:tests/test_auth.py",
                "test",
                "tests/test_auth.py",
                "tests/test_auth.py",
                {"owner": "demo", "language": "python"},
            ),
            Node(
                "EVD-DEMO-001",
                "evidence",
                "Session rotation verification",
                "Evidence/EVD-DEMO-001 - Session rotation verification.md",
                {"owner": "demo", "status": "verified"},
            ),
            Node(
                f"commit:{DEMO_COMMIT_SHA}",
                "commit",
                "feat: rotate authenticated sessions",
                metadata={"owner": "demo", "sha": DEMO_COMMIT_SHA},
            ),
        ],
        [
            Edge("REQ-DEMO-001", "ADR-DEMO-001", "drives", "demo-wikilink"),
            Edge("ADR-DEMO-001", "delivery-issue:demo:42", "tracked-by", "demo-delivery"),
            Edge(
                "ADR-DEMO-001",
                "symbol:src/auth.py:rotate_session",
                "implemented-by",
                "demo-review",
            ),
            Edge(
                "delivery-issue:demo:42",
                "pull-request:demo:57",
                "addressed-by",
                "demo-delivery",
            ),
            Edge(
                "delivery-issue:demo:42",
                "symbol:src/auth.py:rotate_session",
                "implemented-by",
                "demo-review",
            ),
            Edge("pull-request:demo:57", "file:src/auth.py", "changes", "demo-delivery"),
            Edge("file:src/auth.py", "symbol:src/auth.py:rotate_session", "defines", "demo-ast"),
            Edge(
                "file:tests/test_auth.py",
                "symbol:src/auth.py:rotate_session",
                "tests",
                "demo-ast",
            ),
            Edge("file:tests/test_auth.py", "file:src/auth.py", "tests", "demo-ast"),
            Edge("EVD-DEMO-001", "file:tests/test_auth.py", "proves", "demo-review"),
            Edge(
                "EVD-DEMO-001",
                f"commit:{DEMO_COMMIT_SHA}",
                "recorded-in",
                "demo-review",
            ),
            Edge(
                f"commit:{DEMO_COMMIT_SHA}",
                "file:src/auth.py",
                "changes",
                "demo-git",
            ),
            Edge(
                f"commit:{DEMO_COMMIT_SHA}",
                "symbol:src/auth.py:rotate_session",
                "modifies",
                "demo-diff-hunk",
            ),
        ],
    )
    return graph


def serve_demo(*, host: str = "127.0.0.1", port: int = 4317, open_browser: bool = True) -> None:
    """Serve the showcase from automatically cleaned temporary storage."""
    with TemporaryDirectory(prefix="intentatlas-demo-") as temporary:
        graph_path = Path(temporary) / "graph.json"
        build_demo_graph().save(graph_path)
        print("Opening the built-in IntentAtlas intent-to-proof demo.")
        serve_graph(graph_path, host=host, port=port, open_browser=open_browser)
