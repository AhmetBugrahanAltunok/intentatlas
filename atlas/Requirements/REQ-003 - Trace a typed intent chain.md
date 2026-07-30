---
id: REQ-003
type: requirement
status: accepted
phase: 2
---
# Trace a typed intent chain

A developer can distinguish why two nodes are connected and read the relationship correctly from
either traversal direction without losing compatibility with an existing graph cache.

## Acceptance

- A fixed, documented relation vocabulary covers intent, delivery, implementation, verification,
  evidence, history, structure, and generic references.
- Markdown authors can declare typed links with `relation:: [[target]]` while ordinary wikilinks
  remain generic references.
- Issue notes are first-class, user-owned, durable graph nodes.
- Incoming relationships use meaningful inverse labels in CLI, vault, and viewer output.
- Schema-1 graph caches load safely and serialize as schema 2.
- Unknown or inconsistent typed relation data is rejected or safely reduced to a reference.

## Typed links

- drives:: [[Decisions/ADR-003 - Typed relation vocabulary]]

## Trace

- Roadmap: [[Brain/Product Roadmap]]
- Delivery continues through ADR-003 to ISSUE-001.
- Planned evidence: [[Evidence/EVD-003 - Phase 2 typed chain verification]]
