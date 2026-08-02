# Indexed query scale benchmark

IntentAtlas uses one lazy in-memory `GraphIndex` for incoming and outgoing edge lookup. The index
supports node-wide and exact-relation buckets, preserves canonical edge order, and is reused until
a newly accepted edge invalidates it.

## Benchmark

`benchmark-scale` constructs a synthetic graph containing one relevant commit-to-file-to-test
chain plus unrelated import edges. It then builds the index once and repeatedly runs both an impact
query and a medium-confidence test recommendation.

```console
intentatlas benchmark-scale
intentatlas benchmark-scale --unrelated-edges 50000 --iterations 500
intentatlas benchmark-scale --unrelated-edges 50000 --iterations 500 --format json
```

Defaults are 25,000 unrelated edges and 200 iterations. Inputs are bounded to 100,000 unrelated
edges and 10,000 iterations. Booleans, negative values, zero iterations, and excessive values are
rejected.

Output includes:

- stable node, edge, index, recommendation, and impact counts;
- a deterministic reference estimate of edge inspections performed by the previous full-scan
  query shape;
- the number of matching indexed bucket edges inspected by the same query shape;
- environment-specific graph construction, cold index construction, and warm query timings.

Timing varies with hardware, operating system, Python version, and concurrent load. It is not a
release promise. Correct result identities, index reuse/invalidation, deterministic ordering, and
bounded local edge work are the regression contract.

The benchmark is offline and synthetic. It reads no repository, runs no project code, writes no
graph, and makes no network request.

Phase 13 additionally exercises an exact 100,000-node/500,000-edge deterministic graph. Evidence
records construction counters, peak process working set, 240-node/900-edge overview payload bytes,
global search latency, and bounded two-hop neighborhood latency on declared reference hardware.
The local viewer obtains its initial bounded window from `/api/graph/overview`; search,
neighborhood, paths, and report details use separate bounded loopback endpoints. Every graph query
returns one snapshot identity plus explicit total, returned, and omitted counts.
