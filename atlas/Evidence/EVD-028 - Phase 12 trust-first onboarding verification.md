---
id: EVD-028
type: evidence
status: in-progress
phase: 12
---
# EVD-028 - Phase 12 trust-first onboarding verification

This is a verification plan, not evidence that Phase 12 has passed.

Automated implementation and verification are complete. The required independent human first-run
observations have not been supplied, so this note does not claim Phase 12 pass.

## Claim to verify

A new maintainer can obtain and correctly interpret an aligned, explainable real-repository result
within ten minutes through a deterministic no-write path, while text, JSON, and UI preserve the same
trust, omission, and fallback semantics.

## Required evidence

- [x] Exact starting and implementation revisions and the Phase 11B compatibility baseline used.
- [x] Diagnostic/report schema versions and complete change/documentation inventory.
- [x] Before/after filesystem metadata and Git-state snapshots proving no-write behavior for every
      diagnostic and preview command, including missing-config and missing-vault repositories.
- [x] Private/symlink/path/hostile-label/oversize/unsupported-language/ambiguous-root regressions.
- [x] Golden text/JSON/UI comparison proving identical ordering, evidence, thresholds, paths,
      candidate counts, selected/omitted meaning, and execution strategy.
- [x] Real Chrome-family keyboard/accessibility, Host/header/escaping, bounded-window, and report-
      navigation results.
- [x] Exact synthetic-demo and real-repository onboarding commands from a clean installed wheel.
- [x] English/Turkish documentation-command checks and hashes for deterministic example/report/
      screenshot inputs.
- [ ] At least five anonymized, consented first-run observations with timing method, median time,
      task success, confusion points, and resulting changes; no secrets or repository contents.
- [x] Focused regression commands and exact results.
- [x] Complete test, coverage, lint, type, security, package, installed-wheel, extracted-sdist, and
      documentation command results.
- [x] Two-pass vault bytes/mtime check, user-owned snapshot, zero-orphan result, and explicit full
      durable-chain assertions.
- [x] Approved network audit and complete remote CI results, or an explicit open gate.
- [x] Exact generated Commit-note link, remaining risks, and public-launch status.

## Provenance and contract boundary

- Phase 12 started from clean, synchronized `main` revision
  `dd6d00b7b47c8f22778fac1502a786d0efed2550` at `2026-08-02T16:44:40+03:00`.
- Phase 11B Review was `pass`. Its compatibility matrix classified supported CLI text/JSON and
  ChangeSet/ChangeAnalysis/ChangeReport schema 1 as stable additive contracts.
- Production implementation commit:
  `1db98472a04b24aa6c05b8e8befb84f96a5f3c34` (`feat: add trust-first repository onboarding`).
- Real-browser keyboard/accessibility gate commit:
  `5651c34ab2f1d5755fe319a07313e7c7ba7c4063` (`test: verify viewer keyboard accessibility`).
- Diagnostic JSON starts at schema 1. Change Report remains schema 1 with additive scope,
  revision, freshness, selection-count, reason, evidence, recorded-path, and omission fields.
  Recommendation scores and production ordering rules did not change.

## Implementation and documentation inventory

- `src/intentatlas/diagnostic.py` defines bounded deterministic diagnostic text/JSON; `cli.py`
  exposes `diagnose` and keeps viewer startup behind explicit `--open`.
- `change_report.py` exposes the same immutable report snapshot's selection counts, reasons,
  evidence, paths, omissions, exact revision/scope/freshness, and fallback strategy without tuning
  scores. The loopback UI renders those recorded paths and keeps generic shortest paths confined
  to graph connectivity detail.
- The viewer report is the initial panel when the user explicitly opens the report viewer. It keeps
  IPv4 loopback binding, Host validation, security headers, escaping, bounded graph windows,
  keyboard activation, Escape close, focus transfer, and accessible dialog naming.
- English/Turkish README entry points, `docs/index.md`, `docs/trust-first-preview.md`, and the
  observation guide separate synthetic demo, no-write real-repository preview, and persistent
  adoption. The original artifacts are `docs/examples/trust-first-report.json` and
  `docs/assets/trust-first-preview.svg`.
- Focused tests cover diagnostic safety/capability, no-write CLI snapshots, cross-surface report
  semantics, documentation ordering/hashes, loopback policy, bounded rendering, and real Chrome
  keyboard/accessibility behavior. Generated Code/Symbol/Test/Commit/Dashboard notes were rebuilt.

## No-write, cross-surface, and browser results

- `tests/test_diagnostic.py` snapshots every non-Git directory/file path, type, byte size,
  nanosecond mtime, and SHA-256 before and after repeated missing-config/missing-vault diagnostics;
  Git porcelain state is unchanged. JSON is deterministic and reports `read_only=true`,
  `network_required=false`, capability/ambiguity/evidence state, and the safe next command.
- `tests/test_trust_first.py` runs diagnostic text/JSON and `changes --commit HEAD --report`
  text/JSON in a clean repository with no config or vault. Before/after file byte size,
  nanosecond mtime, SHA-256, HEAD, porcelain status, worktree diff, and cached diff are identical;
  no config, vault, cache, or graph appears.
- Private configuration is rejected without emitting or modifying the sentinel; symlink/path,
  hostile-label escaping, oversize, unsupported-language, ambiguous-root, Host/header, and bounded
  graph regressions pass in the focused/full suites.
- Change Report text/JSON tests assert the same threshold, selected/total/filtered/limit-omitted
  counts, score/confidence, evidence, exact recorded paths, reasons, strategy, and advisory. The
  Chrome DOM asserts those fields; the UI never calls generic path search for ranking cards.
- Real Chrome uses DevTools Protocol input events: the accessibility tree contains the named
  `dialog`, Escape closes it, Enter on the report toggle reopens it, and focus moves to the close
  button. Both the 320-node bounded window and same-file report scenarios pass.

## Commands and exact automated results

- Focused trust-first command:
  `.venv\Scripts\python.exe -m pytest tests/test_diagnostic.py tests/test_change_report.py
  tests/test_trust_first.py tests/test_viewer.py tests/test_browser_e2e.py tests/test_cli.py
  tests/test_e2e.py -q` passed after the documented compatibility-count correction. The final
  browser/viewer/trust subset reported `9 passed`.
- Exact-HEAD complete command with `INTENTATLAS_REQUIRE_BROWSER=1`:
  `.venv\Scripts\python.exe -m pytest --cov=intentatlas --cov-report=term-missing
  --cov-fail-under=80 -ra` reported `418 passed, 2 skipped` in 102.53 seconds and branch-aware
  coverage `86.38%`. The skips are Windows-unavailable symlink and FIFO cases; simulated coverage
  remains present.
- `.venv\Scripts\python.exe -m ruff check .`, `.venv\Scripts\python.exe -m mypy`,
  `.venv\Scripts\python.exe -m bandit -q -r src tools`, `node --check
  src/intentatlas/web/app.js`, `.venv\Scripts\python.exe -m pip check`, and `git diff --check`
  passed. Mypy checked 41 maintained source files.
- Fixed `SOURCE_DATE_EPOCH=1704067200` repeated builds were byte-identical. Provenance bound to
  `5651c34ab2f1d5755fe319a07313e7c7ba7c4063` records wheel SHA-256
  `f7d3b5c5d551a0d06396278ade657f874db251103e76594934223e0982782183` (48 files) and sdist
  SHA-256 `4055e6f134455f92638cba7f59a27c6c60c079fe0ce196483b3a5f2bf73ae8c2` (174 files).
  The fixed-epoch sdist rebuild matched the wheel; installed-wheel version, demo JSON, diagnostic
  JSON, real-repository report JSON, clean Git state, and extracted-sdist tests passed. An initial
  sdist-wheel comparison without the fixed epoch correctly differed and was rerun with the required
  epoch rather than recorded as pass.
- Approved `.venv\Scripts\python.exe -m pip_audit --skip-editable` returned `No known
  vulnerabilities found`.
- Two exact-head scans reported 1,324 nodes, 3,025 relationships, and 1,165 generated notes; all
  three adapter fragments were reused on pass two. Snapshots of 159 explicitly enumerated
  user-owned files and 1,166 generated files were byte/UTC-mtime identical across the second pass.
  Status reported zero durable orphans. Exact assertions passed for REQ-028 `drives` ADR-028,
  ADR-028 `tracked-by` ISSUE-026, ISSUE-026 `implemented-by` diagnostic code, EVD-028 `proves`
  REQ-028, and EVD-028 `proves` the no-write test. `atlas/Private/` was not enumerated or accessed.
- Fast-forward pushes succeeded. Exact-head GitHub Actions run `30752781634` completed successfully
  with 13/13 jobs, including Python 3.11/3.12/3.13 tests, six Windows/macOS/Linux installed-wheel
  E2E jobs, real Chrome, static types, security/network audit, and reproducible package/sdist.

## Human observation gate

No participant observation has been supplied or inferred. Count: `0/5`; median time: not
calculated; task-success and recurring-confusion results: unavailable. Follow
`docs/first-run-observation-guide.md` and retain consent, anonymized elapsed times, failed steps,
interpretations, and confusion. Phase 12 remains open until this evidence is real and reviewed.

## Remaining risks and launch status

- Independent first-run usability and the below-ten-minute median are unverified. Documentation or
  implementation may still change when observations reveal repeated confusion.
- The diagnostic is bounded metadata/readiness evidence, not completeness; language adapters remain
  experimental, and fallback/unknown reports still require the displayed full-suite strategy.
- No telemetry, hosted dependency, account, model/API key, automatic user-note edit, tag, release,
  publication, deployment, or public-launch action was added or performed. Phase 13 has not begun.

## Stop conditions

Keep the phase open if preview writes state, any surface omits material trust information, the UI
changes ranking semantics, omission is presented as no impact, a listener/network action happens
without explicit user choice, the median observation gate is unmet, or a required verification
result is missing.

## Links

- proves:: [[Requirements/REQ-028 - Deliver trust-first first-run value]]
- recorded-in:: [[Commits/Commit 1db9847 - feat- add trust-first repository onboarding]]
- recorded-in:: [[Commits/Commit 5651c34 - test- verify viewer keyboard accessibility]]
- implemented-by:: [[Code/src - intentatlas - diagnostic.py]]
- implemented-by:: [[Code/src - intentatlas - change_report.py]]
- implemented-by:: [[Code/src - intentatlas - cli.py]]
- implemented-by:: [[Code/src - intentatlas - web - app.js]]
- proves:: [[Tests/tests - test_diagnostic.py]]
- proves:: [[Tests/tests - test_trust_first.py]]
- proves:: [[Tests/tests - test_change_report.py]]
- proves:: [[Tests/tests - test_browser_e2e.py]]
- proves:: [[Tests/tests - test_viewer.py]]
- Decision: [[Decisions/ADR-028 - Make the change report the primary product surface]]
- Delivery issue: [[Issues/ISSUE-026 - Implement zero-footprint onboarding and trust-first reporting]]
- Review: [[Reviews/Phase 12 Trust-First Onboarding Review]]
- Strategy: [[Brain/Phase 11B-13 Delivery Strategy]]
