---
id: EVD-014
type: evidence
status: verified
phase: 6B2B2B2A
---
# EVD-014 — Phase 6B2B2B2A guided demo verification

## Requirement and decision

- proves:: [[Requirements/REQ-014 - Explain the product through a guided local demo]]
- Decision: [[Decisions/ADR-014 - Packaged first-party demo and bounded evidence paths]]
- Delivery issue: [[Issues/ISSUE-012 - Implement guided demo and viewer evidence paths]]
- Review: [[Reviews/Phase 6B2B2B2A Guided Demo Review]]

## Change inventory

- Added an original nine-node, thirteen-relationship graph covering requirement, decision,
  delivery issue, pull request, file, symbol, test, evidence, and commit records.
- Built the example with production `AtlasGraph`, node, edge, relation, serialization,
  recommendation, and viewer contracts rather than a separate mock interface.
- Added `intentatlas demo` with the same loopback host/port controls as `open`. It scans no
  directory and serves its graph from automatically cleaned temporary storage.
- Moved loopback and port validation into the viewer serving boundary so CLI and direct-library
  callers receive the same protection.
- Added one reusable viewer adjacency table plus deterministic bidirectional breadth-first evidence
  paths for proof-oriented destinations, bounded to depth 6, 800 visited nodes, and 6 results.
- Rendered actual forward/inverse relation names and destination kinds/labels, escaped graph data,
  explicit uncertainty language, a no-result state, click activation, and Enter/Space activation.
- Preserved direct relationships as a separate detail section and retained search, layers, node
  selection, fit, pan, zoom, responsive layout, and existing project viewing.
- Added a guided demo document and updated English/Turkish READMEs, architecture, security,
  changelog, roadmap, requirement, ADR, issue, Evidence, and Review.
- Re-reviewed the self-hosted complete-test-set label after `tests/test_demo.py` became a genuine
  production recommendation-query consumer.

## Focused verification

- `.venv\\Scripts\\python.exe -m pytest tests/test_demo.py tests/test_viewer.py tests/test_cli.py
  tests/test_graph.py tests/test_recommendations.py` — 30 passed.
- `.venv\\Scripts\\python.exe -m pytest tests/test_demo.py tests/test_viewer.py` — 7 passed after
  the final explicit keyboard activation change.
- Focused Ruff, JavaScript syntax, and whitespace checks passed.

Focused tests cover exact demo identities/counts, stable edge ordering, complete durable
connectivity, production recommendation behavior, temporary-file lifetime, cleanup after normal
shutdown, CLI option forwarding, loopback/port rejection including booleans, packaged viewer
markers, and existing server lifecycle behavior.

## Complete quality and security suite

- `.venv\\Scripts\\python.exe -m pytest --cov=intentatlas --cov-report=term-missing` — 125 passed.
- Coverage — total 90%; `cli.py` 91%; `viewer.py` 58%; fully covered `demo.py` was omitted by
  `skip_covered`.
- `.venv\\Scripts\\python.exe -m ruff check .` — passed.
- `.venv\\Scripts\\python.exe -m bandit -q -r src` — passed.
- `.venv\\Scripts\\python.exe -m pip check` — no broken requirements.
- `node --check src/intentatlas/web/app.js` — passed.
- `git diff --check` — passed.
- No networked dependency refresh was run because this phase had no network approval or need.

## Demo and local viewer

The actual `intentatlas demo --no-browser --port 4321` flow served exactly 9 nodes and 13 links on
`127.0.0.1`. Selecting `Keep customer sessions secure` exposed deterministic paths to its pull
request, commit, test, and evidence. Every path displayed actual typed direction and relation
labels. Activating the test path opened `tests/test_auth.py` with its evidence, commit, pull-request,
file, and symbol context. A second browser pass verified that both graph-node selection and
evidence-path navigation work through Enter-key activation. Server error logs were empty and all
temporary browser/server sessions were closed.

The real repository scan before closure produced 640 nodes, 1,342 relationships, 569 generated
notes, and zero durable orphans.

## Package verification

- `.venv\\Scripts\\python.exe -m pip wheel . --no-deps --no-build-isolation` produced
  `intentatlas-0.1.0-py3-none-any.whl` with final SHA-256
  `af5a9fb22f011848524db24e65d8888e137b80ec55fd882c76758b32ca5bc51f`.
- The wheel installed with `--no-deps` into a new virtual environment.
- The installed CLI exposed `demo --host --port --no-browser`; its packaged graph contained the
  exact 9 nodes and 13 relationships, and the packaged web asset contained the final keyboard
  activation implementation.
- An earlier full installed-package pass also reported version 0.1.0, initialized and scanned a
  clean fixture, and returned six durable nodes, nine relationships, and zero durable orphans.

## Recommendation compatibility

After adding `tests/test_demo.py`, the reviewed Phase 6B1 expected set increased from five to six
tests because the new test directly calls the production recommendation query. At medium
confidence the two self-hosted cases now total TP 10, FP 3, FN 0, precision 0.769231, and recall
1.0. At high confidence they total TP 5, FP 0, FN 5, precision 1.0, and recall 0.5. The updated
label file SHA-256 is `b4f3a44c25a8f48a8c50c3d1d5f51653396c4a3892b2e0007512d57579d302a6`.

The original three-project corpus metrics remained unchanged: medium precision 0.666667/recall
1.0 and high precision 1.0/recall 0.5. No recommendation scores were changed for the demo.

## Corrections made during verification

- Initial tests incorrectly expected relationship count inside the node-kind summary. They were
  corrected to inspect the schema's edge collection instead of changing the production schema.
- Initial tests expected high confidence for exact-symbol plus structural-test evidence. They were
  corrected to the established medium-confidence policy rather than weakening or retuning it.
- Browser verification showed that explicit path-button keyboard handling made automation and
  accessibility behavior unambiguous, so Enter/Space activation was added for both evidence-path
  and direct-relationship buttons.
- The historical self-hosted label was expanded when the new demo test became genuinely relevant;
  the new recommendation was not hidden as a false positive.

## Determinism and final closure

After Evidence and Review entered the graph, two consecutive scans each produced 643 nodes, 1,356
relationships, 570 generated notes, and zero durable orphans. The normalized graph SHA-256 was
identical at `0723e35a21f19af55a83a7583372e3621d78475c398179fe15f618580c44007f`.
Explicitly enumerated user-owned areas were byte-identical before and after both scans;
`atlas/Private/` was not enumerated or read. Generated bytes plus UTC modification ticks were
identical at `06ace427ab51dbed241c4830a9e5b5ca05f2f35452858e35ef09c185bf2fff5f`, proving the second
scan did not rewrite unchanged generated notes.

## Remaining risks and boundaries

- The demo is intentionally small and first-party. It proves onboarding mechanics and product
  storytelling, not recommendation accuracy or latency on real repositories.
- Evidence paths are bounded shortest structural routes. They do not score semantic relevance and
  cannot establish causality, completeness, evidence freshness, or that a test must run.
- Viewer traversal is client-side and reuses adjacency after graph load; the current depth, visit,
  and result bounds still need validation on genuinely large real-world UI graphs.
- Abnormal process termination can bypass normal temporary-directory cleanup; operating-system
  temporary cleanup remains the fallback.
- Public-repository validation, independent labels, license review, and generated-output policy
  remain Phase 6B2B2B2B and require explicit network approval before external acquisition.

## Decision

REQ-014 acceptance criteria are satisfied. Phase 6B2B2B2A passes as an original, offline,
one-command product showcase with bounded and honest evidence-path explanations.
