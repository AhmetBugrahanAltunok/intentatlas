---
id: EVD-022
type: evidence
status: verified
phase: 10A
---
# EVD-022 — Phase 10A content-addressed scan verification

This evidence verifies [[Requirements/REQ-022 - Reuse trustworthy scan work safely]] through
[[Decisions/ADR-022 - Cache adapter fragments by declared input fingerprint]] and delivery issue
[[Issues/ISSUE-020 - Implement content-addressed scan foundation]].

## Change inventory

- Built-in adapters now declare a cache contract version and complete input suffix family: Python
  `.py`, JavaScript/TypeScript `.js`/`.jsx`/`.ts`/`.tsx`, and Go `.go` plus `.mod`.
- The CLI uses a per-adapter content fingerprint covering identity, contract version, parse limit,
  path, file kind, and bytes while `scan_repository` remains the cache-independent reference.
- Strict 64 MiB JSON fragments retain only allowlisted symbol metadata and structural evidence.
  Duplicate keys, unknown fields, unsafe entries, dangling endpoints, incompatible contracts,
  injected metadata, malformed documents, and oversized state become cache misses.
- Adapter output is canonically deduplicated before persistence so the cache matches `AtlasGraph`
  semantics. Input fingerprints are rechecked after analysis; concurrent changes fail closed before
  graph publication.
- Cache write failures preserve the prior fragment and use the fresh in-memory result while the CLI
  reports skipped writes. Main graph replacement is atomic and propagates failure without damaging
  the prior complete graph.
- README, Turkish README, architecture, changelog, and `docs/incremental-scanning.md` document the
  behavior, limits, deletion/rebuild contract, and remaining whole-adapter granularity.
- Product Roadmap, REQ-022, ADR-022, ISSUE-020, kickoff session, Evidence, and Review keep the phase
  traceable in the canonical `atlas/` vault.

## Focused verification

Command:

`python -m pytest tests/test_scan_cache.py tests/test_scanner.py tests/test_graph.py tests/test_cli.py tests/test_adapters.py::test_scanner_rejects_invalid_adapter_fragments -q`

Result: 40 passed. Covered exact reuse, clean-scan equivalence, Python-only invalidation, `go.mod`
invalidation, corrupt and injected cache data, dangling endpoints, unsafe cache entries, failed
cache replacement, duplicate-edge canonicalization, concurrent input mutation, atomic graph
failure, CLI metrics, and cache-independent adapter compatibility.

## Complete quality and security verification

- `python -m pytest --cov=intentatlas --cov-report=term-missing` — 206 passed; 88% total branch
  coverage.
- `python -m ruff check .` — passed.
- `python -m bandit -q -r src` — passed.
- `python -m pip check` — passed with no broken requirements.
- `node --check src/intentatlas/web/app.js` — passed.
- `bash -n .github/actions/intentatlas-review/run.sh` — passed.
- `git diff --check` — passed.

No new dependency was declared. The networked `pip-audit` check was not rerun because networked
audits require separate explicit approval; this is recorded as unverified rather than passed.

## CLI, determinism, and graphical workflow

- After canonicalizing the two stale raw cache entries, the next real scan reported `3 reused, 0
  rebuilt`; a graph diff against the preceding scan exited 0 with no semantic changes.
- Final two-pass closure scans each produced 971 nodes, 2,282 relationships, 854 generated notes,
  `3 reused, 0 rebuilt`, zero semantic graph diff, and zero durable orphans. Generated-note
  fingerprints were identical and all 117 allowed user-owned Markdown notes remained byte-identical.
  `atlas/Private/` was neither enumerated nor included.
- The installed local CLI served the exact graph at `http://127.0.0.1:8765/`. The in-app browser
  displayed 969 nodes and 2,268 links, filtered REQ-022, selected it through the supported keyboard
  interaction, and displayed its metadata and evidence paths. Browser warning/error count was zero;
  the test server was stopped and the listener count returned to zero.

## Acceptance decision and remaining limits

All REQ-022 acceptance criteria pass. Phase 10A is verified.

- Reuse is whole-adapter, not per-file; a one-file edit still re-parses that language family.
- Fingerprinting still reads eligible file bytes, and Git history, reports, delivery inputs, user
  notes, and vault materialization are not incremental in this slice.
- Adapter cache versions and input declarations are an author responsibility until the later Phase
  10C conformance contract automates more checks.
- Cross-platform remote CI was not triggered because this phase was not pushed. Existing unit and
  installed-wheel gates passed locally on Windows; remote CI remains a commit/push-time check.

## Links

- proves:: [[Requirements/REQ-022 - Reuse trustworthy scan work safely]]
- reviewed-by:: [[Reviews/Phase 10A Content-Addressed Scan Review]]
