---
id: EVD-009
type: evidence
status: verified
phase: 6B1
---
# EVD-009 — Phase 6B1 test recommendation verification

## Requirement and decision

- proves:: [[Requirements/REQ-009 - Recommend tests with explainable confidence]]
- Decision: [[Decisions/ADR-009 - Evidence-ranked test recommendations]]
- Delivery issue: [[Issues/ISSUE-007 - Implement explainable test recommendations]]
- Review: [[Reviews/Phase 6B1 Test Recommendation Review]]

## Change inventory

- Added a pure, offline recommendation query for commit, file, and symbol graph targets.
- Added `intentatlas recommend-tests TARGET [PATH]` with fixed confidence filtering, a bounded
  result limit, deterministic text output, and schema-1 JSON output.
- Added five documented direct-signal scores: changed test 100, structural exact-symbol file 80,
  filename exact-symbol file 70, structural changed file 65, and filename changed file 45.
- Added stable deduplication and supersession rules so exact-symbol evidence replaces its weaker
  file fallback and structural test edges replace duplicate filename conventions.
- Every retained reason contains true graph relations and evidence names. JUnit results are shown
  only as observations and never change the recommendation score.
- Queries are bounded to 1,000 artifact signals, 10,000 test candidates, 100 returned tests, 25
  reasons per test, and 25 observations per test; visible counters disclose truncation.
- Unsupported targets and invalid bounds fail clearly. Empty output and every normal response say
  that recommendations are advisory and cannot prove unaffected behavior.
- English and Turkish READMEs, architecture, security, changelog, roadmap, requirement, ADR, and
  issue records document the behavior and its limits.

## Focused regression verification

Command:

`python -m pytest tests/test_recommendations.py tests/test_cli.py tests/test_viewer.py`

Result: 12 passed.

The focused tests cover signal ordering, exact-symbol and file fallbacks, filename evidence,
changed-test self-recommendation, deduplication, reason and observation bounds, confidence and
limit filters, JSON determinism, unsupported targets, invalid bounds, empty results, CLI routing,
and viewer regressions.

## Complete quality suite

- `python -m pytest` — 67 passed.
- Coverage — total 88.6099%; `recommendations.py` 87.6161%; `cli.py` 83.9450%.
- `python -m ruff check .` — passed.
- `python -m bandit -q -r src` — passed.
- `python -m pip check` — no broken requirements.
- `python -m pip_audit` — no known vulnerabilities; the local unpublished
  `intentatlas==0.1.0` package was explicitly skipped because it is not on PyPI.
- `node --check src/intentatlas/web/app.js` — passed.
- `git diff --check` — passed.
- Attribution-privacy scan of the complete change diff — clean.

## Real repository CLI verification

The accepted graph query for commit `8c229ae8f55f7d5589b3cf71befee5340be631a4` returned seven
deterministically ordered candidates at the default medium threshold:

- Four changed tests at score 100/high: `tests/test_git_history.py`, `tests/test_graph.py`,
  `tests/test_relations.py`, and `tests/test_scanner.py`.
- Three structurally related tests at score 80/medium: `tests/test_adapters.py`,
  `tests/test_delivery.py`, and `tests/test_evidence.py`.

Both text and JSON exposed the advisory warning. JSON reported schema version 1 and the same seven
results. Explanation paths used the real `changes`, `modifies`, `defined-in`, and `tested-by`
relations, and evidence names were unique within each reason.

## Vault and determinism

Three accepted real-project scans after implementation each produced 477 nodes, 938 relationships,
and 431 generated notes. Consecutive graph files had the identical normalized SHA-256
`b423c6be31b60ad4827fda34dfd2799c2f48ebe2d468e482bbddf80624a13d45` after removing only the
explicit `generated_at` field. The SHA-256 aggregate of the allowed user-owned Brain,
Requirements, Decisions, Issues, Evidence, Reviews, and Sessions areas remained identical across
the comparison; `atlas/Private/` was never enumerated or read.

One earlier scan encountered a transient Windows file lock while replacing a generated Symbol
note and stopped after partially clearing generated output. The recovery scan rebuilt every
generated area, and two subsequent scans passed. No user-owned note was changed. This incident is
retained as a known generated-output durability risk rather than hidden as a successful check.

After adding this Evidence note and the phase Review, two final closure scans each produced 479
nodes, 951 relationships, 431 generated notes, and zero durable orphans. Their normalized graph
SHA-256 was identical at
`59dc4d0005b308799ea28a274aa22064a463256ae746bc7a2eb46760a129d1c1`, and their allowed
user-area SHA-256 aggregates were identical to each other. The aggregate value is intentionally
not embedded here because this Evidence note is itself part of that aggregate.

## Local viewer

The loopback viewer returned HTTP 200 and loaded the accepted 477-node/938-link graph in the
in-app browser. Search accepted `REQ-009`; keyboard selection opened its requirement detail with
three relationships; the graph, layers, metadata, and relationship panel rendered correctly; and
the browser console contained no warnings or errors. The temporary viewer process was stopped.

## Package verification

- `python -m pip wheel . --no-deps --no-build-isolation` produced
  `intentatlas-0.1.0-py3-none-any.whl` with SHA-256
  `cb6bde418e335865b82f8eda8e1b3986e71e0e2b38fa3cab78cd47133e5f19ad`.
- The wheel installed with `--no-deps` into a newly created virtual environment.
- The installed CLI exposed `recommend-tests` and returned the same seven results with the first
  result at high confidence.

The first packaging command attempted `python -m build`, which was unavailable in the development
environment. It made no repository change. The dependency-free `pip wheel` fallback then passed.

## Corrections made during verification

- The first real-repository ranking treated a file-level test relation beside an exact symbol as
  high confidence. That claim was rejected because a file edge cannot prove symbol execution. The
  score was lowered to 80/medium and the confidence boundary was fixed at 85.
- Duplicate structural and filename explanations were removed through explicit supersession.
- Explanation paths were changed from an ambiguous node-only arrow list to the true relation
  sequence, and evidence names were deduplicated.

## Remaining risks and boundaries

- Recommendations use direct structural evidence only; they do not execute tests or prove runtime
  coverage, business impact, or that omitted behavior is unaffected.
- A test-to-file edge still cannot establish which function the test executes. Runtime per-test
  coverage or execution traces are needed before raising that evidence to high confidence.
- Transitive dependency propagation, learned ranking, TypeScript/JavaScript and Go symbol spans,
  large-graph indexing, and labeled precision/recall benchmarks remain future work.
- Generated vault synchronization can be interrupted by an external Windows file lock. A later
  phase should make generated-note replacement transactional or retry-safe.

## Decision

REQ-009 acceptance criteria are satisfied. Phase 6B1 passes with conservative confidence,
inspectable evidence, explicit uncertainty, and the documented generated-output durability risk.
