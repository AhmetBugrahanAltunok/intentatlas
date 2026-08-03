<p align="center">
  <img src="docs/assets/logo.svg" width="132" alt="IntentAtlas logo">
</p>

<h1 align="center">IntentAtlas</h1>

<p align="center"><strong>The living intent map for software projects.</strong></p>

<p align="center">
  <a href="README.tr.md">Türkçe</a> ·
  <a href="https://github.com/AhmetBugrahanAltunok/IntentAtlas/blob/main/atlas/Brain/Product%20Roadmap.md">Product roadmap</a> ·
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
- Pressure graph and untrusted JSON boundaries with replayable fixed-seed property/mutation tests,
  and render the bounded large-graph window through a real Chrome-family browser in CI.
- Produce deterministic release provenance that binds verified artifact hashes to an exact Git
  revision and fixed build epoch; package publication remains separately approved.
- Link Go tests to uniquely owned exported declarations they actually reference, while keeping
  ambiguous and filename-only matches conservative.
- Follow one exact Go symbol-caller hop when a directly tested wrapper calls the changed symbol.
- Reuse a lazy deterministic adjacency index for impact and recommendation queries, with a bounded
  synthetic scale benchmark for contributors.
- Keep requirements, decisions, evidence, reviews, and project memory in Git.

## Release candidate status

The current candidate source identifies itself as `0.3.0rc1`. This is a release candidate, not a
published package or compatibility promise. No tag or package-index release is implied. From a
trusted checkout of the intended source revision, build and exercise that checkout:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install .
.\.venv\Scripts\intentatlas.exe --version
.\.venv\Scripts\intentatlas.exe demo --report text
```

This confirms the version and behavior of the current checkout; it does not by itself prove the
Git revision or artifact hash. The exact source, reproducible-build, provenance, and hash procedure
is documented in [the release process](RELEASING.md).

The report exits without opening a listener and shows why one test is recommended while another
test connected to a different symbol in the same source file is not recommended from the available
exact-symbol evidence. Omission is not a claim that the other requirement is unaffected or that
its test is unnecessary.

## Quick start

From a real repository in an interactive terminal, run one command:

```powershell
intentatlas
```

IntentAtlas shows the nearest safe Git root and a conservative scope before doing the analysis.
Press Enter once to accept it. Conflict, unstaged, or untracked state selects `worktree`; a
staged-only repository selects `staged`; a clean repository selects the exact `HEAD`; an unborn
repository selects `worktree`. The result uses the production Change Report and writes nothing.
Pipes, redirects, CI, or any other non-TTY invocation keep argparse's existing stderr/exit-2
behavior and never prompt or scan. Use `intentatlas guide [PATH]` for the same flow at an explicit
path. See the [guided CLI contract](docs/guided-cli.md).

The interactive transcript uses a prominent IntentAtlas heading, clearly named source/safety/
analysis/recommendation/Atlas sections, wrapped evidence, and one option per line. The browser
viewer keeps page and graph geometry stable when **Change report** and **Fit graph** are used
repeatedly.

To analyze a public GitHub repository without cloning it manually, use a real interactive
terminal:

```text
intentatlas https://github.com/OWNER/REPOSITORY
# or: intentatlas guide https://github.com/OWNER/REPOSITORY
```

Before any network or cache effect, IntentAtlas shows the normalized URL, managed-cache write,
shallow/resource bounds, and disabled execution behavior. Enter is the only approval. The result
shows the exact cached revision and uses the same production, no-write Change Report and immutable
viewer snapshot. Private/authenticated repositories, redirects, repository page URLs, hooks,
filters, LFS, submodules, and project execution are unsupported. See the
[managed repository cache](docs/managed-repository-cache.md).

To evaluate the packaged synthetic contract without touching a repository:

```powershell
intentatlas demo --report text
intentatlas demo --report json
intentatlas demo
```

The built-in showcase is original, offline, and temporary. Its synthetic graph and relationships
are prebuilt, so it exercises the production graph, recommendation, report, and viewer layers but
does not exercise repository discovery, AST parsing, or Git diff extraction. It does not scan the
current directory. See the [guided demo](docs/guided-demo.md).

The explicit expert commands remain available for a zero-footprint preview:

```powershell
intentatlas diagnose C:\path\to\your-project
intentatlas changes C:\path\to\your-project --commit HEAD --report
intentatlas changes C:\path\to\your-project --commit HEAD --report --format json
```

These commands are offline and no-write. The diagnostic reports bounded capability, ambiguity,
evidence readiness, and the safe next command. The report states its exact revision and scope,
freshness, confidence threshold, selected and omitted candidates, recorded ranking paths, and
fallback test strategy. An omission is not proof that intent is unaffected or a test unnecessary.
Only `--open` explicitly starts the loopback-only viewer for that same in-memory report snapshot.
See the [trust-first preview](docs/trust-first-preview.md) and [documentation index](docs/index.md).

After interpreting the preview, deliberately adopt the persistent vault workflow:

```powershell
.\.venv\Scripts\intentatlas.exe init C:\path\to\your-project
.\.venv\Scripts\intentatlas.exe scan C:\path\to\your-project
.\.venv\Scripts\intentatlas.exe open C:\path\to\your-project
```

`init` creates generic guidance and empty intent folders; it never seeds IntentAtlas's own
requirements, decisions, evidence, reviews, or dated sessions into the target repository.

Repeated CLI scans reuse a bounded content-addressed fragment for each unchanged built-in language
adapter. The command reports reused and rebuilt adapter counts. This cache contains graph metadata,
not source text, and is always safe to remove; a malformed or stale entry is rebuilt. Graph and
cache files are replaced atomically. See [incremental scanning](docs/incremental-scanning.md).

Then open the `atlas/` directory as an Obsidian vault. The standard Graph View will
show requirements, decisions, code, tests, evidence, and commits as color-coded nodes.

On macOS or Linux, replace `.\.venv\Scripts\intentatlas.exe` with
`./.venv/bin/intentatlas` and use an explicit path such as `/path/to/your-project`.

Python 3.11, 3.12, and 3.13 are supported. The complete suite runs on Linux, while an installed
wheel smoke test covers the CLI, scan, recommendation, and loopback viewer workflow on Linux,
Windows, and macOS for the oldest and newest supported Python versions. CI also runs maintained
source typing, immutable Action-reference policy, and real-browser rendering gates. See
[the release process](RELEASING.md) for the local reproducibility and artifact checks.
The candidate's exact wheel also passes an isolated pipx install/reinstall/uninstall lifecycle,
but no package has been published and no zero-prerequisite Windows installer exists. See
[installation status](docs/installation.md).

## Core commands

```text
intentatlas init [PATH]                  Create the project brain and local config
intentatlas guide [SOURCE]               Guide a local path or approved public GitHub URL
intentatlas cache list|info|clear         Inspect or clear exact managed cache entries offline
intentatlas diagnose [PATH]              Inspect readiness without writing project state
intentatlas scan [PATH]                  Rebuild the graph and generated vault notes
intentatlas status [PATH]                Show graph and orphan-note health
intentatlas impact TARGET [--depth 2]    Explain upstream/downstream relationships
intentatlas recommend-tests TARGET       Rank advisory test candidates with explanations
intentatlas changes --commit REV         Inspect bounded revision-scoped change metadata
intentatlas review --base REV --head REV Review a range in non-blocking CI shadow mode
intentatlas evaluate-recommendations LABELS  Measure recommendations against reviewed labels
intentatlas evaluate-corpus CORPUS       Compare thresholds across labeled local graphs
intentatlas evaluate-real-world MANIFEST CHECKOUTS  Validate pinned public checkouts offline
intentatlas evaluate-longitudinal MANIFEST CHECKOUTS  Measure a frozen pilot offline
intentatlas benchmark-scale              Measure indexed queries on a synthetic large graph
intentatlas demo [--report text|json]    Open the showcase or print its bounded evidence report
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
[CI shadow review](docs/ci-shadow-review.md) for the output and trust boundary.
The local `--open` view serves the exact in-memory graph and review used by the command. The
[review pilots](docs/review-pilots.md) record aligned, stale, and fallback regression boundaries.

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
[open evidence imports](docs/open-evidence.md).

To compare the current cache with a saved baseline:

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

From a full IntentAtlas repository checkout, measure recommendation quality against its explicitly
exhaustive reviewed label set:

```text
intentatlas evaluate-recommendations benchmarks/intentatlas-recommendations.json
intentatlas evaluate-recommendations benchmarks/intentatlas-recommendations.json --minimum-confidence high --format json
```

Evaluation reports TP, FP, FN, precision, and recall without running tests or changing ranking
scores. This repository-only two-case baseline is a regression aid, not evidence of accuracy on
other repositories; it is not included in the source-distribution corpus. See
[the evaluation schema and metric contract](docs/recommendation-evaluation.md).

To compare all confidence thresholds across the original Python, TypeScript, and Go graph
scenarios:

```text
intentatlas evaluate-corpus benchmarks/recommendation-corpus.json
intentatlas evaluate-corpus benchmarks/recommendation-corpus.json --format json
```

Corpus output contains compact per-project and micro totals. These small original fixtures verify
aggregation and confidence behavior; they are not copied repositories or real-world accuracy
evidence. See [the corpus schema](docs/recommendation-corpus.md).

For a reproducible real-world check from a full IntentAtlas repository checkout, acquire the six
approved public repositories only after network approval, pin them to the repository-only manifest
commits, then run:

```text
intentatlas evaluate-real-world benchmarks/real-world/manifest.json .intentatlas/real-world/checkouts
```

The command verifies origin, commit, clean state, and reviewed license hash before scanning in
memory. It does not clone, install, execute tests, run project code, or retain third-party source,
history, logos, or generated graphs. See the
[real-world validation protocol](docs/real-world-validation.md).

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

See the [longitudinal pilot protocol and benchmark card](docs/longitudinal-pilot.md) and the
[pre-1.0 compatibility policy](docs/compatibility-policy.md).

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
- `Private/` is local-only, user-provisioned, ignored by Git, and never created or scanned by
  IntentAtlas.

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

Adapter conformance contract version 1 turns the shared boundary into an executable check. Fresh
and cached fragments must satisfy the same bounded symbol, relation, endpoint, evidence, ordering,
and determinism rules before graph merge. Built-in adapters pass one fixture-driven helper; this is
not an external plugin loader. See [language adapter conformance](docs/adapter-conformance.md).

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
an original twelve-node same-file counterexample and removes its temporary graph when the viewer
stops. `intentatlas demo --report text` and `--report json` render the same bounded evidence story
without starting a listener.

For large repositories, the viewer retains the complete graph for local navigation but renders a
deterministic window of at most 240 nodes and 900 edges. The default overview balances graph layers;
global search, report links, and relationship links can open a bounded two-hop neighborhood around
any hidden node. Total and rendered counts remain visible, and relationship details explicitly
report omitted items instead of creating unbounded browser DOM.

The real-world evaluator adds a provenance gate around the same scanner and corpus evaluator. A
strict manifest binds each local checkout to an exact GitHub origin, commit, SPDX identifier,
license-file hash, and reviewed labels. The included 18 cases across Python, JavaScript, and Go
are useful validation evidence for those pinned changes only; they are not a general accuracy
claim.

Ongoing work and completion status are tracked in the
[Product Roadmap](https://github.com/AhmetBugrahanAltunok/IntentAtlas/blob/main/atlas/Brain/Product%20Roadmap.md). The root `ROADMAP.md` is retained only as
an explicitly archived snapshot of the original 0.1–0.3 technical plan.

## Inspiration

The vault-first memory model is inspired by
[breferrari/obsidian-mind](https://github.com/breferrari/obsidian-mind), while IntentAtlas
adds a code-and-delivery intent graph. No third-party source code is bundled.

MIT licensed. See [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.
