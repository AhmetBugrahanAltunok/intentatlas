---
id: EVD-029
type: evidence
status: verifying
phase: 13
---
# EVD-029 - Phase 13 semantic monorepo verification

Phase 13A-13C implementation and the local code, browser, scale, vault, and approved network gates
below passed. This Evidence remains verifying until the current source-bound package artifacts,
push, complete remote CI, and final Review are recorded.

## Claim under verification

IntentAtlas preserves conservative, explainable change and test evidence across declared workspace
boundaries and large graphs, strengthens aligned paths with imported semantic evidence, and
abstains on ambiguity or staleness without executing repository-controlled tooling.

## Exact implementation provenance and scope basis

- Phase 13 starting revision: `e206787a27d60db0b75a544a51dbb372ec480a9c`.
- Foundation commit: `7f45361005163a4951f9afaa18b20e892057fa6f`.
- Exact locally verified implementation snapshot:
  `17bbb8700885af11932ba3ee654283c2282a959b`.
- Handoff checkpoint: `d3e4e56ebdb3cdd8dc4ae1be7082584da3f78ab0`.
- Phase 11B supplied the frozen workspace basis: reviewed `antfu-utils` and `zustand` histories and
  34 evaluation false-positive paths classified as resolver ambiguity. Phase 13 added no language
  and did not tune recommendation scoring.
- Owner authorization explicitly covered Phase 13 code/docs/tests, licensed public pilot
  acquisition, commits, push, remote CI, and necessary network audits. It excluded
  `atlas/Private/`, Phase 11C, tag, release, publication, hosted behavior, telemetry, and arbitrary
  indexer/plugin execution.

## Schema and compatibility inventory

- Graph schema `4` reads supported schemas `1`, `2`, and `3` deterministically; relation schema `5`
  adds `contains`/`contained-by`, `declares`/`declared-by`, and `owns`/`owned-by`.
- Workspace schema `1` defines repository, Python project, JavaScript package, Go module, and
  source-root identities. Every file and adapter symbol retains the full candidate set plus aligned
  owners; a relationship requiring one owner is omitted unless one aligned candidate exists.
- Viewer query schema `1` returns snapshot identity and total/returned/omitted counts for bounded
  overview, search, neighborhood, and path responses. The initial application request is
  `/api/graph/overview?node_limit=240&edge_limit=900`, never complete `graph.json`.
- Adapter/workspace cache files remain internal and rebuildable. The graph and vault compatibility
  boundaries remain stable; workspace projection, query JSON, evidence adapters, and language
  adapters remain experimental under `docs/compatibility-policy.md`.
- `tests/test_graph.py` proves old-schema migration, round trip, relation-catalog validation, and
  actionable rejection of unsupported versions without mutating durable Markdown identities.

## 13A workspace and ambiguity evidence

Focused command:

`\.venv\Scripts\python.exe -m pytest tests/test_workspace.py tests/test_adapters.py
tests/test_scan_cache.py tests/test_scanner.py tests/test_graph.py -q`

Result: pass. Original cases cover repeated Python module names scoped by explicit setuptools
source roots, owner-scoped TypeScript JSON/JSONC aliases, duplicate alias targets that abstain,
explicit Go `require` cross-module resolution, undeclared Go cross-module abstention, duplicate
package diagnostics, workspace candidate stability, dependency-aware partition invalidation,
repository budget rejection, and a subprocess guard against project tooling. A real Hatch case
exposed duplicate qualified Python declarations; the adapter now drops that ambiguous symbol
instead of selecting by traversal order.

Reviewed ephemeral public-workspace results, acquired only below ignored `var/phase13-pilots/`:

- `pypa/hatch` revision `849e894fa87c803682a208c152613a9ad56496cb`; `LICENSE.txt`
  SHA-256 `15d9f75684e8c6571ae6714517fe453b21de6d3a07b1546dc8813bc7469a3ca6`;
  4,154 graph nodes, 4,255 edges, 7 workspace nodes, 102 structural edges, no workspace
  diagnostics. An ephemeral intent probe linked REQ-PHASE13-HATCH to
  `backend/src/hatchling/builders/wheel.py`, two real commits, and
  `tests/backend/builders/test_wheel.py`.
- `pmndrs/zustand` revision `beca84e600e4e250f6b244d22878e72948f331c7`; `LICENSE` SHA-256
  `f0dcbb086850a46d51446679126b274b0752801d85ca1f6ddb067ed046ccc2e2`;
  344 nodes, 452 edges, 7 workspace nodes, 109 structural edges, no workspace diagnostics. An
  ephemeral probe linked REQ-PHASE13-ZUSTAND to `src/index.ts`, the pinned commit, and multiple
  real tests.
- Phase 11B `antfu/utils` revision `91f8cf73bebddae8f7ebcac82e47c9bcba9805e2` retained its
  frozen MIT license hash
  `157381f8592cbf45b6a1f7e8aa2ec9c676fafaed849726692eedf95adfac43e9`;
  the scan produced 125 nodes, 206 edges, and 82 structural edges.
- Warm rerun reused Hatch 4/4 and Zustand 5/5 adapter/workspace partitions with zero rebuilds.
  Third-party source, branding, history, and vault material were not committed or packaged.

## 13B revision-bound SCIP evidence

Focused command:

`\.venv\Scripts\python.exe -m pytest tests/test_open_evidence.py tests/test_evidence.py
tests/test_workspace.py -q`

Result: pass. The exact compatibility matrix accepts schema `0.3.0` only for `scip-python`,
`scip-typescript`, or `scip-go`. Each exact occurrence additionally requires a full revision equal
to HEAD, Git-aligned artifact bytes, one workspace owner, valid 0-based range, non-empty symbol,
and role `0` reference or `1` definition. The aligned fixture produced two exact observations and
one test-to-symbol `scip-exact` edge. The same two occurrences became fallback after revision
staleness; a two-owner/unsupported-role counterexample produced one fallback and zero exact edges;
the legacy producer-less fixture retained two fallback observations.

Unsafe/Private report paths are rejected before read; malformed, duplicate-key, binary, excessive,
invalid-range, and unsupported producer/role inputs cannot create exact edges. Persisted output
contains normalized path/range/role, producer/schema/revision/freshness, confidence, owner, and a
SHA-256 symbol fingerprint. Assertions prove raw SCIP symbols, source, diagnostics, project-root
metadata, and input document content are absent. A subprocess guard allows only IntentAtlas's
bounded Git inspection and fails if any compiler, indexer, build tool, package manager, hook,
plugin, or repository program is launched.

## 13C partition, budget, query, and scale evidence

- Cache regression changes the `beta` Python workspace and proves only `beta` plus declared
  dependent `alpha` rebuild; unrelated `gamma` reuses its fragment. Fingerprints include bounded
  partition files, roots, aliases, and dependency closure. Corrupt, unsafe, stale, oversized, and
  failed writes remain misses while atomic replacement retains the prior complete fragment.
- Pre-work defaults are 250,000 files, 8 GiB scanned bytes, 1,000,000 graph nodes, and 4,000,000
  graph edges. Evidence reports retain their separate 10 MiB and record/tree limits. Focused tests
  lower each budget, prove rejection before adapter parsing or publication, and retain atomic
  last-good graph/cache behavior.
- Query tests prove bounded snapshot/total/returned/omitted responses, unknown/unbounded request
  rejection, and visited-node work limits. Real Chrome tests prove initial bounded overview,
  global search, focus navigation, keyboard behavior, relationship details, Host-header rejection,
  no complete-graph fetch in `app.js`, and packaged UI behavior.

Reference hardware: Microsoft Windows 11 Pro `10.0.26200` 64-bit; Intel Core i7-12700H, 14 cores /
20 logical processors; 16,515,176 KiB visible memory; Python `3.13.14`; Node `20.12.0`; Chrome
`150.0.7871.188`.

Exact 100,000-node/500,000-edge deterministic run:

- constructed nodes/edges: `100000` / `500000`;
- graph build / cold index: `1.258458 s` / `1.131421 s`;
- overview: 240 nodes, 900 edges, 99,760 omitted nodes, 285 omitted matching edges,
  `178992`-byte JSON, `0.065875 s`;
- global search: one exact result in `0.015574 s`;
- two-hop neighborhood: 21 nodes in `0.000165 s`;
- peak process working set: `397877248` bytes.

Wall time is environment-specific; deterministic construction counts, response identities, and
bounded work/payload are the portable regression contract.

## Complete local quality and package results

- `INTENTATLAS_REQUIRE_BROWSER=1 \.venv\Scripts\python.exe -m pytest
  --cov=intentatlas --cov-report=term-missing --cov-fail-under=80 -ra`: `441 passed, 2 skipped` in
  83.01 seconds, branch-aware coverage `86.03%`. Windows-unavailable symlink and FIFO checks were
  skipped; their simulated security tests remain present.
- `\.venv\Scripts\python.exe -m ruff check .`, `\.venv\Scripts\python.exe -m mypy src`,
  `\.venv\Scripts\python.exe -m bandit -q -r src`, `node --check
  src/intentatlas/web/app.js`, `\.venv\Scripts\python.exe -m pip check`, and
  `git diff --check`: pass. Mypy checked 43 maintained source files.
- Two fixed-epoch builds (`SOURCE_DATE_EPOCH=1704067200`) at exact source revision
  `17bbb8700885af11932ba3ee654283c2282a959b` were byte-identical. Wheel
  `intentatlas-0.3.0rc1-py3-none-any.whl` SHA-256
  `30f07be36d8252ed6fdeeffdd26f5ed3a092e4de5eb5102dc4fb569f494acbe1` has 50 files; sdist
  `intentatlas-0.3.0rc1.tar.gz` SHA-256
  `9c96e4fb0c909384ff707a12b9f5e4bbcb00dc617a013155fb97be5e6b9ef830` has 180 files.
  Deterministic provenance schema 1 records those hashes and exact revision.
- A fresh venv installed that wheel with `--no-deps`; `IntentAtlas 0.3.0rc1` and installed-wheel
  `demo --report json` schema 1 passed. The already safety-validated sdist was extracted into a new
  local directory and its full test suite exited 0 with browser execution required.
- Approved network audit `\.venv\Scripts\python.exe -m pip_audit --skip-editable` returned
  `No known vulnerabilities found`; `pip check` returned `No broken requirements found`.

## Pending closure evidence

- [x] Two-pass generated-vault bytes/UTC-mtime and explicit user-owned snapshot remain identical:
      1,276 generated files and 160 explicitly allowlisted user-owned files.
- [x] Status reports zero durable orphans and exact REQ -> ADR -> ISSUE -> Code/Test -> EVD ->
      Commit links pass without accessing or enumerating `atlas/Private/`.
- [x] Generated Commit notes for foundation commit
      `7f45361005163a4951f9afaa18b20e892057fa6f` and exact locally verified snapshot
      `17bbb8700885af11932ba3ee654283c2282a959b` are present and linked.
- [x] Current source-bound fixed-epoch builds, artifact hashes, installed-wheel, and extracted-sdist
      checks are recorded.
- [ ] Closure records are committed and pushed; complete remote CI passes at the pushed head.
- [ ] Phase 13 Review records the final decision and this Evidence becomes complete.

## Remaining limits and risks

- Supported metadata is intentionally incomplete: Python setuptools roots and PEP 621 dependency
  names, JavaScript package/tsconfig paths, and Go module requirements are not full compiler/build
  system emulations. Unsupported structures abstain or remain diagnostics.
- SCIP exactness is evidence alignment, not behavioral completeness. SCIP binary input is not
  decoded; users must explicitly supply bounded protobuf JSON from separately trusted tooling.
- Cache partitions are local and derived, not distributed or cross-repository. Viewer queries are
  loopback-only and bounded; the server still maintains the complete local graph in memory.
- No population-wide monorepo accuracy, hosted operation, telemetry, public launch, tag, release,
  package publication, or human usability claim is made.

## Typed links

- proves:: [[Requirements/REQ-029 - Scale precise evidence across monorepos]]
- references:: [[Decisions/ADR-029 - Model workspace boundaries and import semantic evidence]]
- references:: [[Issues/ISSUE-027 - Implement semantic monorepo foundation]]
- proves:: [[file:tests/test_workspace.py]]
- proves:: [[file:tests/test_open_evidence.py]]
- proves:: [[file:tests/test_scan_cache.py]]
- proves:: [[file:tests/test_graph_query.py]]
- proves:: [[file:tests/test_browser_e2e.py]]
- recorded-in:: [[commit:7f45361005163a4951f9afaa18b20e892057fa6f]]
- recorded-in:: [[commit:17bbb8700885af11932ba3ee654283c2282a959b]]
- reviewed-by:: [[Reviews/Phase 13 Semantic Monorepo Foundation Review]]
- strategy:: [[Brain/Phase 11B-13 Delivery Strategy]]
