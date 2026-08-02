---
id: review-phase-11b-longitudinal-pilot-compatibility
type: review
status: pending
phase: 11B
---
# Phase 11B Longitudinal Pilot and Compatibility Review

## Acceptance review

- [ ] Phase 11A passed before Phase 11B implementation began.
- [ ] REQ-027 is linked to ADR-027 and ISSUE-025.
- [ ] The baseline and evaluation partitions were frozen before recommendation tuning.
- [ ] At least eight reviewed repositories and sixty chronological cases satisfy the declared
      Python, JavaScript/TypeScript, Go, and workspace cohort contract.
- [ ] Per-project, per-language, per-threshold, and overall reports include quality, coverage,
      abstention, freshness, strategy, cohort size, and uncertainty without generalization claims.
- [ ] Every FP/FN is classified and evaluation labels remain independent from the implementation.
- [ ] Unknown/fallback cases preserve abstention/full-suite safeguards.
- [ ] No unapproved network access, telemetry, third-party source persistence, or raw patch
      persistence was introduced.
- [ ] Stable, experimental, and internal compatibility boundaries are documented and tested.
- [ ] Focused/full local quality, package, CLI, deterministic-vault, and approved network gates pass.
- [ ] Exact implementation provenance, durable-chain assertions, push, and full remote CI pass.
- [ ] EVD-027 contains the complete inventory, exact commands/results, limitations, and risks.

## Evidence to examine

- [[Evidence/EVD-027 - Phase 11B longitudinal pilot verification]]
- [[Requirements/REQ-027 - Establish longitudinal recommendation evidence]]
- [[Decisions/ADR-027 - Freeze pilot evidence before recommendation tuning]]
- [[Issues/ISSUE-025 - Implement longitudinal pilot and compatibility baseline]]

## Review decision

Pending. Do not begin Phase 12 and do not convert advisory recommendations into blocking policy
until every acceptance item above passes.
