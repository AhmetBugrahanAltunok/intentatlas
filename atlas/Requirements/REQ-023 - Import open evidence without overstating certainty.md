---
id: REQ-023
type: requirement
status: accepted
phase: 10B
---
# Import open evidence without overstating certainty

A project can opt into local SCIP JSON, SARIF 2.1.0, and per-test execution-map reports so existing
tool evidence becomes navigable in IntentAtlas without executing project code, retaining raw source
or diagnostic text, or treating an observation as proof of impact or test necessity.

## Acceptance

- Configuration explicitly lists each local report; default scanning remains unchanged and offline.
- Paths are project-relative, bounded, link-safe, outside `atlas/Private/`, and parsed with duplicate
  key, record-count, string-length, nesting, and input-size limits.
- SCIP support targets the protobuf JSON mapping and aggregates document occurrences, definitions,
  references, and diagnostic counts only for uniquely resolved project files. Binary protobuf SCIP
  is rejected rather than guessed in this phase.
- SARIF support accepts version 2.1.0 and aggregates rule/level counts only for safe project-relative
  artifact URIs. Messages, snippets, fixes, code flows, properties, absolute paths, and raw results
  are never persisted.
- SCIP and SARIF evidence references files as observations; it does not create causal impact or test
  necessity claims.
- Test execution schema 1 carries a full commit identity, a fixed complete-observed-set policy,
  unique test paths, and unique observed source paths.
- Runtime `tests` relationships are created only when the report commit exactly matches current
  Git HEAD and every mapped test/source file remains tracked and unchanged from HEAD. Stale or
  unknown freshness is visible but cannot influence test recommendations.
- Clean/incremental scans remain equivalent and deterministic; all focused/full, CLI/UI, security,
  vault, Evidence, and Review gates pass before Phase 10B closes.

## Typed links

- drives:: [[Decisions/ADR-023 - Separate observations from aligned execution evidence]]

## Trace

- Roadmap: [[Brain/Product Roadmap]]
- Strategy: [[Brain/Phase 8-10 Strategy]]
- Delivery: [[Issues/ISSUE-021 - Implement bounded open evidence imports]]
