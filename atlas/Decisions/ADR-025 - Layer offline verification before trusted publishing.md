---
id: ADR-025
type: decision
status: accepted
phase: 10D
---
# ADR-025 — Layer offline verification before trusted publishing

## Context

Phase 7D established reproducible archives and cross-platform installed-wheel checks. Phase 10
still requires hostile-input properties, executable browser coverage, static type analysis,
immutable CI dependencies, artifact provenance, and a publication boundary. Combining all of
these with an automatic upload would make a verification failure capable of becoming an external
release action.

## Decision

Keep the default CI workflow verification-only. Add deterministic, bounded property and mutation
tests using fixed seeds and generated cases that are reproducible without a network. Exercise the
packaged viewer through an installed Chrome-family browser and assert rendered DOM state, not only
served asset bytes. Apply one checked-in static typing policy to maintained Python source.

Pin every external Action by full commit SHA and enforce that invariant with a repository test.
Extend repeated-build verification to emit a canonical provenance JSON record for an explicitly
provided 40-character source revision and fixed build epoch. The record describes verified bytes;
it is not represented as a signature or hosted attestation.

Treat trusted publishing as a separate manual workflow over the exact recorded artifacts. It must
use a protected release environment, short-lived identity, immutable dependencies, and explicit
owner approval. Implementing or exercising that external path is not permission to publish.

## Consequences

- Parser and graph invariants receive broad deterministic pressure while failures remain exactly
  replayable.
- Browser regressions become observable at the rendered DOM boundary without adding runtime
  dependencies to IntentAtlas.
- Provenance binds the approval conversation to exact bytes and source, but authenticity still
  depends on the reviewed Git revision and externally configured protected publishing identity.
- Static typing and browser tooling are development gates only; the installed CLI remains offline
  and dependency-free.
- Remote dependency resolution, CI execution, and any publication remain separate approval and
  closure gates.

## Links

- Requirement: REQ-025 (available through the incoming `drives` relationship)
- tracked-by:: [[Issues/ISSUE-023 - Implement verification and provenance hardening]]
