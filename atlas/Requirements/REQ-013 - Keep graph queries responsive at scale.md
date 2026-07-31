---
id: REQ-013
type: requirement
status: accepted
phase: 6B2B2B1
---
# Keep graph queries responsive at scale

A maintainer can run repeated impact and test-recommendation queries on a large graph without each
local relationship lookup rescanning the complete edge collection.

## Acceptance

- `AtlasGraph` exposes one deterministic adjacency index for incoming and outgoing edges, with
  optional exact relation filtering.
- The index is built lazily, reused by repeated reads, and invalidated whenever a new edge enters
  the graph.
- Index construction is linear in edge count; local lookups inspect only the matching adjacency
  bucket and return stable edge order.
- Degree, orphan health, impact traversal, symbol/file projection, test lookup, and test-result
  lookup use the shared index where applicable.
- Existing impact and recommendation text/JSON, ordering, confidence, reasons, paths, observations,
  corpus metrics, graph serialization, and schema behavior remain unchanged.
- A bounded, offline synthetic benchmark measures cold graph/index construction and repeated warm
  impact/recommendation queries without executing project code or accessing the network.
- Benchmark inputs reject booleans and excessive edge/iteration counts, and output states that
  local timing is environment-specific.
- Focused equivalence, invalidation, scale, complete test, lint, security, CLI, package,
  determinism, and UI gates pass before the phase is complete.

## Scope boundary

This phase improves in-memory query complexity and adds a reproducible local scale probe. It does
not change ranking policy, persist an index, claim a universal latency guarantee, add public
repositories, or redesign the viewer. Those remain Phase 6B2B2B2 and Phase 7 work.

## Typed links

- drives:: [[Decisions/ADR-013 - Lazy deterministic adjacency index]]

## Trace

- Roadmap: [[Brain/Product Roadmap]]
- Planned evidence: [[Evidence/EVD-013 - Phase 6B2B2B1 indexed query verification]]
