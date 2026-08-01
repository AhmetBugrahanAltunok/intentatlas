---
id: ADR-014
type: decision
status: accepted
phase: 6B2B2B2A
---
# ADR-014 — Packaged first-party demo and bounded evidence paths

## Context

The normal first run requires initializing and scanning a repository before the local viewer can
show value. The viewer lists direct relationships, but a newcomer must mentally reconstruct how
intent connects to implementation and proof. External showcase repositories would add network,
license, attribution, maintenance, and reproducibility concerns before the product story itself is
clear.

## Decision

Build a compact first-party graph with the production `AtlasGraph`, `Node`, `Edge`, relation
catalog, serializer, and viewer. `intentatlas demo` writes that graph to a temporary directory,
serves it through the existing loopback-only viewer, and removes the temporary graph when the
viewer stops. It does not inspect or modify the current project.

In the viewer, compute evidence paths in the browser from the loaded graph. Use deterministic
breadth-first traversal in both relationship directions, bounded by maximum depth, visited nodes,
and returned results. Prefer proof-oriented destinations such as tests, evidence, coverage,
test-results, commits, and pull requests. Render every hop with its actual forward or inverse
relation and retain direct relationships as a separate section.

## Consequences

- A fresh installation has a one-command product tour with no repository setup or external data.
- The demo exercises production graph and viewer contracts instead of maintaining a separate mock
  interface.
- Evidence paths explain connectivity but do not prove causality, completeness, freshness, test
  necessity, or real-world accuracy.
- Client-side traversal remains bounded and deterministic; larger path analytics and server-side
  query APIs are deferred until real user demand justifies them.
- External fixtures and claims remain isolated in the next approval-gated phase.

## Links

- Requirement: REQ-014 (available through the incoming `drives` relationship)
- tracked-by:: [[Issues/ISSUE-012 - Implement guided demo and viewer evidence paths]]
