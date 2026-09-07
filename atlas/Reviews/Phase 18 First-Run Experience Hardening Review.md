---
id: review-phase-18-first-run-experience-hardening
type: review
status: passed
phase: 18
---
# Phase 18 First-Run Experience Hardening Review

## Change inventory

- Beginner documentation: simplified English/Turkish entry, original demo GIF, shortest install,
  product boundaries, real example and expected output, command-choice/freshness/cache guidance.
- Python evidence: unique markerless `src.` module resolution and exact file-to-symbol-to-test
  recommendation paths without weakening ambiguity abstention.
- First-run safety: repository-state-aware diagnostic scope, saved-graph exact-link health,
  deterministic `.gitignore` protection, explicit project identity, and actionable TTY, graph,
  baseline, evaluation, traversal, threshold, viewer, and `diff --check` output.
- Compatibility: additive diagnostic/recommendation fields, unchanged public schema versions, and
  native Windows/POSIX command quoting expectations.
- Verification: focused and complete regressions, lint, typing, security, package reproducibility,
  browser, three Python versions, and six operating-system E2E combinations.

## Acceptance review

- [x] All REQ-034 documentation and first-command criteria pass in English and Turkish.
- [x] The reported minimal `src.auth` defect is reproduced, corrected, and regression-covered.
- [x] Relevant exact evidence outranks unrelated co-change without changing canonical confidence
      bands or overstating missing evidence.
- [x] Diagnostic scope follows actual Git state and clearly separates readiness, saved graph health,
      and unassessed freshness.
- [x] Persistent local state is protected by deterministic, idempotent ignore rules after explicit
      initialization.
- [x] CLI failure and context messages give safe recovery steps without project execution or hidden
      network/write effects.
- [x] The five implementation commits and all accepted raw-report findings are retained in EVD-034.
- [x] Final local gates pass with 528 tests, Ruff, mypy, Bandit, and diff integrity.
- [x] Final exact pushed head `f407e496c6c0393e34921a17398666ee876cb41c` passes all 13 GitHub
      Actions jobs and the repository remains private.
- [x] No release, publication, deployment, telemetry, API key, hosted account, or Private access
      occurred.

## Decision

Pass. The complete first-run hardening series meets REQ-034. The observed semantic defect now has
exact bounded evidence, workflow blockers have actionable recovery, beginner documentation matches
the implemented trust boundaries, and all local plus remote quality gates pass at the final
implementation head. Phase 18 closes as private release-candidate hardening only; it does not
replace the independent human validation required before public launch.

## Links

- [[Requirements/REQ-034 - Harden the first-run experience from observed use]]
- [[Decisions/ADR-036 - Use repository-state-aware first-run guidance]]
- [[Issues/ISSUE-034 - Apply first-run observation fixes]]
- [[Evidence/EVD-034 - Phase 18 first-run experience hardening verification]]
- [[Requirements/REQ-028 - Deliver trust-first first-run value]]
- [[Requirements/REQ-033 - Preserve recommendation integrity across supported surfaces]]
