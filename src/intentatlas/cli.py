from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .config import ProjectConfig
from .corpus import (
    MAX_CORPUS_GRAPH_BYTES_TOTAL,
    CorpusProject,
    evaluate_corpus,
    load_corpus_manifest,
    render_corpus,
    validate_corpus_graph_size,
)
from .demo import serve_demo
from .evaluation import evaluate_recommendations, load_evaluation_labels, render_evaluation
from .graph import AtlasGraph
from .graph_diff import graph_diff, render_graph_diff
from .recommendations import recommend_tests, render_recommendations
from .scale import render_scale_benchmark, run_scale_benchmark
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

    recommend_parser = commands.add_parser(
        "recommend-tests",
        help="Rank tests for a commit, file, or symbol with explainable confidence",
    )
    recommend_parser.add_argument("target", help="Commit, file, or symbol target")
    _path_argument(recommend_parser)
    recommend_parser.add_argument(
        "--minimum-confidence",
        choices=("low", "medium", "high"),
        default="medium",
    )
    recommend_parser.add_argument("--limit", type=int, default=20)
    recommend_parser.add_argument(
        "--format",
        dest="output_format",
        choices=("text", "json"),
        default="text",
    )

    evaluate_parser = commands.add_parser(
        "evaluate-recommendations",
        help="Compare test recommendations with an exhaustive local label set",
    )
    evaluate_parser.add_argument(
        "labels",
        help="Evaluation label JSON path below the project root",
    )
    _path_argument(evaluate_parser)
    evaluate_parser.add_argument(
        "--minimum-confidence",
        choices=("low", "medium", "high"),
        default="medium",
    )
    evaluate_parser.add_argument("--limit", type=int, default=20)
    evaluate_parser.add_argument(
        "--format",
        dest="output_format",
        choices=("text", "json"),
        default="text",
    )

    corpus_parser = commands.add_parser(
        "evaluate-corpus",
        help="Compare recommendation confidence across labeled local graphs",
    )
    corpus_parser.add_argument(
        "corpus",
        help="Corpus manifest JSON path below the project root",
    )
    _path_argument(corpus_parser)
    corpus_parser.add_argument("--limit", type=int, default=20)
    corpus_parser.add_argument(
        "--format",
        dest="output_format",
        choices=("text", "json"),
        default="text",
    )

    scale_parser = commands.add_parser(
        "benchmark-scale",
        help="Measure indexed queries on a bounded synthetic graph",
    )
    scale_parser.add_argument("--unrelated-edges", type=int, default=25_000)
    scale_parser.add_argument("--iterations", type=int, default=200)
    scale_parser.add_argument(
        "--format",
        dest="output_format",
        choices=("text", "json"),
        default="text",
    )

    demo_parser = commands.add_parser(
        "demo",
        help="Launch the built-in intent-to-proof showcase",
    )
    _viewer_arguments(demo_parser)

    diff_parser = commands.add_parser("diff", help="Compare the current graph with a baseline")
    diff_parser.add_argument("base", help="Baseline graph path below the project root")
    _path_argument(diff_parser)
    diff_parser.add_argument("--output", help="Write deterministic JSON below the project root")
    diff_parser.add_argument(
        "--check",
        action="store_true",
        help="Return exit status 1 when graph changes exist",
    )

    open_parser = commands.add_parser("open", help="Launch the local interactive graph")
    _path_argument(open_parser)
    _viewer_arguments(open_parser)
    return parser


def _path_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "path", nargs="?", default=".", help="Project root (default: current directory)"
    )


def _viewer_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4317)
    parser.add_argument("--no-browser", action="store_true")


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        root = Path(getattr(args, "path", ".")).resolve()
        if args.command == "init":
            return _init(root)
        if args.command == "scan":
            return _scan(root)
        if args.command == "status":
            return _status(root)
        if args.command == "impact":
            return _impact(root, args.target, args.depth, args.direction)
        if args.command == "recommend-tests":
            return _recommend_tests(
                root,
                args.target,
                args.minimum_confidence,
                args.limit,
                args.output_format,
            )
        if args.command == "evaluate-recommendations":
            return _evaluate_recommendations(
                root,
                args.labels,
                args.minimum_confidence,
                args.limit,
                args.output_format,
            )
        if args.command == "evaluate-corpus":
            return _evaluate_corpus(
                root,
                args.corpus,
                args.limit,
                args.output_format,
            )
        if args.command == "benchmark-scale":
            result = run_scale_benchmark(
                unrelated_edges=args.unrelated_edges,
                iterations=args.iterations,
            )
            print(render_scale_benchmark(result, args.output_format), end="")
            return 0
        if args.command == "demo":
            serve_demo(host=args.host, port=args.port, open_browser=not args.no_browser)
            return 0
        if args.command == "diff":
            return _diff(root, args.base, args.output, args.check)
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


def _recommend_tests(
    root: Path,
    target: str,
    minimum_confidence: str,
    limit: int,
    output_format: str,
) -> int:
    config = ProjectConfig.load(root)
    graph = AtlasGraph.load(config.graph_path(root))
    origin = graph.find(target)
    result = recommend_tests(
        graph,
        origin.id,
        minimum_confidence=minimum_confidence,
        limit=limit,
    )
    print(render_recommendations(result, output_format), end="")
    return 0


def _evaluate_recommendations(
    root: Path,
    labels: str,
    minimum_confidence: str,
    limit: int,
    output_format: str,
) -> int:
    config = ProjectConfig.load(root)
    graph = AtlasGraph.load(config.graph_path(root))
    labels_path = _project_path(
        root,
        config,
        labels,
        "evaluation labels",
        must_exist=True,
    )
    parsed = load_evaluation_labels(labels_path)
    result = evaluate_recommendations(
        graph,
        parsed,
        minimum_confidence=minimum_confidence,
        limit=limit,
    )
    print(render_evaluation(result, output_format), end="")
    return 0


def _evaluate_corpus(
    root: Path,
    corpus: str,
    limit: int,
    output_format: str,
) -> int:
    config = ProjectConfig.load(root)
    corpus_path = _project_path(
        root,
        config,
        corpus,
        "corpus manifest",
        must_exist=True,
    )
    manifest = load_corpus_manifest(corpus_path)
    projects: list[CorpusProject] = []
    graph_bytes = 0
    for entry in manifest.projects:
        graph_path = _project_path(
            root,
            config,
            entry.graph,
            f"corpus graph for {entry.id}",
            must_exist=True,
        )
        labels_path = _project_path(
            root,
            config,
            entry.labels,
            f"corpus labels for {entry.id}",
            must_exist=True,
        )
        graph_bytes += validate_corpus_graph_size(graph_path)
        if graph_bytes > MAX_CORPUS_GRAPH_BYTES_TOTAL:
            raise ValueError(
                "Corpus graphs exceed the "
                f"{MAX_CORPUS_GRAPH_BYTES_TOTAL}-byte aggregate limit"
            )
        projects.append(
            CorpusProject(
                entry.id,
                entry.name,
                AtlasGraph.load(graph_path),
                load_evaluation_labels(labels_path),
            )
        )
    result = evaluate_corpus(manifest.name, tuple(projects), limit=limit)
    print(render_corpus(result, output_format), end="")
    return 0


def _open(root: Path, host: str, port: int, open_browser: bool) -> int:
    config = ProjectConfig.load(root)
    graph_path = config.graph_path(root)
    if not graph_path.exists():
        _scan(root)
    serve_graph(graph_path, host=host, port=port, open_browser=open_browser)
    return 0


def _diff(root: Path, base: str, output: str | None, check: bool) -> int:
    config = ProjectConfig.load(root)
    current_path = config.graph_path(root)
    base_path = _project_path(root, config, base, "baseline graph", must_exist=True)
    current = AtlasGraph.load(current_path)
    baseline = AtlasGraph.load(base_path)
    value = graph_diff(baseline, current)
    rendered = render_graph_diff(value)
    if output is None:
        print(rendered, end="")
    else:
        output_path = _project_path(root, config, output, "graph diff output", must_exist=False)
        if output_path in {base_path, current_path}:
            raise ValueError("Graph diff output may not overwrite an input graph")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"Graph diff: {output_path.relative_to(root)}")
    return 1 if check and value["has_changes"] else 0


def _project_path(
    root: Path,
    config: ProjectConfig,
    configured: str,
    label: str,
    *,
    must_exist: bool,
) -> Path:
    candidate = Path(configured)
    unresolved = candidate if candidate.is_absolute() else root / candidate
    if unresolved.is_symlink():
        raise ValueError(f"Configured {label} may not be a symbolic link: {configured}")
    target = unresolved.resolve()
    if target == root or root not in target.parents:
        raise ValueError(f"Configured {label} must be below the project root: {configured}")
    private = (config.vault_path(root) / "Private").resolve()
    if target == private or private in target.parents:
        raise ValueError(f"Configured {label} may not be inside atlas/Private: {configured}")
    if must_exist and not target.is_file():
        raise ValueError(f"Configured {label} does not exist: {configured}")
    return target
