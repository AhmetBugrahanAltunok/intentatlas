---
id: ISSUE-026
type: issue
status: in-progress
phase: 12
---
# Implement zero-footprint onboarding and trust-first reporting

Make the aligned change report the first real-repository experience and preserve the complete trust
contract across CLI text, JSON, documentation, and the loopback viewer.

## Entry condition

- [x] [[Reviews/Phase 11B Longitudinal Pilot and Compatibility Review]] records a final pass.
- [x] The Phase 11B compatibility matrix identifies the report and diagnostic contracts that this
      phase may extend.

Phase 12 began from exact revision `dd6d00b7b47c8f22778fac1502a786d0efed2550` at
`2026-08-02T16:44:40+03:00`. Phase 11B Review was already `pass`, `main` matched `origin/main`,
and the worktree was clean. The Phase 11B compatibility matrix classifies versioned CLI text/JSON
and change-set/change-analysis/change-report output as stable additive contracts; the new
diagnostic starts at schema version 1 and will be added to that stable boundary.

## Work packages

- [x] Define the versioned read-only diagnostic model and deterministic text/JSON rendering.
- [x] Report adapter support, unsupported/experimental capability, ambiguity, evidence freshness,
      and safe next actions without reading Private or writing project state.
- [x] Add filesystem/Git snapshot regressions proving diagnostic and preview commands are no-write.
- [x] Promote the existing change-report flow as the primary real-repository quick start; add an
      alias only if observation shows the existing command is the barrier.
- [x] Expose revision/scope, analysis/freshness, threshold, candidate counts, evidence paths,
      selected/omitted reasons, and execution strategy consistently in text, JSON, and UI.
- [x] Ensure UI drill-down uses recorded ranking paths and never substitutes an unrelated generic
      shortest path as the explanation.
- [x] Preserve loopback, Host, header, escaping, keyboard, bounded-window, and no-network contracts.
- [x] Rework English/Turkish README entry points, add a docs index, and separate synthetic demo,
      zero-footprint preview, and persistent adoption flows.
- [x] Add one original example and deterministic trust-first report/screenshot artifact without
      copied third-party branding or assets.
- [x] Execute at least five distinct task-based synthetic/cognitive walkthroughs for safe first
      action, aligned explanation, omission interpretation, stale-analysis fallback, and ambiguous
      or unsupported scope; retain exact commands/results without presenting them as human studies.
- [x] Add exact Code and Test links after implementation artifacts exist.
- [ ] Run focused CLI/no-write/browser/accessibility/docs regressions and the complete local,
      package, deterministic-vault, approved network, and remote-CI closure gates.
- [ ] Complete EVD-028, bind it to the exact implementation commit, and obtain final Review.

## Non-goals

- No hosted UI, account, telemetry, model integration, or automatic user-note generation.
- No editor plugin, issue tracker, requirements editor, or drag-and-drop graph authoring.
- No change to recommendation scores unless separately driven by Phase 11B evidence.
- No public release, tag, or package publication without the conditional owner launch approval.

## Owner scope amendment

On 2026-08-02 the owner moved five independent human observations and the below-ten-minute median
from Phase 12 closure to Phase 11C. Phase 12 now establishes technical onboarding readiness; the
deferred observations remain mandatory before public launch or any real user-time claim.

## Typed links

- implements:: [[Requirements/REQ-028 - Deliver trust-first first-run value]]
- decided-by:: [[Decisions/ADR-028 - Make the change report the primary product surface]]
- implemented-by:: [[Code/src - intentatlas - diagnostic.py]]
- implemented-by:: [[Code/src - intentatlas - change_report.py]]
- implemented-by:: [[Code/src - intentatlas - cli.py]]
- implemented-by:: [[Code/src - intentatlas - web - app.js]]
- verified-by:: [[Tests/tests - test_diagnostic.py]]
- verified-by:: [[Tests/tests - test_trust_first.py]]
- verified-by:: [[Tests/tests - test_onboarding_walkthroughs.py]]
- verified-by:: [[Tests/tests - test_change_report.py]]
- verified-by:: [[Tests/tests - test_browser_e2e.py]]
- verified-by:: [[Tests/tests - test_viewer.py]]
- planned-evidence:: [[Evidence/EVD-028 - Phase 12 trust-first onboarding verification]]
- reviewed-by:: [[Reviews/Phase 12 Trust-First Onboarding Review]]

## Planning links

- Strategy: [[Brain/Phase 11B-13 Delivery Strategy]]
- Handoff: [[Sessions/2026-08-02 - Phase 11B-13 roadmap handoff]]
