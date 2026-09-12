# Command reference

Every command IntentAtlas exposes. If you are here for the first time, start with the
[README](../README.md) instead: it covers installing, the two-minute demo, and choosing your
first command.

Maintainer and benchmark commands are not listed by `intentatlas --help`; they are named in
its epilog and documented here.

```text
intentatlas init [PATH]                  Create the project brain and local config
intentatlas guide [SOURCE]               Guide a local path or approved public GitHub URL
intentatlas cache list                    List managed cache entries and their CACHE_ID
intentatlas cache info CACHE_ID           Inspect one exact managed cache entry offline
intentatlas cache clear CACHE_ID          Clear one exact managed cache entry offline
intentatlas diagnose [PATH]              Inspect readiness without writing project state
intentatlas scan [PATH]                  Rebuild the graph and generated vault notes
intentatlas status [PATH]                Show graph and orphan-note health
intentatlas impact TARGET [PATH] [--depth 2]  Explain upstream/downstream relationships
intentatlas recommend-tests TARGET [PATH]    Rank advisory test candidates with explanations
intentatlas changes [PATH] --commit REV      Inspect bounded revision-scoped change metadata
intentatlas review [PATH] --base REV --head REV  Review a range in non-blocking CI shadow mode
intentatlas evaluate-recommendations LABELS  Measure recommendations against reviewed labels
intentatlas evaluate-corpus CORPUS       Compare thresholds across labeled local graphs
intentatlas evaluate-real-world MANIFEST CHECKOUTS  Validate pinned public checkouts offline
intentatlas evaluate-longitudinal MANIFEST CHECKOUTS  Measure a frozen pilot offline
intentatlas benchmark-scale              Measure indexed queries on a synthetic large graph
intentatlas demo [--report text|json]    Open the showcase or print its bounded evidence report
intentatlas diff BASE [PATH] [--check]   Compare the cached graph with a baseline
intentatlas open [PATH]                  Launch an existing graph (run scan explicitly first)
```

`status` is also a graph-health gate: it returns exit status 1 when one or more durable notes are
orphaned and 0 when none are orphaned. Invalid requests or unreadable graph state retain exit 2.

The same deterministic ChangeSet schema covers a commit, endpoint range, index, or current
worktree:

```text
intentatlas changes --commit HEAD
intentatlas changes --base main --head HEAD --format json
intentatlas changes --staged
intentatlas changes --worktree
intentatlas changes --staged --analyze --format json
intentatlas changes --staged --report --format json
intentatlas changes --worktree --report --open
```

Choose the scope by what you mean to inspect: `--worktree` includes current staged, unstaged, and
untracked changes; `--staged` inspects only the index; `--commit HEAD` inspects the committed HEAD
snapshot and expects its affected files to still match that revision. On a dirty repository, use
the command printed by `diagnose` instead of guessing.

| Output term | Meaning |
| --- | --- |
| `aligned` | The selected change-side artifact matches the current file that was safely scanned. |
| `stale` | The selected commit/index artifact differs from the current file, so exact claims abstain. |
| `analyzed` | Exact supported artifact evidence was formed for the changed file. |
| `fallback` | Only broader file-level evidence was available; follow the displayed full-suite policy. |
| `unknown` | The artifact could not be safely matched or analyzed; no targeted-sufficiency claim is made. |

`--analyze` returns the per-file state, freshness, confidence, and artifact IDs. `--report` performs
that same fresh analysis and additionally ranks requirement impacts and tests, selects a test
strategy, and explains omissions. `--report --open` shows that same in-memory report in the local
viewer.

ChangeSet output contains statuses, safe project-relative paths, resolved commit IDs, and
current-side hunk ranges. Git output is capped while it is being drained, and raw diff lines are
never stored. Worktree mode includes ignored-aware untracked paths but does not read or emit their
contents. If an indexed deletion is followed by an untracked recreation at the same path, the
combined worktree state is reported as `modified`; `--staged` still reports the index deletion.
`--analyze` explicitly performs a fresh,
bounded local scan and labels each file `analyzed`, `fallback`, or `unknown`, with
`aligned`/`stale` freshness, confidence, artifact IDs, and evidence. It may read supported
worktree files through the normal scanner but never executes project code or persists raw source.
The literal `atlas/Private/` boundary, the configured vault, and configured scanner exclusions are
excluded at the Git pathspec boundary before metadata or patch output is collected.

`--report` performs the same aligned analysis and ranks requirement impacts plus candidate tests.
Exact symbol-to-intent paths may meet the default medium threshold; a relationship found only by
sharing a file stays low confidence. `fallback` analysis never treats targeted tests as sufficient:
it emits a targeted-plus-full-suite or full-suite-fallback strategy. `unknown` analysis abstains
from ranked claims and requires the full suite. The report is advisory and does not prove that
unlisted requirements or tests are unaffected.
Add `--open` to inspect that same in-memory report in the loopback viewer without persisting a
second graph or report artifact.

Both `--analyze` and `--report` perform a fresh bounded worktree scan; they do not reuse the saved
graph, so a large repository can take noticeably longer than `status` or `impact`. Text output
shows the score bands (`low` 0–64, `medium` 65–84, `high` 85–100). Lowering the threshold to `low`
is useful only to inspect weaker exploratory evidence. `Additional signals` counts other recorded
ranking reasons; inspect `tests[].reason_details` in `--format json` to see them.

For pull-request or CI experimentation, `review` composes the same range ChangeSet and Change
Report into deterministic Markdown, JSON, or bounded SARIF 2.1.0:

```text
intentatlas review --base origin/main --head HEAD
intentatlas review --base origin/main --head HEAD --format json
intentatlas review --base origin/main --head HEAD --format sarif
intentatlas review --base origin/main --head HEAD --test-outcomes .intentatlas/test-outcomes.json
intentatlas review --base origin/main --head HEAD --open
```

This first integration is deliberately shadow-only: valid findings return success, do not publish
or modify a pull request, and require no provider credential or network request. SARIF contains
safe project-relative locations and hunk regions but no source snippets or absolute paths. See
[CI shadow review](ci-shadow-review.md) for the output and trust boundary.
The local `--open` view serves the exact in-memory graph and review used by the command. The
[review pilots](review-pilots.md) record aligned, stale, and fallback regression boundaries.

Verification reports are opt-in. Add project-relative paths to `intentatlas.json`, generate the
reports with your existing CI tools, and run `intentatlas scan`:

```json
{
  "coverage_reports": ["coverage.xml"],
  "test_reports": ["junit.xml"]
}
```

IntentAtlas reads these XML files offline and stores only bounded per-file aggregates. It does not
run a test command, retain failure output, or persist absolute source paths.

Open evidence reports are also opt-in:

```json
{
  "scip_reports": ["reports/index.scip.json"],
  "sarif_reports": ["reports/results.sarif"],
  "test_execution_reports": ["reports/test-execution.json"]
}
```

SCIP support accepts the protobuf JSON mapping, not binary protobuf. SCIP and SARIF become bounded
file observations and never imply impact or test necessity. A strict execution map can add observed
`test -> source` evidence only when its full commit equals current Git HEAD and every mapped file is
tracked and unchanged from that HEAD. Stale or unknown maps are visible
but withheld from recommendations. Raw symbols, diagnostics, messages, snippets, fixes,
code flows, source content, and absolute paths are not retained. See
[open evidence imports](open-evidence.md).

To compare the current graph with a saved baseline, first scan a known-good state and save that
generated graph. After the project changes, scan again and compare it with the saved copy:

```powershell
intentatlas scan
Copy-Item .intentatlas\graph.json .intentatlas\baseline.json
# Make the intended project change, then refresh the current graph:
intentatlas scan
intentatlas diff .intentatlas/baseline.json --output .intentatlas/diff.json --check
```

On macOS or Linux, use `cp .intentatlas/graph.json .intentatlas/baseline.json`. A baseline is an
explicit snapshot chosen by the user; `scan` does not create or overwrite it automatically.
With `--check`, exit status `1` means graph changes were found—the expected CI signal, not a runtime
failure. Exit status `0` means no graph changes. The command prints this explanation to stderr so
the JSON written to stdout or `--output` remains machine-readable.

To rank test files for a commit, file, or symbol without running them:

```text
intentatlas recommend-tests commit:FULL_SHA --minimum-confidence medium
intentatlas recommend-tests src/auth.py --minimum-confidence low --format json
```

Scores are fixed, inspectable structural signals. Exact symbol changes plus exact static test
links rank above file-level or filename-convention evidence. A file-level relationship cannot
become a default medium-confidence claim for an unrelated symbol in the same file; such fallback
is low confidence or omitted when contradictory exact-symbol evidence exists. Results are
advisory: omitted tests and absent recommendations never prove that behavior is unaffected.
Imported JUnit summaries are displayed only as observations because their freshness is unknown.

From a full IntentAtlas repository checkout, measure recommendation quality against its explicitly
exhaustive reviewed label set:

```text
intentatlas scan
intentatlas evaluate-recommendations benchmarks/intentatlas-recommendations.json
intentatlas evaluate-recommendations benchmarks/intentatlas-recommendations.json --minimum-confidence high --format json
```

Evaluation reports TP, FP, FN, precision, and recall without running tests or changing ranking
scores. This repository-only two-case baseline is a regression aid, not evidence of accuracy on
other repositories; it is not included in the source-distribution corpus. Its targets are pinned
historical commits, so the saved graph's `git_history_limit` must still include them. This checkout
uses the maximum bounded history of 250 for that reason. `evaluate-corpus` differs: it reads the
small saved graphs named by its manifest and does not require a project `scan`. See
[the evaluation schema and metric contract](recommendation-evaluation.md).

To compare all confidence thresholds across the original Python, TypeScript, and Go graph
scenarios:

```text
intentatlas evaluate-corpus benchmarks/recommendation-corpus.json
intentatlas evaluate-corpus benchmarks/recommendation-corpus.json --format json
```

Corpus output contains compact per-project and micro totals. These small original fixtures verify
aggregation and confidence behavior; they are not copied repositories or real-world accuracy
evidence. See [the corpus schema](recommendation-corpus.md).

For a reproducible real-world check from a full IntentAtlas repository checkout, acquire the six
approved public repositories only after network approval, pin them to the repository-only manifest
commits, then run:

```text
intentatlas evaluate-real-world benchmarks/real-world/manifest.json .intentatlas/real-world/checkouts
```

The command verifies origin, commit, clean state, and reviewed license hash before scanning in
memory. It does not clone, install, execute tests, run project code, or retain third-party source,
history, logos, or generated graphs. See the
[real-world validation protocol](real-world-validation.md).

The frozen longitudinal pilot expands that evidence to eight repositories and 64 chronological
cases with explicit calibration/evaluation partitions, three language cohorts, and two workspace
histories. Its evaluation partition records low/medium precision 50.00% with recall 100.00% and
coverage 90.625%; high precision 100.00% with recall 79.4118% and coverage 71.875%. Wilson
intervals, cohort sizes, abstention, analysis/freshness, execution strategy, and reviewed FP/FN
classifications are reported beside the point estimates. These bounded results are not general
accuracy or targeted-sufficiency claims, and duration/savings remain unknown.

```text
intentatlas evaluate-longitudinal benchmarks/longitudinal/manifest.json .intentatlas/real-world/checkouts
```

See the [longitudinal pilot protocol and benchmark card](longitudinal-pilot.md) and the
[pre-1.0 compatibility policy](compatibility-policy.md).

To run the offline query-scale probe without reading or executing a project:

```text
intentatlas benchmark-scale
intentatlas benchmark-scale --unrelated-edges 50000 --iterations 500 --format json
```

The benchmark reports stable graph/result/work counts plus environment-specific timings. It is a
regression and diagnostic tool, not a portable latency promise. See
[the scale benchmark contract](query-scale-benchmark.md).

Delivery context is also opt-in and offline. Configure
`"delivery_reports": ["reports/delivery.json"]` and scan again. IntentAtlas retains only bounded
metadata and exact local links; see [the delivery schema](delivery-schema.md).

