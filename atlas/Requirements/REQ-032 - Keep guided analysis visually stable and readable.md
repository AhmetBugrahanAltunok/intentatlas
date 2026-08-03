---
id: REQ-032
type: requirement
status: accepted
phase: 16
---
# Keep guided analysis visually stable and readable

## User outcome

A user can read the guided source-to-atlas result in PowerShell without a wall of text and can
repeatedly inspect or fit the same interactive Atlas without displacing the page or graph.

## Acceptance

- Phase 15 is accepted at exact synchronized entry
  `5bb46ed42b79e1b35c364083af6a32cbe6e24dfb`; its four owner-observation files are preserved and
  linked into Phase 16.
- The exact `pypa/sampleproject@621e4974ca25ce531773def586ba3ed8e736b3fc` owner sequence is
  reproduced and its measured root cause is recorded.
- Repeated Change Report close/open and Fit Graph activation leaves document scroll, main/stage
  bounds, and the settled graph transform unchanged at wide and narrow viewports.
- Mouse and keyboard interactions pass with ChangeReport present; Fit Graph remains idempotent in
  graph-only mode and existing bounded large-graph behavior remains intact.
- PowerShell output begins with a prominent IntentAtlas heading, groups source/scope, safety,
  analysis, recommendations, Atlas, and next actions, wraps long evidence copy, and renders each
  choice on a separate line without color or cursor control.
- EN/TR preserve the same trust meaning and immutable snapshot. Canonical enums, IDs, commands,
  flags, JSON, exact scope/revision, state, freshness, confidence, reasons, omissions, strategy,
  advisory, and `Tests executed: 0` do not change.
- Non-TTY, no-write, network consent, cache, Private exclusion, package, browser accessibility,
  deterministic output, durable-chain, and remote-CI contracts regress cleanly.
- EVD-032 is complete and the Phase 16 Review passes only after final pushed-HEAD CI is green.
- No Phase 11C, human-usability/time claim, tag, release, publication, deployment, telemetry,
  settings/visibility change, or announcement occurs.

## Typed links

- drives:: [[Decisions/ADR-032 - Prevent focus-driven viewport drift and structure terminal presentation]]
- delivered-by:: [[Issues/ISSUE-030 - Fix cumulative viewer layout drift after report and fit controls]]
- delivered-by:: [[Issues/ISSUE-031 - Improve guided PowerShell readability]]
- proved-by:: [[Evidence/EVD-032 - Phase 16 guided experience stability verification]]
