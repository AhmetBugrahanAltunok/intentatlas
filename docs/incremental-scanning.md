# Incremental scanning

`intentatlas scan` avoids repeated language parsing by caching graph fragments per built-in adapter
and explicit workspace owner. The cache is an optimization, never a source of project truth. Markdown and
wikilinks in `atlas/` remain portable source material, and a clean scan can rebuild every derived
artifact without network access or an API key.

## Reuse contract

An adapter fragment is reused only when all of these values match:

- cache schema, adapter name, and adapter cache version;
- shared maximum parse size;
- workspace owner, declared source roots, aliases, and dependency closure;
- every declared input's sorted project-relative path and derived file kind;
- the bytes of every declared input at or below the parse-size limit.

Python inputs are `.py`. JavaScript/TypeScript inputs are `.js`, `.jsx`, `.ts`, and `.tsx`. Go
inputs are `.go` and `.mod`; a module declaration can change local import resolution even when Go
source is unchanged. A local edit rebuilds its workspace and declared dependents while unrelated
workspace partitions remain reusable.

IntentAtlas fingerprints inputs again after each adapter completes. If an input changes during
analysis, scanning stops before publishing a graph rather than mixing observations from different
worktree states.

## Trust boundary

Cache files live below `.intentatlas/adapter-cache/` and have a 64 MiB per-file limit. Parsers reject
duplicate JSON keys, unexpected fields, incompatible versions, unsafe links, invalid ordering,
duplicate nodes or edges, unknown metadata, and evidence outside the built-in adapter vocabulary.
Only graph nodes and relationships are stored. Raw source, source excerpts, environment values,
credentials, test output, and repository code are not retained.

A missing, stale, malformed, or unsafe cache entry becomes a normal cache miss. If writing a cache
entry fails, the current scan can still use the freshly computed in-memory fragment and the prior
complete cache file remains intact. The CLI reports any skipped cache writes.

## Atomic artifacts

Both the main graph and adapter cache files are written to a temporary file in the destination
directory, flushed, and atomically replaced. If replacement fails, the last complete destination
file is preserved and the temporary file is removed.

The entire `.intentatlas/adapter-cache/` directory may be deleted at any time. The next CLI scan
will rebuild its entries. Library callers that need a cache-independent reference can continue to
use `scan_repository`; `scan_repository_incremental` returns the graph plus reused/rebuilt metrics.
