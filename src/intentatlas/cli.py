from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .change_analysis import analyze_change_set, render_change_analysis
from .change_report import (
    collect_change_report,
    collect_change_report_context,
    render_change_report,
)
from .change_set import collect_change_set, render_change_set
from .config import ProjectConfig
from .corpus import (
    MAX_CORPUS_GRAPH_BYTES_TOTAL,
    CorpusProject,
    evaluate_corpus,
    load_corpus_manifest,
    render_corpus,
    validate_corpus_graph_size,
)
from .demo import build_demo_report, render_demo_report, serve_demo
from .diagnostic import diagnose_repository, render_diagnostic
from .evaluation import evaluate_recommendations, load_evaluation_labels, render_evaluation
from .graph import AtlasGraph
from .graph_diff import graph_diff, render_graph_diff
from .longitudinal import (
    evaluate_longitudinal,
    load_pilot_manifest,
    render_longitudinal,
)
from .onboarding import run_guide
from .real_world import (
    evaluate_real_world,
    load_real_world_manifest,
    render_real_world,
)
from .recommendations import recommend_tests, render_recommendations
from .review import build_review_report, render_review
from .scale import render_scale_benchmark, run_scale_benchmark
from .scanner import USER_VAULT_AREAS, scan_repository_incremental
from .test_outcomes import load_test_outcomes
from .vault import ProjectVault
from .viewer import serve_graph


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="intentatlas",
        description="Build a living map from project intent to implementation evidence.",
    )
    parser.add_argument("--version", action="version", version=f"IntentAtlas {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    guide_parser = commands.add_parser(
        "guide",
        help="Interactively analyze one safe Git scope without writing project state",
    )
    guide_parser.add_argument("path", nargs="?", help="Repository or nested directory")
    guide_parser.add_argument("--language", choices=("en", "tr"))

    init_parser = commands.add_parser("init", help="Create the project brain and config")
    _path_argument(init_parser)

    diagnose_parser = commands.add_parser(
        "diagnose",
        help="Inspect repository readiness without writing project state",
    )
    _path_argument(diagnose_parser)
    diagnose_parser.add_argument(
        "--format",
        dest="output_format",
        choices=("text", "json"),
        default="text",
    )

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

    changes_parser = commands.add_parser(
        "changes",
        help="Inspect a bounded commit, range, staged, or worktree change set",
    )
    _path_argument(changes_parser)
    changes_parser.add_argument("--commit", help="Commit revision to inspect")
    changes_parser.add_argument("--base", help="Base revision for a revision range")
    changes_parser.add_argument("--head", help="Head revision for a revision range")
    changes_parser.add_argument("--staged", action="store_true", help="Inspect staged changes")
    changes_parser.add_argument(
        "--worktree",
        action="store_true",
        help="Inspect tracked worktree changes and untracked paths",
    )
    changes_parser.add_argument(
        "--format",
        dest="output_format",
        choices=("text", "json"),
        default="text",
    )
    changes_parser.add_argument(
        "--analyze",
        action="store_true",
        help="Scan the current worktree and report analysis state and freshness",
    )
    changes_parser.add_argument(
        "--report",
        action="store_true",
        help="Rank affected requirements and tests with explicit fallback policy",
    )
    changes_parser.add_argument(
        "--minimum-confidence",
        choices=("low", "medium", "high"),
        default="medium",
    )
    changes_parser.add_argument("--limit", type=int, default=20)
    changes_parser.add_argument(
        "--open",
        dest="open_report",
        action="store_true",
        help="Open the report in the local interactive viewer",
    )
    _viewer_arguments(changes_parser)

    review_parser = commands.add_parser(
        "review",
        help="Review a revision range in non-blocking CI shadow mode",
    )
    _path_argument(review_parser)
    review_parser.add_argument("--base", required=True, help="Base revision")
    review_parser.add_argument("--head", required=True, help="Head revision")
    review_parser.add_argument(
        "--minimum-confidence",
        choices=("low", "medium", "high"),
        default="medium",
    )
    review_parser.add_argument("--limit", type=int, default=20)
    review_parser.add_argument(
        "--test-outcomes",
        help="Commit-keyed test outcome JSON below the project root",
    )
    review_parser.add_argument(
        "--format",
        dest="output_format",
        choices=("markdown", "json", "sarif"),
        default="markdown",
    )
    review_parser.add_argument(
        "--open",
        dest="open_report",
        action="store_true",
        help="Open the review with its fresh graph in the local viewer",
    )
    _viewer_arguments(review_parser)

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

    real_world_parser = commands.add_parser(
        "evaluate-real-world",
        help="Evaluate pinned, license-reviewed checkouts without executing project code",
    )
    real_world_parser.add_argument(
        "manifest",
        help="Real-world manifest JSON path below the project root",
    )
    real_world_parser.add_argument(
        "checkouts",
        help="Directory of pinned checkouts below the project root",
    )
    _path_argument(real_world_parser)
    real_world_parser.add_argument("--limit", type=int, default=20)
    real_world_parser.add_argument(
        "--format",
        dest="output_format",
        choices=("text", "json"),
        default="text",
    )

    longitudinal_parser = commands.add_parser(
        "evaluate-longitudinal",
        help="Evaluate a frozen, partitioned longitudinal pilot offline",
    )
    longitudinal_parser.add_argument(
        "manifest",
        help="Longitudinal pilot manifest JSON path below the project root",
    )
    longitudinal_parser.add_argument(
        "checkouts",
        help="Directory of pinned pilot checkouts below the project root",
    )
    _path_argument(longitudinal_parser)
    longitudinal_parser.add_argument("--limit", type=int, default=20)
    longitudinal_parser.add_argument(
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
    demo_parser.add_argument(
        "--report",
        dest="report_format",
        choices=("text", "json"),
        help="Print the deterministic same-file evidence report and exit",
    )

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
    arguments = list(sys.argv[1:] if argv is None else argv)
    if not arguments and sys.stdin.isatty() and sys.stdout.isatty():
        try:
            return run_guide()
        except (OSError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
    args = build_parser().parse_args(arguments)
    try:
        if args.command == "guide":
            return run_guide(args.path, language=args.language)
        root = Path(getattr(args, "path", ".")).resolve()
        if args.command == "init":
            return _init(root)
        if args.command == "diagnose":
            print(render_diagnostic(diagnose_repository(root), args.output_format), end="")
            return 0
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
        if args.command == "changes":
            return _changes(
                root,
                args.commit,
                args.base,
                args.head,
                args.staged,
                args.worktree,
                args.analyze,
                args.report,
                args.open_report,
                args.minimum_confidence,
                args.limit,
                args.output_format,
                args.host,
                args.port,
                not args.no_browser,
            )
        if args.command == "review":
            return _review(
                root,
                args.base,
                args.head,
                args.minimum_confidence,
                args.limit,
                args.output_format,
                args.test_outcomes,
                args.open_report,
                args.host,
                args.port,
                not args.no_browser,
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
        if args.command == "evaluate-real-world":
            return _evaluate_real_world(
                root,
                args.manifest,
                args.checkouts,
                args.limit,
                args.output_format,
            )
        if args.command == "evaluate-longitudinal":
            return _evaluate_longitudinal(
                root,
                args.manifest,
                args.checkouts,
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
            if args.report_format:
                print(render_demo_report(build_demo_report(), args.report_format), end="")
                return 0
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
    scan_result = scan_repository_incremental(root, config)
    graph = scan_result.graph
    graph_path = config.graph_path(root)
    graph.save(graph_path)
    sync_result = vault.sync(graph)
    print(f"Scanned {root.name}: {len(graph.nodes)} nodes, {len(graph.edges)} relationships")
    print(
        "Adapter cache: "
        f"{len(scan_result.statistics.reused_adapters)} reused, "
        f"{len(scan_result.statistics.rebuilt_adapters)} rebuilt"
    )
    if scan_result.statistics.skipped_cache_writes:
        print(
            "Adapter cache writes skipped: "
            + ", ".join(scan_result.statistics.skipped_cache_writes)
        )
    print(f"Graph: {graph_path.relative_to(root)}")
    print(f"Obsidian vault: {config.vault_path(root).relative_to(root)}")
    print(f"Generated notes: {sync_result['generated_notes']}")
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


def _changes(
    root: Path,
    commit: str | None,
    base: str | None,
    head: str | None,
    staged: bool,
    worktree: bool,
    analyze: bool,
    report: bool,
    open_report: bool,
    minimum_confidence: str,
    limit: int,
    output_format: str,
    host: str,
    port: int,
    open_browser: bool,
) -> int:
    config = ProjectConfig.load(root)
    private_paths = _private_paths(root, config)
    range_selected = base is not None or head is not None
    selections = sum((commit is not None, range_selected, staged, worktree))
    if selections != 1:
        raise ValueError(
            "Select exactly one change scope: --commit, --base with --head, --staged, "
            "or --worktree"
        )
    if range_selected and (base is None or head is None):
        raise ValueError("Revision range requires both --base and --head")
    if analyze and report:
        raise ValueError("Select either --analyze or --report, not both")
    if open_report and not report:
        raise ValueError("--open requires --report")
    if commit is not None:
        result = collect_change_set(
            root, scope="commit", revision=commit, excluded_paths=private_paths
        )
    elif range_selected:
        result = collect_change_set(
            root,
            scope="range",
            base=base,
            head=head,
            excluded_paths=private_paths,
        )
    elif staged:
        result = collect_change_set(
            root, scope="staged", excluded_paths=private_paths
        )
    else:
        result = collect_change_set(
            root, scope="worktree", excluded_paths=private_paths
        )
    if report:
        if open_report:
            graph, change_report = collect_change_report_context(
                root,
                result,
                config,
                minimum_confidence=minimum_confidence,
                limit=limit,
            )
            graph_document = (
                json.dumps(graph.to_dict(), ensure_ascii=False, sort_keys=True) + "\n"
            ).encode("utf-8")
            report_document = render_change_report(change_report, "json").encode("utf-8")
            serve_graph(
                None,
                host=host,
                port=port,
                open_browser=open_browser,
                graph_document=graph_document,
                change_report_document=report_document,
            )
        else:
            change_report = collect_change_report(
                root,
                result,
                config,
                minimum_confidence=minimum_confidence,
                limit=limit,
            )
            print(render_change_report(change_report, output_format), end="")
    elif analyze:
        analyzed = analyze_change_set(root, result, config)
        print(render_change_analysis(analyzed, output_format), end="")
    else:
        print(render_change_set(result, output_format), end="")
    return 0


def _review(
    root: Path,
    base: str,
    head: str,
    minimum_confidence: str,
    limit: int,
    output_format: str,
    test_outcomes_path: str | None,
    open_report: bool,
    host: str,
    port: int,
    open_browser: bool,
) -> int:
    config = ProjectConfig.load(root)
    change_set = collect_change_set(
        root,
        scope="range",
        base=base,
        head=head,
        excluded_paths=_private_paths(root, config),
    )
    test_outcomes = None
    if test_outcomes_path is not None:
        outcome_path = _project_path(
            root,
            config,
            test_outcomes_path,
            "test outcomes",
            must_exist=True,
        )
        test_outcomes = load_test_outcomes(outcome_path)
    if open_report:
        graph, change_report = collect_change_report_context(
            root,
            change_set,
            config,
            minimum_confidence=minimum_confidence,
            limit=limit,
        )
        review = build_review_report(change_report, test_outcomes)
        graph_document = (
            json.dumps(graph.to_dict(), ensure_ascii=False, sort_keys=True) + "\n"
        ).encode("utf-8")
        review_document = render_review(review, "json").encode("utf-8")
        serve_graph(
            None,
            host=host,
            port=port,
            open_browser=open_browser,
            graph_document=graph_document,
            review_document=review_document,
        )
    else:
        change_report = collect_change_report(
            root,
            change_set,
            config,
            minimum_confidence=minimum_confidence,
            limit=limit,
        )
        review = build_review_report(change_report, test_outcomes)
        print(render_review(review, output_format), end="")
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


def _evaluate_real_world(
    root: Path,
    manifest: str,
    checkouts: str,
    limit: int,
    output_format: str,
) -> int:
    config = ProjectConfig.load(root)
    manifest_path = _project_path(
        root,
        config,
        manifest,
        "real-world manifest",
        must_exist=True,
    )
    checkouts_path = _project_directory(
        root,
        config,
        checkouts,
        "real-world checkout root",
    )
    parsed = load_real_world_manifest(manifest_path)
    result = evaluate_real_world(root, checkouts_path, parsed, limit=limit)
    print(render_real_world(result, output_format), end="")
    return 0


def _evaluate_longitudinal(
    root: Path,
    manifest: str,
    checkouts: str,
    limit: int,
    output_format: str,
) -> int:
    config = ProjectConfig.load(root)
    manifest_path = _project_path(
        root,
        config,
        manifest,
        "longitudinal pilot manifest",
        must_exist=True,
    )
    checkouts_path = _project_directory(
        root,
        config,
        checkouts,
        "longitudinal pilot checkout root",
    )
    parsed = load_pilot_manifest(manifest_path)
    result = evaluate_longitudinal(
        root,
        checkouts_path,
        manifest_path,
        parsed,
        limit=limit,
    )
    print(render_longitudinal(result, output_format), end="")
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
    lexical_target = Path(os.path.abspath(unresolved))
    if any(
        lexical_target == private or private in lexical_target.parents
        for private in _private_roots(root, config)
    ):
        raise ValueError(f"Configured {label} may not be inside atlas/Private: {configured}")
    if unresolved.is_symlink():
        raise ValueError(f"Configured {label} may not be a symbolic link: {configured}")
    target = unresolved.resolve()
    if target == root or root not in target.parents:
        raise ValueError(f"Configured {label} must be below the project root: {configured}")
    if any(
        target == private or private in target.parents
        for private in _private_roots(root, config)
    ):
        raise ValueError(f"Configured {label} may not be inside atlas/Private: {configured}")
    if must_exist and not target.is_file():
        raise ValueError(f"Configured {label} does not exist: {configured}")
    return target


def _project_directory(
    root: Path,
    config: ProjectConfig,
    configured: str,
    label: str,
) -> Path:
    candidate = Path(configured)
    unresolved = candidate if candidate.is_absolute() else root / candidate
    lexical_target = Path(os.path.abspath(unresolved))
    if any(
        lexical_target == private or private in lexical_target.parents
        for private in _private_roots(root, config)
    ):
        raise ValueError(f"Configured {label} may not be inside atlas/Private: {configured}")
    if unresolved.is_symlink():
        raise ValueError(f"Configured {label} may not be a symbolic link: {configured}")
    target = unresolved.resolve()
    if target == root or root not in target.parents:
        raise ValueError(f"Configured {label} must be below the project root: {configured}")
    if any(
        target == private or private in target.parents
        for private in _private_roots(root, config)
    ):
        raise ValueError(f"Configured {label} may not be inside atlas/Private: {configured}")
    if not target.is_dir():
        raise ValueError(f"Configured {label} does not exist: {configured}")
    return target


def _private_roots(root: Path, config: ProjectConfig) -> tuple[Path, ...]:
    return tuple(
        sorted(
            {
                root.resolve() / "atlas" / "Private",
                config.vault_path(root) / "Private",
            },
            key=lambda path: path.as_posix().casefold(),
        )
    )


def _private_paths(root: Path, config: ProjectConfig) -> tuple[str, ...]:
    return tuple(path.relative_to(root).as_posix() for path in _private_roots(root, config))
