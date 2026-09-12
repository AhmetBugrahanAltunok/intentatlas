---
id: ISSUE-039
type: issue
status: open
phase: 21C
---
# Resolve the documentation divergence decisions

Four conventions questions were opened; one is closed. They interact, so they should be decided together rather
than closed one at a time. They are project-owner decisions, not implementation work.

- [ ] **English README length.** 675 lines. The first-run path competes with capability lists,
  command reference, status, and inspiration sections. The Phase 22 gate targets a below-ten-minute
  first use, and reading time counts against it. Option: keep the root README to the first-run
  path and move reference material under `docs/`, which already has an index.
- [ ] **Turkish README scope.** `README.tr.md` has no `## What works today` and no `## Core
  commands`. A Turkish reader gets no capability list and no command reference. Options: translate
  both sections, or apply the same split to both languages so neither carries a reference table.
  Expanding the Turkish file before deciding the split above would have to be undone.
- [x] **ADR-034 generated-vault governance.** Closed 2026-09-12 by
  [[Decisions/ADR-042 - Untrack derived vault output and keep commit notes]]. `Symbols/`, `Code/`,
  `Tests/` and `Dashboard/` left the index; they stay on disk and regenerate deterministically.
  `Commits/` stayed tracked because durable notes cite commit notes by name and untracking them
  would break recorded evidence for 70 of 1863 files. Tracked `atlas/` went from 2114 to 321, of
  which 245 are human-written. No file was deleted and no history was rewritten.
- [ ] **Durable relation vocabulary.** The durable notes use `delivered-by::`, `reviewed-by::`,
  `extends::`, and `planned-in::`. None are in the accepted relation catalog, so each degrades to a
  generic `references` edge. No link is lost, but the intent chain carries less meaning than the
  notes appear to declare — which matters for a product whose contract is that links group by
  meaning. Two of the four already have catalog equivalents: `tracked-by` covers intent tracked by
  a delivery item, and `recorded-in` covers a note recorded in a plan. `reviewed-by` and `extends`
  have none. Options: add the missing relations to the catalog, or rewrite the notes onto existing
  vocabulary. Either is a migration across roughly 40 durable notes and should not be applied
  piecemeal. Recorded in the Phase 21A review; `drives::` and `proved-by::` already resolve as
  typed, so the convention is inconsistent rather than uniformly wrong.

Installation and post-failure recovery instructions are already identical across both languages;
that was verified in EVD-039 and needs no change.

## Links

- implements:: [[Requirements/REQ-039 - Deliver a useful first report from a clean install]]
- verified-by:: [[Evidence/EVD-039 - Phase 21C first-run walkthrough verification]]
- reviewed-by:: [[Reviews/Phase 21C First-Run Walkthrough Review]]
- follows:: [[Decisions/ADR-034 - Retain generated vault outputs under single-writer governance]]
