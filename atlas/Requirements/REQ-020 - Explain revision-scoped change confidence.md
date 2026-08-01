---
id: REQ-020
type: requirement
status: accepted
phase: 8
---
# Explain revision-scoped change confidence

For a commit, revision range, staged change, or worktree change, a developer can inspect which
requirements may be affected and which tests are candidates, together with the exact evidence,
scope, freshness, and known analysis gaps behind each result.

## Acceptance

- Fresh initialization creates generic project guidance and templates without seeding
  IntentAtlas-specific requirements, decisions, evidence, reviews, or dated sessions.
- Commit, range, staged, and worktree inputs share one bounded, deterministic change-set model.
- Exact symbol evidence is distinguishable from file fallback; an unrelated symbol in the same
  file does not create a medium- or high-confidence test claim.
- Results expose analysis completeness, provenance, revision scope, confidence, and freshness.
- Unsupported or incomplete analysis abstains or emits an explicit conservative fallback.
- Requirement-impact and test-recommendation output is deterministic and available to CLI and UI.
- Same-file multi-symbol and other adversarial holdout cases pass without weakening current
  public-project benchmark behavior.
- The full phase completion protocol is recorded before the phase is closed.

## Typed links

- drives:: [[Decisions/ADR-020 - Separate exact change evidence from fallback]]

## Trace

- Roadmap: [[Brain/Product Roadmap]]
- Strategy: [[Brain/Phase 8-10 Strategy]]
- Delivery: [[Issues/ISSUE-018 - Implement trustworthy change intelligence]]
