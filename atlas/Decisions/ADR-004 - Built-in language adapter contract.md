---
id: ADR-004
type: decision
status: accepted
phase: 3
---
# ADR-004 — Built-in language adapter contract

## Context

The initial scanner contains Python parsing and module resolution directly inside repository
orchestration. Adding languages that way would couple discovery, parsing, resolution, and graph
mutation, making regressions and third-language work harder to isolate.

## Decision

IntentAtlas defines a small built-in adapter protocol. An adapter declares its name and supported
suffixes, receives an immutable view of discovered files and their kinds, and returns a graph
fragment containing nodes and edges. Repository orchestration merges fragments in stable adapter
order after file discovery.

The Python implementation moves behind this protocol without semantic changes. The first new
adapter family handles TypeScript, JavaScript, TSX, and JSX with a conservative, dependency-free
structural parser. It recognizes only explicit declarations and static relative module references.
It resolves files and `index` modules locally, never runs Node or project code, and never follows
bare package names into dependency directories.

Adapter output contains structural metadata only. Source text, environment values, and secrets are
not persisted. Parse failures and oversized files are skipped rather than guessed.

## Consequences

- Language support becomes independently testable and reusable by later Go, Rust, or Java work.
- Python and TypeScript/JavaScript share graph semantics instead of maintaining parallel schemas.
- The first TypeScript/JavaScript parser intentionally favors precision over complete syntax
  coverage; richer parsing can be introduced later without changing the adapter contract.
- Built-in adapters preserve an offline, zero-runtime-dependency CLI.

## Links

- Requirement: REQ-004 (available through the incoming `drives` relationship)
- tracked-by:: [[Issues/ISSUE-002 - Implement TypeScript and JavaScript adapter]]
- Strategy: [[Brain/Language Adapter Strategy]]
