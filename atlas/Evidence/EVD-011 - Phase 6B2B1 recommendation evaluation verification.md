---
id: EVD-011
type: evidence
status: verified
phase: 6B2B1
---
# EVD-011 — Phase 6B2B1 recommendation evaluation verification

## Requirement and decision

- proves:: [[Requirements/REQ-011 - Measure test recommendation quality]]
- Decision: [[Decisions/ADR-011 - Closed-world recommendation evaluation]]
- Delivery issue: [[Issues/ISSUE-009 - Implement labeled recommendation evaluation]]
- Review: [[Reviews/Phase 6B2B1 Recommendation Evaluation Review]]

## Change inventory

- Added a strict schema-1 `complete-test-set` JSON parser with duplicate-key, field, type, path,
  symbolic-link, identity, byte, case, and expected-test bounds.
- Added a pure evaluator around the unchanged production `recommend_tests` query. It calculates
  ranked per-case TP, FP, FN, precision, and recall plus micro-aggregated totals.
- Undefined precision or recall remains JSON `null` and text `n/a`; no absent denominator is
  reported as a perfect or zero metric.
- Added deterministic, timestamp-free text and JSON rendering with an explicit completeness and
  generalization advisory.
- Added `evaluate-recommendations` with confidence, result-limit, and output-format controls. The
  label path must remain below the project root and outside `atlas/Private/`.
- Added a reviewed two-case self-hosted benchmark and documented its current-graph semantics,
  review basis, and limits.
- Updated English and Turkish READMEs, architecture, security, changelog, roadmap, requirement,
  ADR, issue, benchmark documentation, Evidence, and Review.

## Focused verification

- `python -m pytest tests/test_evaluation.py tests/test_recommendations.py tests/test_cli.py` —
  21 passed.
- `python -m ruff check src/intentatlas/evaluation.py src/intentatlas/cli.py
  tests/test_evaluation.py` — passed.

Focused coverage includes deterministic parsing and rendering, exact TP/FP/FN accounting,
micro aggregation, undefined metrics, confidence and limit behavior, duplicate keys/cases/targets/
tests, schema and policy validation, unsafe and Private paths, symlinks, size/count bounds, stale
targets, wrong target kinds, missing expected tests, CLI JSON, and project boundaries.

## Reviewed baseline

Command:

`intentatlas evaluate-recommendations benchmarks/intentatlas-recommendations.json --format json`

At the default medium threshold:

- Phase 6A symbol impact: TP 4, FP 3, FN 0, precision 0.571429, recall 1.0.
- Phase 6B1 recommendations: TP 3, FP 0, FN 0, precision 1.0, recall 1.0.
- Micro totals: TP 7, FP 3, FN 0, precision 0.7, recall 1.0.

At the high threshold, micro totals were TP 5, FP 0, FN 2, precision 1.0, recall 0.714286. This
records the expected tradeoff: high removes the reviewed file-level false positives but omits two
relevant medium-confidence tests. Recommendation scores were not changed to improve the metric.

The label set was reviewed against the current graph. During packaging verification, the newly
added evaluator test correctly appeared for the earlier recommendation-engine commit because it
now exercises that production query. The complete set and benchmark explanation were updated to
make this current-test-suite behavior explicit rather than misclassifying the new relevant test.

## Complete quality and security suite

- `python -m pytest --cov=intentatlas --cov-report=term-missing` — 90 passed; total coverage 89%.
- `python -m ruff check .` — passed.
- `python -m bandit -q -r src` — passed.
- `python -m pip check` — no broken requirements.
- `python -m pip_audit` — no known vulnerabilities; unpublished local
  `intentatlas==0.1.0` was skipped because it is not on PyPI.
- `node --check src/intentatlas/web/app.js` — passed.

## CLI and local viewer

The real repository scan produced 550 nodes, 1,109 relationships, 494 generated notes, and zero
durable orphans before Evidence and Review closure notes were added. Both medium and high
evaluation commands completed offline against the saved graph with the reviewed counts above.

The loopback viewer returned the 550-node/1,109-link graph in the in-app browser. Search accepted
`REQ-011`; keyboard activation opened the exact requirement and displayed three relationship
cards. Graph totals, layer counts, detail identity, and relationships rendered correctly. The
browser console contained no warnings or errors, and the temporary server was stopped.

## Package verification

- `python -m pip wheel . --no-deps --no-build-isolation` produced
  `intentatlas-0.1.0-py3-none-any.whl` with SHA-256
  `3cb3ad6e1b60863aef1a4128b2ab32a5f6db0be1d3e3f396cace869270470950`.
- The wheel installed with `--no-deps` into a new virtual environment.
- The installed CLI reported version 0.1.0, initialized a clean fixture, completed two scans, and
  reported six durable nodes, nine relationships, and zero durable orphans.
- The installed CLI also evaluated the real repository label file through the packaged evaluator.

## Determinism and final closure

After Evidence and Review entered the graph, two consecutive scans each produced 552 nodes, 1,122
relationships, 494 generated notes, and zero durable orphans. The normalized graph SHA-256 was
identical at `1ffe59ffa3708b6b901c7159929193a4f410d6db98d0e3ebac32208eb3d7d136`.
Explicitly enumerated user-owned areas were byte-identical across the scans; `atlas/Private/` was
not enumerated or read. Generated bytes plus UTC modification ticks were identical at
`13be45f3532fcaec6d4d0999b072b8c9be970062ec52416c68f940f122badbe2`, proving the
second scan did not rewrite unchanged generated notes. The deterministic medium-threshold
benchmark output was also identical at
`2ba3d45a18a483d59600cee1a5f86337b79e25d710b45f2b4bc465a968c7993b`.

## Remaining risks and boundaries

- Two self-hosted cases cannot estimate performance on independent repositories or justify score
  tuning. Phase 6B2B2 must add independently reviewed fixtures and reviewers.
- `complete-test-set` is a human completeness assertion, not automatically proven ground truth.
  Labels require re-review when current test dependencies change.
- Metrics describe the selected confidence threshold and per-case limit. A low limit can create
  false negatives by truncation and must remain visible with the result.
- The evaluator measures direct file/symbol evidence only. It does not yet model transitive runtime
  dependencies, dynamic dispatch, environment behavior, or semantic requirements.
- Expected identities are exact by design; graph or path migrations require explicit label updates.

## Decision

REQ-011 acceptance criteria are satisfied. Phase 6B2B1 passes as an honest, bounded measurement
foundation; it does not claim that the current recommendation policy is generally accurate.
