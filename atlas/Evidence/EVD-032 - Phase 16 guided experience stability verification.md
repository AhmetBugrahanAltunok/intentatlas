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

### Focused and complete behavior

- `INTENTATLAS_REQUIRE_BROWSER=1 python -m pytest tests/test_browser_e2e.py
  tests/test_guided_cli.py tests/test_onboarding_walkthroughs.py tests/test_source_to_atlas.py
  tests/test_viewer.py tests/test_compatibility_policy.py -q` passed. One Windows link-capability
  case remained an expected skip.
- `INTENTATLAS_REQUIRE_BROWSER=1 python -m pytest --cov=intentatlas --cov-report=term
  --cov-report=json:var/phase16-coverage.json --cov-fail-under=80` passed `500` tests with `4`
  platform-capability skips and `85.52%` branch coverage.
- The structured Turkish owner-style transcript against this repository retained no-write
  worktree analysis, exact base `5bb46ed...`, fallback/freshness/threshold/omission/strategy/
  advisory truth, `Tests executed: 0`, Atlas counts, and explicit action `4` under the new layout.

### Static, security, and package gates

- `python -m ruff check .`, strict `python -m mypy` (`46` source files),
  `python -m bandit -q -r src tools`, `node --check src/intentatlas/web/app.js`,
  `python -m pip check`, and `git diff --check` passed.
- Approved `python -m pip_audit --skip-editable` reported no known vulnerabilities; only the local
  editable IntentAtlas distribution was explicitly skipped.
- Implementation commit: `e3056809b957d0c2124a301a198fdcbda2dab990`; generated note
  [[Commits/Commit e305680 - Implement Phase 16 guided experience stability]].
- Two `SOURCE_DATE_EPOCH=1704067200 python -m build --sdist --wheel` runs were byte-identical.
  `tools/verify_release.py` validated wheel `52` files and sdist `189` files with exact source
  provenance:
  - wheel `intentatlas-0.3.0rc1-py3-none-any.whl`, SHA-256
    `5075e08eb339de3421f4babcca34fac73db6d6d98ae7cedaf4bf9789233d4153`;
  - sdist `intentatlas-0.3.0rc1.tar.gz`, SHA-256
    `7dc39187a2af1713706039297ae3635d51226d0d48a2fc7b690d4dc200cd5655`.
- `tools/verify_pipx_install.py` passed isolated install, command discovery, reinstall, and
  uninstall. The sdist rebuilt the exact wheel hash, its clean venv passed version and JSON demo
  smoke checks, and its extracted source suite passed with only platform/browser capability skips.

### Network and vault gates

- Approved inert `git ls-remote` resolved public source HEAD to the pinned
  `621e4974ca25ce531773def586ba3ed8e736b3fc`; cached origin and clean checkout matched. MIT
  `LICENSE.txt` SHA-256 remained
  `71e0bd649395f47e82b500dc6261ce4b8e8d03774727f583e09f5b947e75de97`.
- Final two scans each produced `1,647 nodes`, `3,578 relationships`, and `1,464` generated notes. The
  second reused all `3` adapter partitions and rebuilt none. All `183` files in the explicitly
  allowed user-owned folders retained identical bytes, sizes, and mtimes; all generated files were
  identical across the second pass. `intentatlas status` reported `durable orphans 0`.
- The public cache and all verification artifacts remain under ignored `var/`; no third-party
  source, graph, cache, license, package artifact, or coverage report is committed.

### Remote closure

Local verification head `c59eb36c788622e3e514377fb1ce9d4de185efbd` was pushed. GitHub Actions
run `30780041529` passed `12/13` jobs, including all three Python test matrices, six installed-wheel
cross-platform E2E jobs, real Chrome, static typing, and security. Its reproducible-package job
failed only in the extracted-sdist suite: the new browser regression used a fixed 4.5-second
force-layout wait, and a slower Linux runner retained a tiny intentional node movement
(`scale` delta about `0.00022`) before the exact transform assertion.

The test now waits boundedly for two stable node-transform samples instead of assuming wall-clock
speed. Page geometry, exact settled fit transform, interaction-count, and timeout assertions remain
unchanged. The real-Chrome test passed three consecutive local runs, then the complete suite passed
again at `500 passed, 4 skipped`, `85.52%`. A pushed rerun and final synchronized-HEAD CI remain the
only open evidence.

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
- [x] Full pytest/coverage, Ruff, mypy, Bandit, Node syntax, pip-check/audit, diff-check, real Chrome,
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
