---
id: ADR-042
type: decision
status: accepted
phase: 21G
---
# Untrack derived vault output and keep commit notes

## Context

ADR-034 retained the whole generated vault in Git through Phase 17 and required a separate
governance review before contributor intake. This is that review.

The counts are the argument. Against 51 tracked files under `src/`, `atlas/` carries 2114:

```text
Symbols     1609      derived
Code          97      derived
Tests         86      derived
Dashboard      1      derived
Commits       70      derived, but durable notes link to these by name
durable      245      written by a person
```

Someone opening the repository meets 1609 symbol notes before they meet the product. The
first impression is of the methodology, not the tool. Phase 22 will send independent people to
this URL, so the first impression stops being a matter of taste.

Nothing is lost by untracking derived output: two consecutive scans were verified byte-identical,
so regeneration is deterministic and the files are recoverable by running `scan`.

## Decision

Stop tracking `atlas/Symbols/`, `atlas/Code/`, `atlas/Tests/`, and `atlas/Dashboard/`. They stay on
disk, stay in `.gitignore`, and regenerate deterministically from `intentatlas scan`.

**Keep `atlas/Commits/` tracked.** Durable evidence and session notes cite commit notes by name —
`[[Commits/Commit 041069a - fix- harden analysis reliability and change coverage]]` — and those
links are part of the intent chain this product exists to preserve. Untracking them would break
recorded evidence for anyone who clones, in exchange for removing 70 of 1863 files. The trade is
not worth it. Commit notes are also append-mostly: an existing commit's note is byte-identical on
every rescan, so they do not churn.

Tracked count moves from 2114 to 315, of which 245 are human-written.

No file is deleted from disk and no history is rewritten. `git rm --cached` removes them from the
index only; every past revision still contains them.

## Consequences

- A visitor sees 51 source files against 245 durable notes and 70 commit notes, which is the
  shape the product actually claims.
- Wikilinks from durable notes into `Symbols/`, `Code/`, and `Tests/` do not resolve in a fresh
  clone until `intentatlas scan` runs once. This is the real cost and is documented in the vault
  README path rather than left to be discovered. Links into `Commits/` keep resolving immediately.
- Scans no longer produce diff noise, so a source change is legible in `git status` without
  1800 regenerated notes beside it.
- The repository stops being a browsable snapshot of its own graph on GitHub. That was the
  original ADR-034 benefit and it is genuinely given up; the graph remains inspectable locally
  through `open` and the vault itself.
- A commit note for a revision older than the configured `git_history_limit` will eventually fall
  out of regeneration for new clones. The tracked copies are therefore the durable record, which
  is the second reason to keep them tracked.

## Links

- supersedes:: [[Decisions/ADR-034 - Retain generated vault outputs under single-writer governance]]
- implements:: [[Requirements/REQ-043 - Make the repository legible to a first-time visitor]]
- recorded-in:: [[Evidence/EVD-043 - Phase 21G vault governance verification]]
