---
id: ADR-038
type: decision
status: accepted
phase: 20
---
# Preserve uncovered change ranges and deletion uncertainty

## Context

Any-overlap completeness and whole-hunk innermost selection lose changes outside a nested symbol.
Dropping zero-count Git ranges can also make a mixed edit/deletion look fully covered.
These cases can produce targeted-only advice without complete evidence.

## Decision

Use symbol interval boundaries to determine the most-specific owners of each changed segment.
Keep a parent when changed lines remain outside its strictly contained children. Verify the union
of symbol intervals covers the entire positive hunk, including gaps and leading/trailing lines.
Do not expand a range into individual line numbers.

Preserve valid Git deletion-only ranges as `DiffHunk(path, start, 0)` in surviving files, including
the Git start-zero form. Shared mapping marks these ranges incomplete and emits no exact symbol
for them. Existing ChangeSet schema 1 fields remain unchanged; count zero is explicitly documented.
Positive ranges still supply independently valid symbol history. File-level ChangeAnalysis fallback
and the existing full-suite strategy handle uncertainty; no scoring or threshold change is needed.

The browser regression selects once after the page is ready, then observes the asynchronous result.
It must not repeatedly clear the rendering it is attempting to verify.

## Consequences

Reports may become more conservative for mixed deletion or module-level changes. That is an
intentional correction, not a regression to hide by adjusting frozen benchmark labels. Consumers
must not assume every serialized hunk has count greater than zero. No source excerpts or old-side
code are persisted. No new package dependency or network requirement is introduced.

## Links

- implements:: [[Requirements/REQ-036 - Require complete change coverage before targeted advice]]
- refines:: [[Decisions/ADR-008 - Conservative diff-to-symbol projection]]
- refines:: [[Decisions/ADR-020 - Separate exact change evidence from fallback]]
- delivered-by:: [[Issues/ISSUE-036 - Close partial hunk deletion and browser regressions]]
