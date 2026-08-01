from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from .graph import AtlasGraph
from .models import Edge, Node
from .recommendations import RecommendationResult, recommend_tests
from .viewer import serve_graph

DEMO_COMMIT_SHA = "1111111111111111111111111111111111111111"
DEMO_REPORT_SCHEMA_VERSION = 1
DEMO_SOURCE_FILE_ID = "file:src/auth.py"
DEMO_CHANGED_SYMBOL_ID = "symbol:src/auth.py:rotate_session"
DEMO_UNRELATED_SYMBOL_ID = "symbol:src/auth.py:record_login_audit"
DEMO_ADVISORY = (
    "This original synthetic scenario demonstrates available structural evidence. A requirement "
    "or test omitted from the exact-symbol result is not proven unaffected or unnecessary."
)


@dataclass(frozen=True, slots=True)
class DemoReport:
    target: Node
    changed_symbol: Node
    same_file_requirements: tuple[Node, ...]
    exact_symbol_requirements: tuple[Node, ...]
    recommendations: RecommendationResult
    same_file_tests_not_recommended: tuple[Node, ...]

    def to_dict(self) -> dict[str, Any]:
        exact_ids = {node.id for node in self.exact_symbol_requirements}
        return {
            "schema_version": DEMO_REPORT_SCHEMA_VERSION,
            "scenario": "same-file-exact-symbol",
            "advisory": DEMO_ADVISORY,
            "target": self.target.to_dict(),
            "changed_symbol": self.changed_symbol.to_dict(),
            "same_file_requirements": [node.to_dict() for node in self.same_file_requirements],
            "requirements_with_exact_changed_symbol_evidence": [
                node.to_dict() for node in self.exact_symbol_requirements
            ],
            "same_file_requirements_without_exact_changed_symbol_evidence": [
                node.to_dict() for node in self.same_file_requirements if node.id not in exact_ids
            ],
            "test_recommendations": self.recommendations.to_dict(),
            "same_file_tests_not_recommended": [
                node.to_dict() for node in self.same_file_tests_not_recommended
            ],
        }


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
                "REQ-DEMO-002",
                "requirement",
                "Preserve login audit events",
                "Requirements/REQ-DEMO-002 - Preserve login audit events.md",
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
                DEMO_SOURCE_FILE_ID,
                "file",
                "src/auth.py",
                "src/auth.py",
                {"owner": "demo", "language": "python"},
            ),
            Node(
                DEMO_CHANGED_SYMBOL_ID,
                "symbol",
                "rotate_session",
                "src/auth.py",
                {"owner": "demo", "qualified_name": "rotate_session", "symbol_kind": "function"},
            ),
            Node(
                DEMO_UNRELATED_SYMBOL_ID,
                "symbol",
                "record_login_audit",
                "src/auth.py",
                {
                    "owner": "demo",
                    "qualified_name": "record_login_audit",
                    "symbol_kind": "function",
                },
            ),
            Node(
                "file:tests/test_auth_rotation.py",
                "test",
                "tests/test_auth_rotation.py",
                "tests/test_auth_rotation.py",
                {"owner": "demo", "language": "python"},
            ),
            Node(
                "file:tests/test_auth_audit.py",
                "test",
                "tests/test_auth_audit.py",
                "tests/test_auth_audit.py",
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
            Edge("REQ-DEMO-001", DEMO_CHANGED_SYMBOL_ID, "implemented-by", "demo-review"),
            Edge("REQ-DEMO-002", DEMO_UNRELATED_SYMBOL_ID, "implemented-by", "demo-review"),
            Edge("ADR-DEMO-001", "delivery-issue:demo:42", "tracked-by", "demo-delivery"),
            Edge(
                "ADR-DEMO-001",
                DEMO_CHANGED_SYMBOL_ID,
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
                DEMO_CHANGED_SYMBOL_ID,
                "implemented-by",
                "demo-review",
            ),
            Edge("pull-request:demo:57", DEMO_SOURCE_FILE_ID, "changes", "demo-delivery"),
            Edge(DEMO_SOURCE_FILE_ID, DEMO_CHANGED_SYMBOL_ID, "defines", "demo-ast"),
            Edge(DEMO_SOURCE_FILE_ID, DEMO_UNRELATED_SYMBOL_ID, "defines", "demo-ast"),
            Edge(
                "file:tests/test_auth_rotation.py",
                DEMO_CHANGED_SYMBOL_ID,
                "tests",
                "demo-ast",
            ),
            Edge(
                "file:tests/test_auth_audit.py",
                DEMO_UNRELATED_SYMBOL_ID,
                "tests",
                "demo-ast",
            ),
            Edge("EVD-DEMO-001", "file:tests/test_auth_rotation.py", "proves", "demo-review"),
            Edge(
                "EVD-DEMO-001",
                f"commit:{DEMO_COMMIT_SHA}",
                "recorded-in",
                "demo-review",
            ),
            Edge(
                f"commit:{DEMO_COMMIT_SHA}",
                DEMO_SOURCE_FILE_ID,
                "changes",
                "demo-git",
            ),
            Edge(
                f"commit:{DEMO_COMMIT_SHA}",
                DEMO_CHANGED_SYMBOL_ID,
                "modifies",
                "demo-diff-hunk",
            ),
        ],
    )
    return graph


def build_demo_report() -> DemoReport:
    """Derive the same-file demo result through production graph and recommendation contracts."""
    graph = build_demo_graph()
    index = graph.index
    source_symbols = {
        edge.target
        for edge in index.outgoing(DEMO_SOURCE_FILE_ID)
        if edge.relation == "defines" and graph.nodes[edge.target].kind == "symbol"
    }
    same_file_requirements = _incoming_nodes(
        graph,
        source_symbols,
        relation="implemented-by",
        kind="requirement",
    )
    exact_symbol_requirements = _incoming_nodes(
        graph,
        {DEMO_CHANGED_SYMBOL_ID},
        relation="implemented-by",
        kind="requirement",
    )
    same_file_tests = _incoming_nodes(
        graph,
        source_symbols,
        relation="tests",
        kind="test",
    )
    recommendations = recommend_tests(graph, f"commit:{DEMO_COMMIT_SHA}")
    recommended_ids = {item.test.id for item in recommendations.recommendations}
    return DemoReport(
        target=graph.nodes[f"commit:{DEMO_COMMIT_SHA}"],
        changed_symbol=graph.nodes[DEMO_CHANGED_SYMBOL_ID],
        same_file_requirements=same_file_requirements,
        exact_symbol_requirements=exact_symbol_requirements,
        recommendations=recommendations,
        same_file_tests_not_recommended=tuple(
            node for node in same_file_tests if node.id not in recommended_ids
        ),
    )


def _incoming_nodes(
    graph: AtlasGraph,
    targets: set[str],
    *,
    relation: str,
    kind: str,
) -> tuple[Node, ...]:
    nodes = {
        edge.source: graph.nodes[edge.source]
        for target in sorted(targets)
        for edge in graph.index.incoming(target)
        if edge.relation == relation and graph.nodes[edge.source].kind == kind
    }
    return tuple(nodes[node_id] for node_id in sorted(nodes))


def render_demo_report(report: DemoReport, output_format: str = "text") -> str:
    """Render the bounded same-file demo result without starting a listener."""
    if output_format == "json":
        return json.dumps(report.to_dict(), indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if output_format != "text":
        raise ValueError(f"Unknown demo report format: {output_format}")

    exact_ids = {node.id for node in report.exact_symbol_requirements}
    lines = [
        f"IntentAtlas same-file evidence demo (schema {DEMO_REPORT_SCHEMA_VERSION})",
        f"Target commit: {report.target.label}",
        f"Exact changed symbol: {report.changed_symbol.label} ({report.changed_symbol.path})",
        "Requirements with exact changed-symbol evidence:",
    ]
    lines.extend(f"- {node.label}" for node in report.exact_symbol_requirements)
    lines.append("Same-file requirements without exact changed-symbol evidence:")
    lines.extend(
        f"- {node.label}" for node in report.same_file_requirements if node.id not in exact_ids
    )
    lines.append("Recommended tests:")
    lines.extend(
        f"- {item.test.path or item.test.label} [{item.confidence} {item.score}]"
        for item in report.recommendations.recommendations
    )
    lines.append("Same-file tests not recommended from available exact-symbol evidence:")
    lines.extend(
        f"- {node.path or node.label}" for node in report.same_file_tests_not_recommended
    )
    lines.append(f"Boundary: {DEMO_ADVISORY}")
    return "\n".join(lines) + "\n"


def serve_demo(*, host: str = "127.0.0.1", port: int = 4317, open_browser: bool = True) -> None:
    """Serve the showcase from automatically cleaned temporary storage."""
    with TemporaryDirectory(prefix="intentatlas-demo-") as temporary:
        graph_path = Path(temporary) / "graph.json"
        build_demo_graph().save(graph_path)
        print("Opening the built-in IntentAtlas intent-to-proof demo.")
        serve_graph(graph_path, host=host, port=port, open_browser=open_browser)
