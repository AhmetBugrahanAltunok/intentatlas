---
id: ADR-011
type: decision
status: accepted
phase: 6B2B1
---
# ADR-011 — Closed-world recommendation evaluation

## Context

Precision cannot be calculated honestly from a list that contains only a few known-positive tests:
an unlisted recommendation might be irrelevant, or the human may simply have omitted it. Recall
has the same problem when the relevant set is incomplete. Before extending recommendation reach,
IntentAtlas needs a reproducible contract that makes the completeness assumption explicit.

## Decision

Accept only schema-1 JSON label documents with `label_policy: "complete-test-set"`. Each bounded
case has a stable ID, one exact graph target ID, and the complete project-relative set of tests a
reviewer judges relevant for that change. Empty relevant sets are allowed to measure unwanted
recommendations.

For a selected confidence threshold and output limit, run the unchanged production
`recommend_tests` query for every case. Compare returned test paths with the exhaustive expected
set:

- true positive: recommended and expected;
- false positive: recommended but not expected;
- false negative: expected but not recommended;
- precision: `TP / (TP + FP)` when at least one test was recommended, otherwise undefined;
- recall: `TP / (TP + FN)` when at least one test was expected, otherwise undefined.

Aggregate metrics are micro averages from summed counts, not an average of case percentages.
Undefined values serialize as JSON `null` and render as `n/a`. Output is schema 1, deterministic,
timestamp-free, bounded by 500 cases and 1,000 expected tests per case, and carries an explicit
generalization warning.

The first committed baseline uses two already accepted IntentAtlas commits. Labels are based on
manual behavioral review, not copied from the recommendation output. The benchmark is useful for
regression and threshold comparison but is too small and self-hosted to justify score tuning.

## Consequences

- Ranking changes can be compared quantitatively without executing project tests.
- The completeness assumption is visible and machine-checked.
- Stale labels fail loudly when graph identities change.
- Reliable generalization claims remain impossible until independent repositories and reviewers
  are added.

## Links

- Requirement: REQ-011 (available through the incoming `drives` relationship)
- tracked-by:: [[Issues/ISSUE-009 - Implement labeled recommendation evaluation]]
