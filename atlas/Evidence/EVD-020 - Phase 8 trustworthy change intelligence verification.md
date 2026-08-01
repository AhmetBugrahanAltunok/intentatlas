---
id: EVD-020
type: evidence
status: verified
phase: 8
---
# EVD-020 — Phase 8 trustworthy change intelligence verification

## Requirement and decision

- proves:: [[Requirements/REQ-020 - Explain revision-scoped change confidence]]
- Decision: [[Decisions/ADR-020 - Separate exact change evidence from fallback]]
- Delivery issue: [[Issues/ISSUE-018 - Implement trustworthy change intelligence]]
- Review: [[Reviews/Phase 8 Trustworthy Change Intelligence Review]]

## Change inventory

- Fresh initialization now creates generic guidance, empty intent areas, Obsidian settings, and
  reusable templates without copying this repository's requirement, decision, evidence, review,
  or session records into another project.
- JavaScript/TypeScript and Go same-file relationships no longer become default exact-symbol test
  claims for unrelated declarations. Go retains exact test-to-symbol edges and follows only one
  unique lexical same-package caller hop.
- Graph schema 3 and relation schema 4 preserve read compatibility with prior supported caches.
- ChangeSet schema 1 normalizes commit, endpoint range, staged, and worktree inputs. It resolves
  revisions, stores bounded safe paths/status/current-side hunks, rejects unsafe or oversized
  input, disables external diff behavior, excludes `Private/`, and retains no raw patch text.
- Change Analysis schema 1 performs one fresh read-only scan and classifies every changed path as
  `analyzed`, `fallback`, or `unknown`, with freshness, confidence, artifact identity, and ordered
  provenance. Exact current-change mapping requires aligned blobs and complete validated spans.
- Change Report schema 1 ranks bounded requirement paths and advisory test targets. File-starting
  or file-crossing requirement evidence stays low confidence; fallback requires the full suite;
  any unknown artifact causes complete abstention.
- `intentatlas changes ... --report --open` serves the exact in-memory graph/report pair used by
  analysis. The optional viewer panel shows strategy, coverage, possible requirements, and tests,
  and focuses the corresponding graph node without persisting another report or graph.
- README, Turkish README, architecture, security, changelog, ADR, issue, session, roadmap, CLI help,
  tests, generated vault notes, and phase closure records reflect the same uncertainty contract.

## Acceptance and adversarial verification

- The staged real-Git holdout places REQ-9 and REQ-18 behind different symbols/file evidence in
  the same `auth.py`. Changing only `login` returns REQ-9 at the default threshold, retains REQ-18
  only as a low-confidence candidate, recommends the exact test, and selects targeted execution.
- Fallback fixtures can expose useful tests but always select targeted-plus-full-suite or
  full-suite-fallback. A mixed change with any `unknown` artifact returns no ranked claims and
  selects abstain-and-full-suite. A clean change set selects no-changes.
- Offline pinned evaluation of six license-reviewed public projects and 18 cases remains TP 23,
  FP 0, FN 0 at low and medium confidence. High remains TP 5, FP 0, FN 18. These results apply only
  to the reviewed pinned sample and do not establish general accuracy.
- Live worktree reporting excluded both `atlas/Private/` and the ignored root `.obsidian/` path.

## Final verification

- `.venv\Scripts\python.exe -m pytest tests\test_change_report.py -q` — 4 passed.
- `.venv\Scripts\python.exe -m pytest tests\test_viewer.py tests\test_e2e.py -q` — 6 passed.
- `.venv\Scripts\python.exe -m pytest --cov=intentatlas --cov-branch
  --cov-report=term-missing --cov-fail-under=80` — 175 passed; total coverage 87.99%.
- `.venv\Scripts\python.exe -m ruff check .` — passed.
- `.venv\Scripts\python.exe -m bandit -q -r src` — passed after replacing an initially detected
  production `assert` with startup-time graph validation and immutable served bytes.
- `.venv\Scripts\python.exe -m pip check` — no broken requirements.
- `node --check src/intentatlas/web/app.js` and `git diff --check` — passed.
- Installed CLI/UI E2E launched `changes --worktree --report --open`, retrieved both JSON endpoints,
  and validated schema/state/strategy. A real local browser then opened the report, selected
  REQ-020, focused the correct graph detail, and reported no console warnings or errors. Visual
  review exposed and corrected the report separator and close-icon encoding before final testing.
- No dependency declarations changed in Phase 8. The network-backed dependency audit was not
  rerun because networked audits require separate approval; `pip check`, Bandit, and the prior
  release audit remain recorded, but they are not represented as a new network result.
- Two final closure scans each produced 863 nodes, 1,930 relationships, and 758 generated notes;
  `intentatlas status .` reported zero durable orphans. The normalized graph SHA-256 was stable at
  `d983ffbbf261d6d28d201215a526038b95ded069ed80f8c3aa6fdc8327b4c512`; generated-note content plus
  modification-time fingerprint was stable at
  `5c13c84db188502265a470dbfd923442fe8a27afa52d54699e08184ebebf81fe`; explicit user-owned note
  content and modification times were unchanged across both scans.
- The final live worktree report classified 366 changed paths as explicit analyzed/fallback state,
  selected targeted-plus-full-suite, and contained zero `atlas/Private/` or root `.obsidian/`
  paths. The changed-line attribution scan returned zero prohibited authorship statements, and
  `git diff --check` passed.

## Remaining risks

- Exact current-change spans are presently available only from the Python AST adapter. JavaScript,
  TypeScript, Go, module-level edits, generated code, reflection, runtime configuration, native
  boundaries, and deleted or stale files can require fallback or abstention.
- Requirement ranking depends on explicit, correct vault links. Missing or stale human intent
  cannot be proven automatically.
- File fallback expands only a bounded set of defined symbols and never claims behavioral
  completeness. Full-suite advice can still be expensive.
- The public benchmark is a small regression gate. More diverse held-out repositories and
  per-language diff spans remain future work.

## Decision

REQ-020 acceptance criteria are satisfied. Phase 8 passes locally with exact/fallback/unknown
states preserved from Git input through CLI and UI, an adversarial same-file holdout, unchanged
pinned-project behavior, and explicit residual uncertainty.
