---
id: review-phase-11b-longitudinal-pilot-compatibility
type: review
status: pass
phase: 11B
---
# Phase 11B Longitudinal Pilot and Compatibility Review

## Acceptance review

- [x] Phase 11A passed before Phase 11B implementation began.
- [x] REQ-027 is linked to ADR-027 and ISSUE-025.
- [x] The baseline and evaluation partitions were frozen before recommendation tuning.
- [x] Eight reviewed repositories and 64 chronological cases satisfy the declared Python,
      JavaScript/TypeScript, Go, and two-workspace cohort contract.
- [x] Per-project, per-language, per-threshold, workspace, partition, and overall reports include
      quality, coverage, abstention, freshness, strategy, cohort size, and Wilson 95% uncertainty
      without generalization claims.
- [x] Every FP/FN is classified and evaluation labels remain independent from the implementation.
- [x] Unknown/fallback cases preserve abstention/full-suite safeguards.
- [x] No unapproved network access, telemetry, third-party source persistence, or raw patch
      persistence was introduced.
- [x] Stable, experimental, and internal compatibility boundaries are documented and tested.
- [x] Focused/full local quality, package, installed CLI, deterministic-vault, and approved network
      gates pass.
- [x] Exact implementation provenance, generated Commit-note link, durable-chain assertions,
      fast-forward push, and full remote CI pass.
- [x] EVD-027 contains the complete inventory, exact commands/results, limitations, and risks.

## Evidence examined

- [[Evidence/EVD-027 - Phase 11B longitudinal pilot verification]]
- [[Requirements/REQ-027 - Establish longitudinal recommendation evidence]]
- [[Decisions/ADR-027 - Freeze pilot evidence before recommendation tuning]]
- [[Issues/ISSUE-025 - Implement longitudinal pilot and compatibility baseline]]
- [[Reviews/Phase 11A Release Candidate and Demo Review]]

## Final change inventory

- Strict offline longitudinal schemas, checkout/license/revision validation, frozen partition
  hashes, evaluation composition around the unchanged production recommendation path, deterministic
  text/JSON output, Wilson intervals, and cohort/error aggregation.
- Eight public, license-reviewed, immutable histories with 64 cases split evenly between calibration
  and evaluation, including three non-empty language cohorts and two workspace histories.
- Reviewed hashed classification of every observed false positive and false negative; explicit
  unknown duration/savings; preserved advisory abstention and full-suite safeguards.
- A pre-1.0 stable/experimental/internal compatibility matrix with migration/deprecation rules and
  tests binding every claimed contract.
- README and longitudinal pilot card, source-distribution metadata inclusion, exact release
  allow-list verification, CLI/package regressions, and generated Code/Symbol/Test/Commit/dashboard
  materialization.
- Exact unchanged-baseline commit `d84e54588d56f2b0ec2c3f1768c12de00c1d138e`, documentation
  commit `9557cb1824de3c8ba1b4a4a5c6a6282f885b7b7d`, and implementation/package head
  `9b54c0663e81027bbf1ac301fea4607817158eb6`.

## Exact verification and results

- Focused longitudinal/compatibility/CLI/release suite: `50 passed`.
- Browser-required complete source suite: `411 passed, 2 skipped`; coverage `86.36%`.
- Ruff, mypy over 40 maintained source files, Bandit over `src tools`, `pip check`, Node syntax,
  and `git diff --check` passed.
- Two commit-epoch builds passed exact release verification with 47 wheel and 166 sdist files.
  Wheel SHA-256 is `df1797f68ce397d0124566805d0766aacb5fcadf0411b95d1e9e2dada0c75d7e`;
  sdist SHA-256 is `f7a7eac1d6f3ba803b3ebe29f9996b3b9f8a515bed46cfea10ae3b57e8484a9e`.
  Fresh wheel installation, demo, longitudinal CLI, `pip check`, packaged benchmark presence, and
  extracted-sdist tests passed.
- Two unchanged corpus evaluations reproduced JSON hash
  `dd90bd22ceefba5321e1a0fb2a762adee15f8f943807718b1bcf0117923d3cdd` and text hash
  `0a0b9c530dcd57c9e6ca208e665c408da4d7376c0cc05c4463db8ccbf4aa887d` with zero
  classification gaps.
- `pip-audit 2.10.1` found no known third-party vulnerabilities; the unpublished local
  distribution was the only unavailable PyPI identity. GitHub's official Commit API returned the
  exact five configured Action SHAs with valid verified signatures.
- Two immediate closure scans reported 1,269 nodes, 2,926 relationships, 1,110 generated notes,
  zero second-pass adapter rebuilds, and zero durable orphans. Explicit snapshots of 159 user-owned
  and 1,111 generated files were byte/mtime stable, and the full exact-commit durable chain passed.
- Remote CI run `30749058555` for exact head
  `9b54c0663e81027bbf1ac301fea4607817158eb6` passed all 13 jobs, including security, typing,
  browser, reproducible package/sdist, three source-test, and six cross-platform wheel jobs.

## Remaining risks

- The selected 64-case pilot has wide uncertainty and is not a general accuracy estimate. Resolver
  ambiguity is visible at low/medium confidence; high confidence trades it for labeled misses.
- Historical stale/unknown analysis makes abstention and full-suite fallback necessary. The pilot
  does not supply aligned execution duration, savings, telemetry, or blocking-policy evidence.
- Click and itsdangerous remain excluded due duplicate Python adapter identities; `*.test-d.ts`
  declaration checks remain outside runtime-test labels. These limits are documented, not hidden.
- Public-launch controls, tags, releases, publication, deployment, visibility changes, and hosted
  attestations remain outside this review. `atlas/Private/` was not accessed.

## Review decision

Pass. REQ-027 is satisfied by the frozen unchanged baseline, untouched evaluation partition,
cohort-specific uncertainty-aware evidence, complete error classification, compatibility contract,
deterministic local/package/vault verification, approved network audit, fast-forward push, and
fully passing exact-head remote CI. Phase 11B is complete. No Phase 12 or Phase 13 implementation
was started, and this decision authorizes no tag, release, publication, deployment, or public
launch action.
