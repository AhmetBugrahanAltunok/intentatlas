---
id: review-phase-21a-verification-integrity
type: review
status: passed
phase: 21A
---
# Phase 21A Verification Integrity Review

Decision: **passed for local Phase 21A delivery on 2026-09-11**. The final full-suite result is
612 passed, 4 platform skips, exit 0, with 86.71% branch-enabled total coverage. Acceptance
mapping is recorded in EVD-037. This sub-phase closes the first Phase 21 gate only; Phase 21
remains open.

## What this phase actually corrected

Phase 20 recorded a browser failure and closed with it explained as environment-specific. The
cause is now established: the development environment held a non-editable install, and tests that
start the CLI in a temporary directory copied a parent environment whose relative `src` entry did
not resolve there. The parent session tested current source while the child served a stale
package. An instrumented probe reproducing the same interaction reported the expected single
request three times out of three, and the same test passes with an absolute import root.

The correction is therefore not a viewer change. No `src/intentatlas` runtime module was modified
in this phase. What changed is that a run can no longer be ambiguous about what it verified.

## Comprehensive change inventory

- `tests/_package_identity.py`: resolve the imported package root, compare it against the declared
  mode, and build subprocess environments from that root rather than an assumed layout.
- `tests/conftest.py`: refuse the session at `pytest_sessionstart` when the declaration and the
  import disagree, before any test is collected.
- `tests/test_package_identity.py`: 11 regressions covering both refusal directions, an unknown
  declaration value, the session hook, and absolute, de-duplicated environment construction.
- `tests/test_e2e.py`, `tests/test_browser_e2e.py`: six CLI spawn sites derive their child
  environment from the imported module.
- `tests/test_guided_cli.py`: the hardcoded relative `src` path is replaced by the shared helper.
- `tests/test_change_analysis.py`: six regressions over the previously untested vault
  classification, covering the `atlas/Private/` boundary, generated areas, durable identity,
  deleted durable notes, a path-derived note identity, and files outside every known area.
- `.github/workflows/ci.yml`: the job that force-installs a wheel declares installed intent, so it
  now proves it verified that artifact instead of assuming it.
- `CONTRIBUTING.md`, `docs/architecture.md`, `CHANGELOG.md`: state the declaration, both refusal
  directions, and the corrected attribution of the Phase 20 browser failure.
- REQ-037 / ADR-039 / ISSUE-037 / EVD-037 / this Review / the 2026-09-11 Sessions checkpoint:
  linked requirement-to-verification chain; roadmap and execution plan updated to match.

## Verification

- Full suite: 612 passed, 4 skipped, exit 0, 86.71% branch-enabled coverage, 179.34s. Collection
  grew from 599 to 616, matching exactly the 17 regressions added.
- `change_analysis.py` coverage: 66% to 84%; the vault classification block is no longer untested.
- Ruff, mypy (50 source files), and Bandit over `src` and `tools` passed.
- Offline wheel round trip: the default claim refused the installed package; the declared
  installed claim passed the end-to-end suite; the editable install was restored.
- End-to-end CLI: `intentatlas changes . --worktree --report` on this repository's own change
  reported REQ-037 at 100/100 through the durable-intent path, wrote no project state.
- Vault continuity: two consecutive scans produced 1752 byte-identical generated files; durable
  areas showed only the notes authored in this phase; `status` reports 0 durable orphans.

## Remaining risks and open gates

- Remote CI has not run. The workflow change is verified by an equivalent local offline wheel
  round trip on one platform, not by the actual operating-system and Python matrix. The next
  remote run is the real gate for that line.
- `pip-audit` was not run; it needs network approval.
- Phase 21 remains open: reproducible dual builds, clean-environment first-run walkthrough,
  EN/TR instruction reconciliation, supported-platform evidence, release inventory, and the
  ADR-034 generated-vault governance choice are all untouched by this sub-phase.
- Identified and deliberately not corrected here: `_vault_artifact` emits `vault-frontmatter-id`
  for a durable match whose identity may have been derived from the note path when no `id:`
  frontmatter exists. The behavior is now pinned by regression so it is visible. Correcting the
  label changes schema-visible evidence strings and needs its own decision record.
- Observed while verifying link health, pre-existing and not introduced here: the durable notes
  use `delivered-by::`, `reviewed-by::`, `extends::`, and `planned-in::`, none of which are in the
  accepted relation vocabulary, so each degrades to a generic `references` edge. `drives::` and
  `proved-by::` resolve as typed. REQ-036 shows the identical pattern, so this is a vault-wide
  convention rather than a defect in this phase's notes, and no link is lost. It does mean the
  intent chain carries less meaning than the notes appear to declare, which matters for a product
  whose stated contract is that links group by meaning. Either the vocabulary should gain these
  four relations or the notes should adopt existing ones; both are migrations with their own
  decision record.
- Nothing was pushed, published, or untracked. No human pilot result is claimed.

## Links

- reviews:: [[Requirements/REQ-037 - Prove which package and boundaries verification covers]]
- reviews:: [[Decisions/ADR-039 - Declare and derive the verified package identity]]
- reviews:: [[Issues/ISSUE-037 - Add the package identity gate and vault boundary regressions]]
- based-on:: [[Evidence/EVD-037 - Phase 21A verification integrity verification]]
- follows:: [[Reviews/Phase 20 Change Coverage Review]]
- governed-by:: [[Brain/Phase Completion Protocol]]
