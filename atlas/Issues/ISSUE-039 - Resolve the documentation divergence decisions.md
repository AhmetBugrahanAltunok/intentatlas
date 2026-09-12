---
id: ISSUE-039
type: issue
status: open
phase: 21C
---
# Resolve the documentation divergence decisions

Four conventions questions were opened; three are closed and one remains. They interact, so they should be decided together rather
than closed one at a time. They are project-owner decisions, not implementation work.

- [x] **English README length.** Closed 2026-09-12 by
  [[Decisions/ADR-043 - Split the READMEs at the first-run boundary]]: 696 to 242 lines, reference
  material moved to `docs/commands.md`, `docs/workflows.md` and `docs/capabilities.md`.
- [x] **Turkish README scope.** Closed with the same decision. `README.tr.md` is 238 lines with the
  identical section sequence and a translated `Bugün ne çalışıyor`. Its 393 lines of existing
  detail were relocated verbatim to `docs/workflows.tr.md` and `docs/capabilities.tr.md` rather
  than dropped, so no Turkish reader loses material.
- [x] **ADR-034 generated-vault governance.** Closed 2026-09-12 by
  [[Decisions/ADR-042 - Untrack derived vault output and keep commit notes]]. `Symbols/`, `Code/`,
  `Tests/` and `Dashboard/` left the index; they stay on disk and regenerate deterministically.
  `Commits/` stayed tracked because durable notes cite commit notes by name and untracking them
  would break recorded evidence for 70 of 1863 files. Tracked `atlas/` went from 2114 to 321, of
  which 245 are human-written. No file was deleted and no history was rewritten.
- [ ] **Durable relation vocabulary.** Measured 2026-09-12; the description below replaces the
  original one, which under-stated the problem as four labels across roughly forty notes.

  **655 typed links, 50 distinct labels, 16 catalog relation types. 300 links — 46% — do not
  resolve and degrade to a generic `references` edge.**

  | Class | Links | Examples |
  | --- | --- | --- |
  | resolves today | 355 (54%) | `implemented-by` 135, `proves` 64, `drives` 39, `tracked-by` 33 |
  | concept the catalog lacks | 141 (22%) | `reviewed-by` 37, `follows` 25, `reviews` 16, `extends` 12 |
  | different word for a catalog concept | 117 (18%) | `verified-by` 44, `delivered-by` 17, `proved-by` 14 |
  | a noun, not a relation | 42 (6%) | `strategy` 10, `evidence` 9, `requirement` 8, `review` 6 |

  A first pass assumed the 117 were a safe mechanical rename. Checking the actual direction and
  source type of each showed that is wrong for most of them. Only `proved-by` (14, Requirements to
  Evidence) is a certain variant of the catalog's `proven-by`, and `delivered-by` (17, to Issues)
  is a defensible use of `tracked-by`. The rest carry meanings the catalog does not have:
  `verified-by` runs from an Issue to a test *file*, not from a claim to evidence; `decided-by`
  runs from an Issue to a Decision, which is neither `drives` nor `driven-by`; `planned-evidence`
  names evidence that does not exist yet, so it is not `proven-by`; `reviewed-in` runs from
  Evidence to a Review, which has no catalog relation at all.

  So roughly 30 links are a safe rename and about 270 need a vocabulary decision.

  The fallback itself is not a defect. ADR-003 made unknown labels degrade to `references`
  deliberately, so vault text cannot inject arbitrary relation types into the graph. The question
  is whether the documented vocabulary should grow to carry the human intent layer, since the
  catalog's 16 types were designed for scanner-generated structure — `defines`, `imports`,
  `calls`, `modifies`, `owns` — with only a thin intent layer on top.

  Options, in increasing cost:
  1. **Rename only the certain variants** (~30 links). No schema change. Resolution 54% to 59%.
     Leaves the real gap recorded and unfixed.
  2. **Extend the catalog** by roughly four types — `reviews`/`reviewed-by`, `follows`,
     `refines` (covering `extends`), `plans`/`planned-in` — then normalise onto the larger
     vocabulary. Relation schema 5 to 6; existing caches are rebuildable so no stored-data
     migration, but it is a documented compatibility event. Resolution would reach roughly 90%.
  3. **Normalise every note onto the existing 16 types**, accepting that several links lose
     meaning or become plain `references`. No schema change, largest edit, worst fidelity.

  Recommended: option 2. The product's contract is that links group by meaning, and 46% of its
  own intent chain currently does not. Option 1 leaves the headline problem intact; option 3
  discards meaning to protect a vocabulary that was never designed for this layer.

Installation and post-failure recovery instructions are already identical across both languages;
that was verified in EVD-039 and needs no change.

## Links

- implements:: [[Requirements/REQ-039 - Deliver a useful first report from a clean install]]
- verified-by:: [[Evidence/EVD-039 - Phase 21C first-run walkthrough verification]]
- reviewed-by:: [[Reviews/Phase 21C First-Run Walkthrough Review]]
- follows:: [[Decisions/ADR-034 - Retain generated vault outputs under single-writer governance]]
