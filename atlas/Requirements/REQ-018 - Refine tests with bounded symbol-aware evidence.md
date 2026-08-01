---
id: REQ-018
type: requirement
status: accepted
phase: 7C
---
# Refine tests with bounded symbol-aware evidence

Developers can receive narrower Python recommendations and recover strongly evidenced indirect
JavaScript/TypeScript tests without enabling unrestricted transitive dependency guesses.

## Acceptance

- Python tests link to exact imported local top-level symbols, including bounded and cycle-safe
  package re-exports and qualified module attributes.
- A nested changed symbol may use its referenced owner, but an available owner-named test focuses
  the candidate set instead of recommending every user of the large owner type.
- JavaScript/TypeScript named and default static imports link to an unambiguous discovered symbol.
- Dependency propagation follows at most one production file that imports the exact target symbol,
  then only a test directly linked to that dependent file.
- File and symbol targets may use bounded tests from the artifact's latest dated analyzed
  co-change, with a separate reason and evidence path.
- Dynamic imports, arbitrary data flow, unrestricted barrel traversal, and runtime dispatch remain
  outside automatic proof; every recommendation remains advisory.
- The unchanged 18-case real-world labels show no regression in any project and the previously
  recorded Axios misses and Click false positives are resolved at the medium threshold.
- Focused and complete tests, coverage, lint, security, CLI, UI, package, determinism, attribution,
  and Obsidian closure gates pass.

## Typed links

- drives:: [[Decisions/ADR-018 - Bound dependency propagation with exact symbols and co-change]]

## Trace

- Roadmap: [[Brain/Product Roadmap]]
- Planned evidence: [[Evidence/EVD-018 - Phase 7C symbol-aware dependency verification]]
