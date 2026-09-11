---
id: ADR-039
type: decision
status: accepted
phase: 21A
---
# Declare and derive the verified package identity

## Context

`intentatlas` is importable from the working tree or from an installed distribution. Nothing
distinguished them. A non-editable install in a development environment made `python -m pytest`
fail at collection, and setting `PYTHONPATH` to a relative `src` repaired the parent session while
subprocesses started in a temporary directory silently loaded the stale installed package instead.
That produced a browser failure attributed to the product for the duration of Phase 20; the
Phase 20 evidence records the `PYTHONPATH` workaround as an environment note rather than a defect.

The opposite confusion is equally available. The cross-platform job force-reinstalls a built wheel
over an editable install and then runs the end-to-end suite. If that reinstall ever failed, the job
would verify the working tree while reporting a packaged result, and nothing would say so.

## Decision

A test session declares the package identity it verifies through `INTENTATLAS_TEST_PACKAGE`, with
`source` as the default and `installed` as the explicit alternative. A session-start hook compares
the declaration with the resolved parent of the imported `intentatlas` package and fails closed on
any contradiction, including an unrecognized declaration value. The message names the imported
root, the working tree, the editable install command, and the variable that selects the other mode.

Subprocess environments derive their import root from the imported module rather than from an
assumed repository layout, so the same helper is correct for editable installs, explicit
`PYTHONPATH` use, and installed distributions. An import root already on the interpreter's default
path is left untouched; a working-tree root is prepended in absolute form so a child started in any
directory resolves it. The previous hardcoded relative `src` path is removed.

The gate governs test-session identity only. It adds no runtime dependency, changes no product
behavior, and does not execute or inspect project code.

## Consequences

- A contributor with a non-editable install receives one actionable message instead of collection
  errors or, worse, a passing run against stale code.
- The packaging job now proves it tested the artifact it installed.
- Historical green results obtained under the ambiguous setup describe the state they were run in;
  they are not retroactively invalidated, but they are not evidence for the current source either.
- Any future job that verifies an installed artifact must declare it, which is the intended cost.

## Links

- implements:: [[Requirements/REQ-037 - Prove which package and boundaries verification covers]]
- delivered-by:: [[Issues/ISSUE-037 - Add the package identity gate and vault boundary regressions]]
- refines:: [[Decisions/ADR-038 - Preserve uncovered change ranges and deletion uncertainty]]
