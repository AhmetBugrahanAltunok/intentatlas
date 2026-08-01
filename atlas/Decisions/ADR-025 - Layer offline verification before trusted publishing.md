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

Before writing that record, require positive source-archive and exact wheel manifests and compare
every packaged runtime byte in both artifacts with the reviewed checkout. Validate a hook-free,
fixed Hatch build configuration plus the complete supported project field set and all base/extra
dependency metadata against the checkout `pyproject.toml`; wheel/sdist equality alone is
insufficient because both artifacts could contain the same injected content. Parse
security-critical workflow policy as YAML mappings and exact step contracts rather than text
patterns.

Treat trusted publishing as a separate manual workflow over the exact recorded artifacts. It must
use a protected release environment, short-lived identity, immutable dependencies, and explicit
owner approval. The job that checks out source, resolves build dependencies, builds, and verifies
artifacts must not receive OIDC permission. It transfers only hash-approved artifacts and
provenance to a separate protected job; that job may receive OIDC, rechecks the transferred hashes,
runs no project or build code, and passes those same bytes to the trusted-publishing Action.
The external release environment must restrict deployment to protected `main` or an explicitly
approved release ref. The checked-out source revision must also equal the protected `main` workflow
dispatch revision; validating only the input's SHA shape is insufficient. Implementing or
exercising that external path is not permission to publish.

## Consequences

- Parser and graph invariants receive broad deterministic pressure while failures remain exactly
  replayable.
- Browser regressions become observable at the rendered DOM boundary without adding runtime
  dependencies to IntentAtlas.
- Provenance binds the approval conversation to exact bytes and source, but authenticity still
  depends on the reviewed Git revision and externally configured protected publishing identity.
- A deterministic backend cannot make identically modified wheel/sdist payloads appear bound to a
  revision; source, exact archive manifests, build configuration, and complete package metadata
  must also match the checkout.
- A compromised source tree or build dependency cannot request the package-index identity because
  the build job has no OIDC permission; the protected publisher trusts only immutable transfer and
  publishing Actions plus fixed runner shell primitives.
- Static typing and browser tooling are development gates only; the installed CLI remains offline
  and dependency-free.
- Remote dependency resolution, CI execution, and any publication remain separate approval and
  closure gates.

## Links

- Requirement: REQ-025 (available through the incoming `drives` relationship)
- tracked-by:: [[Issues/ISSUE-023 - Implement verification and provenance hardening]]
