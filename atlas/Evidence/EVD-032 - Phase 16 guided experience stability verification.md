---
id: EVD-032
type: evidence
status: in-progress
phase: 16
---
# EVD-032 - Phase 16 guided experience stability verification

## Entry identity

- Expected and verified Phase 15 entry:
  `HEAD == main == origin/main == 5bb46ed42b79e1b35c364083af6a32cbe6e24dfb`.
- Phase 15 Review was `passed`, EVD-031 was `complete`, and GitHub Actions run `30771610757`
  passed all `13/13` jobs.
- The two modified and two untracked owner-observation records were preserved as supplied. They are
  owner first-use feedback, not Phase 11C human evidence.

## 16A controlled reproduction and fix

- Source: `https://github.com/pypa/sampleproject` at exact cached revision
  `621e4974ca25ce531773def586ba3ed8e736b3fc`; origin matched and no third-party source is committed.
- Before the fix, closing and reopening Change Report moved `main.x` and `stage.x` from `0/236` to
  `-372/-136` while the SVG transform remained unchanged. This isolated document focus scrolling,
  not accumulated graph fit math, as the cause.
- The report's close control received focus while the CSS transition still positioned it outside
  the viewport. The browser scrolled horizontally to reveal that control.
- The implementation retains focus semantics but uses `preventScroll` for report open/close focus
  transfer. Six real-browser sampleproject cycles then retained `scrollX=0`, `main.x=0`,
  `stage.x=236`, full-width right bounds, and the same settled graph transform.
- Automated real-Chrome coverage repeats five cycles at `1280x800` and `640x760`, checks mouse and
  keyboard behavior, and separately proves keyboard Fit Graph idempotence in graph-only mode.

## 16B terminal presentation

- The guided transcript now starts with `I N T E N T A T L A S` and explicit source/scope, safety,
  analysis, recommendation, Atlas, and next-action sections.
- Confirmation, acquisition, scope, and result actions are one option per line. Selected identity,
  confidence, reason, and evidence remain visible but are indented and wrapped after sanitization.
- English and Turkish retain equivalent trust meaning. Canonical enums, IDs, commands, flags,
  JSON, revision/scope/freshness/confidence/omission/strategy/advisory meaning, zero executed tests,
  one-Enter access, no-write, and non-TTY behavior are unchanged.

## Verification results

Final exact commands, counts, coverage, package provenance, network audit, vault determinism,
commit identities, pushed HEAD, and remote CI will be recorded after all closure gates pass.

## Remaining risks

- This is technical and owner-feedback verification, not independent human usability evidence.
  Phase 11C's five-person and median-time gate remains open.
- Terminal rendering remains deliberately line-oriented rather than a full-screen adaptive TUI.
- Initial graph force placement intentionally moves nodes until the bounded simulation settles;
  the regression distinguishes that motion from page or fitted-transform drift.

## Required evidence

- [x] Exact entry, owner-record preservation, pinned source/revision, reproduction metrics, root
      cause, and before/after real-browser measurements.
- [x] Wide/narrow, mouse/keyboard, report/report-free, fit-idempotence, bounded-large-graph, and
      accessibility focused regressions.
- [x] Structured EN/TR terminal, wrapping, option layout, one-Enter, hostile/plain/ASCII, no-write,
      non-TTY, semantic-parity, and immutable-snapshot focused regressions.
- [ ] Full pytest/coverage, Ruff, mypy, Bandit, Node syntax, pip-check/audit, diff-check, real Chrome,
      wheel/sdist/install/provenance, cross-platform E2E, deterministic vault, zero orphan, and
      approved network gates.
- [ ] Exact implementation/closure commits, generated Commit notes, push, final-HEAD remote CI,
      clean worktree, and synchronized `main == origin/main`.

## Typed links

- proves:: [[Requirements/REQ-032 - Keep guided analysis visually stable and readable]]
- references:: [[Decisions/ADR-032 - Prevent focus-driven viewport drift and structure terminal presentation]]
- references:: [[Issues/ISSUE-030 - Fix cumulative viewer layout drift after report and fit controls]]
- references:: [[Issues/ISSUE-031 - Improve guided PowerShell readability]]
- reviewed-by:: [[Reviews/Phase 16 Guided Experience Stability Review]]
- strategy:: [[Brain/Phase 16 Guided Experience Stability Strategy]]
