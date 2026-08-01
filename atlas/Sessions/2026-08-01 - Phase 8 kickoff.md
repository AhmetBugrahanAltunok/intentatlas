---
id: SESSION-2026-08-01-PHASE-8-KICKOFF
type: session
status: active
phase: 8
---
# 2026-08-01 — Phase 8 kickoff

Phase 8 begins from [[Brain/Phase 8-10 Strategy]] with two trust defects selected for the first
implementation slice:

1. A fresh external project currently receives IntentAtlas-specific sample intent records.
2. Same-file JavaScript/TypeScript and Go test relationships can be mistaken for exact evidence
   about an unrelated changed symbol.

The slice is tracked by [[Issues/ISSUE-018 - Implement trustworthy change intelligence]] and must
satisfy [[Requirements/REQ-020 - Explain revision-scoped change confidence]]. Phase 8 remains open;
an Evidence note and final Review will be created only after every acceptance item and completion
gate passes.

## First implementation slice

- Fresh `init` now creates only generic `Home.md`, empty purpose folders, Obsidian settings, and
  reusable templates. It does not seed this repository's own requirement, decision, evidence,
  review, or session records into another project.
- Generated dashboards no longer hard-code this repository's REQ-001/ADR-001/EVD-001 links.
- JavaScript/TypeScript and Go test-to-file edges cannot become default medium-confidence evidence
  for an unrelated symbol when exact evidence points to another symbol in that file.
- Go test evidence now retains exact symbol targets and separate file navigation edges.
- A bounded Go `calls`/`called-by` edge is emitted only for a unique lexical function/method target
  in the same package. Recommendations follow at most one exact caller hop to a directly linked
  test; ambiguous or transitive calls are not guessed.
- Graph schema 3 reads prior schema-1/schema-2 caches and rewrites them with relation schema 4.
- The original saved corpus was updated with exact Python symbol evidence that the production
  scanner already emits; historical phase evidence remains unchanged.

## Verification performed

- Focused regression command:
  `.venv/Scripts/python.exe -m pytest tests/test_graph.py tests/test_scanner.py tests/test_recommendations.py tests/test_corpus.py -q`
  — 49 passed.
- Complete branch-aware suite:
  `.venv/Scripts/python.exe -m pytest --cov=intentatlas --cov-branch --cov-report=term-missing --cov-fail-under=80`
  — 164 passed; total coverage 89.97%.
- `.venv/Scripts/python.exe -m ruff check .` — passed.
- `.venv/Scripts/python.exe -m bandit -q -r src` — passed.
- `.venv/Scripts/python.exe -m pip check` — no broken requirements.
- `node --check src/intentatlas/web/app.js` — passed.
- The complete suite includes installed CLI initialization, scan, status, impact, recommendation,
  and loopback viewer retrieval; the focused installed CLI/UI test also passed after the generic
  initialization change.
- Offline pinned real-world evaluation across six projects and 18 reviewed cases — low and medium
  TP 23, FP 0, FN 0; high TP 5, FP 0, FN 18. These bounded labels do not establish general
  accuracy.
- Original three-project corpus — low TP 4/FP 2/FN 0, medium TP 4/FP 1/FN 0, high TP 2/FP 0/FN 2.
  Medium precision improved from 66.67% to 80% while recall remained 100%.
- Two consecutive final local scans each produced 783 nodes, 1,782 relationships, and 680 generated
  notes. `intentatlas status .` reported zero durable orphans.
- `git diff --check` — passed.

## Remaining risks and phase status

- Go call evidence is deliberately lexical, same-package, unique-name, and one-hop. Interface
  dispatch, reflection, generated code, build tags, runtime configuration, and deeper calls remain
  unknown rather than inferred.
- The pinned benchmark contains only six commits and 18 labeled views; it is a regression gate,
  not a population accuracy claim.
- Revision-range/staged/worktree ChangeSet support, explicit analysis completeness and freshness,
  requirement-impact ranking, full-test fallback, broader adversarial holdouts, and the final
  Evidence/Review records remain open.
- No network, publication, push, tag, or deployment action was performed.

Decision: the first slice is accepted as an interim Phase 8 improvement. Phase 8 remains in
progress under [[Brain/Phase Completion Protocol]].

## Second implementation slice — unified ChangeSet

- Added deterministic ChangeSet schema 1 for commit, endpoint range, staged, and worktree scopes.
- Added `intentatlas changes` with text and JSON output. Revisions are validated and resolved to
  full commit IDs before diffing; a commit compares with its first parent and root commits use an
  explicit root path.
- Stored data is limited to file status, safe current/previous project-relative paths, and
  current-side hunk ranges. Raw patch lines are parsed but never retained in the result.
- Worktree mode combines tracked changes with ignored-aware untracked paths without reading or
  emitting untracked file contents.
- External diff drivers, text conversion, color, and submodule traversal are disabled. Revision,
  byte, file, hunk, path, and command-time bounds fail closed.
- Added parser, root-commit, commit, range, staged, worktree, invalid-revision, size-limit,
  determinism, CLI, and installed-flow regressions under [[tests - test_change_set.py|tests/test_change_set.py]],
  [[tests - test_cli.py|tests/test_cli.py]], and [[tests - test_e2e.py|tests/test_e2e.py]].

### Second-slice verification

- Focused ChangeSet/Git/CLI/graph suite — 28 passed.
- Complete branch-aware suite — 169 passed; total coverage 89.29%.
- Ruff, Bandit, `pip check`, and viewer JavaScript syntax checks — passed.
- A live `changes --worktree --format json` smoke check on this repository returned schema 1 with
  a resolved base commit and no raw contents. A separate boundary check found no
  `atlas/Private/` or root `.obsidian/` paths.
- Installed-flow coverage initializes a repository, invokes the JSON ChangeSet command, scans,
  checks health/impact/recommendations, and retrieves the loopback viewer.
- Offline pinned real-world recommendation regression remains TP 23, FP 0, FN 0 at low and medium
  confidence across six projects and 18 reviewed cases.
- Two consecutive final scans each produced 809 nodes, 1,814 relationships, and 706 generated
  notes; `intentatlas status .` reported zero durable orphans.
- No network, publication, push, tag, or deployment action was performed.

Decision: the ChangeSet slice is accepted. Explicit analysis completeness/freshness,
requirement-impact ranking, abstention/full-test fallback, and adversarial holdouts remain open, so
Phase 8 is still in progress.

## Third implementation slice — analysis completeness and freshness

- Added optional Change Analysis schema 1 through `intentatlas changes ... --analyze`.
- Every changed path now reports `analyzed`, `fallback`, or `unknown`; `aligned`, `stale`, or
  `unknown` freshness; `high`, `low`, or `none` confidence; artifact IDs; and ordered provenance.
- Analysis always builds a fresh, read-only worktree graph. Staged changes compare normalized
  worktree bytes with index blobs; commit/range changes compare with the resolved head tree. A
  mismatch becomes `unknown/stale` before any symbol inference.
- Exact analysis requires every current-side hunk to intersect validated symbol spans. Python AST
  spans can currently satisfy this; JavaScript/TypeScript, Go, configuration, binary, and other
  incomplete-span cases remain explicit file fallback rather than guessed symbols.
- Present but unsupported files are `fallback`; deleted, missing, unmerged, private, or stale
  artifacts are `unknown`. Durable vault notes map through frontmatter identity, while generated
  vault notes are classified as derived output rather than hundreds of false unknowns.
- The configured `Private/` directory is excluded at the Git pathspec boundary. A regression
  fixture verifies that a private file does not appear in ChangeSet or analysis output.
- Base ChangeSet collection still does not read untracked contents. Explicit analysis may read
  supported files through the normal bounded scanner but never executes or persists them.

### Third-slice verification

- Focused analysis, ChangeSet, and CLI regressions — 11 passed.
- Complete branch-aware suite — 171 passed; total coverage 88.46%.
- Ruff, Bandit, `pip check`, viewer JavaScript syntax, and `git diff --check` — passed.
- Live analysis of this repository classified all current changed paths as analyzed or explicit
  fallback, with no private/root-Obsidian boundary matches and no false `unknown` caused by derived
  vault output: 245 files, 246 hunks, 230 analyzed, and 15 fallback.
- Offline pinned real-world recommendation regression remains TP 23, FP 0, FN 0 at low and medium
  confidence across six projects and 18 reviewed cases.
- No network, publication, push, tag, or deployment action was performed.
- Two consecutive final scans each produced 828 nodes, 1,854 relationships, and 725 generated
  notes; `intentatlas status .` reported zero durable orphans.

Decision: the analysis-state/freshness slice is accepted. Requirement-impact ranking,
abstention/full-test fallback, adversarial holdouts, and final Evidence/Review remain open; Phase 8
is not complete.

## Fourth implementation slice — requirement impact and test policy

- Added Change Report schema 1 and `intentatlas changes ... --report` for a deterministic combined
  view of analysis state, possible requirement impacts, candidate tests, paths, evidence, and test
  execution strategy.
- Requirement traversal is bounded to durable intent relations. An exact changed symbol can reach
  the default medium threshold through `implemented-by`, `tracked-by`, and `drives`; a route that
  starts at a file or crosses `defines` is capped at low confidence.
- The same-file adversarial fixture proves that changing `login` can surface REQ-9 without
  promoting file-only REQ-18 to a default impact claim.
- Test selection reuses the existing recommendation query. A file fallback can still find bounded
  symbol-linked tests, but their score is capped and the report requires the full suite as well.
- `unknown` analysis abstains from requirement and test ranking and requires the full suite.
  A clean change set reports `no-changes`; all outputs remain advisory and bounded.
- Change analysis now retains the safe file artifact identity for aligned file fallbacks, allowing
  the report to explain useful low-confidence evidence without retaining raw source or diff text.
- README, Turkish README, architecture, ADR, issue links, and CLI help now describe the report and
  its uncertainty contract. CLI delivery is complete; viewer presentation and broader adversarial
  holdouts remain part of Phase 8.

### Fourth-slice verification

- Test-first focused report/analysis/CLI regressions — 9 passed.
- Complete branch-aware suite — 174 passed; total coverage 88.12%.
- Ruff, Bandit, `pip check`, viewer JavaScript syntax, installed CLI/UI E2E, and
  `git diff --check` — passed.
- The installed-flow check retrieved the local loopback viewer successfully; no browser, network,
  publication, push, tag, or deployment action was performed.
- Offline pinned real-world recommendation regression remains TP 23, FP 0, FN 0 at low and medium
  confidence across six projects and 18 reviewed cases. High remains TP 5, FP 0, FN 18.
- Live worktree report returned schema 1 with `fallback` and `targeted-plus-full-suite`: 272 changed
  paths, 17 requirement candidates, 3 default-threshold requirements, and 20 bounded displayed
  tests. It contained zero `atlas/Private/` and zero root `.obsidian/` paths.
- Two consecutive final scans each produced 852 nodes, 1,907 relationships, and 749 generated
  notes; `intentatlas status .` reported zero durable orphans.
- Changed-line attribution scan found no prohibited project-authorship statements.

Decision: the report-policy slice is accepted. UI presentation, adversarial holdouts, and the final
Evidence/Review closure remain open, so Phase 8 is not complete.

## Fifth implementation slice — UI, holdout, and phase closure

- Added `changes ... --report --open`. The viewer receives the exact fresh in-memory graph/report
  pair, exposes a dedicated report panel, and focuses selected requirement/test graph nodes.
- Added an installed subprocess/HTTP regression and a real-Git staged holdout with two unrelated
  requirements sharing `auth.py`. Only the exact `login` requirement crosses the default threshold.
- Real browser verification opened the report, selected REQ-020, reached the correct detail panel,
  and found no console errors. Visual review caught and corrected two report-only encoding defects.
- The first final Bandit run rejected a production `assert` in the new viewer path. Startup now
  validates and snapshots graph bytes explicitly; Bandit and the full suite pass after correction.
- Final complete suite — 175 passed; total branch-aware coverage 87.99%. Ruff, Bandit, `pip check`,
  JavaScript syntax, installed CLI/UI E2E, pinned public-project regression, and diff checks pass.
- Two deterministic closure scans each produced 863 nodes, 1,930 relationships, 758 generated
  notes, and zero durable orphans; graph bytes after timestamp normalization, generated-note
  content/times, and user-owned note content/times remained stable.
- Closure evidence: [[Evidence/EVD-020 - Phase 8 trustworthy change intelligence verification]].
- Closure review: [[Reviews/Phase 8 Trustworthy Change Intelligence Review]].

Decision: all REQ-020 acceptance criteria and the phase completion protocol pass. Phase 8 is
complete; remaining language-span, dynamic-analysis, intent-quality, and benchmark-size limits are
recorded rather than treated as solved.
