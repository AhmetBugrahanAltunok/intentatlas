---
id: ADR-028
type: decision
status: proposed
phase: 12
---
# ADR-028 - Make the change report the primary product surface

## Context

The packaged synthetic demo proves the recommendation contract quickly, but the current real-
repository quick start leads with initialization, scanning, and a generic graph. A fresh vault has
no project-specific intent, so a first scan can resemble an ordinary code graph before the user
experiences the Requirement -> Decision -> Code -> Test value.

The existing revision-scoped change report already carries the stronger product truth: scope,
alignment, freshness, requirement impact, ranked and filtered tests, evidence paths, and safe
fallback strategy. Terminal output exposes more of that reasoning than the current viewer panel.

## Decision

Make a zero-footprint change report the primary real-repository entry point. Reuse the existing
fresh in-memory scan, ChangeSet, analysis, report, and loopback-viewer snapshot rather than creating
a second recommendation engine or truth store.

Add a read-only diagnostic projection over existing configuration, discovery capability, adapter
support, source-root ambiguity, evidence freshness, and artifact availability. It may inspect only
the same bounded metadata and supported source paths already permitted by the scanner. It does not
save missing configuration, initialize a vault, populate a cache, materialize a graph, or inspect
Private.

Define one versioned diagnostic JSON schema and extend the existing report/view model so text,
JSON, and UI expose:

- revision, scope, alignment, and freshness;
- analyzed, fallback, and unknown coverage;
- minimum threshold, shown/total/filtered candidate counts, score, and confidence;
- exact evidence/relation tags and bounded paths used for ranking;
- selected, omitted, and insufficient-evidence explanations;
- targeted, targeted-plus-full-suite, full-suite-fallback, or abstain strategy;
- an explicit statement that absence is not proof of no impact.

Keep the graph as a bounded drill-down projection of that same immutable in-memory snapshot. A
report selection may navigate to supporting nodes, but a generic shortest path must not be
presented as the ranking reason unless it is the recorded recommendation path.

Documentation offers two distinct promises: evaluate the deterministic synthetic product contract
without touching a repository, then preview a real repository without initialization. Persistent
`init`/`scan` adoption follows only after the user understands the no-write result.

## Consequences

- The first-run path becomes useful even before the user authors durable intent notes.
- Existing change intelligence receives greater UI and documentation importance without another
  scoring implementation.
- No-write behavior becomes a tested product contract rather than an incidental implementation
  detail.
- The viewer requires more explicit report state and omission UX but less emphasis on graph
  cosmetics.
- Human usability observations become a phase gate and may expose documentation work that cannot
  be solved by code alone.
- Persistent adoption still requires deliberate user-authored links; IntentAtlas will explain that
  step instead of silently manufacturing project intent.

## Links

- Requirement: REQ-028 (available through the incoming `drives` relationship)
- tracked-by:: [[Issues/ISSUE-026 - Implement zero-footprint onboarding and trust-first reporting]]
- Change intelligence decision: [[Decisions/ADR-020 - Separate exact change evidence from fallback]]
- Viewer decision: [[Decisions/ADR-024 - Validate adapters and render bounded graph windows]]
- Strategy: [[Brain/Phase 11B-13 Delivery Strategy]]
