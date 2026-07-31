---
id: ADR-010
type: decision
status: accepted
phase: 6B2A
---
# ADR-010 — Failure-preserving atomic vault synchronization

## Context

The original synchronization algorithm deleted every marked generated note before rendering and
rewriting the graph. During Phase 6B1 verification, one Windows sharing violation interrupted that
purge and temporarily left generated areas incomplete. A later scan recovered them, but the
failure mode is too destructive for a tool whose vault is intended to be dependable.

## Decision

Replace purge-then-write with a prepare, replace, then prune pipeline:

1. Compute locations, relationships, and every desired generated document in memory without
   mutating the vault.
2. Leave a target untouched when its bytes already equal the desired UTF-8 content.
3. Write changed content to a dot-prefixed same-directory temporary file, then atomically replace the
   target. Never follow an existing target symlink.
4. Retry only recognized transient permission and sharing failures with a fixed, short, bounded
   delay sequence. Propagate all other errors immediately.
5. Clean temporary files in a `finally` path.
6. Only after all desired replacements succeed, enumerate marked generated notes and remove those
   absent from the desired path set, using the same bounded lock retry.

A persistent replacement failure keeps the old target in place and prevents stale cleanup. A
persistent stale-file deletion failure is reported after all desired files are present; it may
leave an extra obsolete generated note but cannot remove a desired note.

The algorithm continues to skip symbolic links while enumerating stale output and never reads or
modifies `atlas/Private/`.

## Consequences

- A scan failure no longer begins by destroying the last complete generated view.
- Atomic replacement prevents readers from observing a truncated Markdown file.
- Unchanged scans perform substantially fewer filesystem writes and are less likely to conflict
  with Obsidian, antivirus software, or indexers.
- Full cross-file atomicity is not claimed; that would require a versioned directory swap or a
  manifest protocol and is outside this phase.

## Links

- Requirement: REQ-010 (available through the incoming `drives` relationship)
- tracked-by:: [[Issues/ISSUE-008 - Implement resilient generated vault synchronization]]
