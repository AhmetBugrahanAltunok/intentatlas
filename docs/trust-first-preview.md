# Trust-first real-repository preview

If you have not yet evaluated the packaged synthetic contract, start with:

```powershell
intentatlas demo --report text
```

That original scenario is prebuilt and does not claim to exercise repository discovery or Git
alignment. The steps below are the separate real-repository path.

Use this path on a trusted local checkout before IntentAtlas creates configuration, a vault, a
cache, a graph, or generated notes. Neither command requires an API key or network access.

For the shortest interactive path, run `intentatlas` inside the repository and press Enter after
checking the displayed root and scope. `intentatlas guide [PATH]` selects an explicit starting
path. Both routes produce the same production Change Report described below and write no project
state. The explicit commands remain available for automation and advanced use:

```powershell
intentatlas diagnose C:\path\to\project
intentatlas changes C:\path\to\project --commit HEAD --report
intentatlas changes C:\path\to\project --commit HEAD --report --format json
```

On macOS or Linux, replace the path with `/path/to/project`. Use `--worktree` instead of
`--commit HEAD` only when the intended subject is the current tracked/untracked worktree state.

The diagnostic is schema 1. It reports configuration and Git readiness, bounded adapter
capabilities, unsupported languages, oversized inputs, project/source-root ambiguity, configured
evidence without claiming freshness, graph/report availability, and the next safe command. It
reads bounded local metadata and supported sources, excludes the configured vault and literal
`atlas/Private/`, and does not write project or Git state.

The report is Change Report schema 1. Read it in this order:

1. Confirm the exact scope and base/head revision.
2. Check analysis state and freshness. `fallback` or `unknown` requires the displayed full-suite
   strategy; it is not targeted sufficiency.
3. Confirm the minimum confidence threshold and selected/total/filtered/limit-omitted counts.
4. Inspect each score, confidence, evidence tag, reason, and recorded ranking path.
5. Treat an omitted candidate only as below the shown threshold or result limit. It is never proof
   that a requirement is unaffected or a test unnecessary.
6. Follow the displayed test strategy and advisory.

To inspect the same immutable in-memory graph/report snapshot, opt in explicitly:

```powershell
intentatlas changes C:\path\to\project --commit HEAD --report --open
```

The viewer binds only to IPv4 loopback, validates the Host header, escapes project labels, exposes
the report first, supports keyboard navigation and Escape-to-close, and renders bounded graph
windows. The report cards show recorded ranking paths; generic shortest paths appear only in graph
detail and are labeled as connectivity rather than ranking proof.

After the preview is correctly understood, persistent adoption is a separate choice:

```powershell
intentatlas init C:\path\to\project
intentatlas scan C:\path\to\project
intentatlas open C:\path\to\project
```

See the deterministic [example report](examples/trust-first-report.json) and its original
[visual artifact](assets/trust-first-preview.svg). They demonstrate output semantics, not a claim
about discovery accuracy on another repository.
