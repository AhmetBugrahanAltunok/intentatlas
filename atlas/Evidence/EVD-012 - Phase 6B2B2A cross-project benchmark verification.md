---
id: EVD-012
type: evidence
status: verified
phase: 6B2B2A
---
# EVD-012 — Phase 6B2B2A cross-project benchmark verification

## Requirement and decision

- proves:: [[Requirements/REQ-012 - Compare recommendation quality across projects]]
- Decision: [[Decisions/ADR-012 - Aggregate independent closed-world benchmarks]]
- Delivery issue: [[Issues/ISSUE-010 - Implement cross-project recommendation benchmarks]]
- Review: [[Reviews/Phase 6B2B2A Cross-Project Benchmark Review]]

## Change inventory

- Added a strict schema-1 corpus manifest parser with duplicate-key, field, type, identifier, path,
  symbolic-link, byte, project, and duplicate identity/path validation.
- Added per-graph 50 MB, aggregate graph 250 MB, 50-project, and 2,000-total-case limits while
  preserving each label file's existing bounds.
- Added a pure corpus evaluator that runs the unchanged production recommendation query at low,
  medium, and high confidence with the same visible per-case limit.
- Added compact per-project and micro-aggregate case, expected, recommendation, TP, FP, FN,
  precision, and recall output. Undefined metrics remain JSON `null` and text `n/a`.
- Added deterministic schema-1 JSON and text rendering without timestamps. One invalid project
  fails the complete corpus and reports its project ID.
- Added `evaluate-corpus CORPUS [PATH] [--limit N] [--format text|json]`.
- Added three small original MIT graph/label pairs representing Python symbol impact, TypeScript
  file fallback, and Go package relationships. No third-party code, data, logo, or history was
  copied, and no network access was used.
- Hardened production graph loading so duplicate JSON keys, non-object roots, non-list node/edge
  collections, boolean schemas, and malformed record shapes fail with explicit `ValueError`s.
- Updated English and Turkish READMEs, architecture, security, changelog, roadmap, corpus schema,
  benchmark documentation, requirement, ADR, issue, Evidence, and Review.

## Focused verification

- `python -m pytest tests/test_corpus.py tests/test_graph.py tests/test_evaluation.py
  tests/test_recommendations.py tests/test_cli.py` — 50 passed.
- `python -m ruff check src/intentatlas/graph.py src/intentatlas/corpus.py
  src/intentatlas/cli.py tests/test_graph.py tests/test_corpus.py` — passed.

Focused tests cover threshold order, exact aggregate metrics, deterministic text/JSON, undefined
precision, real CLI text/JSON, manifest schemas and unknown fields, unsafe and Private paths,
duplicate IDs/graphs/labels, same-file graph/labels, direct symlinks, manifest/graph/aggregate byte
limits, project/case/result bounds, stale project context, malformed graph roots/collections/
records, duplicate graph keys, and packaged fixture loading.

## Original corpus results

Command:

`intentatlas evaluate-corpus benchmarks/recommendation-corpus.json --format json`

The corpus contains three projects and three complete cases with four expected tests:

- Low: TP 4, FP 3, FN 0, precision 0.571429, recall 1.0.
- Medium: TP 4, FP 2, FN 0, precision 0.666667, recall 1.0.
- High: TP 2, FP 0, FN 2, precision 1.0, recall 0.5.

The TypeScript project at high confidence recommends no tests, so its project precision is
undefined (`null`/`n/a`) while recall is 0.0. The high corpus total remains defined because the
other projects return recommendations. These results expose the intended threshold tradeoff and
support retaining medium as the current default; scores were not tuned from fixture output.

Two consecutive JSON evaluations were byte-identical with SHA-256
`9c2aaed84b5619f40fd41b013b766c1333421b3e5510fd0b8e51a0f7bf1d1592`.

## Complete quality and security suite

- `python -m pytest --cov=intentatlas --cov-report=term-missing` — 112 passed.
- Coverage — total 89%; `corpus.py` 91%; `graph.py` 95%.
- `python -m ruff check .` — passed.
- `python -m bandit -q -r src` — passed.
- `python -m pip check` — no broken requirements.
- `python -m pip_audit` — no known vulnerabilities; unpublished local
  `intentatlas==0.1.0` was skipped because it is not on PyPI.
- `node --check src/intentatlas/web/app.js` — passed.
- `git diff --check` — passed.

## CLI and local viewer

The real repository scan produced 593 nodes, 1,199 relationships, 532 generated notes, and zero
durable orphans before Evidence and Review closure notes were added. Corpus text and JSON completed
offline from both the editable install and packaged wheel.

The loopback viewer rendered all 593 nodes and 1,199 links. Search accepted `REQ-012`; keyboard
activation opened its exact requirement with three relationship cards. Graph statistics, details,
and typed relationships were correct, the browser console contained no warnings or errors, and the
temporary server was stopped.

## Package verification

- `python -m pip wheel . --no-deps --no-build-isolation` produced
  `intentatlas-0.1.0-py3-none-any.whl` with SHA-256
  `b0446d5c8a24f6593b956f3d858e37e8d42ea88b196fb352b45faaadd87e9fe8`.
- The wheel installed with `--no-deps` into a new virtual environment.
- The installed CLI reported version 0.1.0, initialized and scanned a clean fixture, reported six
  durable nodes, nine relationships, and zero durable orphans, then evaluated all three corpus
  thresholds against the repository fixtures.

## Corrections made during verification

- Corpus graphs gained individual and aggregate byte limits so many locally referenced graphs
  cannot bypass bounded-input intent.
- Graph loader hardening converted malformed-root and malformed-record crashes into explicit
  validation failures and rejected boolean schema values and duplicate JSON keys.
- The fixture boundary was stated more precisely: these are independent graph scenarios, not full
  real-world repositories or external-validity evidence.

## Determinism and final closure

After Evidence and Review entered the graph, two consecutive scans each produced 596 nodes, 1,213
relationships, 533 generated notes, and zero durable orphans. The normalized graph SHA-256 was
identical at `d230ca3967775697d04aa4fce41636a4a1122dd099a6657874b3efb2f906aa91`.
Explicitly enumerated user-owned areas were byte-identical across the scans; `atlas/Private/` was
not enumerated or read. Generated bytes plus UTC modification ticks were identical at
`973a5abec2198b6be3f285353b2ac59e735567eb7158ba4d2f80f1207e2d8e88`, proving the
second scan did not rewrite unchanged generated notes. Corpus JSON remained identical at
`9c2aaed84b5619f40fd41b013b766c1333421b3e5510fd0b8e51a0f7bf1d1592`.

## Remaining risks and boundaries

- The three fixtures are small, original, and reviewed by the same project. They validate mechanics
  and threshold behavior but cannot estimate real-world precision or recall.
- Hand-authored graph fixtures do not test scanner-to-recommendation behavior end to end. Public
  repositories with license-reviewed snapshots remain Phase 6B2B2B.
- Corpus processing is bounded but not indexed; graphs are retained in memory for the evaluation.
  Large-repository performance and indexed traversal remain Phase 6B2B2B.
- Closed-world labels remain human judgments and require re-review when a fixture graph or expected
  behavior changes.
- Schema-1 fixture graphs exercise backward-compatible loading. Current schema-2 generated graphs
  remain covered by the main repository and graph tests.

## Decision

REQ-012 acceptance criteria are satisfied. Phase 6B2B2A passes as a bounded cross-project
comparison foundation without changing scores or overstating fixture validity.
