---
id: EVD-018
type: evidence
status: verified
phase: 7C
---
# EVD-018 — Phase 7C symbol-aware dependency verification

## Requirement and decision

- proves:: [[Requirements/REQ-018 - Refine tests with bounded symbol-aware evidence]]
- Decision: [[Decisions/ADR-018 - Bound dependency propagation with exact symbols and co-change]]
- Delivery issue: [[Issues/ISSUE-016 - Implement bounded symbol-aware test evidence]]
- Review: [[Reviews/Phase 7C Symbol-Aware Dependency Review]]

## Change inventory

- Python analysis now records exact test and source relationships to explicitly imported local
  top-level symbols. Qualified module attributes are recognized, and package re-exports resolve
  for at most eight cycle-safe hops.
- Exact Python test-symbol evidence suppresses the broader test-to-file edge for that resolved
  module. A nested changed symbol searches itself and its owners; an available owner-named test is
  preferred and the `owner-name-convention` evidence remains visible.
- JavaScript/TypeScript analysis now records exact named and default static-import relationships
  when the target declaration is discovered unambiguously.
- Recommendations follow only one production file that imports the exact changed symbol, then a
  test directly linked to that dependent file. Fan-out fails closed above 1,000 dependents.
- File targets use exact symbols from their latest dated analyzed change when available. File and
  symbol targets separately rank tests from at most five commits on that latest date as recent
  co-change evidence.
- Added independent regressions for Python package re-exports, JavaScript named/default imports,
  nested owner focus, current file-change scoping, exact one-hop dependents, recent co-change, and
  the dependent bound.
- Updated English/Turkish READMEs, architecture, security, changelog, roadmap, requirement,
  decision, issue, Evidence, and Review records.

## Real-world before and after

Phase 7B's unchanged 18-case labels and medium scores recorded TP 18, FP 3, FN 5, precision 85.71%,
and recall 78.26%. The Click false positives came from sibling declarations in `core.py`; the Axios
misses sat behind indirect or dynamic root imports.

With the bounded rules in this phase and no label changes:

- Low — TP 23, FP 0, FN 0, precision 100%, recall 100%.
- Medium — TP 23, FP 0, FN 0, precision 100%, recall 100%.
- High — TP 5, FP 0, FN 18, precision 100%, recall 21.74%.
- Axios — TP 8, FP 0, FN 0 at low/medium.
- Click — TP 3, FP 0, FN 0 at low/medium.
- Cobra, Match, p-limit, and Schedule remain TP 3, FP 0, FN 0 at low/medium.

Two complete JSON runs were byte-identical at SHA-256
`7fcd5539759e3ba871bef0655b60ddfb1af22269d228b3abe002cd95d65581b0`. All six ignored public
checkouts remained clean; no checkout code, test, hook, dependency, or configuration was executed.

## Focused and complete verification

- `.venv\Scripts\python.exe -m pytest tests/test_scanner.py tests/test_recommendations.py -q` —
  18 passed.
- `.venv\Scripts\python.exe -m pytest --cov=intentatlas --cov-report=term-missing` — 157 passed;
  total coverage 90%, `python.py` 91%, `javascript.py` 90%, and `recommendations.py` 89%.
- `.venv\Scripts\python.exe -m ruff check .` — passed.
- `.venv\Scripts\python.exe -m bandit -q -r src` — passed.
- `.venv\Scripts\python.exe -m pip check` — no broken requirements.
- `.venv\Scripts\python.exe -m pip_audit` — no known vulnerabilities; the unpublished local
  `intentatlas` distribution was skipped because it is absent from PyPI.
- `node --check src/intentatlas/web/app.js` and `git diff --check` — passed.

## Compatibility, package, and UI

- The self-hosted medium baseline remains TP 12, FP 3, FN 0, precision 80%, recall 100%.
- The original three-project corpus remains medium precision 66.67%/recall 100% and high precision
  100%/recall 50%.
- `pip wheel . --no-deps --no-build-isolation` produced
  `intentatlas-0.1.0-py3-none-any.whl` at SHA-256
  `d3d08698be85d2cdb677d0309b2af9c78d5a44cfaea50a179b4cdc19f13a4e08`.
- A fresh local virtual environment installed that wheel with `--no-deps`, reported version 0.1.0,
  and reproduced the 6-project, 18-case TP 23, FP 0, FN 0 medium report.
- The actual loopback demo rendered 9 nodes and 13 relationships. Enter-key selection opened the
  requirement details, and its test evidence-path button navigated to `tests/test_auth.py`. The
  browser tab and server were closed after verification.

## Obsidian closure

Two final closure scans each produced 732 nodes, 1,688 relationships, 639 generated notes, and zero
durable orphans. The normalized graph SHA-256 was identical at
`b0cf7af0ffd924979a38c81d2e2dfcb4d82c2e88e5f393dd94b83598c2bddc35`. Explicitly enumerated
user-owned areas were byte-identical across the scans; `atlas/Private/` was not enumerated or read.
Generated-note bytes plus nanosecond modification times were identical at
`ab665de7404c4be8e2062473da3b5e8c87adc5094656424727c1dc998b11164e`, proving the second scan did
not rewrite unchanged generated notes.

## Remaining risks and boundaries

- The 100% result covers only 23 expected observations in six pinned projects and must not be
  presented as general accuracy.
- Owner-name focus is precision-first and can omit relevant tests with different names.
- Latest co-change can omit unchanged relevant tests or include unrelated tests from a broad
  commit; it is historical evidence, not causal proof.
- JavaScript import recognition remains conservative and regex-based. Dynamic imports, runtime
  registries, arbitrary re-export expressions, data flow, and dependency paths beyond one exact
  symbol hop are not automatically traversed.
- Commit dates have day resolution in graph metadata; multiple latest-date commits are bounded and
  deterministic but may describe more than one logical change.

## Decision

REQ-018 acceptance criteria are satisfied. Phase 7C passes with all behavioral, benchmark,
security, compatibility, package, UI, and deterministic Obsidian closure gates complete.
