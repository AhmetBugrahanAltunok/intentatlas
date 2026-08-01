---
id: EVD-024
type: evidence
status: verified
phase: 10C
---
# EVD-024 — Phase 10C adapter and viewer verification

This evidence verifies
[[Requirements/REQ-024 - Keep adapters trustworthy and large graphs responsive]] through
[[Decisions/ADR-024 - Validate adapters and render bounded graph windows]] and
[[Issues/ISSUE-022 - Implement adapter conformance and bounded viewer windows]].

## Change inventory

- Adapter conformance contract version 1 publishes definition, fragment, repeated-scan, report, and
  error APIs under `intentatlas.adapters` without adding an external loader or dependency.
- Adapter definitions now declare safe stable names, supported suffixes, complete cache inputs,
  positive cache versions, and bounded evidence kinds.
- Fragment validation requires bounded, sorted, unique scanner-owned symbols; valid spans and
  paths; declared evidence; known endpoints; and coherent `calls`, `defines`, `imports`, or `tests`
  shapes before graph merge.
- Fresh and incremental scans use the same validator. Strictly decoded cache fragments reuse that
  validator before admission; a cache miss is validated before cache storage.
- One shared canonical fragment builder moved identical discovery deduplication into the three
  built-in adapter implementations. The new contract exposed that Python, JavaScript/TypeScript,
  and Go could emit duplicate evidence edges even though later graph/cache layers hid them; built-in
  outputs are now unique at their own boundary without changing graph semantics.
- The public conformance helper copies fixture mappings into immutable views, scans twice, rejects
  nondeterminism, and returns a stable contract/version/count report.
- The viewer builds node, edge, degree, search, relationship, and path indexes once. Repeated degree,
  detail, and visible-node access no longer scans the complete graph.
- The default SVG view is a layer-balanced deterministic window of at most 240 nodes and 900 edges.
  A hidden global-search/report/relationship target opens a two-hop focus window that always keeps
  direct focus edges ahead of the edge cap.
- Overview restore, total/rendered counts, a focus-neighborhood action, filter synchronization, and
  an 80-item relationship detail limit make omission explicit and reversible. Overview restore
  clears the previous query so the returned graph is not accidentally dimmed.
- README, Turkish README, architecture, changelog, and `docs/adapter-conformance.md` document the
  executable boundary, trust limits, rendering budgets, and remaining full-JSON scale limit.
- REQ-024, ADR-024, ISSUE-022, Roadmap, kickoff, Evidence, and Review preserve phase traceability in
  the canonical `atlas/` vault.

## Focused verification

Command:

`python -m pytest tests/test_adapter_conformance.py tests/test_adapters.py tests/test_scanner.py tests/test_scan_cache.py tests/test_viewer.py tests/test_cli.py -q`

Result: 52 passed. Coverage includes all three built-in adapters under one repeated-scan contract;
invalid declarations, fixture contexts, return values, size, ordering, duplicates, evidence,
endpoints, symbol metadata/spans, self edges, cross-file definitions, node collisions, cache
admission, and fresh/incremental pre-storage failure. Existing scanner, cache, CLI, packaged viewer,
keyboard/detail, inverse relation, report, and evidence-path behavior remains covered.

## Complete quality and security verification

- `python -m pytest --cov=intentatlas --cov-report=term-missing` — 233 passed; 88% total branch
  coverage; the new conformance module reports 99%.
- `python -m ruff check .` — passed.
- `python -m bandit -q -r src` — passed.
- `python -m pip check` — passed with no broken requirements.
- `node --check src/intentatlas/web/app.js` — passed.
- `bash -n .github/actions/intentatlas-review/run.sh` — passed.
- `git diff --check` — passed.

No dependency was added. The networked `pip-audit` check was not run because networked audits
require separate explicit approval; it remains explicitly unverified rather than passed.

## Large-graph browser pilot

An ignored original synthetic graph contained 10,200 nodes and 10,199 relationships across
requirements, decisions, files, and symbols. It contained no third-party source or project data.

- Initial overview created exactly 240 node elements and 237 edge elements while showing the full
  10,200/10,199 totals and a 9,960-node available-through-navigation notice.
- Global search for hidden `file:src/module-4999.py` opened a deterministic five-node/four-edge
  focused neighborhood with the correct detail ID and enabled Overview action.
- Overview restore returned to 240/237, cleared the search query, left zero dimmed nodes, closed the
  prior detail, and disabled its own action as expected.
- Browser warning/error count was zero. Visual inspection confirmed the graph, counts, layers,
  actions, and status copy rendered without layout breakage.
- Closing review added direct-focus-edge priority so a dense 900-edge window cannot omit every
  relationship incident to its selected focus.
- The browser tab was finalized, the listener returned to zero, and the ignored synthetic pilot was
  completely removed.

## Installed package and CLI pilot

- `pip wheel --no-build-isolation --no-deps` built `intentatlas-0.1.0-py3-none-any.whl` without
  downloading dependencies.
- The wheel installed into a separate ignored virtual environment with `--no-deps`.
- Installed resources exposed contract version 1 and the bounded viewer assets.
- A separate original Python pilot produced 4 nodes and 3 relationships. Its first installed scan
  reported `0 reused, 3 rebuilt`; the second reported `3 reused, 0 rebuilt`; status exited 0 with
  zero durable orphans.
- The installed loopback viewer returned HTTP 200 for HTML, packaged JavaScript, and graph JSON;
  the response contained Overview, `renderLimits`, and the expected `greet` symbol.
- The listener stopped and all ignored wheel, environment, and project pilot directories were
  completely removed.

## Repository determinism and vault safety

- Final two-pass repository closure produced 1,050 nodes, 2,450 relationships, and 921 generated
  notes. Both scans reported `3 reused, 0 rebuilt`.
- Graph diff schema 1 reported zero added, removed, or changed nodes and zero added or removed edges.
- All 129 allowed user-owned notes stayed byte-identical across both scans; status exited 0 and zero
  durable orphans remained.
- `atlas/Private/` was not read or included. Root `.obsidian/` and `.intentatlas/` remained ignored
  local/derived state. Temporary pilot and baseline artifacts were removed.

## Acceptance decision and remaining limits

All REQ-024 acceptance criteria pass. Phase 10C is verified.

- Contract version 1 validates structure and determinism, not semantic completeness or parser
  correctness; representative fixtures and review remain necessary.
- External adapter discovery/loading, isolation, third-party compatibility policy, and new language
  support remain outside this phase.
- The viewer bounds SVG/interaction work after load but still downloads and indexes complete graph
  JSON. Very large future pilots may require server-side shards, workers, or canvas.
- The overview is a reversible ranked projection, not a claim that omitted nodes or edges are absent.
- Remote cross-platform CI and networked dependency audit were not triggered without approval/push.

## Links

- proves:: [[Requirements/REQ-024 - Keep adapters trustworthy and large graphs responsive]]
- reviewed-by:: [[Reviews/Phase 10C Adapter and Large Graph Review]]
