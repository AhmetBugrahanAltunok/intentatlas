---
id: EVD-037
type: evidence
status: verified
phase: 21A
---
# Phase 21A verification integrity verification

Local decision: **verified, 2026-09-11**. Complete suite: **612 passed, 4 skipped**, exit **0**,
branch-enabled total coverage **86.71%**, duration **179.34s**. Every result below was produced on
Windows 11 with `.venv/Scripts/python.exe` after the editable install described in the baseline.

The suite grew from 599 collected to 616 collected, which is exactly the 11 package-identity and
6 vault-classification regressions added here. `change_analysis.py` line coverage rose from 66% to
84%; its previously untested vault classification block, lines 237-288, is now exercised.

## Baseline — 2026-09-11

`.venv` contained a non-editable install of an earlier revision. `python -m pytest` failed during
collection with `ModuleNotFoundError: No module named 'intentatlas.symbol_spans'`, although
`src/intentatlas/symbol_spans.py` exists. Setting a relative `PYTHONPATH=src` repaired the parent
session: 597 passed, 4 skipped, exit 0 — but `tests/test_browser_e2e.py::`
`test_real_browser_renders_same_file_demo_story` still failed, reproducibly, in isolation.

The failure was diagnosed, not assumed. An instrumented CDP probe reproducing the same steps
reported `evidencePathRequests == 1` three times out of three, contradicting the test's observed
`0`. The difference was the server subprocess: the test copies the parent environment and starts
the CLI with `cwd=tmp_path`, where the relative `src` entry does not resolve, so the child served
the stale installed `web/app.js` while the parent tested current source. Re-running the same test
with an absolute `PYTHONPATH` passed 2/2.

`atlas/Evidence/EVD-036` records this environment as a note — "`.venv` has the tools but imports an
older installed package unless the source path is set explicitly" — and works around it. The
Phase 20 browser failure is therefore attributable to import identity, not to the viewer.

Ruff, mypy (50 files), and Bandit passed on that baseline. Total coverage was 86.51%.

## Acceptance and verification

| Acceptance | Evidence | Result |
| --- | --- | --- |
| A session states which package identity it verifies | `INTENTATLAS_TEST_PACKAGE`, default `source`; `declared_mode` regression | passed |
| A contradicting import fails before any test runs | Wheel force-installed over the editable install; session refused with both paths and the editable command | passed |
| A declared distribution cannot resolve to the working tree | `INTENTATLAS_TEST_PACKAGE=installed` on the source tree refused | passed |
| An unknown declaration value is refused | `INTENTATLAS_TEST_PACKAGE=maybe` refused, naming both valid values | passed |
| Subprocesses import the parent session's package | Import root derived from the imported module; absolute and de-duplicated; interpreter-default root left untouched | passed |
| The packaging job declares installed intent | `cross-platform-e2e` sets `INTENTATLAS_TEST_PACKAGE: installed`; other jobs keep the default | passed |
| Private vault changes stay unknown and content-free | Actual Git staged change to `atlas/Private/credentials.md`; `unknown/unknown/none`, no artifact identity, changed content absent from the rendered JSON | passed |
| Generated, durable, deleted, and unknown vault areas classify correctly | Four actual Git-to-analysis cases over a seeded vault | passed |
| Full quality suite with the gate active | 612 passed / 4 platform skips, 86.71% branch-enabled total coverage; Ruff, mypy and Bandit passed | passed |
| Affected CLI workflow end to end | `intentatlas changes . --worktree --report` against this repository's own uncommitted change | passed |

## Verification commands and results

Offline wheel round trip, executed locally:

```text
python -m pip wheel . --no-deps --no-build-isolation --wheel-dir var/identity-check
python -m pip install --force-reinstall --no-deps --no-index var/identity-check/*.whl
python -m pytest tests/test_e2e.py          -> ERROR: refused, names site-packages and src
INTENTATLAS_TEST_PACKAGE=installed ... -q   -> 2 passed
python -m pip install -e ".[dev,release,security,typing]"   (restored)
```

The first restore attempt added `--no-build-isolation` and failed because the editable build
backend requires `editables`; the plain editable install succeeded. That is a local command error,
not a packaging defect.

Focused suites: `tests/test_package_identity.py` 11 passed; `tests/test_change_analysis.py`
9 passed; `tests/test_browser_e2e.py` 2 passed.

End-to-end CLI check, run against this repository's own uncommitted change:

```text
intentatlas changes . --worktree --report
-> Analysis state: fallback; freshness aligned; strategy targeted-plus-full-suite
-> REQ-037: 100/100 (high)
   Evidence: change-set-schema-1, fresh-worktree-scan, vault-frontmatter-id,
             durable-intent-artifact
```

The durable-intent path now covered by regression is therefore also exercised on real data, and
the five changed test files are recommended as changed tests. The command wrote no project state.

Gates: Ruff `All checks passed`; mypy `no issues found in 50 source files`; Bandit over `src` and
`tools` exit 0.

## Change inventory

- `tests/_package_identity.py` (new): resolves the imported package root, compares it with the
  declared mode, and builds subprocess environments from that root.
- `tests/conftest.py` (new): fails the session at `pytest_sessionstart` on any contradiction.
- `tests/test_package_identity.py` (new): 11 regressions covering both refusal directions, the
  unknown value, the session hook, and environment construction.
- `tests/test_e2e.py`, `tests/test_browser_e2e.py`: six spawn sites now build child environments
  from the imported module.
- `tests/test_guided_cli.py`: the hardcoded relative `src` path was removed in favour of the
  shared helper.
- `tests/test_change_analysis.py`: six regressions over the previously untested vault
  classification, including the `atlas/Private/` boundary.
- `.github/workflows/ci.yml`: `cross-platform-e2e` declares installed-artifact intent.
- `CONTRIBUTING.md`, `docs/architecture.md`, `CHANGELOG.md`: document the declaration, both
  refusal directions, and the corrected attribution of the Phase 20 browser failure.

No `src/intentatlas` runtime module was modified. No dependency, network path, or product
behavior changed.

## Limitations and unverified checks

- Remote CI has not run. The `cross-platform-e2e` change is verified locally by an equivalent
  offline wheel round trip on one platform, not by the actual matrix.
- `pip-audit` was not run; it requires network approval.
- Reproducible dual-build verification, the clean-environment first-run walkthrough, the EN/TR
  instruction reconciliation, and the ADR-034 governance choice remain open Phase 21 gates.
- No human pilot, release upload, publication, or push is claimed.

## Identified defect, not corrected in this phase

`_vault_artifact` labels a durable match with evidence `vault-frontmatter-id`. The scanner assigns
`note:<vault-relative-path>` to a user-area note that has no `id:` frontmatter, so that label can
describe an identity derived from the path rather than from frontmatter. The regression
`test_user_area_note_without_frontmatter_keeps_a_derived_note_identity` pins the current behavior
so the inaccuracy is visible rather than assumed. Correcting the label changes schema-visible
evidence strings and belongs to a scoped change with its own ADR.

## Links

- proves:: [[Requirements/REQ-037 - Prove which package and boundaries verification covers]]
- follows:: [[Decisions/ADR-039 - Declare and derive the verified package identity]]
- verifies:: [[Issues/ISSUE-037 - Add the package identity gate and vault boundary regressions]]
- reviewed-in:: [[Reviews/Phase 21A Verification Integrity Review]]
- supersedes-environment-note-in:: [[Evidence/EVD-036 - Phase 20 change coverage verification]]
