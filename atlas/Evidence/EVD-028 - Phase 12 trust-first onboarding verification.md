---
id: EVD-028
type: evidence
status: complete
phase: 12
---
# EVD-028 - Phase 12 trust-first onboarding verification

The owner re-scoped Phase 12 on 2026-08-02 to technical onboarding readiness. External human
usability validation remains a Phase 11C prerequisite for public launch or any real user-time
claim; it is not inferred from the technical checks recorded here.

## Claim to verify

A maintainer-facing workflow provides an aligned, explainable real-repository result through a
deterministic no-write path, while text, JSON, and UI preserve the same trust, omission, and
fallback semantics. Technical task walkthroughs verify the available decisions without claiming
human usability or elapsed user time.

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
- [x] At least five distinct task-based synthetic/cognitive walkthroughs with exact commands and
      results for safe first action, aligned explanation, omission interpretation, stale-analysis
      fallback, and ambiguous or unsupported scope.
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
- Re-scoped technical-walkthrough commit:
  `e039183f369928e36e7eeeaaf4935ab76f716ec7`
  (`test: verify technical onboarding walkthroughs`).
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
- English/Turkish README entry points, `docs/index.md`, `docs/trust-first-preview.md`, the technical
  walkthrough guide, and the Phase 11C observation guide separate synthetic demo, no-write real-
  repository preview, persistent adoption, technical verification, and later human validation.
  The original artifacts are `docs/examples/trust-first-report.json` and
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

## Task-based synthetic/cognitive walkthrough results

Command `.venv\Scripts\python.exe -m pytest tests/test_onboarding_walkthroughs.py
tests/test_trust_first.py tests/test_diagnostic.py tests/test_change_report.py -q` reported
`16 passed`. The five named scenarios in `tests/test_onboarding_walkthroughs.py` verified:

1. an unconfigured checkout yields the deterministic safe next command without a write or network
   requirement;
2. an aligned symbol change exposes the selected requirement, test, exact recorded paths, and
   targeted strategy;
3. a below-threshold requirement remains visible as omitted and is never described as unaffected;
4. stale analysis abstains from recommendations and requires the full suite; and
5. multiple roots, unsupported Rust, and an oversized supported file remain explicit diagnostic
   limits without writes or network use.

These are automated synthetic/cognitive walkthroughs, not participant observations. No human
task-success result, elapsed user time, or median was produced.

## Commands and exact automated results

- Re-scoped focused command `.venv\Scripts\python.exe -m pytest tests/test_diagnostic.py
  tests/test_change_report.py tests/test_trust_first.py tests/test_onboarding_walkthroughs.py
  tests/test_viewer.py tests/test_browser_e2e.py tests/test_cli.py tests/test_e2e.py -q` reported
  `31 passed`, including the five named walkthroughs and real-browser gate.
- Complete command at identical tracked content with `INTENTATLAS_REQUIRE_BROWSER=1`:
  `.venv\Scripts\python.exe -m pytest --cov=intentatlas --cov-report=term-missing
  --cov-fail-under=80 -ra` reported `423 passed, 2 skipped` in 76.43 seconds and branch-aware
  coverage `86.45%`. The skips are Windows-unavailable symlink and FIFO cases; simulated coverage
  remains present.
- `.venv\Scripts\python.exe -m ruff check .`, `.venv\Scripts\python.exe -m mypy`,
  `.venv\Scripts\python.exe -m bandit -q -r src tools`, `node --check
  src/intentatlas/web/app.js`, `.venv\Scripts\python.exe -m pip check`, and `git diff --check`
  passed. Mypy checked 41 maintained source files.
- Fixed `SOURCE_DATE_EPOCH=1704067200` repeated builds were byte-identical. Provenance bound to
  `e039183f369928e36e7eeeaaf4935ab76f716ec7` records wheel SHA-256
  `f7d3b5c5d551a0d06396278ade657f874db251103e76594934223e0982782183` (48 files) and sdist
  SHA-256 `04db249ee0c1da99bba32873a394c45da0b33237d6b1bcad5759721221779e9d` (176 files).
  The fixed-epoch sdist rebuild matched the wheel; installed-wheel version, demo JSON, diagnostic
  JSON, real-repository report JSON, clean Git state, and extracted-sdist tests passed. During the
  re-scope rerun, the verifier correctly rejected the non-revision label `worktree`; it was rerun
  after commit with the exact 40-character revision above and wrote deterministic provenance.
- Approved `.venv\Scripts\python.exe -m pip_audit --skip-editable` returned `No known
  vulnerabilities found`.
- The final two-pass closure scan reported 1,333 nodes, 3,021 relationships, and 1,174 generated
  notes; all three adapter fragments were reused on pass two. Snapshots of 159 explicitly
  enumerated user-owned files and 1,175 generated files were byte/UTC-mtime identical across the
  second pass.
  Status reported zero durable orphans. Exact assertions passed for REQ-028 `drives` ADR-028,
  ADR-028 `tracked-by` ISSUE-026, ISSUE-026 `implemented-by` diagnostic code, EVD-028 `proves`
  REQ-028, and EVD-028 `proves` the no-write test. `atlas/Private/` was not enumerated or accessed.
- Fast-forward pushes succeeded. Re-scoped implementation GitHub Actions run `30754042429` at
  exact commit `e039183f369928e36e7eeeaaf4935ab76f716ec7` completed successfully with 13/13
  jobs, including Python 3.11/3.12/3.13 tests, six Windows/macOS/Linux installed-wheel E2E jobs,
  real Chrome, static types, security/network audit, and reproducible package/sdist.

## External validation boundary

Risk: **external human usability validation not yet performed**. No participant observation,
human task-success result, or elapsed user time is supplied or inferred here. Phase 11C must follow
`docs/first-run-observation-guide.md`, record at least five independent consented observations, and
demonstrate the required below-ten-minute median before public launch or any real user-time claim.
This open launch risk does not satisfy, replace, or block the re-scoped Phase 12 technical gate.

## Remaining risks and launch status

- External human usability and the below-ten-minute median remain unverified; the Phase 11C gate
  may require documentation or implementation changes when real observations reveal confusion.
- The diagnostic is bounded metadata/readiness evidence, not completeness; language adapters remain
  experimental, and fallback/unknown reports still require the displayed full-suite strategy.
- No telemetry, hosted dependency, account, model/API key, automatic user-note edit, tag, release,
  publication, deployment, or public-launch action was added or performed. Phase 13 has not begun.

## Stop conditions

Keep the phase open if preview writes state, any surface omits material trust information, the UI
changes ranking semantics, omission is presented as no impact, a listener/network action happens
without explicit user choice, fewer than five distinct technical walkthroughs pass, or a required
Phase 12 verification result is missing. Keep public launch and real user-time claims blocked until
the separate Phase 11C human-validation gate passes.

## Links

- proves:: [[Requirements/REQ-028 - Deliver trust-first first-run value]]
- recorded-in:: [[Commits/Commit 1db9847 - feat- add trust-first repository onboarding]]
- recorded-in:: [[Commits/Commit 5651c34 - test- verify viewer keyboard accessibility]]
- recorded-in:: [[Commits/Commit e039183 - test- verify technical onboarding walkthroughs]]
- implemented-by:: [[Code/src - intentatlas - diagnostic.py]]
- implemented-by:: [[Code/src - intentatlas - change_report.py]]
- implemented-by:: [[Code/src - intentatlas - cli.py]]
- implemented-by:: [[Code/src - intentatlas - web - app.js]]
- proves:: [[Tests/tests - test_diagnostic.py]]
- proves:: [[Tests/tests - test_trust_first.py]]
- proves:: [[Tests/tests - test_onboarding_walkthroughs.py]]
- proves:: [[Tests/tests - test_change_report.py]]
- proves:: [[Tests/tests - test_browser_e2e.py]]
- proves:: [[Tests/tests - test_viewer.py]]
- Decision: [[Decisions/ADR-028 - Make the change report the primary product surface]]
- Delivery issue: [[Issues/ISSUE-026 - Implement zero-footprint onboarding and trust-first reporting]]
- Review: [[Reviews/Phase 12 Trust-First Onboarding Review]]
- Strategy: [[Brain/Phase 11B-13 Delivery Strategy]]
