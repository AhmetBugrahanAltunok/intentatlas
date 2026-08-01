---
id: EVD-016
type: evidence
status: verified
phase: 7A
---
# EVD-016 — Phase 7A Go symbol-reference verification

## Requirement and decision

- proves:: [[Requirements/REQ-016 - Link Go tests through unique symbol references]]
- Decision: [[Decisions/ADR-016 - Prefer unique Go symbol evidence over filename convention]]
- Delivery issue: [[Issues/ISSUE-014 - Implement conservative Go symbol test links]]
- Review: [[Reviews/Phase 7A Go Symbol-Reference Review]]

## Change inventory

- Extended the dependency-free Go adapter to collect package declarations, exported production
  declarations, and test identifier tokens while processing already bounded files.
- Added `go-symbol-reference` test edges only for compatible same-directory packages and exported
  declaration names owned by exactly one production file.
- Preserved import-derived `go-structural` edges and weak `filename-convention` fallback edges.
- Added positive same-package and external-package coverage plus negative ambiguity and literal-only
  regressions. Existing comment masking continues to reject comment-only references.
- Added an end-to-end assertion that the stronger edge raises the direct Go file recommendation
  from low score 45 to medium score 65 without changing the scoring algorithm.
- Updated the English/Turkish READMEs, architecture, security model, changelog, product roadmap,
  requirement, decision, issue, Evidence, and Review records.

## Focused verification and correction

- `.venv\Scripts\python.exe -m pytest tests/test_adapters.py tests/test_scanner.py
  tests/test_recommendations.py tests/test_real_world.py -q` — 46 passed.
- The selected-module coverage run reported 88% total across the Go adapter, recommendations, and
  real-world evaluator; `go.py` was 86%.
- `.venv\Scripts\python.exe -m ruff check .` and `git diff --check` passed.
- The first focused coverage run found one over-specific test assertion: the explanation evidence
  correctly contained both `selected-target` and `go-symbol-reference`, while the assertion
  expected only the latter. The assertion now checks for the required provenance without hiding
  valid path evidence; the complete focused run then passed.

## Real-world measurement

The unchanged command and reviewed labels were evaluated twice:

`intentatlas evaluate-real-world benchmarks/real-world/manifest.json
.intentatlas/real-world/checkouts`

- Low confidence — TP 9, FP 0, FN 0, precision 100%, recall 100%.
- Medium confidence — TP 9, FP 0, FN 0, precision 100%, recall 100%.
- High confidence — TP 3, FP 0, FN 6, precision 100%, recall 33.33%.

The Go file-only case improved from a filename-only low-confidence recommendation to a medium
recommendation because `match_test.go` directly references exported declarations uniquely owned by
`match.go`. Scores and labels were unchanged. Two JSON results were byte-identical at SHA-256
`44094fabaf218bfc71744ea1ef5d972631a984226fa69a6f4b290a7f089a9eb5`; all three public checkouts
remained clean. These nine cases still do not prove general accuracy.

## Complete quality and security suite

- `.venv\Scripts\python.exe -m pytest --cov=intentatlas --cov-report=term-missing` — 154 passed.
- Coverage — total 90%; `go.py` 86%; `real_world.py` 90%; `recommendations.py` 88%.
- `.venv\Scripts\python.exe -m ruff check .` — passed.
- `.venv\Scripts\python.exe -m bandit -q -r src` — passed.
- `.venv\Scripts\python.exe -m pip check` — no broken requirements.
- `.venv\Scripts\python.exe -m pip_audit` — no known vulnerabilities; the unpublished local
  `intentatlas` distribution was skipped because it is absent from PyPI.
- `node --check src/intentatlas/web/app.js` and `git diff --check` — passed.

## Package, CLI, and local viewer

- `pip wheel . --no-deps --no-build-isolation` produced
  `intentatlas-0.1.0-py3-none-any.whl` with SHA-256
  `17d1b8fa7fda46d4fbc7acceef6e0b7f8f44289b5d88a59e9b39e5b19a286119`.
- The wheel installed with `--no-deps` in a new virtual environment, reported version 0.1.0, and
  its installed CLI returned nine real-world cases with `ephemeral-only` output policy.
- The first package-verification script built the wheel successfully but used the unavailable
  PowerShell `Select-Object -Single` option before installation. The corrected explicit one-wheel
  count completed installation and CLI checks; this was a verification-script error, not a product
  or package failure.
- The loopback demo returned HTTP 200 and rendered 9 nodes and 13 links. Enter-key activation
  selected the requirement and displayed four bounded evidence paths; selecting the test path
  navigated to `tests/test_auth.py`. The browser tab and local server were closed afterward.

## Self-hosted and corpus compatibility

The new `tests/test_scanner.py` assertion directly invokes the production recommendation query and
checks its score, confidence, and provenance. The reviewed self-hosted complete-test-set label was
therefore expanded from seven to eight expected Phase 6B1 tests after source-level review, not from
the evaluator output alone. The resulting two cases total TP 12, FP 3, FN 0, precision 80%, and
recall 100%; the three existing false positives for the older Phase 6A scanner change remain
visible. The original saved three-project corpus is unchanged at medium precision 66.67%/recall
100% and high precision 100%/recall 50%.

## Determinism and final closure

Two final closure scans each produced 697 nodes, 1,479 relationships, 614 generated notes, and zero
durable orphans. The normalized graph SHA-256 was identical at
`dc19a3259e231fd0da6219fa4076610ee3c22b69bae899df36b534b595b678a1`. Explicitly enumerated
user-owned areas were byte-identical across the scans; `atlas/Private/` was not enumerated or read.
Generated-note bytes plus nanosecond modification times were identical at
`8ba0e32669109e0b602221613445ddc6f052f282a322cdcb7f7bee386ce3c296`, proving the second scan did
not rewrite unchanged generated notes.

## Remaining risks and boundaries

- A lexical identifier can be shadowed locally, so a unique declaration-name match is structural
  evidence rather than semantic call resolution.
- The conservative exported-only rule can omit valid tests of unexported helpers.
- Build tags, generated code, reflection, interfaces, callbacks, indirect dependencies, and runtime
  dispatch remain outside this rule.
- The real-world improvement is one Go project and one recovered file case. Larger repositories,
  multiple relevant tests, source-only commits, and negative cases remain Phase 7B work.

## Decision

REQ-016 acceptance criteria are satisfied. Phase 7A passes as a conservative evidence improvement:
the known Go filename-only gap is recovered at medium confidence without package-wide fan-out,
score tuning, label weakening, toolchain execution, or broader accuracy claims.
