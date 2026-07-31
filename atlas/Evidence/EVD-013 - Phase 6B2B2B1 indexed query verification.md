---
id: EVD-013
type: evidence
status: verified
phase: 6B2B2B1
---
# EVD-013 — Phase 6B2B2B1 indexed query verification

## Requirement and decision

- proves:: [[Requirements/REQ-013 - Keep graph queries responsive at scale]]
- Decision: [[Decisions/ADR-013 - Lazy deterministic adjacency index]]
- Delivery issue: [[Issues/ISSUE-011 - Implement indexed graph queries and scale benchmark]]
- Review: [[Reviews/Phase 6B2B2B1 Indexed Query Review]]

## Change inventory

- Added a lazy `GraphIndex` built once from canonical sorted edges, with immutable incoming and
  outgoing buckets by node and by exact `(node, relation)` pair.
- Invalidated the cached index only when a new edge is inserted; duplicate edges and node-only
  changes preserve the reusable edge index.
- Moved degree, orphan, breadth-first impact, commit artifact, symbol ownership, file-to-test, and
  test-result observation lookups from repeated complete-edge scans to shared indexed buckets.
- Preserved graph serialization and final impact/recommendation ordering, paths, confidence,
  reasons, observations, text, JSON, and corpus metrics.
- Added a bounded synthetic scale benchmark and `benchmark-scale` CLI command with deterministic
  counts, cold graph/index timings, repeated warm-query timing, and an environment-specific timing
  advisory.
- Limited the synthetic workload to 100,000 unrelated edges and 10,000 iterations, rejected
  booleans, and kept the benchmark offline without repository reads, project-code execution,
  output writes, or network access.
- Updated English and Turkish READMEs, architecture, security, changelog, benchmark documentation,
  roadmap, requirement, ADR, issue, Evidence, and Review.
- Updated the self-hosted Phase 6B1 complete-test-set label after the new corpus and scale tests
  became genuine consumers of the production recommendation query.

## Focused verification

- `.venv\\Scripts\\python.exe -m pytest tests/test_graph.py tests/test_recommendations.py
  tests/test_evaluation.py tests/test_corpus.py tests/test_scale.py tests/test_cli.py` — 59 passed.

Focused tests cover deterministic index order, identity reuse, mutation invalidation, exact
relation filtering, unchanged impact and recommendation behavior, stable scale counts, local
bucket work, non-negative timings, text/JSON rendering, CLI execution, and invalid bounds including
boolean values.

## Scale result

Command:

`.venv\\Scripts\\python.exe -m intentatlas benchmark-scale --unrelated-edges 25000 --iterations
500 --format json`

The run produced 50,003 nodes and 25,002 edges. Every iteration returned one recommendation and
two impacted nodes. The legacy reference workload was 175,014 complete-edge inspections per
iteration, while the indexed query inspected five relevant bucket edges. On this machine graph
construction took 0.086609 seconds, cold index construction 0.071481 seconds, and 500 warm combined
queries 0.010851 seconds (0.021701 ms mean). Timings are environment-specific diagnostics; stable
counts and result identities are the regression contract.

## Recommendation compatibility

The original three-project corpus remained byte-identical with SHA-256
`9c2aaed84b5619f40fd41b013b766c1333421b3e5510fd0b8e51a0f7bf1d1592`, showing that index adoption
did not change corpus output.

After adding tests that directly exercise the production query, the reviewed self-hosted label
set was updated rather than hiding newly valid recommendations. At medium confidence the two cases
now total TP 9, FP 3, FN 0, precision 0.75, and recall 1.0. At high confidence they total TP 5,
FP 0, FN 4, precision 1.0, and recall 0.555556. The label file SHA-256 is
`9a9bf27a053279361d613fcf348240746a3affb48d19fa60aa230535838a65f8`.

## Complete quality and security suite

- `.venv\\Scripts\\python.exe -m pytest` — 121 passed.
- `.venv\\Scripts\\python.exe -m coverage report -m` — total 90%; `graph.py` 95%; scale module
  fully covered and omitted by `skip_covered`.
- `.venv\\Scripts\\python.exe -m ruff check .` — passed.
- `.venv\\Scripts\\python.exe -m bandit -q -r src` — passed.
- `.venv\\Scripts\\python.exe -m pip check` — no broken requirements.
- `python -m pip_audit` — no known vulnerabilities; unpublished local `intentatlas==0.1.0` was
  skipped because it is not on PyPI.
- `node --check src/intentatlas/web/app.js` — passed.
- `git diff --check` — passed.

## CLI and local viewer

The real repository scan before closure produced 618 nodes, 1,266 relationships, 552 generated
notes, and zero durable orphans. The loopback viewer rendered all 618 nodes and 1,266 links. Search
accepted `REQ-013`; keyboard activation opened the exact requirement, path, ID, and its three
typed relationship cards. The server error log was empty, and the temporary server and browser tab
were closed after the check.

## Package verification

- `.venv\\Scripts\\python.exe -m pip wheel . --no-deps --no-build-isolation` produced
  `intentatlas-0.1.0-py3-none-any.whl` with SHA-256
  `fcede80d2ac9fed1bb266dfe176ab84548b81f0a06d35561d16c43aeea199150`.
- The wheel installed with `--no-deps` into a new virtual environment.
- The installed CLI reported version 0.1.0, initialized and scanned a clean fixture, then reported
  six durable nodes, nine relationships, and zero durable orphans.
- The installed `benchmark-scale` command returned the stable 2,003-node, 1,002-edge, one-
  recommendation, two-impact result for a 1,000-edge/20-iteration smoke run.

## Corrections made during verification

- The self-hosted labels were re-reviewed and expanded when two new test files became relevant to
  the historical recommendation implementation commit through their use of its production query.
- Benchmark documentation was kept explicit that local time measurements are not cross-machine
  performance promises.
- The final security audit invocation was kept separate from offline checks because networked
  vulnerability refreshes remain approval-gated.

## Determinism and final closure

After Evidence and Review entered the graph, two consecutive scans each produced 620 nodes, 1,279
relationships, 552 generated notes, and zero durable orphans. The normalized graph SHA-256 was
identical at `24d68ea2ea47be8cfffc76091ea040b402c29befc75fea85d59dca3e2515ade4`.
Explicitly enumerated user-owned areas were byte-identical before and after both scans;
`atlas/Private/` was not enumerated or read. Generated bytes plus UTC modification ticks were
identical at `5bdaf6a908466d43cbc39dd12cc605826495a56ac9a7672c039b207bc4d1ed42`, proving the second
scan did not rewrite unchanged generated notes.

## Remaining risks and boundaries

- The index stores several immutable tuple views over edge references, adding O(E) memory, and it
  rebuilds after an edge mutation rather than updating incrementally.
- The scale fixture is synthetic. It demonstrates query complexity and regression identities but
  does not estimate latency or accuracy on diverse real repositories.
- The index is in-memory and intentionally not serialized; startup still includes one O(E) build
  on first indexed query.
- Public-repository validation, independently reviewed labels, richer viewer evidence paths, and
  polished demos remain Phase 6B2B2B2 and require separate license/network review.

## Decision

REQ-013 acceptance criteria are satisfied. Phase 6B2B2B1 passes as a deterministic in-memory
query-scale foundation without changing recommendation policy or overstating synthetic timings.
