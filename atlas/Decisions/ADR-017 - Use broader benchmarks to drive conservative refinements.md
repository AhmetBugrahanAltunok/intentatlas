---
id: ADR-017
type: decision
status: accepted
phase: 7B
---
# ADR-017 — Use broader benchmarks to drive conservative refinements

## Context

Three small projects with one relevant test each produced perfect medium-threshold results after
the Go same-package improvement. That result did not exercise source-only commits, multiple test
layers, barrel imports, or a Go package imported by many unrelated tests. A first wider run exposed
18 Cobra false positives and five Axios false negatives that the small set could not reveal.

## Decision

Add pinned cases from Pallets Click, Axios, and Cobra under their original BSD-3-Clause, MIT, and
Apache-2.0 licenses. Keep acquisition separate and evaluation offline under ADR-015. Preserve
manual complete-test-set labels even when they lower aggregate metrics.

Correct only the directly evidenced low-risk defect: for Go test files, replace package-wide local
import edges with unique exported symbol references. Resolve default aliases from the target
package declaration, honor explicit and dot imports, and omit blank, unresolved, or ambiguous
imports. Keep non-test source imports package-wide because they describe implementation structure
rather than a test-necessity claim.

Do not add transitive JavaScript/Python traversal merely to recover the Axios misses or tune scores
to improve the report. Carry those gaps forward for a separately bounded architecture decision.

## Consequences

- The benchmark now exposes realistic precision and recall limits instead of preserving a perfect
  small-sample result.
- Cobra's unrelated documentation tests no longer attach to every root-package file.
- Click retains one explainable file-level false positive per case, and Axios retains five
  indirect-dependency false negatives.
- Blank-import initialization and unexported/ambiguous Go behavior can be omitted by design.

## Links

- Requirement: REQ-017 (available through the incoming `drives` relationship)
- tracked-by:: [[Issues/ISSUE-015 - Expand and refine real-world validation]]
