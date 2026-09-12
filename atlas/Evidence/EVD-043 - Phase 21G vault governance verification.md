---
id: EVD-043
type: evidence
status: verified
phase: 21G
---
# Phase 21G vault governance verification

Local decision: **verified, 2026-09-12**. Complete suite: **684 passed, 4 skipped**, exit **0**.
Ruff, mypy and Bandit passed.

## What changed

| Area | Files | Tracked after |
| --- | --- | --- |
| `atlas/Symbols/` | 1609 | no |
| `atlas/Code/` | 97 | no |
| `atlas/Tests/` | 86 | no |
| `atlas/Dashboard/` | 1 | no |
| `atlas/Commits/` | 70 | **yes** |
| durable notes | 245 | yes |

Tracked `atlas/` moved from 2114 to 321 against 51 tracked files under `src/`. `git rm --cached`
touched the index only: 1793 files left the index, none left the disk, and no history was
rewritten.

## Fresh-clone verification

The claim that makes this safe is that a clone regenerates the derived vault. It was tested, not
asserted.

A clone of the committed repository contained `Commits/` (70 files) and none of `Symbols/`,
`Code/`, `Tests/` or `Dashboard/`. One `intentatlas scan` produced 1863 generated notes: 1609,
97, 86 and 1 respectively — the same counts as the working tree. A second scan inside that clone
was **byte-identical** to the first, so regeneration is deterministic per checkout.

## Two ways regenerated output legitimately differs between checkouts

Comparing the clone against the working tree showed differences. Both were explained rather than
waved away, and both are properties worth knowing.

**Repository directory name.** A clone into a directory named `clonecheck` produced 82 notes
differing from the working tree, all carrying the workspace owner name:
`[[Code/clonecheck|clonecheck]]` against `[[Code/IntentAtlas - c1f62610|IntentAtlas]]`. The
workspace boundary is named after the checkout directory, so generated notes are not portable
across differently-named clones.

**Working-tree line endings.** Cloning into a directory named `IntentAtlas` reduced the difference
to 23 notes, each differing only in a recorded `Size Bytes` field — for example `18332` against
`18571` for `CHANGELOG.md`. The gap is exactly 239 bytes and `CHANGELOG.md` has exactly 239 lines,
so the cause is CRLF in this Windows working tree against the LF the repository stores under
`.gitattributes`. The 23 affected notes are precisely the files edited in this session. Nothing in
the product is non-deterministic; it is recording a real byte size of a real local file.

Generated notes are therefore deterministic **for a given checkout**, not identical **across**
checkouts. That is a reason to regenerate rather than to track them, so it supports the decision
rather than undermining it.

## Acceptance and verification

| Acceptance | Evidence | Result |
| --- | --- | --- |
| Derived areas leave the index, stay on disk | 1793 index deletions; 1609 files still present under `atlas/Symbols/` | passed |
| A fresh clone regenerates them | Clone scanned to 1609/97/86/1, matching counts | passed |
| Regeneration is deterministic | Two scans inside the clone byte-identical | passed |
| Commit notes still resolve in a clone | `Commits/` present in the clone with 70 files before any scan | passed |
| Nothing deleted, no history rewritten | `git rm --cached` only; files on disk; past revisions unchanged | passed |
| Human-written content dominates | 245 durable of 321 tracked `atlas/` files | passed |
| Differences measured, not assumed | Directory-name and CRLF causes both isolated to exact counts | passed |
| Quality gates | 684 passed / 4 skips; Ruff, mypy, Bandit | passed |

## The cost this accepts

Wikilinks from durable notes into `Symbols/`, `Code/` and `Tests/` do not resolve in a fresh clone
until `scan` runs once. Links into `Commits/` resolve immediately, which is why those 70 files
stayed tracked. The repository also stops being a browsable snapshot of its own graph on GitHub —
the original ADR-034 benefit, given up deliberately.

## Links

- proves:: [[Requirements/REQ-043 - Make the repository legible to a first-time visitor]]
- follows:: [[Decisions/ADR-042 - Untrack derived vault output and keep commit notes]]
- reviewed-in:: [[Reviews/Phase 21G Vault Governance Review]]
