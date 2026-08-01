---
id: ISSUE-024
type: issue
status: in-progress
phase: 11A
---
# Implement the honest 0.3.0 release candidate demo

Deliver the canonical candidate version, adversarial same-file regression demo, deterministic terminal/JSON
report, installed-wheel verification, and documentation required by REQ-026.

## Acceptance checklist

- [x] Canonical `0.3.0rc1` version configuration and drift regression.
- [x] Same-file two-requirement/two-symbol/two-test demo graph.
- [x] Production-derived deterministic text and JSON demo report.
- [x] Default interactive demo parity through a same-snapshot Change Report, visible full advisory,
      and real-browser verification.
- [x] Canonical symbol identities, graph-derived changed-symbol selection, and explicit file
      fallback counterfactual regression.
- [x] Exact artifact-name, cross-platform archive-safety, positive source manifest,
      checkout-payload/dependency metadata, and source-archive test gates.
- [x] OIDC-free build/verification job separated from the protected publishing identity, with
      semantic workflow-policy regression checks.
- [x] English/Turkish onboarding, guided demo, changelog, and release documentation.
- [x] Focused/full local gates, reproducible working-tree artifacts, exact-wheel/sdist E2E, and
      real-browser verification.
- [ ] Exact committed provenance, deterministic vault closure, network audit, remote CI, final
      Evidence, and Review.

## Links

- implements:: [[Requirements/REQ-026 - Make the release candidate honest and immediately evaluable]]
- decided-by:: [[Decisions/ADR-026 - Separate scriptable demo evidence from interactive viewing and publication]]
- planned-evidence:: [[Evidence/EVD-026 - Phase 11A release candidate and demo verification]]
- kickoff:: [[Sessions/2026-08-01 - Phase 11A kickoff]]
