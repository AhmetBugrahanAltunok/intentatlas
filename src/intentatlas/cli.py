from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .config import ProjectConfig
from .graph import AtlasGraph
from .scanner import USER_VAULT_AREAS, scan_repository
from .vault import ProjectVault
from .viewer import serve_graph


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="intentatlas",
        description="Build a living map from project intent to implementation evidence.",
    )
    parser.add_argument("--version", action="version", version=f"IntentAtlas {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    init_parser = commands.add_parser("init", help="Create the project brain and config")
    _path_argument(init_parser)

    scan_parser = commands.add_parser("scan", help="Scan the repository and rebuild outputs")
    _path_argument(scan_parser)

    status_parser = commands.add_parser("status", help="Show graph and durable-note health")
    _path_argument(status_parser)

    impact_parser = commands.add_parser("impact", help="Trace relationships around a target")
    impact_parser.add_argument("target", help="Node ID, path, label, or unique partial match")
    _path_argument(impact_parser)
    impact_parser.add_argument("--depth", type=int, default=2, help="Traversal depth (default: 2)")
    impact_parser.add_argument(
        "--direction",
        choices=("both", "upstream", "downstream"),
        default="both",
    )

    open_parser = commands.add_parser("open", help="Launch the local interactive graph")
    _path_argument(open_parser)
    open_parser.add_argument("--host", default="127.0.0.1")
    open_parser.add_argument("--port", type=int, default=4317)
    open_parser.add_argument("--no-browser", action="store_true")
    return parser


def _path_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "path", nargs="?", default=".", help="Project root (default: current directory)"
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        root = Path(args.path).resolve()
        if args.command == "init":
            return _init(root)
        if args.command == "scan":
            return _scan(root)
        if args.command == "status":
            return _status(root)
        if args.command == "impact":
            return _impact(root, args.target, args.depth, args.direction)
        if args.command == "open":
            return _open(root, args.host, args.port, not args.no_browser)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 2


def _init(root: Path) -> int:
    root.mkdir(parents=True, exist_ok=True)
    config = ProjectConfig.load(root)
    config_path = config.save_if_missing(root)
    vault = ProjectVault(config.vault_path(root))
    vault.initialize()
    print(f"Initialized IntentAtlas in {root}")
    print(f"Config: {config_path.relative_to(root)}")
    print(f"Obsidian vault: {config.vault_path(root).relative_to(root)}")
    print("Next: intentatlas scan")
    return 0


def _scan(root: Path) -> int:
    if not root.is_dir():
        raise ValueError(f"Project path is not a directory: {root}")
    config = ProjectConfig.load(root)
    config.save_if_missing(root)
    vault = ProjectVault(config.vault_path(root))
    vault.initialize()
    graph = scan_repository(root, config)
    graph_path = config.graph_path(root)
    graph.save(graph_path)
    result = vault.sync(graph)
    print(f"Scanned {root.name}: {len(graph.nodes)} nodes, {len(graph.edges)} relationships")
    print(f"Graph: {graph_path.relative_to(root)}")
    print(f"Obsidian vault: {config.vault_path(root).relative_to(root)}")
    print(f"Generated notes: {result['generated_notes']}")
    return 0


def _status(root: Path) -> int:
    config = ProjectConfig.load(root)
    graph = AtlasGraph.load(config.graph_path(root))
    print(f"IntentAtlas status — {root.name}")
    for kind, count in graph.summary().items():
        print(f"  {kind:12} {count}")
    print(f"  {'relationships':12} {len(graph.edges)}")
    durable = set(USER_VAULT_AREAS.values())
    orphans = graph.orphans(durable)
    print(f"  {'durable orphans':12} {len(orphans)}")
    for node in orphans[:10]:
        print(f"    - {node.id}: {node.label}")
    return 1 if orphans else 0


def _impact(root: Path, target: str, depth: int, direction: str) -> int:
    if depth < 1 or depth > 10:
        raise ValueError("Depth must be between 1 and 10")
    config = ProjectConfig.load(root)
    graph = AtlasGraph.load(config.graph_path(root))
    origin = graph.find(target)
    records = graph.impact(origin.id, depth=depth, direction=direction)
    print(f"{origin.label} [{origin.kind}] — {origin.id}")
    if not records:
        print("  No relationships in the selected direction.")
        return 0
    for record in records:
        marker = "->" if record.direction == "downstream" else "<-"
        relation = (
            record.edge.relation if record.direction == "downstream" else record.edge.inverse
        )
        print(
            f"{'  ' * record.depth}{marker} [{relation} · {record.edge.category}] "
            f"{record.node.label} ({record.node.kind}) via {record.edge.evidence}"
        )
    return 0


def _open(root: Path, host: str, port: int, open_browser: bool) -> int:
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("The prototype viewer may only bind to a loopback address")
    if port < 0 or port > 65535:
        raise ValueError("Port must be between 0 and 65535")
    config = ProjectConfig.load(root)
    graph_path = config.graph_path(root)
    if not graph_path.exists():
        _scan(root)
    serve_graph(graph_path, host=host, port=port, open_browser=open_browser)
    return 0
