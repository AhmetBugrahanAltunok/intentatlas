---
id: REQ-044
type: requirement
status: accepted
phase: 21H
---
# Stop both READMEs at the first-run boundary

## User outcome

A newcomer in either language reads one short page that gets them to a useful first report, and
finds everything else through a clear index. Neither language is the poor relation.

## Acceptance

- Both READMEs carry the same sections in the same order and stop at the first-run boundary.
- Reference material lives under `docs/`, reachable from a documentation table in both READMEs.
- The Turkish README gains the capability list it lacked, closing the recorded divergence.
- No Turkish content is lost: the Turkish detail is relocated verbatim, not dropped or deferred
  to translation.
- The confidence legend stays in both READMEs, because the example output shows a confidence word
  the reader cannot otherwise interpret.
- The safe command order — demo, diagnose, changes, init — survives in both.
- Every relative link in both READMEs and every moved document resolves.
- The full suite, Ruff, mypy, and Bandit pass.

## Links

- drives:: [[Decisions/ADR-043 - Split the READMEs at the first-run boundary]]
- proved-by:: [[Evidence/EVD-044 - Phase 21H documentation split verification]]
- reviewed-by:: [[Reviews/Phase 21H Documentation Split Review]]
