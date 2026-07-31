---
id: ADR-012
type: decision
status: accepted
phase: 6B2B2A
---
# ADR-012 — Aggregate independent closed-world benchmarks

## Context

The first recommendation baseline contains two cases from IntentAtlas itself. It proves that the
evaluation contract is reproducible, but it cannot show whether confidence tradeoffs remain
visible across different graph shapes or languages. Score changes would be premature without a
stable multi-project comparison surface.

## Decision

Add schema-1 corpus manifests containing a stable corpus name and a bounded list of projects. Each
project has a stable ID, display name, one project-relative saved graph, and one project-relative
schema-1 `complete-test-set` label file. Paths are canonical POSIX paths, remain below the invoking
project root, avoid `atlas/Private/`, cannot be symbolic links, and cannot be reused across corpus
entries.

Load every graph and label through the production validators. Evaluate all projects at low,
medium, and high confidence with the same per-case result limit. For each threshold, retain
per-project totals and calculate corpus micro totals by summing counts. Do not average project
percentages, silently skip invalid projects, execute project code, tune ranking scores, or infer
labels from recommendation output.

Corpus output is aggregate-only and bounded by 50 projects. Detailed ranked cases remain available
through `evaluate-recommendations` for each label file. Text and JSON remain timestamp-free and
carry an explicit warning that fixture results do not prove real-world accuracy.

The first corpus uses small original graph fixtures representing Python, TypeScript, and Go
relationships. They exercise the language-neutral recommendation contract and are MIT-licensed
with IntentAtlas. They are regression scenarios, not copied repositories or statistical evidence.

## Consequences

- Confidence tradeoffs can be compared consistently across multiple graph shapes.
- One malformed or stale fixture fails loudly, preserving corpus integrity.
- Compact aggregate output stays reviewable even when individual label files contain many cases.
- Real-world external validity, licensing review for public repositories, and large-graph
  performance remain explicit future work.

## Links

- Requirement: REQ-012 (available through the incoming `drives` relationship)
- tracked-by:: [[Issues/ISSUE-010 - Implement cross-project recommendation benchmarks]]
