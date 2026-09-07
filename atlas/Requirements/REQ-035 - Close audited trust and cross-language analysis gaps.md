---
id: REQ-035
type: requirement
status: accepted
phase: 19
---
# Close audited trust and cross-language analysis gaps

## User outcome

A maintainer can rely on bounded Change Report totals, secret-safe imported delivery context,
controlled Git diagnostics, complete-graph viewer paths, and conservative exact change analysis
across Python, JavaScript/TypeScript, and Go without treating uncertainty as proof.

## Acceptance

- Change Report counts the full bounded test-candidate population before its result limit and
  distinguishes complete counts from lower bounds when artifact or test-signal analysis truncates.
- Delivery source, repository, identifiers, titles, states, URLs, labels, and persisted report
  paths are redacted before graph or vault persistence; redaction collisions fail closed.
- Diagnostic and change-set Git processes terminate on timeout or byte overflow without retaining
  unbounded stdout, leaking a traceback, or leaving descendant processes behind.
- Staged deletion followed by same-path worktree recreation has deterministic staged/worktree
  semantics, and stale managed-cache locks can be recovered only after a safe age boundary and a
  non-live owner check.
- Viewer evidence paths come from the bounded complete-graph server snapshot, not only the rendered
  graph window; bounded path omissions are marked unknown rather than misreported as an exact count.
- Saved graph and viewer inputs have explicit byte, node, and edge ceilings.
- JavaScript/TypeScript and Go symbols publish an end line only for conservatively balanced
  declaration forms; ambiguous or malformed forms abstain and retain file fallback.
- Python overload sequences retain exactly one proven implementation while shadowed, conditional,
  overload-only, and duplicate definitions abstain.
- Focused regressions, complete tests with branch coverage, lint, typing, security, browser E2E,
  and diff integrity pass locally.
- No release, publication, deployment, network audit, or access to `atlas/Private/` occurs.

## Links

- drives:: [[Decisions/ADR-037 - Bound trust claims and abstain on uncertain structure]]
- delivered-by:: [[Issues/ISSUE-035 - Apply audited reliability fixes]]
- proved-by:: [[Evidence/EVD-035 - Phase 19 audited reliability verification]]
- reviewed-by:: [[Reviews/Phase 19 Audited Reliability Review]]
- preserves:: [[Requirements/REQ-033 - Preserve recommendation integrity across supported surfaces]]
- extends:: [[Requirements/REQ-034 - Harden the first-run experience from observed use]]
