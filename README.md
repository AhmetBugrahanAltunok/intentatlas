<p align="center">
  <img src="docs/assets/logo.svg" width="132" alt="IntentAtlas logo">
</p>

<h1 align="center">IntentAtlas</h1>

<p align="center"><strong>The living intent map for software projects.</strong></p>

<p align="center">
  <a href="README.tr.md">Türkçe</a> ·
  <a href="atlas/Brain/Product%20Roadmap.md">Product roadmap</a> ·
  <a href="CONTRIBUTING.md">Contributing</a>
</p>

IntentAtlas connects the reason a system exists to the code that implements it:

```text
Requirement → Decision → Issue → Code → Test → Evidence → Commit
```

Most code graphs explain what calls what. IntentAtlas explains **why a change exists,
what proves it, and what could be affected next**. It runs locally, requires no API key,
and keeps its human-readable project memory in an Obsidian-compatible vault.

## What works today

- Scan Python, TypeScript/JavaScript, and Go repositories into a deterministic relationship graph.
- Connect files, symbols, imports, tests, Markdown documents, and Git commits.
- Generate a linked Obsidian vault with purpose-based folders and wikilinks.
- Explore the same graph in a local, dependency-free web viewer.
- Trace upstream and downstream impact from the command line.
- Import existing Cobertura coverage and JUnit test evidence without running project code.
- Produce a deterministic, versioned graph diff for CI.
- Import bounded issue and pull-request metadata from explicit local JSON snapshots.
- Link recent commits to exact modified Python symbols when zero-context diff hunks intersect
  validated AST source spans and the worktree file matches that commit's blob, while retaining
  file-level history as a safe fallback.
- Rank test files for a commit, file, or symbol with fixed confidence levels, complete evidence
  paths, and deterministic text or JSON output.
- Measure recommendations against exhaustive, human-reviewed local labels with deterministic
  per-case and micro-aggregate precision and recall.
- Compare low, medium, and high confidence across a bounded corpus of labeled local graphs.
- Re-run the unchanged recommendation query against clean, pinned, license-reviewed public
  checkouts without bundling or executing third-party code.
- Verify the installed wheel workflow on Windows, macOS, and Linux CI, and reject release
  candidates whose repeated wheel or source builds differ byte-for-byte.
- Link Go tests to uniquely owned exported declarations they actually reference, while keeping
  ambiguous and filename-only matches conservative.
- Follow one exact Go symbol-caller hop when a directly tested wrapper calls the changed symbol.
- Reuse a lazy deterministic adjacency index for impact and recommendation queries, with a bounded
  synthetic scale benchmark for contributors.
- Keep requirements, decisions, evidence, reviews, and project memory in Git.

## Quick start

Try the complete intent-to-proof story immediately after installation:

```powershell
intentatlas demo
```

The built-in showcase is original, offline, and temporary. It does not scan the current directory.
See the [guided demo](docs/guided-demo.md). For your own repository:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\intentatlas.exe init
.\.venv\Scripts\intentatlas.exe scan
.\.venv\Scripts\intentatlas.exe open
```

`init` creates generic guidance and empty intent folders; it never seeds IntentAtlas's own
requirements, decisions, evidence, reviews, or dated sessions into the target repository.

Then open the `atlas/` directory as an Obsidian vault. The standard Graph View will
show requirements, decisions, code, tests, evidence, and commits as color-coded nodes.

On macOS or Linux, replace `.\.venv\Scripts\intentatlas.exe` with
`./.venv/bin/intentatlas`.

Python 3.11, 3.12, and 3.13 are supported. The complete suite runs on Linux, while an installed
wheel smoke test covers the CLI, scan, recommendation, and loopback viewer workflow on Linux,
Windows, and macOS for the oldest and newest supported Python versions. See
[the release process](RELEASING.md) for the local reproducibility and artifact checks.

## Core commands

```text
intentatlas init [PATH]                  Create the project brain and local config
intentatlas scan [PATH]                  Rebuild the graph and generated vault notes
intentatlas status [PATH]                Show graph and orphan-note health
intentatlas impact TARGET [--depth 2]    Explain upstream/downstream relationships
intentatlas recommend-tests TARGET       Rank advisory test candidates with explanations
intentatlas changes --commit REV         Inspect bounded revision-scoped change metadata
intentatlas evaluate-recommendations LABELS  Measure recommendations against reviewed labels
intentatlas evaluate-corpus CORPUS       Compare thresholds across labeled local graphs
intentatlas evaluate-real-world MANIFEST CHECKOUTS  Validate pinned public checkouts offline
intentatlas benchmark-scale              Measure indexed queries on a synthetic large graph
intentatlas demo                         Open the built-in intent-to-proof showcase
intentatlas diff BASE [PATH] [--check]   Compare the cached graph with a baseline
intentatlas open [PATH]                  Launch the local interactive graph
```

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

ChangeSet output contains statuses, safe project-relative paths, resolved commit IDs, and
current-side hunk ranges. It never stores raw diff lines. Worktree mode includes ignored-aware
untracked paths but does not read or emit their contents. `--analyze` explicitly performs a fresh,
bounded local scan and labels each file `analyzed`, `fallback`, or `unknown`, with
`aligned`/`stale` freshness, confidence, artifact IDs, and evidence. It may read supported
worktree files through the normal scanner but never executes project code or persists raw source.
The configured vault's `Private/` area is excluded before Git metadata is collected.

`--report` performs the same aligned analysis and ranks requirement impacts plus candidate tests.
Exact symbol-to-intent paths may meet the default medium threshold; a relationship found only by
sharing a file stays low confidence. `fallback` analysis never treats targeted tests as sufficient:
it emits a targeted-plus-full-suite or full-suite-fallback strategy. `unknown` analysis abstains
from ranked claims and requires the full suite. The report is advisory and does not prove that
unlisted requirements or tests are unaffected.
Add `--open` to inspect that same in-memory report in the loopback viewer without persisting a
second graph or report artifact.

Verification reports are opt-in. Add project-relative paths to `intentatlas.json`, generate the
reports with your existing CI tools, and run `intentatlas scan`:

```json
{
  "coverage_reports": ["coverage.xml"],
  "test_reports": ["junit.xml"]
}
```

IntentAtlas reads these XML files offline and stores only bounded per-file aggregates. It does not
run a test command, retain failure output, or persist absolute source paths. To compare the current
cache with a saved baseline:

```text
intentatlas diff .intentatlas/baseline.json --output .intentatlas/diff.json --check
```

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

To measure recommendation quality against an explicitly exhaustive reviewed label set:

```text
intentatlas evaluate-recommendations benchmarks/intentatlas-recommendations.json
intentatlas evaluate-recommendations benchmarks/intentatlas-recommendations.json --minimum-confidence high --format json
```

Evaluation reports TP, FP, FN, precision, and recall without running tests or changing ranking
scores. The bundled two-case baseline is a regression aid, not evidence of accuracy on other
repositories. See [the evaluation schema and metric contract](docs/recommendation-evaluation.md).

To compare all confidence thresholds across the original Python, TypeScript, and Go graph
scenarios:

```text
intentatlas evaluate-corpus benchmarks/recommendation-corpus.json
intentatlas evaluate-corpus benchmarks/recommendation-corpus.json --format json
```

Corpus output contains compact per-project and micro totals. These small original fixtures verify
aggregation and confidence behavior; they are not copied repositories or real-world accuracy
evidence. See [the corpus schema](docs/recommendation-corpus.md).

For a reproducible real-world check, acquire the six approved public repositories only after
network approval, pin them to the manifest commits, then run:

```text
intentatlas evaluate-real-world benchmarks/real-world/manifest.json .intentatlas/real-world/checkouts
```

The command verifies origin, commit, clean state, and reviewed license hash before scanning in
memory. It does not clone, install, execute tests, run project code, or retain third-party source,
history, logos, or generated graphs. See the
[real-world validation protocol](docs/real-world-validation.md).

To run the offline query-scale probe without reading or executing a project:

```text
intentatlas benchmark-scale
intentatlas benchmark-scale --unrelated-edges 50000 --iterations 500 --format json
```

The benchmark reports stable graph/result/work counts plus environment-specific timings. It is a
regression and diagnostic tool, not a portable latency promise. See
[the scale benchmark contract](docs/query-scale-benchmark.md).

Delivery context is also opt-in and offline. Configure
`"delivery_reports": ["reports/delivery.json"]` and scan again. IntentAtlas retains only bounded
metadata and exact local links; see [the delivery schema](docs/delivery-schema.md).

## The project brain

The `atlas/` vault deliberately separates ownership:

- `Brain/`, `Requirements/`, `Decisions/`, `Issues/`, `Evidence/`, `Reviews/`, and `Sessions/`
  are written by people and agents.
- `Code/`, `Symbols/`, `Tests/`, and `Commits/` are generated by the scanner.
- `Private/` is local-only, ignored by Git, and never scanned.

Generated-note synchronization prepares the complete desired view before changing files. It
leaves byte-identical notes untouched, atomically replaces changed notes with bounded retries for
transient file locks, and removes stale generated notes only after every desired note is present.
A persistent error therefore fails clearly without first deleting the previous generated view.

Folders group by purpose; links group by meaning. An orphaned durable note is treated
as a health issue, because project knowledge only becomes useful when it is connected.

Typed Markdown links use the portable `relation:: [[target]]` form. For example,
`drives:: [[Decisions/ADR-001 - Vault-first intent graph]]` preserves the meaning of a link;
ordinary wikilinks remain safe generic references.

## Status

IntentAtlas is an early working prototype. Python, TypeScript/JavaScript, and Go analysis share a
language-neutral built-in adapter contract. The TypeScript/JavaScript adapter covers `.ts`, `.tsx`,
`.js`, and `.jsx` files with conservative symbol, local-import, re-export, and test relationships.
The Go adapter covers `.go` files, `go.mod` module boundaries, named types, functions, methods,
module-local package imports, and tests. Same-directory tests gain structural evidence only for
referenced exported declarations owned by one production file; ambiguous names remain unlinked and
filename matching stays a weak fallback. Neither adapter runs a language runtime or project code.

Configured Cobertura and JUnit reports now create generated coverage and test-result evidence in
the graph. Graph diff schema 1 provides stable node and relationship changes for CI without a
generation timestamp.

Explicit local delivery snapshots connect requirements and decisions to issues, pull requests,
changed files, and known commits without credentials or provider API access.

Recent Git history also records direct `modifies` relationships for Python classes, functions,
and methods when changed new-side lines intersect their AST spans and the current file still
matches the analyzed commit blob. File-level `changes` links stay available for stale files,
deletions, module-level edits, unsupported span adapters, and uncertain cases.

`recommend-tests` consumes those validated graph relationships and ranks test-file candidates as
high, medium, or low confidence. Python tests can target exact imported symbols through bounded
package re-exports; nested changes can use a focused owning-symbol test when its test name agrees.
JavaScript/TypeScript records exact named and default static imports, and follows at most one exact
symbol-dependent source file to a directly linked test. For a selected file or symbol, tests from
the artifact's most recent analyzed co-change provide separate medium-confidence evidence. The
query never performs unrestricted transitive traversal and defaults to medium confidence to reduce
false positives.

`evaluate-recommendations` reuses that production query unchanged and compares it with strict,
closed-world local labels. Its timestamp-free schema-1 output makes threshold tradeoffs and
ranking regressions visible while keeping undefined metrics explicit.

`evaluate-corpus` applies the same query to multiple saved graphs and reports low, medium, and high
confidence side by side. It fails the complete corpus when any graph or label is invalid, so stale
or malformed projects cannot silently improve aggregate metrics.

Impact and recommendation queries share a lazy deterministic adjacency index. Repeated local
lookups inspect only matching incoming or outgoing buckets; adding an edge invalidates and safely
rebuilds the in-memory index.

The local viewer also derives a bounded set of shortest structural paths from the selected node to
tests, evidence, coverage, test results, commits, and pull requests. These paths make the
intent-to-proof story easier to follow; they explain graph connectivity and do not claim causality,
completeness, freshness, or test necessity. `intentatlas demo` opens the same production viewer on
a packaged nine-node first-party example and removes its temporary graph when the viewer stops.

The real-world evaluator adds a provenance gate around the same scanner and corpus evaluator. A
strict manifest binds each local checkout to an exact GitHub origin, commit, SPDX identifier,
license-file hash, and reviewed labels. The included 18 cases across Python, JavaScript, and Go
are useful validation evidence for those pinned changes only; they are not a general accuracy
claim.

Ongoing work and completion status are tracked in the
[Product Roadmap](atlas/Brain/Product%20Roadmap.md). The root `ROADMAP.md` is retained only as
an explicitly archived snapshot of the original 0.1–0.3 technical plan.

## Inspiration

The vault-first memory model is inspired by
[breferrari/obsidian-mind](https://github.com/breferrari/obsidian-mind), while IntentAtlas
adds a code-and-delivery intent graph. No third-party source code is bundled.

MIT licensed. See [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.
