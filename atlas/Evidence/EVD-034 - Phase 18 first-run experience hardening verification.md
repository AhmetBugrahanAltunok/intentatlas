---
id: EVD-034
type: evidence
status: complete
phase: 18
---
# EVD-034 - Phase 18 first-run experience hardening verification

## Scope and provenance

This record covers every first-run change after the Phase 17 closure head
`3854f044828fb36c5e4fe9cf0ef0cfd19968711e` through final implementation head
`f407e496c6c0393e34921a17398666ee876cb41c`:

1. `310d9d58cb00e3dc7a60fc93c23b6f7fa9e87676` — improve first-run documentation and demo.
2. `a8ef7009dae445e9d1a40a7ad59d7613ae062f54` — fix first-run analysis and guidance.
3. `69366983bded8efe00585c56752af9fa6c15612d` — fix first-run workflow blockers.
4. `c83138c37a1a259399d1eed4b384522d2b4939f1` — improve first-run analysis guidance.
5. `f407e496c6c0393e34921a17398666ee876cb41c` — fix cross-platform diagnostic command tests.

Across the range, 35 files changed with 1,479 insertions and 168 deletions, including the original
`docs/assets/intentatlas-demo.gif`. The repository remained private. No tag, release, package
publication, deployment, telemetry, API key, hosted account, or `atlas/Private/` access occurred.

## Observation evidence

- A first-run environment reached the first meaningful result in 41 seconds; the complete README
  command walkthrough took 7 minutes 52 seconds. These are evaluator walkthrough measurements,
  not independent human usability evidence and not a public performance guarantee.
- Installation, demo, viewer, diagnose, impact, evaluation, corpus evaluation, and scale benchmark
  commands completed in the walkthrough.
- A minimal real project using
  `tests/test_auth_rotation.py -> from src.auth import rotate_session` failed to create the demo's
  exact symbol-to-test relationship. The relevant and unrelated tests therefore shared weak
  co-change ranking. This was reproduced as a product defect rather than treated as a documentation
  misunderstanding.
- Additional accepted findings were: `init` allowed generated state to be staged; project identity
  was unclear in impact/recommendation output; missing graph/baseline errors lacked recovery steps;
  `diff --check` exit 1 was unexplained; non-TTY refusal lacked an alternative; command choice,
  saved-artifact freshness, cache IDs, and analysis/report differences required clearer language.
- Three disposable raw first-run report Markdown files were removed after their accepted findings
  were consolidated here. They were never committed as durable project records.

## Implemented behavior

- English and Turkish onboarding now begin with a short demo, use the checked-in GIF, provide the
  shortest installation path, define what IntentAtlas is and is not, and show a real use case with
  expected output. Tables separate demo, local no-write preview, explicitly approved public
  acquisition, and persistent adoption.
- Markerless Python `src/` modules retain their conventional stripped identity and gain an explicit
  `src.` identity only under unique ownership. Direct symbols and bounded re-exports use the same
  identities. Ambiguous ownership/module/symbol resolution still abstains.
- File recommendations inspect symbols defined by the selected file and prefer their exact incoming
  `tests` edges. The reproduced relevant test ranks `80/medium` with an exact
  file-to-symbol-to-test path, while unrelated co-change evidence remains `60/low`.
- `diagnose` reports the resolved project; chooses worktree, staged, commit HEAD, or unborn
  worktree from bounded Git state; excludes generated/private paths from that choice; and reports
  exact Python symbol-test link health from a saved graph without claiming freshness or completeness.
- `init` appends only missing deterministic rules for `.intentatlas/`, `.venv-intentatlas/`, and
  Obsidian workspace/cache state. Existing ignore content and newline style are preserved.
- Impact and recommendation output identify the project. Missing graph/baseline errors explain the
  next command. `diff --check` explicitly identifies exit 1 as the expected change signal. The
  non-TTY guide error gives diagnostic and report alternatives.
- Confidence bands, threshold behavior, ranking reasons, traversal indentation, evaluation-label
  recovery, viewer startup flushing, UTF-8 BOM input, bounded oversized-file freshness, network,
  cache, scan/init, and artifact freshness semantics are clearer and regression-covered.

## Acceptance checks

- README opening, demo GIF, shortest install, product boundaries, real example, and command-choice
  criteria: passed in both English and Turkish documentation.
- Markerless `src.auth` exact link and file recommendation separation: passed scanner and
  recommendation regressions.
- Clean/staged/worktree/unborn diagnostic selection and saved-graph exact-link health: passed
  diagnostic regressions and a real dirty-repository JSON smoke; the smoke recommended
  `intentatlas changes D:\Projects\IntentAtlas --worktree --report`.
- Generated-state ignore protection, project display, missing-artifact recovery, TTY alternatives,
  and exit semantics: passed CLI, trust-first, guided, configuration, viewer, evaluation, and E2E
  regressions.
- Platform-native path quoting: the first pushed implementation CI correctly exposed two tests
  that forced Windows double quotes on Linux. Tests now validate `subprocess.list2cmdline` on
  Windows and `shlex.quote` on POSIX without changing the application behavior.

## Exact verification commands and results

- Focused final regression:
  `PYTHONPATH=src python -m pytest tests/test_diagnostic.py tests/test_trust_first.py -q`
  — `10 passed`.
- Complete final local suite:
  `PYTHONPATH=src python -m pytest -ra`
  — `528 passed, 4 skipped in 343.79s`. Skips were Windows-unavailable directory-link, symbolic-
  link, and FIFO capabilities.
- `python -m ruff check .` — passed.
- `python -m mypy` — passed with no issues in 48 source files.
- `python -m bandit -q -r src` — passed.
- `git diff --check` — passed.
- Initial pushed-head GitHub Actions run
  `https://github.com/AhmetBugrahanAltunok/intentatlas/actions/runs/31654734294` failed only because
  two test expectations used Windows quoting on Linux; static typing, security, browser, and all
  cross-platform E2E jobs that completed independently passed.
- Corrected final-head GitHub Actions run
  `https://github.com/AhmetBugrahanAltunok/intentatlas/actions/runs/31655672551` passed all 13 jobs:
  Python 3.11/3.12/3.13 test and coverage, six installed-wheel Windows/macOS/Linux E2E jobs,
  browser E2E, static typing, security with dependency audit, and reproducible package/pipx/
  extracted-sdist verification.
- Final synchronization check at implementation head: local `main` and `origin/main` were `0 0`,
  the worktree was clean, and GitHub reported repository visibility `PRIVATE`.

## Obsidian closure

- The first closure scan produced 1,779 nodes, 4,356 relationships, and 1,580 generated notes;
  two adapter partitions were reused and the changed Python partition was rebuilt.
- `intentatlas status` reported `durable orphans 0` with all 34 requirements, 36 decisions,
  34 issues, 34 evidence notes, and 34 reviews connected to the graph.
- Generated Commit notes now exist for all five covered commits: `310d9d5`, `a8ef700`, `6936698`,
  `c83138c`, and `f407e49`.
- A repeated scan reused all three adapter partitions and retained the same 1,779 nodes, 4,356
  relationships, and 1,580 generated notes. With the explicit `generated_at` field excluded, both
  structural graph hashes were
  `A29681D849FD844ED770529CDAF64245BB5B16A5FEC5C77134114A6EDB07AA87`.
- Generated Code, Symbols, Tests, Commits, and Dashboard note manifests were byte-identical across
  the repeated scan, SHA-256
  `CBBE0C9B485FF537480E253210747833504B65F2C8596DBF3CF6836495C62F7D`.

## Remaining risks

- The walkthrough measurements are not human usability evidence. Independent user testing remains
  required before any public ease-of-use or time-to-value claim.
- Exact symbol-to-test health observes the saved graph and does not prove graph freshness, complete
  test coverage, or support for dynamic import behavior.
- The markerless `src.` alias is deliberately bounded to unique ownership. Ambiguous monorepos or
  unsupported packaging semantics may abstain and reduce recall.
- `.gitignore` protection applies after explicit `init`; a user who creates generated state through
  other means before initialization must still manage repository hygiene.
- The repository is still an unpublished private release candidate; public launch and Phase 11C
  remain outside this phase.

## Links

- proves:: [[Requirements/REQ-034 - Harden the first-run experience from observed use]]
- references:: [[Decisions/ADR-036 - Use repository-state-aware first-run guidance]]
- delivered-by:: [[Issues/ISSUE-034 - Apply first-run observation fixes]]
- reviewed-by:: [[Reviews/Phase 18 First-Run Experience Hardening Review]]
- extends:: [[Evidence/EVD-028 - Phase 12 trust-first onboarding verification]]
- preserves:: [[Evidence/EVD-033 - Phase 17 recommendation integrity verification]]
