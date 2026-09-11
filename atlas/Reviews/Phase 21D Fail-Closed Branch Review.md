---
id: review-phase-21d-fail-closed-branches
type: review
status: passed
phase: 21D
---
# Phase 21D Fail-Closed Branch Review

Decision: **passed, 2026-09-11**. 637 passed, 4 platform skips, exit 0, 87.60% branch-enabled
total coverage. Ruff, mypy and Bandit passed. No runtime module was modified; this sub-phase adds
evidence for behaviour that already existed.

## What changed in what is known

Before: the product documented abstention at every bound, and the modules implementing those
bounds were the least covered in the project. `viewer.py` served four query routes and an error
contract that no in-process test ever called. `bounded_process.py` had seven distinct fail-closed
exits, most unproven. `change_set.py`'s text renderer had no direct test at all.

After: the viewer's served surface is exercised over real HTTP in process, every bounded-process
refusal has a case, and ChangeSet rendering and freshness abstention are pinned. The aggregate
moved little — 86.47% to 87.60% — which is the point: the modules that moved are the ones whose
uncovered lines were load-bearing.

## Worth keeping

Two findings are recorded in EVD-040 rather than buried:

A malformed-query case uses a percent-encoded Arabic-Indic digit, because `str.isdigit()` accepts
it while the code's `isascii()` guard does not. The guard was correct; nothing had ever
demonstrated it.

The uncollectable-child test passed on first run while coverage still showed the block it targeted
as unexercised. A direct probe established that the intended path did run and that the remaining
gap was a different branch — the reader-still-alive cleanup — which needed a genuinely new
scenario: a descendant holding the stdout pipe after the parent exits cleanly. A green assertion
was not evidence that the intended code ran, and treating it as such would have left the only
path through that branch untested.

## Limits of this evidence

Coverage is not correctness. These tests fix current behaviour at the boundaries; they do not
argue the boundaries are correctly chosen. The residual `bounded_process.py` gap is platform-gated
in both directions and cannot be closed on one operating system without mocking the operating
system, which would prove the mock. `acquisition.py` at 76% and `longitudinal.py` at 75% remain.

## Links

- reviews:: [[Requirements/REQ-040 - Prove the fail-closed branches rather than assert them]]
- based-on:: [[Evidence/EVD-040 - Phase 21D fail-closed branch verification]]
- follows:: [[Reviews/Phase 21C First-Run Walkthrough Review]]
- governed-by:: [[Brain/Phase Completion Protocol]]
