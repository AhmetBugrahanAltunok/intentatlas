---
id: EVD-035
type: evidence
status: verified
phase: 19
---
# EVD-035 - Phase 19 audited reliability verification

> Local Phase 19 verification passed on the final unchanged source tree. Release, publication,
> deployment, and networked audit remain separate approval-gated activities.

## Change inventory

- Change Report now aggregates the complete bounded recommendation candidate set, reports true
  high-fan-out totals, and exposes additive artifact/test-signal analysis coverage. Exceeding the
  analysis bound produces deterministic lower-bound output and a full-suite strategy.
- Delivery ingestion redacts every persisted external string, including exact
  `token`/`auth`/`authorization` keys, quoted JSON-shaped secret fields, and Bearer-style headers;
  redacted-ID collisions fail closed.
- Diagnostic, change-set, history, onboarding, and acquisition helpers collect subprocess output
  under byte/time bounds. Windows children start suspended, join a kill-on-close Job Object before
  executing, and then resume; timeout, overflow, setup failure, and inherited-pipe descendants are
  contained. Git acquisition also checks output and disk bounds after a fast process exit.
- Worktree merging handles staged deletion plus untracked recreation as a modification. Managed
  repository locks carry bounded owner metadata, refuse to reap a live local owner, and recover
  stale locks through an exact-target rename/retry flow.
- Viewer evidence paths use `/api/graph/paths` over the full immutable snapshot. Path traversal
  marks unknown omitted populations with `null` plus explicit truncation flags.
- Saved graphs are bounded to 256 MiB, one million nodes, and four million edges before model
  construction; viewer file-backed and in-memory graphs share the byte limit.
- Go and JavaScript/TypeScript adapters incremented their cache versions and emit `end_line` only
  for balanced declarations, including conservative TypeScript generic and conditional return-type
  handling. Python overload groups preserve only a proven unconditional implementation. Shared
  most-specific span selection covers scan and change analysis; malformed or ambiguous syntax
  remains spanless.
- Local viewer host validation accepts the equivalent `localhost`/`127.0.0.1` loopback forms while
  rejecting foreign Host values. `open` remains no-write and directs users to an explicit scan.

## Exact verification commands and results

- Final process/acquisition/change-set regression:
  `PYTHONPATH=src python -m pytest tests/test_bounded_process.py tests/test_acquisition.py tests/test_change_set.py -q --basetemp var/pytest-containment-final`
  — `50 passed, 1 skipped` (`51 collected`). The Windows Job setup-failure test also passed five
  consecutive isolated repetitions.
- Complete suite with branch coverage:
  `PYTHONPATH=src python -m pytest --basetemp var/pytest-p19-final-green --cov=src/intentatlas --cov-branch --cov-report=term-missing --cov-fail-under=80`
  — `570 passed, 4 skipped in 237.75s`; total branch coverage `86.44%`.
- Final browser/trust-first E2E:
  `PYTHONPATH=src python -m pytest tests/test_browser_e2e.py tests/test_trust_first.py -q --basetemp var/pytest-p19-ui-final`
  — `4 passed` using installed Google Chrome.
- `python -m ruff check . --no-cache` — passed.
- `python -m mypy --platform linux src` and `python -m mypy --platform win32 src` — both passed
  with no issues in 48 source files.
- `python -m bandit -q -r src tools` — passed.
- `python -m pip check` — no broken requirements.
- `git diff --check` — passed.
- `PYTHONPATH=src python -m intentatlas scan D:\Projects\IntentAtlas` — `1915 nodes`,
  `4415 relationships`, `3 rebuilt` adapter caches, and `1711` generated notes.
- `PYTHONPATH=src python -m intentatlas status D:\Projects\IntentAtlas` — 35 requirements,
  37 decisions, 35 issues, 35 evidence notes, 35 reviews, and `durable orphans 0`.

## Acceptance assessment

- High-fan-out 101-test repro: `101 candidate / 100 selected / 1 limit omitted` — passed.
- Artifact and test-signal truncation: explicit analyzed/candidate/omitted coverage and conservative
  strategy — passed.
- Delivery secret-shaped input: no raw secret remains in graph or synchronized vault output —
  passed.
- Diagnostic timeout/output overflow and Git acquisition fast-exit limits: complete process tree
  terminated, bounds enforced, and no traceback — passed.
- Staged delete/recreation and stale-lock recovery: focused real filesystem/Git regressions —
  passed.
- Cross-language spans and Python overloads: exact mappings pass for proven declarations;
  ambiguous, conditional, duplicate, and unclosed bodies abstain.
- Complete-graph viewer path: Chrome rendered the server-returned test path — passed.

## Remaining risks

- JavaScript/TypeScript and Go analyzers remain conservative structural parsers, not complete
  language parsers. Unsupported syntax reduces recall through explicit file fallback.
- Exact omitted path population remains unknowable under a bounded traversal; the API now reports
  this honestly as `null` rather than computing unbounded work.
- The additive Change Report coverage object may require allowlist updates in strict consumers.
- Networked dependency audit, remote multi-OS CI, package reproducibility, publication, and
  deployment were not part of this local implementation turn. Linux and Windows mypy semantics
  were both checked locally, but this does not replace the remote CI matrix.
- Existing Phase 18 durable closure notes and generated `atlas/` scan output were already untracked
  or modified before this phase; they were not rewritten here.

## Links

- proves:: [[Requirements/REQ-035 - Close audited trust and cross-language analysis gaps]]
- references:: [[Decisions/ADR-037 - Bound trust claims and abstain on uncertain structure]]
- delivered-by:: [[Issues/ISSUE-035 - Apply audited reliability fixes]]
- reviewed-by:: [[Reviews/Phase 19 Audited Reliability Review]]
