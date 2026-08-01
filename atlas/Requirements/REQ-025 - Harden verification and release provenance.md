---
id: REQ-025
type: requirement
status: active
phase: 10D
---
# Harden verification and release provenance

Maintainers can exercise IntentAtlas against malformed inputs and a real browser, apply static
type checks, and bind reviewed release artifacts to an exact source revision before any approved
publication.

## Acceptance

- Deterministic property and mutation-fuzz tests cover graph and untrusted JSON boundaries without
  network access, uncontrolled randomness, hangs, or unexpected exception classes.
- A real installed Chrome-family browser loads the loopback viewer, executes its JavaScript, and
  proves that a graph larger than the render window remains bounded and usable.
- Static type analysis covers the maintained Python source and release verifier in the normal CI
  gate.
- Every third-party GitHub Action reference is pinned to an immutable full commit SHA and a local
  policy regression prevents mutable references from returning.
- Repeated verified artifacts produce one deterministic provenance record containing their names,
  sizes, SHA-256 digests, exact source revision, fixed build epoch, and completed verification set.
- Publishing remains a separate, environment-protected, manually approved operation over the exact
  previously verified artifacts; no package is published as part of this phase.
- Focused and complete tests, coverage, lint, security, package, CLI/UI, determinism, attribution,
  remote CI, and Obsidian closure gates pass.

## Typed links

- drives:: [[Decisions/ADR-025 - Layer offline verification before trusted publishing]]

## Trace

- Roadmap: [[Brain/Product Roadmap]]
- Planned evidence: [[Evidence/EVD-025 - Phase 10D verification and provenance]]
