---
id: review-phase-21d-fail-closed-branches
type: review
status: passed
phase: 21D
---
# Phase 21D Fail-Closed Branch Review

Decision: **passed, 2026-09-11**. 641 passed, 4 platform skips, exit 0, 87.70% branch-enabled
total coverage. Ruff, mypy and Bandit passed. No runtime module was modified; this sub-phase adds
evidence for behaviour that already existed.

## What changed in what is known

Before: the product documented abstention at every bound, and the modules implementing those
bounds were the least covered in the project. `viewer.py` served four query routes and an error
contract that no in-process test ever called. `bounded_process.py` had seven distinct fail-closed
exits, most unproven. `change_set.py`'s text renderer had no direct test at all.

After: the viewer's served surface is exercised over real HTTP in process, every bounded-process
refusal has a case, ChangeSet rendering and freshness abstention are pinned, and acquisition's
local-protocol refusal has its first test. The aggregate moved little — 86.47% to 87.70% —
which is the point: the modules that moved are the ones whose uncovered lines were load-bearing.

## Worth keeping

Three findings are recorded in EVD-040 rather than buried:

A malformed-query case uses a percent-encoded Arabic-Indic digit, because `str.isdigit()` accepts
it while the code's `isascii()` guard does not. The guard was correct; nothing had ever
demonstrated it.

The uncollectable-child test passed on first run while coverage still showed the block it targeted
as unexercised. A direct probe established that the intended path did run and that the remaining
gap was a different branch — the reader-still-alive cleanup — which needed a genuinely new
scenario: a descendant holding the stdout pipe after the parent exits cleanly. A green assertion
was not evidence that the intended code ran, and treating it as such would have left the only
path through that branch untested.

A third finding came from a task that could not be completed as planned. Covering
`acquisition.py`'s clone path offline turned out to be impossible, because the transport sets
`protocol.file.allow=never` and refuses local and `file://` origins outright. Rather than relax
that setting to reach the code — which would have tested a weakened configuration and quietly
removed a security control's justification — the attempt was converted into a regression for the
control itself, and the residual gap was recorded as structural. `acquisition.py` moved only
76% to 78% as a result, and that number is the honest one.

## Limits of this evidence

Coverage is not correctness. These tests fix current behaviour at the boundaries; they do not
argue the boundaries are correctly chosen. The residual `bounded_process.py` gap is platform-gated
in both directions and cannot be closed on one operating system without mocking the operating
system, which would prove the mock. `acquisition.py`'s clone path needs a real remote.
`longitudinal.py` at 75% was not addressed and remains available work.

## Links

- reviews:: [[Requirements/REQ-040 - Prove the fail-closed branches rather than assert them]]
- based-on:: [[Evidence/EVD-040 - Phase 21D fail-closed branch verification]]
- follows:: [[Reviews/Phase 21C First-Run Walkthrough Review]]
- governed-by:: [[Brain/Phase Completion Protocol]]
