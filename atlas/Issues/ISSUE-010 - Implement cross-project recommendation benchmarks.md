---
id: ISSUE-010
type: issue
status: closed
phase: 6B2B2A
---
# ISSUE-010 — Implement cross-project recommendation benchmarks

Implement ADR-012 as a bounded, deterministic, offline corpus evaluator over saved graphs and
closed-world labels.

## Acceptance checklist

- [x] Corpus manifest parsing is strict, path-safe, symlink-safe, and bounded.
- [x] Duplicate project IDs, graph paths, and label paths are rejected.
- [x] All three confidence thresholds reuse the unchanged production recommendation query.
- [x] Per-project and micro totals preserve correct undefined-metric behavior.
- [x] CLI text and JSON are deterministic, compact, and explicitly advisory.
- [x] Original Python, TypeScript, and Go regression fixtures are labeled and documented.
- [x] README, architecture, security, changelog, roadmap, Evidence, and Review are updated.
- [x] Focused and complete CLI/UI, package, determinism, and security gates pass.

## Planned implementation links

- implemented-by:: [[src - intentatlas - corpus.py|src/intentatlas/corpus.py]]
- implemented-by:: [[src - intentatlas - cli.py|src/intentatlas/cli.py]]
- implemented-by:: [[tests - test_corpus.py|tests/test_corpus.py]]
- implemented-by:: [[benchmarks - recommendation-corpus.json|benchmarks/recommendation-corpus.json]]

## Context

- Requirement: REQ-012 (linked through ADR-012)
- Decision: ADR-012 (available through the incoming `tracked-by` relationship)
- Planned evidence: [[Evidence/EVD-012 - Phase 6B2B2A cross-project benchmark verification]]
- Planned review: [[Reviews/Phase 6B2B2A Cross-Project Benchmark Review]]
