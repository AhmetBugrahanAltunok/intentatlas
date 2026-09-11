---
id: session-2026-09-11-phase-21a
type: session
status: active
---
# Phase 21A verification integrity

## Objective

The project owner asked for a review of the repository, then handed over delivery ownership with
instructions to organize the project as needed and record durable notes. The review found one
reproducible defect. This session closed it as the first Phase 21 gate rather than starting the
full Phase 21 scope.

## Current state

**Phase 21A is complete with a passed local review. Phase 21 remains open.** Start from
[[Brain/Alpha Release Execution Plan]] and [[Brain/Product Roadmap]]; do not restart completed
phases. `atlas/Private/` was not read, indexed, or modified.

Full suite: **612 passed, 4 skipped, exit 0, 86.71% branch-enabled total coverage**. Ruff, mypy
(50 files) and Bandit passed. Two scans produced 1752 byte-identical generated files with 0
durable orphans.

Local source checkpoint: `f0e6719db1cccae61e050c6b215349c577eac9ad`
(`test: declare and verify the package identity under test`), covering 11 test, workflow and
product-documentation files. The final suite and every gate were re-run against that exact tree
before it was committed. Durable notes and refreshed generated output follow in the next local
documentation commit. No push occurred.

## What was found and corrected

The reported Phase 20 browser failure was not a product defect. `.venv` held a non-editable
install of an earlier revision, so `python -m pytest` failed at collection and the documented
relative `PYTHONPATH=src` workaround repaired only the parent session: tests that start the CLI
with `cwd=tmp_path` could not resolve that relative entry and served the stale package instead.
An instrumented CDP probe reported the expected single request 3/3, and the test passes with an
absolute import root.

Rather than fix the environment by hand again, this phase removed the ambiguity: a session now
declares which package it verifies, and a contradiction fails before collection in either
direction. The packaging job that installs a wheel declares that intent, so it proves what it
tested. Subprocesses derive their import root from the imported module.

The second correction is coverage of a real safety claim. `_vault_artifact` in
`change_analysis.py` was entirely untested, including the `atlas/Private/` boundary. Six
regressions now cover it; module coverage moved from 66% to 84%.

## Verification commands

```text
python -m pip install -e ".[dev,release,security,typing]"
python -m pytest --cov=intentatlas --cov-report=term-missing --cov-fail-under=80
python -m ruff check .
python -m mypy
python -m bandit -q -r src tools
python -m pip wheel . --no-deps --no-build-isolation --wheel-dir var/identity-check
python -m pip install --force-reinstall --no-deps --no-index var/identity-check/*.whl
python -m pytest tests/test_e2e.py                          -> refused, as designed
INTENTATLAS_TEST_PACKAGE=installed python -m pytest tests/test_e2e.py -q   -> 2 passed
intentatlas changes . --worktree --report
intentatlas scan .   (twice)
intentatlas status .
```

Exact results and the acceptance table are in
[[Evidence/EVD-037 - Phase 21A verification integrity verification]].

## Next action

Continue Phase 21 with the reproducible-build and clean-environment gates: produce two wheel/sdist
pairs under one fixed `SOURCE_DATE_EPOCH`, run `tools/verify_release.py`, and record artifact
identity against a source revision. The import-identity prerequisite is now satisfied, so a clean
candidate install can be verified without ambiguity about what was tested.

Two Phase 21 items remain decisions for the owner rather than implementation work: the ADR-034
generated-vault governance choice before contributor intake, and whether to split the 675-line
README so the first-run path matches the Phase 22 ten-minute target.

Nothing was pushed, published, or untracked. Remote CI, `pip-audit`, exact release artifacts, and
human pilot observation remain unverified.

## Links

- [[Requirements/REQ-037 - Prove which package and boundaries verification covers]]
- [[Decisions/ADR-039 - Declare and derive the verified package identity]]
- [[Issues/ISSUE-037 - Add the package identity gate and vault boundary regressions]]
- [[Evidence/EVD-037 - Phase 21A verification integrity verification]]
- [[Reviews/Phase 21A Verification Integrity Review]]
- [[Sessions/2026-09-07 - Alpha readiness checkpoint]]
