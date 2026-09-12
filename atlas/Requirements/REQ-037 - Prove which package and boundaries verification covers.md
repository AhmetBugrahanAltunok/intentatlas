---
id: REQ-037
type: requirement
status: accepted
phase: 21A
---
# Prove which package and boundaries verification covers

## User outcome

A maintainer can trust that a passing local or CI run describes the artifact they intended to
verify. A run against an installed distribution can never be mistaken for a run against the
working tree, and the declared `atlas/Private/` boundary has executable evidence rather than
documentation alone.

## Acceptance

- A session states which package identity it verifies. The default is the working tree.
- An imported package that contradicts the declaration fails the session before any test runs,
  with a message naming both paths and the exact command that corrects it.
- A declared installed distribution that resolves to the working tree fails the same way, so a
  packaging job cannot silently verify source it already had.
- An unknown declaration value is refused rather than treated as either mode.
- Every subprocess that runs the CLI imports the same package as its parent session, resolved
  from the imported module rather than an assumed repository layout, and works from any
  working directory.
- The CI job that deliberately installs a wheel declares that intent; every other job verifies
  the working tree.
- Changed `atlas/Private/` files remain `unknown` state, `unknown` freshness, and `none`
  confidence, carry no artifact identity, and contribute no file content to any rendered report.
- Generated vault areas are recognized as derived artifacts; durable notes resolve to their
  recorded identity; a deleted durable note abstains; a vault file outside every known area
  stays a capped fallback.
- Focused tests, full branch-coverage suite (minimum 80%), Ruff, mypy, and Bandit pass with the
  gate active.

## Links

- drives:: [[Decisions/ADR-039 - Declare and derive the verified package identity]]
- tracked-by:: [[Issues/ISSUE-037 - Add the package identity gate and vault boundary regressions]]
- proven-by:: [[Evidence/EVD-037 - Phase 21A verification integrity verification]]
- reviewed-by:: [[Reviews/Phase 21A Verification Integrity Review]]
- extends:: [[Requirements/REQ-036 - Require complete change coverage before targeted advice]]
- planned-in:: [[Brain/Alpha Release Execution Plan]]
