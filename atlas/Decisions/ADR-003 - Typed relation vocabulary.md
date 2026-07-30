---
id: ADR-003
type: decision
status: accepted
phase: 2
---
# ADR-003 — Typed relation vocabulary

## Context

Schema 1 stored relation names as unrestricted strings and converted every user wikilink to
`references`. That retained connectivity but erased the meaning required for reliable impact
analysis.

## Decision

IntentAtlas uses a small allowlisted relation catalog. Every relation has a stable name, inverse
label, category, and description. Edge serialization includes the derived category and inverse;
schema 2 can load schema-1 caches and rewrites them on the next scan.

Typed user links use `relation:: [[target]]`. Unknown labels remain generic references because
vault content is untrusted data. Structural adapters continue to emit fixed relations such as
`defines`, `imports`, `tests`, and `changes`.

Issue notes become a user-owned vault area so the durable product chain can represent delivery
work without depending on a hosted issue tracker.

## Consequences

- Impact output can explain both directions without inventing prose at query time.
- Relation additions become schema decisions and require tests.
- Existing ordinary wikilinks and schema-1 caches remain usable.
- Endpoint-kind constraints remain a future option; Phase 2 validates vocabulary and metadata.

## Links

- Requirement: REQ-003 (available through the incoming `drives` relationship)
- tracked-by:: [[Issues/ISSUE-001 - Implement typed intent chain]]
- Language sequence: [[Brain/Language Adapter Strategy]]
