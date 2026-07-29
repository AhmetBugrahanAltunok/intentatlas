
---
id: ADR-001
type: decision
status: accepted
---
# ADR-001 — Vault-first intent graph

## Decision

Human and agent knowledge remains portable Markdown with wikilinks. Rebuildable scanner
output connects that knowledge to code structure and Git history.

## Why

The vault stays useful without IntentAtlas, Obsidian, an account, or an API key. This supports
[[Requirements/REQ-001 - Explain change impact]] while keeping meaning under user control.

## Implementation

The language-neutral graph lives in [[src › intentatlas › graph.py]]. Generated notes are
separate from user-owned notes so scans cannot overwrite decisions.
