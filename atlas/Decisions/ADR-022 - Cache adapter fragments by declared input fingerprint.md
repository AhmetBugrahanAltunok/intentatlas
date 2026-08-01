---
id: ADR-022
type: decision
status: accepted
phase: 10A
---
# ADR-022 — Cache adapter fragments by declared input fingerprint

## Context

Every scan currently re-parses all supported language files even when only intent notes, reports,
or one language changed. The graph and vault are rebuildable, but repeated whole-language analysis
will become expensive on larger repositories. File-by-file caching is unsafe because Python, Go,
and JavaScript adapters resolve relationships across multiple files and module boundaries.

## Decision

Cache one complete graph fragment per built-in adapter, not isolated file fragments. Each adapter
declares an input-suffix set broad enough to cover every file that can affect its output and an
explicit cache version. The cache key hashes the adapter identity, cache contract, parse limit,
sorted project-relative paths, derived file kinds, and bytes of every declared input. Go therefore
includes both `.go` and `.mod`; Python and JavaScript/TypeScript include their source families.

Store fragments below the IntentAtlas-owned `.intentatlas/adapter-cache/` area as strict bounded
JSON. Persist only nodes, edges, fingerprints, and contract metadata. Never store source contents.
Treat every cache file as disposable untrusted data: reject links, duplicate keys, unsafe names,
wrong schemas, incompatible versions, invalid nodes or edges, and excessive size; then rebuild.

Verify the input fingerprint again after an adapter runs or a cached fragment is loaded. If it
changed, stop before publishing a mixed graph and ask for a stable retry. Write both cache entries
and the main graph through same-directory temporary files and atomic replacement so an interrupted
write leaves the last complete artifact intact.

Keep the existing `scan_repository` library path as a clean full scan. The CLI uses the incremental
path and reports reused/rebuilt adapter counts. This makes cache behavior visible while preserving
a simple cache-independent reference implementation for equivalence testing.

## Consequences

- Unchanged languages avoid repeated parsing, while cross-file semantics within each language stay
  intact.
- A change may rebuild a whole language fragment; finer incremental parsing remains future work.
- Adapter authors must update the declared input set or cache version when semantics change.
- Markdown and wikilinks remain the portable source; all cached state is safe to delete and rebuild.

## Links

- Requirement: REQ-022 (available through the incoming `drives` relationship)
- tracked-by:: [[Issues/ISSUE-020 - Implement content-addressed scan foundation]]
- Strategy: [[Brain/Phase 8-10 Strategy]]
