---
id: ISSUE-030
type: issue
status: in-progress
phase: 16
---
# Fix cumulative viewer layout drift after report and fit controls

## Owner observation

On 2026-08-03, the owner completed the real public source-to-atlas flow for
`https://github.com/pypa/sampleproject` and opened the immutable loopback viewer. The acquired
revision shown by the guided session was `621e4974ca25ce531773def586ba3ed8e736b3fc`.

After using **Change report** and **Fit graph** repeatedly, the page/graph layout was reported to
shift cumulatively instead of returning to one stable fitted layout. The supplied screenshot shows
the Change Report panel open and the graph/viewer region displaced with unused viewport space.

This is an owner field observation, not an independent Phase 11C human-usability observation.

## Phase 16 diagnosis

Controlled reproduction at the exact revision measured a 372-pixel horizontal document shift:
`main.x` moved from `0` to `-372` and `stage.x` from `236` to `-136`, while the SVG transform stayed
unchanged. The report open path focused its close button before the animated offscreen transform
had completed, causing native browser focus scrolling. This was page displacement, not accumulated
Fit Graph transform arithmetic.

## Reproduction target

1. Run the guided public-repository flow for the exact cached revision above.
2. Open action `4`, the exact immutable interactive Atlas.
3. Alternate **Change report** and **Fit graph** repeatedly without resizing the browser.
4. Compare the graph transform, panel bounds, control alignment, and unused viewport area after
   each repetition.
5. Repeat in the supported Chrome-family browser at wide and narrow viewport sizes and with
   keyboard activation.

## Expected behavior

- **Change report** toggles one bounded panel without cumulative page or canvas displacement.
- **Fit graph** is idempotent for an unchanged graph, panel state, and viewport.
- Repeating either control keeps the graph within the visible stage and the controls aligned.
- Closing and reopening the report restores the same stable transform for the same state.
- Mouse and keyboard activation have equivalent, responsive behavior.

## Acceptance criteria

- [x] Reproduce the owner-observed sequence or record bounded evidence explaining why it cannot be
      reproduced.
- [x] Identify whether drift originates in panel layout, viewport measurement, accumulated SVG
      transform state, transition timing, or another verified cause.
- [x] Make repeated report-toggle/fit sequences deterministic and idempotent without weakening
      bounded large-graph behavior.
- [x] Add a real-browser regression that repeats the sequence and asserts stable viewport,
      transform, controls, and interaction responsiveness.
- [x] Cover wide, narrow, mouse, keyboard, ChangeReport-present, and no-ChangeReport states.
- [ ] Run focused browser tests and the complete quality/security/package/viewer suite before
      closure.
- [ ] If reproduction confirms a Phase 15 viewer acceptance regression, reopen the affected
      Evidence/Review decision until the fix and remote CI pass.

## Links

- observed-in:: [[Sessions/2026-08-03 - Owner viewer layout observation]]
- follows:: [[Issues/ISSUE-029 - Implement frictionless source-to-atlas onboarding]]
- requirement:: [[Requirements/REQ-024 - Keep adapters trustworthy and large graphs responsive]]
- phase-evidence:: [[Evidence/EVD-031 - Phase 15 source-to-atlas verification]]
- phase-review:: [[Reviews/Phase 15 Source-to-Atlas Review]]
- implements:: [[Requirements/REQ-032 - Keep guided analysis visually stable and readable]]
- decided-by:: [[Decisions/ADR-032 - Prevent focus-driven viewport drift and structure terminal presentation]]
- planned-evidence:: [[Evidence/EVD-032 - Phase 16 guided experience stability verification]]
- reviewed-by:: [[Reviews/Phase 16 Guided Experience Stability Review]]
