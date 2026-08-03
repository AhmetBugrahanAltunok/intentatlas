---
id: ADR-032
type: decision
status: accepted
phase: 16
---
# Prevent focus-driven viewport drift and structure terminal presentation

## Context

The Phase 15 owner flow exposed two presentation failures without exposing a second analysis truth.
Opening the animated report panel focused its close control while that control was still
transformed outside the viewport, so browser focus scrolling displaced the entire document even
though SVG fit state was unchanged. The guided terminal preserved all Phase 14/15 semantics, but
presented headings, result facts, evidence, and choices as an undifferentiated stream.

## Decision

Keep the existing absolute report overlay, graph simulation, fit calculation, production
ChangeReport, and immutable graph/report bytes. When focus moves between report controls, request
focus without document scrolling. Do not counter-transform the graph, reset user pan/zoom, add a
second fit state, or move the panel into a separate frontend.

Keep the guided CLI's line-oriented `TerminalIO` and sanitizer. Add only a presentation projection:
an ASCII-safe banner, explicit semantic sections, bounded wrapping after sanitization, and one
choice per line. Do not add ANSI color, full-screen TUI behavior, terminal-width probing, cursor
animation, or a runtime dependency. The projection reorganizes copy; it does not alter canonical
values, analysis, recommendation, consent, no-write, or snapshot semantics.

## Consequences

- `focus({preventScroll: true})` preserves keyboard focus and screen-reader dialog behavior while
  removing the verified horizontal page-scroll side effect.
- A settled unchanged graph has one repeatable fit transform. Initial force-layout movement remains
  intentional and is separated from viewport-drift assertions in real-browser tests.
- Long terminal facts are easier to scan while still available in full; option keys remain stable.
- The Phase 14/15 guided presentation remains experimental, so this readability-only layout change
  does not migrate stable CLI JSON or explicit command contracts.

## Links

- requirement: [[Requirements/REQ-032 - Keep guided analysis visually stable and readable]]
- tracked-by: [[Issues/ISSUE-030 - Fix cumulative viewer layout drift after report and fit controls]]
- tracked-by: [[Issues/ISSUE-031 - Improve guided PowerShell readability]]
- preserves: [[Decisions/ADR-028 - Make the change report the primary product surface]]
- preserves: [[Decisions/ADR-030 - Layer a TTY-guided flow over deterministic contracts]]
- preserves: [[Decisions/ADR-031 - Acquire explicit public repositories into a managed local cache]]
- strategy: [[Brain/Phase 16 Guided Experience Stability Strategy]]
