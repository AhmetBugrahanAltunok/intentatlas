---
id: review-phase-21g-vault-governance
type: review
status: passed
phase: 21G
---
# Phase 21G Vault Governance Review

Decision: **passed, 2026-09-12**. 684 passed, 4 platform skips, exit 0. Ruff, mypy and Bandit
passed. ADR-034's deferred governance question is answered and ISSUE-039's third item is closed.

## What was decided and why it is not the obvious answer

The obvious move was to untrack the whole generated vault: 1863 files, one command, tracked
`atlas/` down to 245. `Commits/` was kept instead, for a reason that only shows up if you read the
durable notes: evidence and session records cite commit notes by name, and those citations are the
intent chain this product exists to preserve. Untracking them would have broken recorded evidence
for every future clone in exchange for removing 70 of 1863 files.

Tracked `atlas/` went from 2114 to 321, of which 245 are human-written, against 51 under `src/`.

## What the verification actually found

The safety of this decision rests entirely on regeneration, so a clone was made and scanned rather
than trusted. It produced the same counts, and a second scan inside it was byte-identical.

Comparing the clone against the working tree did not match, and both causes are worth keeping:

The workspace owner is named after the checkout directory, so a clone named `clonecheck` produced
82 notes naming `clonecheck`. Generated notes are not portable across differently-named clones.

With the name matched, 23 notes still differed — each only in a recorded `Size Bytes`. The gap for
`CHANGELOG.md` was exactly 239 bytes against exactly 239 lines: CRLF in this Windows working tree
against the LF the repository stores. The 23 files are precisely those edited in this session.

Neither is a defect. Together they say generated notes are deterministic *for a checkout* and not
identical *across* checkouts — which is an argument for regenerating them rather than tracking
them, and would have been easy to miss by asserting determinism instead of measuring it.

## What this gives up

The repository is no longer a browsable snapshot of its own graph on GitHub. That was ADR-034's
stated benefit and it is genuinely surrendered. Wikilinks into `Symbols/`, `Code/` and `Tests/`
need one `scan` before they resolve in a clone.

Both were judged worth it because Phase 22 sends independent people to this URL, and 1609 derived
symbol notes ahead of 51 source files misrepresents what the project is.

## Links

- reviews:: [[Requirements/REQ-043 - Make the repository legible to a first-time visitor]]
- reviews:: [[Decisions/ADR-042 - Untrack derived vault output and keep commit notes]]
- based-on:: [[Evidence/EVD-043 - Phase 21G vault governance verification]]
- follows:: [[Reviews/Phase 21F Readable First Answer Review]]
- governed-by:: [[Brain/Phase Completion Protocol]]
