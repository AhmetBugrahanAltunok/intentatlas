---
id: ADR-034
type: decision
status: accepted
phase: 17
---
# Retain generated vault outputs under single-writer governance

## Context

Scanner-owned Code, Symbols, Tests, Commits, and dashboard outputs are currently tracked in Git.
That makes one reviewed repository revision portable and inspectable, but concurrent scans at
different revisions would create a large merge-conflict surface. Phase 17 correctness work does
not justify an unplanned storage-policy migration.

## Decision

Retain the tracked generated vault through Phase 17 under the current single-writer, two-pass
deterministic scan process. Treat generated merge conflicts as regeneration conflicts, not manual
content to combine. Before Phase 11C contributor intake or multi-writer scanning, require a
separate governance review to choose tracked snapshots, artifact publication, or local-only
generation with an explicit migration and durable-link policy.

Do not bulk untrack, relocate, or rewrite generated areas in this phase. Human-owned durable notes
remain tracked and scanner-protected; `atlas/Private/` remains local and inaccessible.

## Consequences

- Current portable vault and durable commit links remain intact.
- Multi-writer contribution remains an explicit open governance risk rather than an implicit safe
  workflow.
- Any future policy change must preserve rebuildability, deterministic identity, and durable links.

## Links

- governance-for:: [[Brain/Product Roadmap]]
- recorded-in:: [[Evidence/EVD-033 - Phase 17 recommendation integrity verification]]
