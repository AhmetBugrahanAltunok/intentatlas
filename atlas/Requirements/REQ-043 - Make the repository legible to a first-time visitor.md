---
id: REQ-043
type: requirement
status: accepted
phase: 21G
---
# Make the repository legible to a first-time visitor

## User outcome

Someone who opens the repository before Phase 22 sees the product and the reasoning behind it,
not 1609 derived symbol notes. The durable intent chain that the project exists to demonstrate
stays intact and stays linked.

## Acceptance

- Derived vault areas leave the Git index while remaining on disk and in `.gitignore`.
- A fresh clone regenerates them from one `intentatlas scan`, and two scans inside that clone are
  byte-identical.
- Commit notes stay tracked, because durable evidence and session notes cite them by name and
  those links must resolve in a fresh clone.
- No file is deleted from disk and no history is rewritten; every past revision still contains
  the derived output.
- The remaining tracked `atlas/` content is dominated by human-written notes.
- Any way in which regenerated output legitimately differs between checkouts is measured and
  recorded rather than claimed to be absent.
- The full suite, Ruff, mypy, and Bandit pass.

## Links

- drives:: [[Decisions/ADR-042 - Untrack derived vault output and keep commit notes]]
- proved-by:: [[Evidence/EVD-043 - Phase 21G vault governance verification]]
- reviewed-by:: [[Reviews/Phase 21G Vault Governance Review]]
- planned-in:: [[Brain/Alpha Release Execution Plan]]
