---
id: session-2026-08-03-owner-viewer-layout-observation
type: session
status: complete
phase: 15
---
# Owner viewer layout observation

## Context

- Observer: project owner.
- Date: 2026-08-03.
- Entry: current IntentAtlas `0.3.0rc1` guided public-repository flow from PowerShell.
- Public source: `https://github.com/pypa/sampleproject`.
- Exact displayed revision: `621e4974ca25ce531773def586ba3ed8e736b3fc`.
- Viewer: explicit action `4`, serving the same immutable graph/ChangeReport snapshot.
- Browser family/version, zoom, resize history, and exact repetition count: not recorded.

## Observation

The repository acquisition and analysis completed, reporting `44` nodes, `46` relationships, and
`7` disconnected nodes. The owner then opened the interactive Atlas. Repeated use of **Change
report** and **Fit graph** caused a visible cumulative layout/graph shift rather than a stable fitted
state. A screenshot supplied in the session showed the Change Report panel open, the graph/viewer
region displaced, and unused space at the right side of the viewport.

No diagnosis or performance claim is derived from the screenshot alone. The observation is routed
to [[Issues/ISSUE-030 - Fix cumulative viewer layout drift after report and fit controls]] for
controlled reproduction and a real-browser regression.

## Validation classification

This is useful owner first-use evidence, but it is not an independent participant observation and
does not satisfy or reduce the Phase 11C five-person usability gate. It also does not record an
elapsed completion time.

## Links

- reports:: [[Issues/ISSUE-030 - Fix cumulative viewer layout drift after report and fit controls]]
- follows:: [[Sessions/2026-08-03 - Phase 15 source-to-atlas handoff]]
- evidence-context:: [[Evidence/EVD-031 - Phase 15 source-to-atlas verification]]

