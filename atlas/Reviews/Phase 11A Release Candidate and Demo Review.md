---
id: review-phase-11a-release-candidate-demo
type: review
status: pending
phase: 11A
---
# Phase 11A Release Candidate and Demo Review

## Acceptance review

- [ ] REQ-026 is linked to ADR-026 and ISSUE-024.
- [ ] One canonical version source produces `0.3.0rc1` everywhere.
- [ ] The demo proves exact-symbol selection without promoting same-file ambiguity.
- [ ] Deterministic text/JSON reports and the default interactive viewer tell the same story.
- [ ] Documentation and changelog describe candidate installation and limitations accurately.
- [ ] Focused/full local, package, installed-wheel, CLI/UI, browser, provenance, determinism,
      dependency-audit, remote CI, and vault gates pass.

## Evidence examined

- [[Evidence/EVD-026 - Phase 11A release candidate and demo verification]]
- [[Requirements/REQ-026 - Make the release candidate honest and immediately evaluable]]
- [[Decisions/ADR-026 - Separate scriptable demo evidence from interactive viewing and publication]]
- [[Issues/ISSUE-024 - Implement the honest 0.3.0 release candidate demo]]

## Review decision

Pending. Phase 11A remains open until every acceptance item and the complete phase protocol pass.
