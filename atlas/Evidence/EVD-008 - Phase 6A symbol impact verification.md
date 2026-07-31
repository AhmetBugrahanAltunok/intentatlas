---
id: EVD-008
type: evidence
status: verified
phase: 6A
---
# EVD-008 — Phase 6A symbol impact verification

## Requirement and decision

- proves:: [[Requirements/REQ-008 - Trace symbol-level commit impact]]
- Decision: [[Decisions/ADR-008 - Conservative diff-to-symbol projection]]
- Delivery issue: [[Issues/ISSUE-006 - Implement symbol-level commit impact]]
- Review: [[Reviews/Phase 6A Symbol Impact Review]]

## Change inventory

- Python AST symbols now retain deterministic inclusive `line` and `end_line` spans, including
  decorators in the start boundary.
- The Git history adapter keeps complete path history and additionally reads zero-context patches
  for at most the newest 25 configured commits through fixed read-only Git commands.
- Patch collection disables external diff and text conversion, validates full commit identifiers,
  and rejects output above 10,000,000 bytes or 50,000 hunks.
- Patch parsing accepts only safe current-side project paths, bounded positive new-side ranges,
  and deterministic unique hunks. Deleted, quoted, malformed, or excessive input creates no
  symbol claim.
- Projection candidates come directly from the scanner's accepted symbol paths with trusted spans:
  Python in this phase. Excluded paths, including `atlas/Private/`, are never blob candidates. At
  most 1,000 commit/path candidates and 1,000,000 bytes per source are checked.
- A historical hunk is projected only when the current file equals that commit's raw Git blob
  after line-ending normalization. This prevents stale historical line numbers from being applied
  to a later file version.
- The scanner maps each accepted hunk to the smallest intersecting Python span. A changed method
  therefore does not directly mark its containing class or sibling method as modified.
- Existing `commit → changes → file` edges remain. Exact matches add
  `commit → modifies → symbol` with `git-diff-hunk` provenance.
- Relation schema 3 adds invertible `modifies`/`modified-by` history semantics. CLI, vault notes,
  the local viewer, and packaged installations consume the same rebuilt graph.
- README files, architecture, security, changelog, roadmap, requirement, ADR, and issue records
  document the conservative boundary.

## Focused regression verification

Command:

`python -m pytest tests/test_git_history.py tests/test_scanner.py tests/test_relations.py tests/test_graph.py -q`

Result: 23 passed.

The real-Git integration fixture contains two sibling methods in one Python class. Changing one
method maps only that method; changing the sibling in a later commit also proves that the earlier
commit's stale line numbers are not projected into the newer file. A JavaScript change retains its
file-level fallback. Parser tests cover deletions, unsafe quoted paths, malformed ranges, byte
limits, and filtering of languages without trusted spans.

## Complete quality suite

- `python -m pytest --cov=intentatlas --cov-report=term-missing --cov-report=json:var/phase6a-coverage-final.json -q`
  — 62 passed.
- Coverage — total 88.65%; `git_history.py` 82.56%; `scanner.py` 91.12%.
- `python -m ruff check .` — passed.
- `python -m bandit -q -r src` — passed.
- `python -m pip check` — no broken requirements.
- `node --check src/intentatlas/web/app.js` — passed.
- `git diff --check` — passed.

## CLI, vault, and determinism

Two consecutive accepted real-project scans each produced 439 nodes, 857 relationships, 396
generated notes, and 105 direct `modifies` edges. Graph diff reported `has_changes: false`.
SHA-256 comparison of the explicitly allowed user-owned Brain, Requirements, Decisions, Issues,
Evidence, Reviews, and Sessions areas was identical across both scans; `atlas/Private/` was not
enumerated or read. `intentatlas status` reported zero durable orphans.

`intentatlas impact commit:042c1dd1920fb9b76a35e544ba5161c90ea9bc6f --depth 1
--direction downstream` displayed complete file-level `changes` and 29 symbol-level `modifies`
records with the history category and `git-diff-hunk` provenance.

## Local viewer

The browser workflow verified both `modifies` and inverse `modified-by` presentation, symbol line
metadata, and an empty warning/error console. The final loopback-server check then served the
accepted 439-node/857-edge graph with 105 `modifies` edges: `/` and `/graph.json` both returned
HTTP 200 with the expected Content Security Policy. The temporary server was stopped afterward.

## Package verification

- `python -m pip wheel . --no-deps --no-build-isolation` produced
  `intentatlas-0.1.0-py3-none-any.whl`.
- SHA-256: `3E013441B8D00E30E1C0AEECF4D4B2A3BE7A998E93612238D22AE863AB4F642B`.
- `python -m pip install --no-index --no-deps --target <new-empty-directory> <wheel>` passed.
- The clean installed package reported zero durable orphans and exposed the same 29 `modifies`
  records for commit `042c1dd`.

An initial packaging verification command used an unsupported PowerShell selection parameter and
stopped after successfully building the wheel. It did not count as a product failure. The wheel
was subsequently installed into a newly generated, previously nonexistent target and verified.

## Corrections made during verification

- An early implementation projected old hunk line numbers directly into the current AST. Its
  271/270-edge scan results were rejected as evidence. Commit-blob equality was added and a later
  sibling-change regression test now protects this boundary.
- The first blob-alignment guard counted every changed Markdown and source path against a global
  1,000-pair budget, so this repository safely but incorrectly produced zero symbol edges. That
  intermediate result was also rejected. Candidate checks now include only scanned paths with
  trusted spans, and a regression test proves unsupported or excluded files cannot exhaust the
  symbol budget or trigger a worktree read.

## Remaining risks and boundaries

- Only Python currently exposes trusted spans. TypeScript/JavaScript and Go remain at file level.
- Pure deletions, module-level edits, ambiguous paths, merge representations without simple
  new-side hunks, stale historical file versions, and commits outside the newest 25 analysis
  window do not receive direct symbol claims.
- A `modifies` edge proves structural intersection, not business impact, requirement impact, or
  which test must run. Confidence-aware ranking and per-test execution evidence remain Phase 6B.
- Absence of `modifies` never proves that a symbol or requirement is unaffected.

## Decision

REQ-008 acceptance criteria are satisfied. Phase 6A passes with the documented conservative
fallbacks and may be closed.
