---
id: ADR-009
type: decision
status: accepted
phase: 6B1
---
# ADR-009 — Evidence-ranked test recommendations

## Context

A changed file may implement several unrelated requirements, and a test related to that file may
cover only part of it. Treating every nearby test as mandatory would recreate the false-positive
problem that symbol-level impact was designed to reduce.

## Decision

Build recommendations as a pure deterministic query over the validated graph. Start from commit,
file, or symbol targets and rank only direct test relationships:

1. A changed test file recommends itself with score 100 (`high`).
2. A structural test relationship to the file containing an exact modified symbol scores 80
   (`medium`): the file link does not prove that the test executes that symbol.
3. A filename-convention relationship to that exact-symbol file scores 70 (`medium`).
4. A structural test relationship to a changed file without exact symbol evidence scores 65
   (`medium`).
5. A filename-convention relationship to a changed file scores 45 (`low`).

Confidence bands are fixed and inspectable: high is 85–100, medium is 65–84, and low is 0–64.
Multiple signals for the same test retain the highest score and all unique non-superseded reasons.
A structural relation supersedes a duplicate filename-convention relation, and exact-symbol
signals supersede the same file fallback. Sorting is by descending score and stable test identity.
The default minimum is medium, so weak filename-only file matches do not appear unless requested.

Imported JUnit aggregates are observations, not selection evidence: they can explain the last
known local report but cannot increase the score because report freshness and per-source coverage
are unknown. Cobertura per-file aggregates likewise cannot identify an individual test.

Text and schema-1 JSON outputs must state that recommendations are advisory. Absence of a result
must never be interpreted as proof of no impact. Transitive imports and semantic inference are
excluded until a labeled real-repository evaluation can measure their false-positive cost.

A query accepts at most 1,000 changed-artifact signals and 10,000 candidate test files. Output is
limited to 100 recommendations, 25 reasons per test, and 25 JUnit observations per test; truncation
counts remain visible so bounded output never looks complete when explanations were omitted.

## Consequences

- Every score is reproducible and explainable without an API key or probabilistic model.
- Exact symbol evidence improves ranking while file-level fallback remains useful.
- The first version intentionally sacrifices recall to protect developer trust.
- Future execution-trace or SCIP evidence can add new documented signals without silently changing
  the meaning of existing scores.

## Links

- Requirement: REQ-009 (available through the incoming `drives` relationship)
- tracked-by:: [[Issues/ISSUE-007 - Implement explainable test recommendations]]
