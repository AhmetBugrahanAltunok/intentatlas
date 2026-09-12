---
id: EVD-044
type: evidence
status: verified
phase: 21H
---
# Phase 21H documentation split verification

Local decision: **verified, 2026-09-12**. Complete suite: **683 passed, 4 skipped**, exit **0**,
branch-enabled total coverage **88.11%**. Ruff, mypy (50 source files) and Bandit passed.

## Before and after

| | Before | After |
| --- | --- | --- |
| `README.md` | 696 lines, 9 sections | 242 lines, 7 sections |
| `README.tr.md` | 559 lines, 6 sections | 238 lines, 7 sections |
| Structural parity | English had `What works today` and `Core commands`; Turkish had neither | identical section sequence |

New documents: `docs/commands.md` (245), `docs/workflows.md` (159), `docs/capabilities.md` (102),
`docs/workflows.tr.md` (321), `docs/capabilities.tr.md` (86).

## No content was lost

The split was performed with line accounting rather than by hand. Every one of the 696 English
lines was assigned to exactly one destination and the partition was asserted to sum back to 696
before anything was written. The Turkish 559 lines were partitioned the same way.

The Turkish detail — 393 lines of workflows and capability inventory that the Turkish README
carried — was recovered from the committed revision and relocated verbatim into
`workflows.tr.md` and `capabilities.tr.md`. Moving only the English detail would have quietly cost
Turkish readers material they already had; that was noticed during the split, not afterwards.

`README.tr.md` gained a translated `Bugün ne çalışıyor`, which is the divergence ISSUE-039
originally recorded.

## Links

Relocating content broke every root-relative link inside it: `](docs/x.md)` no longer resolves from
inside `docs/`. All five moved documents were rewritten — `docs/` prefixes dropped, root files
repointed to `../`. A checker then resolved every relative link in both READMEs and all fifteen
`docs/*.md` files against the filesystem: **no broken targets**.

## Three regressions that guarded the documentation

| Test | What it guards | Outcome |
| --- | --- | --- |
| `test_frozen_pilot_metadata_and_benchmark_card_match` | the longitudinal benchmark caveat, hashes and command are documented | content moved to `docs/commands.md`; the assertion now reads that file |
| `test_trust_first_documentation_sequence_and_artifacts_are_frozen` | `demo` before `diagnose` before `changes` before ` init ` | the order survives in the renamed section; the split anchor was updated and the ordering re-verified in both languages |
| `test_low_mode_and_static_direct_reference_tiers_are_explained` | both READMEs explain `exploratory`, `medium or higher`, `80/medium` | **a real regression** — the confidence legend had left the READMEs with the moved sections |

The third is the one worth recording. The example output shows `[medium confidence]`; a reader who
cannot interpret that word is exactly the Phase 22 failure mode the previous phase was built to
avoid. It was fixed by restoring a compact legend to both READMEs, not by moving the assertion to
wherever the text had landed. Two of the three tests were location changes; one had caught a
defect, and treating all three the same way would have shipped it.

## Acceptance and verification

| Acceptance | Evidence | Result |
| --- | --- | --- |
| Identical section sequence | 7 sections each, same order | passed |
| Reference material reachable | documentation table in both; `docs/index.md` lists the new files with Turkish variants | passed |
| Turkish capability list exists | `## Bugün ne çalışıyor`, 34 items | passed |
| No Turkish content lost | 393 lines relocated verbatim from the committed revision | passed |
| Confidence legend retained | present in both; regression asserts the exact terms in both languages | passed |
| Safe command order retained | asserted programmatically in both READMEs, and by the trust-first regression | passed |
| Every link resolves | checker over both READMEs and all `docs/*.md`: no broken targets | passed |
| Quality gates | 683 passed / 4 skips, 88.11%; Ruff, mypy, Bandit | passed |

## Limitations

- Parity is now a maintenance commitment, not a property. `workflows` and `capabilities` exist in
  two languages and nothing enforces that a change to one reaches the other.
- The command reference is English-only by decision. A Turkish reader following the documentation
  table reaches an English page there, which the table states.
- Shorter is not the same as clearer. Whether 242 lines actually gets a newcomer further than 696
  is a Phase 22 question and is not established here.

## Links

- proves:: [[Requirements/REQ-044 - Stop both READMEs at the first-run boundary]]
- follows:: [[Decisions/ADR-043 - Split the READMEs at the first-run boundary]]
- reviewed-in:: [[Reviews/Phase 21H Documentation Split Review]]
