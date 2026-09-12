---
id: review-phase-21h-documentation-split
type: review
status: passed
phase: 21H
---
# Phase 21H Documentation Split Review

Decision: **passed, 2026-09-12**. 683 passed, 4 platform skips, exit 0, 88.11% branch-enabled total
coverage. Ruff, mypy and Bandit passed. Two of the three remaining ISSUE-039 items are closed.

## What was decided

Both READMEs now stop at the first-run boundary with identical structure: 696 to 242 lines in
English, 559 to 238 in Turkish. Reference material moved to `docs/` behind a documentation table.

The two questions were held together for a reason and it paid off. Deciding the English split
first and the Turkish scope second would have meant translating 130 lines into a file that was
about to lose 393 of its own.

## The finding that changed the work

The Turkish README carried 393 lines of workflows and capability detail that the English one
organised differently. Moving only the English detail into `docs/` would have left Turkish readers
with a shorter page and nowhere to go — a regression introduced while claiming to fix a
divergence. That content was recovered from the committed revision and relocated verbatim, so no
reader loses anything and no translation debt is created.

The remaining asymmetry is deliberate and stated in the table: the command reference is English
only.

## The regression that mattered

Three tests asserting on README content failed. Two were location changes: the benchmark caveat
moved to `docs/commands.md`, and the safe-order test split on a renamed heading. The third had
caught a real defect — the confidence legend had left the READMEs with the moved sections, while
the example output still shows `[medium confidence]`.

A reader who cannot interpret that word is precisely the Phase 22 failure the previous phase was
built to avoid: not someone who gives up, but someone who trusts a number they have not been
taught to read. It was fixed by restoring the legend, not by relocating the assertion. Treating
all three failures as bookkeeping would have shipped it.

## Limits

Parity is now a commitment rather than a property: `workflows` and `capabilities` exist twice and
nothing enforces that an edit to one reaches the other. And shorter is not clearer — whether 242
lines gets a newcomer further than 696 is a Phase 22 question, not something this phase can claim.

## Links

- reviews:: [[Requirements/REQ-044 - Stop both READMEs at the first-run boundary]]
- reviews:: [[Decisions/ADR-043 - Split the READMEs at the first-run boundary]]
- based-on:: [[Evidence/EVD-044 - Phase 21H documentation split verification]]
- follows:: [[Reviews/Phase 21G Vault Governance Review]]
- governed-by:: [[Brain/Phase Completion Protocol]]
