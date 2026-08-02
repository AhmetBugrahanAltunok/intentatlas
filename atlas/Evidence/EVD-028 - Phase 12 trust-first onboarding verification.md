---
id: EVD-028
type: evidence
status: pending
phase: 12
---
# EVD-028 - Phase 12 trust-first onboarding verification

This is a verification plan, not evidence that Phase 12 has passed.

## Claim to verify

A new maintainer can obtain and correctly interpret an aligned, explainable real-repository result
within ten minutes through a deterministic no-write path, while text, JSON, and UI preserve the same
trust, omission, and fallback semantics.

## Required evidence

- [ ] Exact starting and implementation revisions and the Phase 11B compatibility baseline used.
- [ ] Diagnostic/report schema versions and complete change/documentation inventory.
- [ ] Before/after filesystem metadata and Git-state snapshots proving no-write behavior for every
      diagnostic and preview command, including missing-config and missing-vault repositories.
- [ ] Private/symlink/path/hostile-label/oversize/unsupported-language/ambiguous-root regressions.
- [ ] Golden text/JSON/UI comparison proving identical ordering, evidence, thresholds, paths,
      candidate counts, selected/omitted meaning, and execution strategy.
- [ ] Real Chrome-family keyboard/accessibility, Host/header/escaping, bounded-window, and report-
      navigation results.
- [ ] Exact synthetic-demo and real-repository onboarding commands from a clean installed wheel.
- [ ] English/Turkish documentation-command checks and hashes for deterministic example/report/
      screenshot inputs.
- [ ] At least five anonymized, consented first-run observations with timing method, median time,
      task success, confusion points, and resulting changes; no secrets or repository contents.
- [ ] Focused regression commands and exact results.
- [ ] Complete test, coverage, lint, type, security, package, installed-wheel, extracted-sdist, and
      documentation command results.
- [ ] Two-pass vault bytes/mtime check, user-owned snapshot, zero-orphan result, and explicit full
      durable-chain assertions.
- [ ] Approved network audit and complete remote CI results, or an explicit open gate.
- [ ] Exact generated Commit-note link, remaining risks, and public-launch status.

## Stop conditions

Keep the phase open if preview writes state, any surface omits material trust information, the UI
changes ranking semantics, omission is presented as no impact, a listener/network action happens
without explicit user choice, the median observation gate is unmet, or a required verification
result is missing.

## Links

- proves:: [[Requirements/REQ-028 - Deliver trust-first first-run value]]
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
