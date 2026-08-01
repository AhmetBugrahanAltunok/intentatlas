---
id: ADR-023
type: decision
status: accepted
phase: 10B
---
# ADR-023 — Separate observations from aligned execution evidence

## Context

SCIP, SARIF, and test execution maps describe different facts. SCIP records indexing occurrences,
SARIF records tool findings, and an execution map records paths observed during a particular test
run. Treating all three as interchangeable `proves` edges would overstate confidence and could make
stale runtime data silently influence recommendations.

## Decision

Add three explicit configuration lists: `scip_reports`, `sarif_reports`, and
`test_execution_reports`. Reuse the existing bounded project-relative report boundary and parse
JSON with duplicate-key rejection. Do not auto-discover reports.

Support SCIP's protobuf JSON representation, not binary protobuf, in Phase 10B. Aggregate one
source-free observation node per resolved document file with occurrence, definition, reference,
and diagnostic counts. Support SARIF 2.1.0 by aggregating one source-free finding summary per
resolved artifact file with fixed level counts and a bounded sorted rule-ID set. Connect both
summary kinds to files through neutral `references` edges, not `proves`, `changes`, or `tests`.

Define Test Execution Map schema 1 with a full lowercase commit, fixed
`complete-observed-set` policy, and unique canonical project-relative test/file paths. Record one
summary node per resolved test and its freshness. Resolve repository HEAD and compare every mapped
artifact with HEAD through fixed read-only Git commands. Only an exact commit match whose mapped
paths are all tracked and unchanged is `aligned` and adds `test -> source` `tests` edges with
`test-execution-map` evidence. `stale` or `unknown` reports retain summary/reference metadata but
withhold runtime test edges.

Persist only bounded aggregate metadata and canonical local graph identities. Never retain source,
messages, snippets, stack traces, fixes, code flows, environment values, raw output, absolute paths,
or external symbol text. Invalid configured reports fail closed; unresolved individual artifact
paths are ignored rather than guessed.

## Consequences

- Open tool evidence is navigable without changing the local-first/no-execution contract.
- Exact aligned runtime evidence can improve test selection through the existing recommendation
  engine without adding a second ranking model.
- SCIP binary users must export protobuf JSON for this phase.
- Aggregation intentionally sacrifices individual diagnostic detail to keep the graph bounded and
  source-free.

## Links

- Requirement: REQ-023 (available through the incoming `drives` relationship)
- tracked-by:: [[Issues/ISSUE-021 - Implement bounded open evidence imports]]
- Strategy: [[Brain/Phase 8-10 Strategy]]
