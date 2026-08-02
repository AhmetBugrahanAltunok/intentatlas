---
id: ISSUE-026
type: issue
status: open
phase: 12
---
# Implement zero-footprint onboarding and trust-first reporting

Make the aligned change report the first real-repository experience and preserve the complete trust
contract across CLI text, JSON, documentation, and the loopback viewer.

## Entry condition

- [ ] [[Reviews/Phase 11B Longitudinal Pilot and Compatibility Review]] records a final pass.
- [ ] The Phase 11B compatibility matrix identifies the report and diagnostic contracts that this
      phase may extend.

## Work packages

- [ ] Define the versioned read-only diagnostic model and deterministic text/JSON rendering.
- [ ] Report adapter support, unsupported/experimental capability, ambiguity, evidence freshness,
      and safe next actions without reading Private or writing project state.
- [ ] Add filesystem/Git snapshot regressions proving diagnostic and preview commands are no-write.
- [ ] Promote the existing change-report flow as the primary real-repository quick start; add an
      alias only if observation shows the existing command is the barrier.
- [ ] Expose revision/scope, analysis/freshness, threshold, candidate counts, evidence paths,
      selected/omitted reasons, and execution strategy consistently in text, JSON, and UI.
- [ ] Ensure UI drill-down uses recorded ranking paths and never substitutes an unrelated generic
      shortest path as the explanation.
- [ ] Preserve loopback, Host, header, escaping, keyboard, bounded-window, and no-network contracts.
- [ ] Rework English/Turkish README entry points, add a docs index, and separate synthetic demo,
      zero-footprint preview, and persistent adoption flows.
- [ ] Add one original example and deterministic trust-first report/screenshot artifact without
      copied third-party branding or assets.
- [ ] Record at least five independent first-run observations and resolve or explicitly accept every
      repeated source of confusion.
- [ ] Add exact Code and Test links after implementation artifacts exist.
- [ ] Run focused CLI/no-write/browser/accessibility/docs regressions and the complete local,
      package, deterministic-vault, approved network, and remote-CI closure gates.
- [ ] Complete EVD-028, bind it to the exact implementation commit, and obtain final Review.

## Non-goals

- No hosted UI, account, telemetry, model integration, or automatic user-note generation.
- No editor plugin, issue tracker, requirements editor, or drag-and-drop graph authoring.
- No change to recommendation scores unless separately driven by Phase 11B evidence.
- No public release, tag, or package publication without the conditional owner launch approval.

## Typed links

- implements:: [[Requirements/REQ-028 - Deliver trust-first first-run value]]
- decided-by:: [[Decisions/ADR-028 - Make the change report the primary product surface]]
- planned-evidence:: [[Evidence/EVD-028 - Phase 12 trust-first onboarding verification]]
- reviewed-by:: [[Reviews/Phase 12 Trust-First Onboarding Review]]

## Planning links

- Strategy: [[Brain/Phase 11B-13 Delivery Strategy]]
- Handoff: [[Sessions/2026-08-02 - Phase 11B-13 roadmap handoff]]
