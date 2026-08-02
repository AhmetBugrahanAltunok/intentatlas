---
id: ADR-002
type: decision
status: accepted
phase: 1
---
# ADR-002 — Pruned trust-boundary traversal

## Context

Filtering paths after a recursive walk still enumerates excluded directories. That is incompatible
with [[Requirements/REQ-002 - Harden trust boundaries]], especially for `atlas/Private/`.

## Decision

Repository discovery will use a deterministic directory walk that removes excluded directories
before descent. The scanner will never follow directory symlinks and will enforce the vault's
`Private` area independently of user configuration.

The literal project boundary `atlas/Private/` is invariant even when a custom vault or exclude
list is configured. Vault initialization does not create it, configuration cannot place vault or
graph outputs inside it, and Git history commands exclude it before collecting path or patch
metadata. Configured scanner exclusions are also projected to Git pathspec exclusions. Users may
create and manage Private themselves; IntentAtlas does not inspect whether it exists.

Repository configuration is a bounded, regular, non-linked JSON object with unique keys and
strict field types. Invalid documents fail closed before any output path or traversal is used.

Graph identity collisions across user- and scanner-owned nodes will fail explicitly instead of
silently changing ownership or meaning.

## Consequences

- Excluded directory contents and metadata are not visited.
- Empty Private-area provisioning is an explicit user action rather than an initializer side
  effect.
- Misconfigured or colliding identities stop the scan with an actionable error.
- Regression tests must observe traversal behavior as well as final graph contents.

## Links

- Roadmap: [[Brain/Product Roadmap]]
- Requirement: [[Requirements/REQ-002 - Harden trust boundaries]]
- Implementation: [[src › intentatlas › scanner.py]]
