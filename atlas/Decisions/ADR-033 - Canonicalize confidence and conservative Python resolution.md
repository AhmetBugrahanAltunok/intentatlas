---
id: ADR-033
type: decision
status: accepted
phase: 17
---
# Canonicalize confidence and conservative Python resolution

## Context

An external evaluation at Phase 16 head exposed four confirmed interacting defects: ChangeReport
used 70/90 bands instead of ADR-009's 65/85 bands, did not threshold test candidates, Python
workspace discovery assigned `.` to Flit/Hatchling src layouts, and one exact import plus a weak
filename second hop was scored as if the whole path were structural. This allowed an empty package
marker to displace the real caller. The same source-root mismatch suppressed nearly all self-scan
Python exact-symbol test edges. A recent bulk commit also gave unrelated co-change tests score 70.

## Decision

Use one internal confidence classifier and rank table everywhere: high is `85+`, medium is `65-84`,
and low is `0-64`. Correcting a surface to this already documented stable meaning does not require
a schema bump. ChangeReport applies the threshold before the result limit and before execution
strategy selection, and records low-confidence omissions additively in schema 1.

Discover Python source roots only from bounded declarations or unique repository shape:
setuptools `package-dir`/find, Hatch wheel package paths, Flit module names aligned to one `src`
package, or one project-local `src` tree with Python content. Resolve qualified attributes by the
longest unique local module prefix and one unique top-level symbol. Preserve eight-hop cycle-safe
re-export resolution. Any ownership, module, direct/re-export, or symbol collision abstains.

Candidate eligibility is separate from graph kind. A zero-byte test node is not runnable. For
one-hop dependent recommendations, the path score cannot exceed its weakest hop: filename-only or
a package-initializer re-export without a direct test-symbol edge is 45, while structural direct
dependency remains 65. Co-change is historical correlation, not exact dependency: commits changing
more than 20 artifacts are excluded, bounded narrow co-change scores 60, and recurrence may add
explanations but never raises confidence above low.

Reason copy says no *resolved exact-symbol graph edge* was found; it does not claim the source has
no exact call. Historical stale reports add a clean revision-matched checkout action. Diagnostic
root counts remain heuristic readiness data and explicitly do not assert resolver abstention.

## Consequences

- Existing stable JSON shapes remain schema 1; corrected confidence values and omission contents
  now match their documented meanings. Additive actionable diagnostic/report fields are permitted.
- Experimental workspace/adapter graph material changes deterministically and can be regenerated.
- Precision is preferred over recall when declarations or qualified chains are not unique.
- Frozen evaluation partitions and labels are not changed; before/after metrics expose the effect.

## Links

- requirement:: [[Requirements/REQ-033 - Preserve recommendation integrity across supported surfaces]]
- preserves:: [[Decisions/ADR-009 - Evidence-ranked test recommendations]]
- refines:: [[Decisions/ADR-018 - Bound dependency propagation with exact symbols and co-change]]
- preserves:: [[Decisions/ADR-027 - Freeze pilot evidence before recommendation tuning]]
- tracked-by:: [[Issues/ISSUE-032 - Implement recommendation integrity and Python resolution]]
