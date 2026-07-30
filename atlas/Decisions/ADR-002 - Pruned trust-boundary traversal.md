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

Graph identity collisions across user- and scanner-owned nodes will fail explicitly instead of
silently changing ownership or meaning.

## Consequences

- Excluded directory contents and metadata are not visited.
- Misconfigured or colliding identities stop the scan with an actionable error.
- Regression tests must observe traversal behavior as well as final graph contents.

## Links

- Roadmap: [[Brain/Product Roadmap]]
- Requirement: [[Requirements/REQ-002 - Harden trust boundaries]]
- Implementation: [[src › intentatlas › scanner.py]]
