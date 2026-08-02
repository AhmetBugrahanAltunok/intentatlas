---
id: ADR-027
type: decision
status: proposed
phase: 11B
---
# ADR-027 - Freeze pilot evidence before recommendation tuning

## Context

Existing real-world evaluation is intentionally small and closed-world. It proves that the
production query can be measured, but it cannot justify a general accuracy claim. Tuning rules
against repeatedly inspected cases would also turn the benchmark into training data and conceal
the true false-positive/false-negative tradeoff.

Graph, report, adapter, evidence, and cache schemas now have users inside the repository but do not
yet share one explicit pre-`1.0` compatibility policy. Treating every current shape as permanently
stable would prevent necessary corrections; treating all output as disposable would prevent safe
adoption.

## Decision

Use immutable, license-reviewed, chronologically ordered pilot manifests. Record a committed
baseline before changing any production score, resolver, traversal, or threshold. Split cases into
explicit calibration and evaluation partitions; a case may move only through a separately reviewed
manifest revision and never retroactively improve an already reported result.

Aggregate the unchanged production recommendation path. Report per-project, per-language, per-
threshold, and overall counts together with recommendation coverage, abstention, analysis state,
freshness, and execution strategy. Add confidence intervals only as transparent statistical
context; they do not convert a reviewed sample into a population guarantee. Duration and savings
remain absent unless aligned execution evidence supplies them.

Classify public contracts as:

- `stable`: documented user-facing Markdown/frontmatter, supported CLI text/JSON, and versioned
  interchange schemas with migration/deprecation rules;
- `experimental`: explicitly labeled adapter or evidence capabilities that may evolve through a
  documented version boundary;
- `internal`: rebuildable cache and viewer implementation details that carry no compatibility
  promise.

Keep the entire evaluator offline. Repository acquisition, if approved, occurs outside normal
evaluation and leaves only immutable metadata, labels, license records, and expected observations
in reviewed project material. Do not persist third-party source or raw patches.

## Consequences

- Recommendation changes become slower but their effect is independently measurable.
- Small or undefined cohorts remain visible instead of being hidden by one aggregate percentage.
- A high precision number cannot conceal near-total abstention because coverage and strategy are
  reported beside it.
- Compatibility promises become deliberate and scoped before `1.0` rather than accidental.
- Label quality, licensing, and calendar time become explicit phase risks.
- Blocking CI remains out of scope until sustained evidence justifies a separate decision.

## Links

- Requirement: REQ-027 (available through the incoming `drives` relationship)
- tracked-by:: [[Issues/ISSUE-025 - Implement longitudinal pilot and compatibility baseline]]
- Prior evaluator: [[Decisions/ADR-011 - Closed-world recommendation evaluation]]
- Prior real-world policy: [[Decisions/ADR-015 - Separate public acquisition from offline evaluation]]
- Strategy: [[Brain/Phase 11B-13 Delivery Strategy]]
