---
id: ADR-024
type: decision
status: accepted
phase: 10C
---
# ADR-024 — Validate adapters and render bounded graph windows

## Context

The built-in adapter protocol describes the required attributes and return type, while cache-load
validation currently enforces several output invariants only after a fragment has already been
produced and stored. A fresh non-incremental scan can therefore rely on convention rather than one
executable contract. Separately, the viewer creates SVG elements for every enabled node and edge
and performs repeated linear degree and relationship searches, which does not scale with repository
size.

## Decision

Define adapter conformance contract version 1 as a dependency-free module under
`intentatlas.adapters`. Each adapter declares a safe stable name, supported suffixes, complete cache
input suffixes, a positive cache version, and a bounded set of evidence labels. The shared validator
checks the adapter definition and every fragment before merge. A public conformance helper scans the
same immutable fixture context twice and requires identical canonical output. Cache loading reuses
the same fragment validator so clean and incremental paths accept the same semantics.

The contract permits only sorted unique symbol nodes owned by the scanner and sorted unique
`calls`, `defines`, `imports`, or `tests` edges whose endpoints exist in the discovered-file view or
fragment. Symbol identities and paths must agree, spans must be valid, declared evidence must match,
and structural endpoint shapes must be coherent. Invalid output fails closed with an adapter-scoped
error before it can affect the graph.

Keep the complete graph document in memory for local navigation, but render only deterministic
windows. The default overview ranks enabled nodes by intent/proof importance, connectivity, and
stable identity up to a fixed node/edge budget. Focusing a node produces a breadth-first bounded
neighborhood that always includes the target. Precomputed node, degree, edge, adjacency, and search
indexes serve layout, details, and global search without repeated whole-graph scans. Details and
search matches have explicit limits and omitted-result counts. This phase keeps SVG and avoids a
new browser dependency; canvas, workers, and server-side shards remain later options if measured
pilots exceed the bounded-window design.

## Consequences

- Adapter authors receive one runnable compatibility target instead of prose-only conventions.
- Fresh scans and cache reloads reject the same malformed fragment classes.
- Large graph interaction cost is bounded by the visible window rather than total graph size after
  initial JSON parsing and index construction.
- The overview is intentionally a ranked projection, not a claim that omitted nodes are absent.
- The browser still loads the complete graph JSON; extremely large graphs may later require a
  derived server-side or sharded index.

## Links

- Requirement: REQ-024 (available through the incoming `drives` relationship)
- tracked-by:: [[Issues/ISSUE-022 - Implement adapter conformance and bounded viewer windows]]
- Strategy: [[Brain/Phase 8-10 Strategy]]
