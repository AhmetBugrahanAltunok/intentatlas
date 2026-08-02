---
id: review-phase-15-source-to-atlas
type: review
status: pending
phase: 15
---
# Phase 15 Source-to-Atlas Review

## Acceptance review

- [ ] Phase 14 passed at the exact clean entry revision.
- [ ] Exact-wheel isolated global command lifecycle passes without mutating real user installation.
- [ ] Local and strict public GitHub inputs reach the same production source-to-atlas contracts.
- [ ] Remote consent, URL, Git, authentication, execution, Private, redirect, and bounded-resource
      controls pass without weakening non-TTY or local-offline behavior.
- [ ] Managed cache identity, atomicity, locking, recovery, freshness, metadata, and safe cleanup pass.
- [ ] Terminal reports Atlas/layer/link/revision/scope/freshness/bounds truthfully and invents no
      intent; browser uses the same immutable graph/report snapshot.
- [ ] EN/TR, hostile/plain terminal, accessibility, Chrome, explicit CLI/JSON, and package contracts
      pass without a new runtime dependency or analysis engine.
- [ ] Focused/full/static/security/package/provenance/network/vault and final remote CI gates pass.
- [ ] EVD-031 contains exact commands/results/commits/smoke provenance/limits and zero open gates.
- [ ] No Phase 11C, human-time claim, tag, release, publication, installer publishing, deployment,
      telemetry, settings/visibility change, private auth, or announcement occurred.

## Decision

Pending. Pass is forbidden until every applicable item and EVD-031 gate is complete at a pushed
revision with fully successful remote CI.

## Links

- [[Evidence/EVD-031 - Phase 15 source-to-atlas verification]]
- [[Requirements/REQ-031 - Open a trustworthy atlas from a local path or public GitHub URL]]
- [[Decisions/ADR-031 - Acquire explicit public repositories into a managed local cache]]
- [[Issues/ISSUE-029 - Implement frictionless source-to-atlas onboarding]]
