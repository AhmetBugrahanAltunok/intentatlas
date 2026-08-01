---
id: REQ-024
type: requirement
status: accepted
phase: 10C
---
# Keep adapters trustworthy and large graphs responsive

Language adapters must have one executable conformance contract that rejects unsafe,
nondeterministic, or structurally invalid output before it enters the graph or derived cache. The
local viewer must remain usable when a repository graph is much larger than the browser should
render at once, without silently discarding graph data.

## Acceptance

- A documented public conformance helper validates adapter identity, suffix/input declarations,
  cache version, evidence labels, deterministic repeated output, bounded fragment size, symbol
  shape, relation semantics, endpoints, ordering, and duplicates.
- Built-in Python, JavaScript/TypeScript, and Go adapters pass the same fixture-driven contract;
  malformed adapters fail with stable actionable messages before graph merge or cache storage.
- Validation remains local, offline, read-only, dependency-free, and never executes scanned code or
  persists source text, environment values, secrets, or absolute project paths.
- Large graphs use a deterministic bounded overview and bounded focused neighborhood rather than
  creating one SVG element for every graph node and edge.
- Global search and linked report/detail navigation can reveal a node outside the current window;
  the user can restore the overview and see both total and currently rendered counts.
- Browser indexes avoid repeated whole-graph scans for degree, adjacency, node lookup, and connected
  relationships; relationship/detail rendering is bounded and states when results are omitted.
- Focused/full tests, coverage, lint, security, synthetic large-graph browser E2E, determinism,
  vault closure, Evidence, and Review gates pass before Phase 10C closes.

## Typed links

- drives:: [[Decisions/ADR-024 - Validate adapters and render bounded graph windows]]

## Trace

- Roadmap: [[Brain/Product Roadmap]]
- Strategy: [[Brain/Phase 8-10 Strategy]]
- Delivery: [[Issues/ISSUE-022 - Implement adapter conformance and bounded viewer windows]]
