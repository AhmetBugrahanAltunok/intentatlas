---
id: REQ-017
type: requirement
status: accepted
phase: 7B
---
# Validate recommendations on broader project structures

Contributors can measure IntentAtlas on a more varied license-reviewed set that includes source-only
changes, multiple relevant tests, nested test layouts, package imports, and indirect dependencies.

## Acceptance

- The real-world manifest expands from three small projects and nine cases to six projects and 18
  independently reviewed commit, file, and symbol cases.
- Added projects cover Python, JavaScript, and Go with exact origin, commit, clean-tree, SPDX,
  license path, and license hash verification.
- At least two selected commits change production source without changing tests, and at least one
  selected change has multiple relevant test files across distinct test layers.
- Expected tests are justified from the pinned diff, implementation, and test content before
  accepting evaluator metrics.
- Imported Go-package tests link only to uniquely owned exported declarations they actually
  reference; unrelated package files do not inherit test edges.
- Before-and-after metrics record discovered false positives and false negatives without weakening
  labels or tuning recommendation scores.
- Checkout source, history, branding, and generated graphs remain ignored and outside the MIT
  product boundary; evaluation stays offline and non-executing.
- Focused and complete tests, coverage, lint, security, CLI, UI, package, determinism, attribution,
  and Obsidian closure gates pass.

## Scope boundary

The 18 cases are a diagnostic sample, not a population accuracy claim. Dynamic behavior,
transitive barrel imports, runtime dispatch, build tags, downstream tests, and hidden tests remain
outside the evidence available to this phase.

## Typed links

- drives:: [[Decisions/ADR-017 - Use broader benchmarks to drive conservative refinements]]

## Trace

- Roadmap: [[Brain/Product Roadmap]]
- Planned evidence: [[Evidence/EVD-017 - Phase 7B broader validation verification]]
