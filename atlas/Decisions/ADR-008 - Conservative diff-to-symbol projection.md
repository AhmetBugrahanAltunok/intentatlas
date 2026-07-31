---
id: ADR-008
type: decision
status: accepted
phase: 6A
---
# ADR-008 — Conservative diff-to-symbol projection

## Context

A file can implement several unrelated requirements. Treating every symbol in a changed file as
modified creates misleading impact paths, while removing file-level history would hide changes
that cannot be mapped safely.

## Decision

Retain `commit → changes → file` as the complete conservative history and add
`commit → modifies → symbol` only when changed new-side diff lines intersect a validated symbol
source span. When spans are nested, select the smallest intersecting spans so a method change does
not also claim that its containing class was directly modified.

Start with Python because its standard-library AST exposes reliable start and end lines. Other
language adapters keep file-level fallback until equally bounded span extraction is designed and
tested. Pure deletions and non-symbol edits also remain file-level evidence.

Diff collection uses fixed read-only Git commands, zero context, strict limits, validated commit
identifiers, and deterministic parsing. Before projection, the current file must equal the
commit's bounded raw Git blob after line-ending normalization. This prevents an older hunk's line
numbers from being applied to a later version of the file. Blob comparisons are attempted only
for scanned paths with trusted spans, so excluded paths are never opened, and stop safely when the
1,000 commit/path budget is exceeded.
Malformed, stale, or excessive patch data is discarded rather than partially trusted.

## Consequences

- Exact symbol evidence reduces the ambiguity demonstrated by multi-purpose source files.
- Existing consumers remain compatible because file-level relationships are preserved.
- Direct symbol evidence is intentionally incomplete for deletions and adapters without spans.
- Phase 6B may rank this stronger than file, text, or inferred evidence but must not reinterpret
  missing `modifies` edges as proof of no impact.
- Adding `modifies`/`modified-by` requires a relation-schema revision and graph rebuild.

## Links

- Requirement: REQ-008 (available through the incoming `drives` relationship)
- tracked-by:: [[Issues/ISSUE-006 - Implement symbol-level commit impact]]
