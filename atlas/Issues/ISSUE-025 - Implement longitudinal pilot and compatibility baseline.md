---
id: ISSUE-025
type: issue
status: open
phase: 11B
---
# Implement longitudinal pilot and compatibility baseline

Deliver the frozen, independently reviewable pilot history and compatibility policy required by
REQ-027. Measure the unchanged production recommendation path before considering any refinement.

## Entry condition

- [ ] [[Reviews/Phase 11A Release Candidate and Demo Review]] records a final pass.
- [ ] The starting implementation revision and untouched evaluation manifest are recorded.

## Work packages

- [ ] Define strict versioned pilot, project, change-case, label, partition, and license metadata.
- [ ] Preserve current Private/symlink/path/size/duplicate-key/revision-alignment boundaries.
- [ ] Freeze and hash calibration/evaluation partitions before production recommendation changes.
- [ ] Expand to at least eight repositories and sixty chronological cases with separate Python,
      JavaScript/TypeScript, Go, and workspace-shaped reporting.
- [ ] Report TP/FP/FN, precision/recall, recommendation coverage, abstention, analysis/freshness,
      execution strategy, cohort size, and statistical uncertainty deterministically.
- [ ] Keep savings/duration undefined unless aligned execution evidence supports the claim.
- [ ] Add reviewed FP/FN classifications without storing raw source or patch content.
- [ ] Publish the stable/experimental/internal compatibility matrix and migration/deprecation rules.
- [ ] Commit the unchanged baseline before any optional recommendation refinement.
- [ ] If a refinement is justified, evaluate it once against untouched evaluation data and retain
      the original baseline for comparison.
- [ ] Update the deterministic terminal demo/README benchmark card with cohort size, limitations,
      known misses, and no-generalization wording.
- [ ] Add exact Code and Test links after implementation artifacts exist.
- [ ] Run focused regressions and the full test, lint, type, security, package, CLI, deterministic-
      vault, approved network, and remote-CI closure gates.
- [ ] Complete EVD-027, bind it to the exact implementation commit, and obtain the final Review.

## Non-goals

- No CI blocking or automatic test execution.
- No new language adapter or compiler indexer.
- No telemetry, hosted account, or network requirement in the evaluator or CLI.
- No tuning on the evaluation partition and no general accuracy claim.

## Typed links

- implements:: [[Requirements/REQ-027 - Establish longitudinal recommendation evidence]]
- decided-by:: [[Decisions/ADR-027 - Freeze pilot evidence before recommendation tuning]]
- planned-evidence:: [[Evidence/EVD-027 - Phase 11B longitudinal pilot verification]]
- reviewed-by:: [[Reviews/Phase 11B Longitudinal Pilot and Compatibility Review]]

## Planning links

- Strategy: [[Brain/Phase 11B-13 Delivery Strategy]]
- Handoff: [[Sessions/2026-08-02 - Phase 11B-13 roadmap handoff]]
