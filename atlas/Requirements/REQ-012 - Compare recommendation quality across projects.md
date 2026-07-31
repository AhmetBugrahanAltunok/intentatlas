---
id: REQ-012
type: requirement
status: accepted
phase: 6B2B2A
---
# Compare recommendation quality across projects

A maintainer can evaluate the unchanged test-recommendation policy across multiple independently
labeled local graphs and compare low, medium, and high confidence thresholds in one deterministic
report.

## Acceptance

- A versioned local corpus manifest references bounded, project-relative graph and label files.
- Corpus manifests reject symbolic links, unsafe or Private paths, duplicate keys, unknown fields,
  malformed types, excessive bytes/projects, and duplicate project IDs, graphs, or labels.
- Every graph and label document is validated through the existing production loaders; one invalid
  project fails the corpus instead of being omitted.
- Low, medium, and high thresholds run with the same visible per-case limit and unchanged
  recommendation scores.
- Results contain per-project and micro-aggregate case, expected, recommendation, TP, FP, FN,
  precision, and recall values for every threshold.
- Undefined precision or recall remains `null`/`n/a`; aggregate values are calculated from summed
  counts, never averaged percentages.
- Text and schema-1 JSON output are bounded, deterministic, timestamp-free, and state that fixture
  results do not establish real-world accuracy.
- Original MIT project fixtures cover Python, TypeScript, and Go graph scenarios without copying
  third-party code or history.
- Focused and complete test, lint, security, CLI, package, determinism, and UI gates pass before
  the phase is complete.

## Scope boundary

This phase adds aggregation and original regression fixtures. It does not change recommendation
scores, execute repositories, download public projects, claim independent real-world validity, or
solve large-graph query performance. Public repositories and indexed traversal remain Phase
6B2B2B.

## Typed links

- drives:: [[Decisions/ADR-012 - Aggregate independent closed-world benchmarks]]

## Trace

- Roadmap: [[Brain/Product Roadmap]]
- Planned evidence: [[Evidence/EVD-012 - Phase 6B2B2A cross-project benchmark verification]]
