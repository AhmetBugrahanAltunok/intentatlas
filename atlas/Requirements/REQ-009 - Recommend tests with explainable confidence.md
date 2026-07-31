---
id: REQ-009
type: requirement
status: accepted
phase: 6B1
---
# Recommend tests with explainable confidence

A developer can ask which tests are worth running for a commit, file, or symbol and receive a
deterministic advisory ranking that explains every recommendation without claiming certainty.

## Acceptance

- Recommendations use only relationships and metadata already present in the validated local
  graph; they do not execute tests, repository code, network requests, or language runtimes.
- An exactly modified symbol combined with a structural test relationship ranks above a generic
  changed-file relationship; filename conventions remain explicitly weaker evidence.
- A changed test file recommends itself with the strongest structural confidence.
- Duplicate candidates collapse deterministically to one test while retaining every distinct
  explanation and evidence path.
- Results expose numeric score, `high`/`medium`/`low` confidence, evidence, and an inspectable node
  path. Imported JUnit observations may be displayed but never raise confidence because freshness
  is unknown.
- The default output excludes low-confidence candidates. Users can select a minimum confidence,
  a bounded result limit, and deterministic text or JSON output.
- Unsupported target kinds and invalid bounds fail clearly. No recommendation is never presented
  as proof that a test or behavior is unaffected.
- Focused tests and the complete test, lint, security, CLI, package, determinism, and affected
  interface regression gates pass before the phase is complete.

## Scope boundary

Phase 6B1 provides transparent ranking over direct structural evidence. Transitive dependency
propagation, runtime per-test coverage, learned ranking, large-graph indexing, and richer viewer
interaction remain later work and require measured precision/recall before stronger claims.

## Typed links

- drives:: [[Decisions/ADR-009 - Evidence-ranked test recommendations]]

## Trace

- Roadmap: [[Brain/Product Roadmap]]
- Planned evidence: [[Evidence/EVD-009 - Phase 6B1 test recommendation verification]]
