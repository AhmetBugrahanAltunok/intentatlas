---
id: REQ-022
type: requirement
status: accepted
phase: 10A
---
# Reuse trustworthy scan work safely

A repeated local scan should avoid re-running unchanged language analysis while producing the same
graph as a clean scan. Reuse must be content-addressed, bounded, inspectable, offline, and safe to
discard. A corrupt or stale derived cache must never become authoritative project data.

## Acceptance

- Each built-in adapter declares every file suffix that can affect its output and a cache contract
  version.
- A cache hit requires the adapter identity, contract version, parse limit, path, file kind, and
  content fingerprint of the complete declared input set to match.
- Changing one language invalidates only affected adapter fragments; a clean scan and an incremental
  scan remain graph-equivalent apart from explicit generation timestamps.
- Missing, malformed, duplicate-key, oversized, unsafe, or incompatible cache data is ignored and
  rebuilt without executing project code or using the network.
- Derived state contains graph metadata only, never raw source, secrets, environment values, or
  content excerpts.
- Graph and adapter cache replacement is atomic; a failed replacement preserves the last complete
  graph and does not mark the phase complete.
- Input changes detected while an adapter is scanning fail closed before publishing a graph.
- Focused/full tests, CLI and viewer E2E, determinism, security, Evidence, and Review gates pass.

## Typed links

- drives:: [[Decisions/ADR-022 - Cache adapter fragments by declared input fingerprint]]

## Trace

- Roadmap: [[Brain/Product Roadmap]]
- Strategy: [[Brain/Phase 8-10 Strategy]]
- Delivery: [[Issues/ISSUE-020 - Implement content-addressed scan foundation]]
