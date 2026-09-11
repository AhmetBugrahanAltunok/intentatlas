---
id: ISSUE-039
type: issue
status: open
phase: 21C
---
# Resolve the documentation divergence decisions

Three documentation questions are open. They interact, so they should be decided together rather
than closed one at a time. All three are project-owner decisions, not implementation work.

- [ ] **English README length.** 675 lines. The first-run path competes with capability lists,
  command reference, status, and inspiration sections. The Phase 22 gate targets a below-ten-minute
  first use, and reading time counts against it. Option: keep the root README to the first-run
  path and move reference material under `docs/`, which already has an index.
- [ ] **Turkish README scope.** `README.tr.md` has no `## What works today` and no `## Core
  commands`. A Turkish reader gets no capability list and no command reference. Options: translate
  both sections, or apply the same split to both languages so neither carries a reference table.
  Expanding the Turkish file before deciding the split above would have to be undone.
- [ ] **ADR-034 generated-vault governance.** Still required before contributor intake. 1944
  tracked files under `atlas/` against 51 under `src/`. Compare tracked snapshots, artifact
  publication, and local-only generation on durable-link preservation and migration cost. Do not
  bulk delete or untrack.

Installation and post-failure recovery instructions are already identical across both languages;
that was verified in EVD-039 and needs no change.

## Links

- implements:: [[Requirements/REQ-039 - Deliver a useful first report from a clean install]]
- verified-by:: [[Evidence/EVD-039 - Phase 21C first-run walkthrough verification]]
- reviewed-by:: [[Reviews/Phase 21C First-Run Walkthrough Review]]
- follows:: [[Decisions/ADR-034 - Retain generated vault outputs under single-writer governance]]
