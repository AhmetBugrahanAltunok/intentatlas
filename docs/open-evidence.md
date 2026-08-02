# Open evidence imports

IntentAtlas can import three explicit local JSON evidence families without executing repository
code or calling a network service:

```json
{
  "scip_reports": ["reports/index.scip.json"],
  "sarif_reports": ["reports/results.sarif"],
  "test_execution_reports": ["reports/test-execution.json"]
}
```

Nothing is auto-discovered. Every path must be project-relative, point to a regular non-linked file,
remain outside `atlas/Private/`, and satisfy the shared 10 MiB report limit. JSON parsers reject
duplicate keys, excessive nesting/values/records, oversized strings, non-finite numbers, and invalid
format contracts. Inputs are read on each scan and remain external, disposable evidence sources.

## SCIP protobuf JSON

Phase 10B supports the protobuf JSON mapping of SCIP indexes. Binary `.scip` protobuf input is not
decoded or guessed; export it to JSON with the producer's supported tooling first.

For every `documents[].relativePath` that resolves uniquely to a scanned project file, IntentAtlas
retains only these counts:

- occurrences;
- definitions (`symbolRoles` definition bit);
- references;
- attached diagnostics.

SCIP symbol strings, external symbols, documentation, diagnostic messages, source text, and
project-root metadata are not stored. Persisted semantic observations retain only normalized path,
range, role, producer/schema/revision provenance, confidence, workspace owner, and a one-way symbol
fingerprint.

An exact `scip-exact` relationship is possible only for compatibility-matrix schema `0.3.0` and an
allowlisted producer when the full revision equals HEAD, the artifact matches Git, ownership is
unique, the range is valid, and the role is supported. Stale, unavailable, unsafe, ambiguous, or
unsupported input remains fallback and creates no exact relationship. IntentAtlas imports the
provided JSON; it never runs or downloads an indexer, compiler, package manager, hook, or plugin.

## SARIF 2.1.0

Configured SARIF must declare version `2.1.0`. IntentAtlas examines result locations whose artifact
URI is project-relative (optionally `%SRCROOT%` based), percent-decodes before path validation, and
requires a unique scanned file. Absolute/schemed paths, traversal, query/fragment locations,
unsupported bases, and unresolved artifacts are ignored.

Each resolved file receives aggregate result counts by fixed SARIF level plus a bounded sorted set
of rule IDs. Messages, snippets, fixes, code flows, stacks, properties, tool payloads, and raw result
documents are not retained. A SARIF summary is a neutral observation, not proof of a defect or
behavioral impact.

## Test Execution Map schema 1

The runtime map is deliberately smaller and stricter:

```json
{
  "schema_version": 1,
  "commit": "0123456789abcdef0123456789abcdef01234567",
  "completeness": "complete-observed-set",
  "tests": [
    {
      "test": "tests/test_auth.py",
      "files": ["src/auth.py"]
    }
  ]
}
```

Top-level and test-record fields are exact. The commit is one full lowercase 40-character SHA-1.
Test and source paths must be unique canonical paths already present in the scanned graph; tests
must resolve as test files and observed files must not be tests.

Freshness is resolved against current Git `HEAD` and the mapped worktree artifacts:

- `aligned`: exact commit match and every mapped test/source file is tracked and unchanged from
  HEAD; add `test -> source` `tests` edges with
  `test-execution-map` provenance;
- `stale`: Git HEAD differs or any mapped artifact differs/is untracked; retain the summary,
  withhold runtime test edges;
- `unknown`: HEAD cannot be resolved; retain the summary, withhold runtime test edges.

An aligned map proves only that the configured run observed the file while that test executed. It
does not prove behavioral coverage, necessity, sufficiency, or that omitted tests are irrelevant.
