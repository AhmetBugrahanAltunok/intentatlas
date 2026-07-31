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
- Keep requirements, decisions, evidence, reviews, and project memory in Git.

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\intentatlas.exe init
.\.venv\Scripts\intentatlas.exe scan
.\.venv\Scripts\intentatlas.exe open
```

Then open the `atlas/` directory as an Obsidian vault. The standard Graph View will
show requirements, decisions, code, tests, evidence, and commits as color-coded nodes.

On macOS or Linux, replace `.\.venv\Scripts\intentatlas.exe` with
`./.venv/bin/intentatlas`.

## Core commands

```text
intentatlas init [PATH]                  Create the project brain and local config
intentatlas scan [PATH]                  Rebuild the graph and generated vault notes
intentatlas status [PATH]                Show graph and orphan-note health
intentatlas impact TARGET [--depth 2]    Explain upstream/downstream relationships
intentatlas recommend-tests TARGET       Rank advisory test candidates with explanations
intentatlas evaluate-recommendations LABELS  Measure recommendations against reviewed labels
intentatlas diff BASE [PATH] [--check]   Compare the cached graph with a baseline
intentatlas open [PATH]                  Launch the local interactive graph
```

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

Scores are fixed, inspectable structural signals. Exact symbol changes plus static test links rank
above file-level or filename-convention evidence. Results are advisory: omitted tests and absent
recommendations never prove that behavior is unaffected. Imported JUnit summaries are displayed
only as observations because their freshness is unknown.

To measure recommendation quality against an explicitly exhaustive reviewed label set:

```text
intentatlas evaluate-recommendations benchmarks/intentatlas-recommendations.json
intentatlas evaluate-recommendations benchmarks/intentatlas-recommendations.json --minimum-confidence high --format json
```

Evaluation reports TP, FP, FN, precision, and recall without running tests or changing ranking
scores. The bundled two-case baseline is a regression aid, not evidence of accuracy on other
repositories. See [the evaluation schema and metric contract](docs/recommendation-evaluation.md).

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
module-local package imports, and tests. Neither adapter runs a language runtime or project code.

Configured Cobertura and JUnit reports now create generated coverage and test-result evidence in
the graph. Graph diff schema 1 provides stable node and relationship changes for CI without a
generation timestamp.

Explicit local delivery snapshots connect requirements and decisions to issues, pull requests,
changed files, and known commits without credentials or provider API access.

Recent Git history also records direct `modifies` relationships for Python classes, functions,
and methods when changed new-side lines intersect their AST spans and the current file still
matches the analyzed commit blob. File-level `changes` links stay available for stale files,
deletions, module-level edits, unsupported span adapters, and uncertain cases.

`recommend-tests` consumes those validated graph relationships and ranks direct test-file
candidates as high, medium, or low confidence. The first version deliberately excludes transitive
dependency guesses and defaults to medium confidence to reduce false positives.

`evaluate-recommendations` reuses that production query unchanged and compares it with strict,
closed-world local labels. Its timestamp-free schema-1 output makes threshold tradeoffs and
ranking regressions visible while keeping undefined metrics explicit.

Ongoing work and completion status are tracked in the
[Product Roadmap](atlas/Brain/Product%20Roadmap.md). The root `ROADMAP.md` is retained only as
an explicitly archived snapshot of the original 0.1–0.3 technical plan.

## Inspiration

The vault-first memory model is inspired by
[breferrari/obsidian-mind](https://github.com/breferrari/obsidian-mind), while IntentAtlas
adds a code-and-delivery intent graph. No third-party source code is bundled.

MIT licensed. See [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.
