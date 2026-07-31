---
id: ADR-013
type: decision
status: accepted
phase: 6B2B2B1
---
# ADR-013 — Lazy deterministic adjacency index

## Context

`AtlasGraph.impact` previously filtered the complete sorted edge list for every visited node.
Test recommendation also rescanned all edges when discovering commit changes, symbol ownership,
tests, and observations. Input bounds prevented runaway output, but repeated queries still scaled
with unrelated repository relationships.

## Decision

Build one immutable-view `GraphIndex` lazily from the graph's canonical sorted edges. Store
incoming and outgoing buckets both by node and by `(node, relation)`. Bucket tuples preserve
canonical edge order. `AtlasGraph.index` reuses the same index until a new valid edge is added;
edge insertion invalidates it. Node-only changes do not invalidate edge adjacency.

Use this shared index for degree/orphan checks, breadth-first impact traversal, commit artifact
signals, file-to-symbol evidence, file-to-test evidence, and test-result observations. Preserve the
existing final candidate sort and visited-node behavior so output is byte-compatible for unchanged
graphs.

Add a bounded synthetic benchmark command. It constructs one relevant commit/file/test chain plus
configurable unrelated relationships, measures cold graph/index construction and repeated warm
impact/recommendation queries, and reports deterministic graph/result counts alongside explicitly
environment-specific timings. It executes no project code and reads no repository files.

## Consequences

- Index construction remains O(E), while an adjacency lookup becomes O(local degree) instead of
  O(E).
- Repeated queries reuse the index, making unrelated graph growth much less influential.
- Edge mutation has a clear cache invalidation contract.
- The index adds bounded memory proportional to edges and is rebuilt after mutation; persistence
  and incremental on-disk indexes remain unnecessary at the current product scale.
- Timing results are diagnostic, not portable performance promises.

## Links

- Requirement: REQ-013 (available through the incoming `drives` relationship)
- tracked-by:: [[Issues/ISSUE-011 - Implement indexed graph queries and scale benchmark]]
