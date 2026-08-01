---
id: ADR-026
type: decision
status: accepted
phase: 11A
---
# ADR-026 — Separate scriptable demo evidence from interactive viewing and publication

## Context

Phase 10 satisfies the planned 0.3.0 technical gates, but the package still reports `0.1.0` and the
current single-path demo cannot demonstrate the product's conservative same-file behavior. The
viewer is effective for exploration but unsuitable for a terminal quick check because it starts a
listener and waits for interaction.

## Decision

Make `src/intentatlas/__init__.py` the canonical version source consumed by Hatchling and prepare
the non-published `0.3.0rc1` candidate. A candidate version is a review identity, not permission to
tag, publish, deploy, or change repository visibility.

Expand the first-party demo rather than importing an external showcase. Put two independently
linked requirement/symbol/test paths in the same synthetic source file and attach the example
commit to only one exact symbol. Use the production recommendation and graph traversal contracts to
derive a bounded report; do not hard-code a success claim that bypasses analysis.

Keep `intentatlas demo` as the interactive loopback viewer. Add explicit text and JSON report modes
that render the same graph, terminate immediately, contain a schema version and advisory boundary,
and describe an omitted same-file test as “not recommended from available evidence,” never
“unaffected” or “unnecessary.”

## Consequences

- The first-run story demonstrates the central false-positive problem instead of only a perfect
  linear chain.
- Contributors and CI can inspect a deterministic demo without browser automation or a listener.
- One version source removes manual drift between runtime and build metadata.
- The richer demo remains illustrative evidence and cannot establish real-world accuracy.
- Publication remains protected by ADR-019 and ADR-025 and requires separate explicit approval.

## Links

- Requirement: REQ-026 (available through the incoming `drives` relationship)
- tracked-by:: [[Issues/ISSUE-024 - Implement the honest 0.3.0 release candidate demo]]
