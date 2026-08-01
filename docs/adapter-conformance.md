# Language adapter conformance

IntentAtlas adapter conformance contract version 1 is an executable compatibility boundary for
offline structural analyzers. It validates adapter declarations and graph fragments; it is not an
external plugin loader and does not authorize execution of repository code.

## Declared contract

An adapter implements `LanguageAdapter` and declares:

- `name`: a stable lowercase identifier used by diagnostics and disposable cache files;
- `suffixes`: the source suffixes it analyzes;
- `cache_input_suffixes`: every suffix whose content can change its complete output;
- `cache_version`: a positive integer changed when cached semantics become incompatible;
- `evidence_kinds`: the bounded evidence labels its edges may emit;
- `scan(context)`: a read-only scan returning one `GraphFragment`.

Suffix and evidence declarations are lowercase, bounded, and safe for local identities. Cache inputs
must include every analyzed suffix. Adapters receive immutable project-relative file/kind mappings
and the common parse-size ceiling through `AdapterContext`.

## Fragment contract

A conforming fragment contains sorted unique scanner-owned symbol nodes and sorted unique edges.
Every symbol path belongs to a discovered file handled by the adapter, its ID is
`symbol:<path>::<label>`, and its metadata contains a positive line, optional valid end line,
bounded symbol kind, and `owner: scanner`.

Edges are limited to the shared structural relations:

- `defines`: file to a symbol owned by that same file;
- `imports`: file to file or symbol;
- `tests`: test file to file or symbol;
- `calls`: symbol to symbol.

Every endpoint must exist in the discovered-file view or fragment, self edges are rejected, and the
evidence label must be declared by that adapter. The complete fragment is bounded to 500,000 nodes
and 2,000,000 edges. These are safety ceilings, not recommended output sizes.

## Executable check

Use the same fixture context for every adapter family:

```python
from intentatlas.adapters import AdapterContext, assert_adapter_conforms

context = AdapterContext(files=files, kinds=kinds, max_parse_bytes=1_000_000)
report = assert_adapter_conforms(MyAdapter(), context)
assert report.contract_version == 1
```

The helper freezes copied mappings, scans twice, rejects nondeterministic output, and applies the
same definition/fragment validation used by repository scanning and cache loading. A failure raises
`AdapterConformanceError` with an adapter-scoped reason.

IntentAtlas validates fresh output before graph merge or cache storage. Cached fragments pass strict
JSON decoding and the same conformance validator before reuse. An adapter cannot rely on the graph
or cache layer to silently sort, deduplicate, repair, or reinterpret malformed output.

## Trust boundary

Conformance does not make an adapter semantically complete or safe to load from an arbitrary
package. Built-in adapters remain reviewed first-party code. External discovery, installation,
process isolation, compatibility policy, and third-party publishing are outside contract version 1.
Adapters must remain local, offline, non-executing, source-free in persisted output, and covered by
representative redistributable fixtures.
