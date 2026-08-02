---
id: review-phase-11a-release-candidate-demo
type: review
status: pending
phase: 11A
---
# Phase 11A Release Candidate and Demo Review

## Acceptance review

- [x] REQ-026 is linked to ADR-026 and ISSUE-024.
- [x] One canonical version source produces `0.3.0rc1` in source, installed runtime, wheel, sdist,
      and metadata.
- [x] The prebuilt demo demonstrates downstream exact-symbol selection without promoting
      same-file ambiguity or claiming end-to-end analysis accuracy.
- [x] Deterministic text/JSON reports and the interactive viewer use the same graph snapshot,
      selected test, evidence boundary, and complete visible advisory.
- [x] Documentation and changelog describe candidate installation, prebuilt-demo limits, explicit
      target paths, repository-only benchmarks, reconstruction, publication controls, and
      attribution accurately.
- [x] Focused/full source, coverage, lint, typing, Bandit, package, installed-wheel, sdist rebuild,
      CLI/UI, loopback-security, and required real-browser local gates pass.
- [x] Release verification binds exact wheel/sdist manifests, complete metadata, fixed hook-free
      build configuration, and runtime bytes to the reviewed checkout.
- [x] Publishing identity is isolated from source/build execution; semantic workflow tests bind
      the exact protected-main revision, three-file transfer, hash recheck, and three-step OIDC job.
- [x] Third-party dependency audit and official Action-SHA identity/signature checks pass.
- [x] Final vault materialization, zero-orphan health, user-owned-area preservation, and generated
      byte/mtime determinism pass.
- [x] Exact committed source revision, commit-epoch repeated builds, deterministic provenance,
      sdist-to-wheel equality, and clean candidate installation pass.
- [x] Git-history Private boundary, bounded Git output, Python ambiguous-module abstention,
      strict configuration, no-touch vault initialization, stable bounded input reads, focused and
      complete local regression, package/browser, and deterministic-vault gates pass.
- [ ] The follow-up is bound to an exact implementation commit, generated Commit-note link, and
      source-revision-bound deterministic provenance.
- [ ] Push and remote CI pass.
- [ ] Before the later public-launch phase, GitHub private vulnerability reporting and protected
      `pypi` environment controls are externally verified (not a Phase 11A closure gate).

## Evidence examined

- [[Evidence/EVD-026 - Phase 11A release candidate and demo verification]]
- [[Requirements/REQ-026 - Make the release candidate honest and immediately evaluable]]
- [[Decisions/ADR-025 - Layer offline verification before trusted publishing]]
- [[Decisions/ADR-026 - Separate scriptable demo evidence from interactive viewing and publication]]
- [[Issues/ISSUE-024 - Implement the honest 0.3.0 release candidate demo]]

## Review decision

Pending. The deep audit corrected material demo-evidence, artifact-integrity, metadata, build-hook,
publishing-identity, workflow-policy, local-viewer security, stale-artifact, documentation, and
environment-isolation problems. The follow-up local trust-boundary and resolution hardening passes
its complete local gates but is not yet commit-bound. Phase 11A remains open until exact
commit/provenance materialization, the authorized network audit, and push/remote CI pass. External
launch controls remain a later publication gate. No release or publication action is approved by
this review.
