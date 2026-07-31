---
id: review-phase-6b2b2a-cross-project-benchmark
type: review
status: pass
phase: 6B2B2A
---
# Phase 6B2B2A Cross-Project Benchmark Review

## Acceptance review

- [x] REQ-012 is linked to ADR-012 and ISSUE-010.
- [x] Corpus manifests and referenced inputs are strict, local, Private-safe, symlink-safe, and
  bounded individually and in aggregate.
- [x] Duplicate project IDs, graphs, and labels fail instead of being double-counted.
- [x] Low, medium, and high evaluations reuse unchanged recommendation scores and one result limit.
- [x] Per-project and micro counts are summed correctly without averaging percentages.
- [x] Undefined metrics remain explicit in deterministic, timestamp-free text and JSON.
- [x] One invalid graph or label fails the complete corpus with project context.
- [x] Python, TypeScript, and Go fixtures are original MIT regression scenarios with no copied
  third-party code, history, branding, or data.
- [x] Graph loader failures are explicit for duplicate keys and malformed root/record structures.
- [x] Focused and complete tests, coverage, lint, security, dependencies, JavaScript, CLI, local
  viewer, package, corpus determinism, and vault gates passed.
- [x] Documentation and Obsidian phase records match the implemented scope and limitations.

## Evidence examined

- [[Evidence/EVD-012 - Phase 6B2B2A cross-project benchmark verification]]
- [[Requirements/REQ-012 - Compare recommendation quality across projects]]
- [[Decisions/ADR-012 - Aggregate independent closed-world benchmarks]]
- [[Issues/ISSUE-010 - Implement cross-project recommendation benchmarks]]

## Review decision

Pass. Phase 6B2B2A makes confidence tradeoffs comparable across multiple bounded graphs while
keeping every completeness assumption and external-validity gap visible.

Phase 6B2B2B should next measure and index large-graph recommendation traversal. Adding public
repositories should occur only with explicit network approval, license review, and independently
reviewed labels.
