---
id: ISSUE-025
type: issue
status: in-progress
phase: 11B
---
# Implement longitudinal pilot and compatibility baseline

Deliver the frozen, independently reviewable pilot history and compatibility policy required by
REQ-027. Measure the unchanged production recommendation path before considering any refinement.

## Entry condition

- [x] [[Reviews/Phase 11A Release Candidate and Demo Review]] records a final pass.
- [x] The starting implementation revision and untouched evaluation manifest are recorded.

Phase 11B began from `b45ff0e93b8c53c7d9816dbbf14e92477ef74591` (commit timestamp
`2026-08-02T13:06:36+03:00`). Before any Phase 11B edit, the schema-1 real-world manifest SHA-256
was `9fe11998a2ae638da6b35b318205a5db3504011eff5c4d057bc496372fcfcd93`. Its six label-file
SHA-256 values, in manifest project order, were `8be415e5257798b3ff837cd684f6d457aa9a4d083914d4a904a63bf5186c9909`,
`265f46e60828e03cd3aa72b244d2c4b9895146893724742ca4412e97f7b0daa4`,
`3887db2cf5176e3b4167f3b98914d20cde0ed7740854a4c850e42e9174a3300c`,
`09e819876784a525c7de0e7b8e7dd64cbe89e6c006c3341ebf1380f04fe5c387`,
`f3fdfdebc469cfbe3fa59a2ca790ccb96becd8c92d71db3933b04d6278d8e664`, and
`bb4e4b75eb55303ae048747fd71651c198f1977d5746d5846643efbd8e99778e`.

## Work packages

- [x] Define strict versioned pilot, project, change-case, label, partition, and license metadata.
- [x] Preserve current Private/symlink/path/size/duplicate-key/revision-alignment boundaries.
- [x] Freeze and hash calibration/evaluation partitions before production recommendation changes.
- [x] Expand to at least eight repositories and sixty chronological cases with separate Python,
      JavaScript/TypeScript, Go, and workspace-shaped reporting.
- [x] Report TP/FP/FN, precision/recall, recommendation coverage, abstention, analysis/freshness,
      execution strategy, cohort size, and statistical uncertainty deterministically.
- [x] Keep savings/duration undefined unless aligned execution evidence supports the claim.
- [x] Add reviewed FP/FN classifications without storing raw source or patch content.
- [x] Publish the stable/experimental/internal compatibility matrix and migration/deprecation rules.
- [x] Commit the unchanged baseline before any optional recommendation refinement.
- [x] If a refinement is justified, evaluate it once against untouched evaluation data and retain
      the original baseline for comparison.
- [x] Update the deterministic terminal demo/README benchmark card with cohort size, limitations,
      known misses, and no-generalization wording.
- [x] Add exact Code and Test links after implementation artifacts exist.
- [ ] Run focused regressions and the full test, lint, type, security, package, CLI, deterministic-
      vault, approved network, and remote-CI closure gates.
- [ ] Complete EVD-027, bind it to the exact implementation commit, and obtain the final Review.

## Frozen baseline

- Calibration partition: 32 cases,
  `3a1a903f37ca7e2432007b0210494ea659c64fb3aa2d93f2490de92f09041320`.
- Evaluation partition: 32 cases,
  `edafea2e4225a271664c43b54e90b2987d4c1cf70f67e1ecc5a832d06efb72d5`.
- Manifest SHA-256:
  `391015effa9b3759cfbf6a8d94eb0c8d58a7c2e27bbd538d6e2377c741543731`.
- Two unchanged evaluations produced JSON SHA-256
  `dd90bd22ceefba5321e1a0fb2a762adee15f8f943807718b1bcf0117923d3cdd` and text SHA-256
  `0a0b9c530dcd57c9e6ca208e665c408da4d7376c0cc05c4463db8ccbf4aa887d`, with zero
  unclassified FP/FN observations.
- No production recommendation score, traversal, resolver, threshold, fallback, or full-suite
  behavior changed. The baseline did not justify an optional refinement.
- The unchanged baseline was committed as
  `d84e54588d56f2b0ec2c3f1768c12de00c1d138e` at `2026-08-02T14:42:45+03:00`. Because the
  reviewed baseline did not justify refinement, the conditional refinement package completed with
  no production change and the original evaluation partition remained untouched.

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
- implemented-by:: [[Code/src - intentatlas - longitudinal.py]]
- implemented-by:: [[Code/src - intentatlas - cli.py]]
- verified-by:: [[Tests/tests - test_longitudinal.py]]
- verified-by:: [[Tests/tests - test_compatibility_policy.py]]

## Planning links

- Strategy: [[Brain/Phase 11B-13 Delivery Strategy]]
- Handoff: [[Sessions/2026-08-02 - Phase 11B-13 roadmap handoff]]
