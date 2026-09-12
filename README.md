<p align="center">
  <img src="docs/assets/logo.svg" width="132" alt="IntentAtlas logo">
</p>

<h1 align="center">IntentAtlas</h1>

<p align="center"><strong>The living intent map for software projects.</strong></p>

<p align="center">
  <img alt="Status: beta" src="https://img.shields.io/badge/status-beta-orange">
  <img alt="Version 0.3.0b1" src="https://img.shields.io/badge/version-0.3.0b1-blue">
  <img alt="Python 3.11+" src="https://img.shields.io/badge/python-3.11%2B-blue">
</p>

<p align="center">
  <a href="README.tr.md">Türkçe</a> ·
  <a href="https://github.com/AhmetBugrahanAltunok/IntentAtlas/blob/main/atlas/Brain/Product%20Roadmap.md">Product roadmap</a> ·
  <a href="CONTRIBUTING.md">Contributing</a>
</p>

IntentAtlas shows **why a change exists, which requirement it may affect, and which test has
evidence for it**. It analyzes repositories locally, uploads no source code, and requires no API
key.

```text
Requirement → Decision → Issue → Code → Test → Evidence → Commit
```

<p align="center">
  <img src="docs/assets/intentatlas-demo.gif" width="960" alt="IntentAtlas demo showing the intent graph, change report, and test evidence paths">
</p>

## Get the first demo in two minutes

Prerequisites: Python 3.11, 3.12, or 3.13. Git is required for repository analysis but not for the
built-in demo. The install step may contact your configured Python package index to obtain build
dependencies.

> **Windows: enable long paths before cloning this repository.** IntentAtlas ships its own `atlas/`
> vault, and 51 of its generated symbol notes have paths longer than 120 characters. Cloning into
> anything but a short directory exceeds the 260-character `MAX_PATH` limit and the checkout aborts
> with `Filename too long`, leaving an empty working tree. Run
> `git config --global core.longpaths true` once, or clone to a short path such as
> `C:\src\intentatlas`. This affects cloning IntentAtlas itself, not the repositories it analyzes.

The two-minute target ends when the first text demo appears. Reading the output and trying the
repository workflows below takes longer.

IntentAtlas is currently an unpublished beta. Choose the environment folder once;
if `.venv` already belongs to another setup, change the first line to
`$IntentAtlasVenv = ".venv-intentatlas"`:

```powershell
$IntentAtlasVenv = ".venv"
python -m venv $IntentAtlasVenv
& "$IntentAtlasVenv\Scripts\python.exe" -m pip install .
& "$IntentAtlasVenv\Scripts\intentatlas.exe" demo --report text
```

Python reuses an existing environment folder. Later examples use the short `intentatlas` command
after activating the exact folder selected above:

```powershell
& "$IntentAtlasVenv\Scripts\Activate.ps1"
```

On macOS or Linux, set `IntentAtlasVenv=.venv` (or another name), use
`$IntentAtlasVenv/bin/python` and `$IntentAtlasVenv/bin/intentatlas`, then run
`source "$IntentAtlasVenv/bin/activate"`. If activation is unavailable, keep using the selected
folder's full executable path.

The demo does not scan the current directory or access the network. It prints a small, built-in
scenario with a recommendation and its evidence. Abridged output:

```text
Exact changed symbol: rotate_session (src/auth.py)
Recommended tests:
- tests/test_auth_rotation.py [medium 80]
  Why: The test directly references an exactly modified symbol.
  Path: commit → rotate_session → tests/test_auth_rotation.py
```

`medium 80` means a score of 80 in the medium band: low is 0–64, medium is 65–84, and high is
85–100. Confidence ranks available structural evidence; it is not a probability of correctness.

The guided flow requires a real interactive terminal; pipes, redirects, and non-interactive shells
are rejected. In a non-interactive shell, run `intentatlas diagnose PATH`, then copy its exact
**Next safe command**. To analyze a local Git repository interactively without writing project
files:

```powershell
intentatlas guide C:\path\to\your-project
```

Or inspect a public GitHub repository that you explicitly approve without cloning it manually:

```powershell
intentatlas guide https://github.com/OWNER/REPOSITORY
```

IntentAtlas shows the exact scope, safety limits, and any network/cache effect before asking you to
press Enter. The result explains possible requirement impact, candidate tests, confidence, and the
recorded evidence path. Choose Quit to exit the guide; if you open the local viewer, stop its
terminal process with Ctrl+C. See the [guided CLI walkthrough](docs/guided-cli.md).

### Example from a real repository

Against the pinned Click commit used by the repository's reviewed benchmark, the no-write report
selects one test and explains the exact structural route. Abridged output:

```text
$ intentatlas changes /path/to/click --commit HEAD --report
Changed: __exit__ (src/click/core.py)
Run 1 test:

  tests/test_context.py   [medium confidence]
    The test references the owning symbol of an exactly modified nested symbol.
    __exit__ -> Context -> tests/test_context.py

No requirement is linked to this change.

Impact and test recommendations are bounded structural evidence, not proof that an
omitted requirement is unaffected or that a suggested test is sufficient.
Full detail: --explain    Machine-readable: --format json
```

`--explain` adds the revisions, confidence bands, candidate and omission counts, graph
identifiers and evidence labels behind that answer. `--format json` is the stable schema-1
document for tools; neither the JSON nor the `--explain` text changed when the default became
this summary.

This output is advisory. The checkout is pinned and license-reviewed for reproducibility; project
code and tests are not executed. See the [real-world validation protocol](docs/real-world-validation.md).

That pinned example is intentionally small. A larger change can produce many requirement and test
candidates, and fallback analysis adds a full-suite strategy. Use `--limit 5` for a shorter human
report. `--format json` preserves the bounded analysis, all recorded reason details, and paths for
automation, so even one broad commit can produce thousands of lines; redirect it to a file instead
of treating it as a compact terminal view.

Confidence is a ranking of available structural evidence, not a probability of correctness.
`high` (85-100) means the strongest structural evidence, such as the test itself being in the
changed set. `medium` (65-84) covers direct links such as an `80/medium` static symbol reference.
`low` (below 65) is exploratory discovery with high fan-out; use `medium or higher` for automated
selection. Raising `--minimum-confidence low` shows weaker candidates, it does not strengthen them.

## What IntentAtlas is — and is not

| IntentAtlas is | IntentAtlas is not |
| --- | --- |
| A local evidence graph connecting intent, code, tests, and Git history | An AI code generator or autonomous coding agent |
| A read-only change preview before you adopt a persistent vault | A hosted service that uploads your repository |
| An explainable, confidence-ranked test recommendation tool | A test runner or proof that the suggested tests are sufficient |
| An optional Markdown/Obsidian project memory you can keep in Git | A replacement for Git, issue trackers, CI, or Obsidian |

An omitted requirement is not proven unaffected, and an omitted test is not proven unnecessary.
IntentAtlas makes the available structural evidence visible and abstains when that evidence is not
strong enough.

## What works today

- Scan Python, TypeScript/JavaScript, and Go repositories into a deterministic relationship graph.
- Connect files, symbols, imports, tests, Markdown documents, and Git commits.
- Generate a linked Obsidian vault with purpose-based folders and wikilinks.
- Explore the same graph in a local, dependency-free web viewer.
- Trace upstream and downstream impact from the command line.
- Import existing Cobertura coverage and JUnit test evidence without running project code.
- Produce a deterministic, versioned graph diff for CI.
- Import bounded issue and pull-request metadata from explicit local JSON snapshots.
- Link recent commits to exact modified symbols when zero-context diff hunks intersect validated
  Python AST spans or conservatively balanced JavaScript/TypeScript and Go declaration spans, and
  the worktree file matches that commit's blob, while retaining file-level history as a safe
  fallback.
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

## Beta status

The current source identifies itself as `0.3.0b1`. It has not been tagged or published to a package
index and is not yet a compatibility promise. The quick path above confirms the behavior of the
current checkout; release review additionally verifies the exact revision, reproducible artifacts,
provenance, hashes, installed wheel, and browser workflow. See [installation status](docs/installation.md)
and [the release process](RELEASING.md).

## Choose your first command

| Your situation | Use | Project writes | Network |
| --- | --- | --- | --- |
| You only want to see the idea | `intentatlas demo --report text` | None | None |
| You have an interactive terminal | `intentatlas guide PATH` | None | None for a local path |
| You are non-interactive or unsure which Git scope to use | `intentatlas diagnose PATH`, then its **Next safe command** (`intentatlas changes ...`) | None | None |
| You want a persistent project map | `intentatlas init PATH`, then `intentatlas scan PATH` | `intentatlas.json`, `.gitignore`, `.intentatlas/`, and `atlas/` | None |

Only an explicitly approved public GitHub URL may use the network and managed OS cache. Installing
the package may also contact the configured Python package index; local analysis itself is offline.

Then:

```powershell
intentatlas            # interactive terminal: the guided flow
```

In a non-interactive shell run `intentatlas diagnose PATH` and copy its exact **Next safe
command**. The default report opens with what changed and which tests to run; add `--explain` for
revisions, confidence bands and graph identifiers, or `--format json` for the stable schema.

## Documentation

| | |
| --- | --- |
| [Workflows](docs/workflows.md) | The guided flow, public GitHub analysis, the zero-footprint preview, and adopting the persistent vault |
| [Command reference](docs/commands.md) | Every command, including the maintainer and benchmark ones |
| [Capabilities in detail](docs/capabilities.md) | What each adapter and importer covers, and where it abstains |
| [Installation](docs/installation.md) | Supported versions and current installation status |
| [Architecture](docs/architecture.md) | Trust boundaries and how the layers fit together |
| [Documentation index](docs/index.md) | Everything else |

The project's own intent map lives in [`atlas/`](atlas/) — requirements, decisions, evidence and
reviews for each delivery phase, written with the tool itself. Generated areas are regenerated by
`intentatlas scan` and are not tracked.

## Inspiration

Obsidian's local Markdown graph, architecture decision records, and traceability practice from
safety-critical engineering — applied to everyday repositories, offline, without a hosted service.
