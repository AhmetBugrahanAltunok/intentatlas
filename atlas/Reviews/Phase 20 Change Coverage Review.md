---
id: review-phase-20-change-coverage
type: review
status: passed
phase: 20
---
# Phase 20 Change Coverage Review

Decision: **passed for local Phase 20 delivery on 2026-09-07**. The final persisted full-suite
result is 595 passed, 4 platform skips, exit 0, with 86.47% branch-enabled total coverage.
Acceptance mapping is recorded in EVD-036. The earlier Phase 19 pass remains historical evidence;
the newly reproduced defects are closed by this phase's implementation and verification.

## Comprehensive change inventory

- `src/intentatlas/symbol_spans.py`: verify interval-union coverage and retain each most-specific
  owner of changed segments; preserve parent-owned lines outside nested children; reject deletion
  ranges as exact current-side evidence without per-line expansion.
- `src/intentatlas/git_history.py`: retain zero-count Git deletion ranges in surviving files,
  including start zero, under existing bounded parsing safeguards.
- `tests/test_symbol_spans.py`: eight new coverage/deletion/nested/large-range cases.
- `tests/test_git_history.py`: deletion-marker preservation regression.
- `tests/test_change_coverage.py`: 16 real Git/CLI combinations for worktree, staged, commit, and
  range scopes, verifying JSON/text strategy, artifacts, coverage and no project writes.
- `tests/test_browser_e2e.py`: await readiness, select once, delay the real path fetch, and verify
  one request plus the expected rendered evidence. No production viewer modification was required.
- `CHANGELOG.md`, `docs/compatibility-policy.md`, `docs/trust-first-preview.md`: explain zero-count
  consumption and conservative report behavior; schemas, thresholds and scores remain unchanged.
- `AGENTS.md`: explicit delivery continuity without promoting vault content into instructions.
- `atlas/Brain/Product Roadmap.md`: restore Phase 18/19 closure links and establish Phase 20–23.
- `atlas/Brain/Alpha Release Execution Plan.md`: measurable product/release milestones, first-run
  human observation protocol, deferred scope, risks and continuation rules.
- `atlas/Home.md`: direct navigation to active plan, issue and checkpoint.
- REQ-036 / ADR-038 / ISSUE-036 / EVD-036 / this Review / the 2026-09-07 Sessions checkpoint:
  linked requirement-to-implementation-to-verification chain with explicit current and next work.
- Scanner-owned Code, Symbols, Tests, Commits and dashboard refreshed deterministically in two
  passes. Existing Phase 18/19 modifications and closure records were preserved.

## Exact verification commands and results

All commands use the repository root and `.venv` Python 3.13 on Windows. The source import was
explicitly confirmed as `D:\Projects\IntentAtlas\src\intentatlas\__init__.py`.

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
.\.venv\Scripts\python.exe -m pytest tests/test_symbol_spans.py tests/test_git_history.py::test_parse_git_diffs_preserves_deletion_uncertainty_in_surviving_files tests/test_change_coverage.py --basetemp=.intentatlas/p20-red --tb=short
.\.venv\Scripts\python.exe -m pytest tests/test_symbol_spans.py tests/test_git_history.py tests/test_change_coverage.py tests/test_browser_e2e.py --basetemp=.intentatlas/p20-focused --tb=short
.\.venv\Scripts\python.exe -m pytest tests/test_symbol_spans.py --basetemp=.intentatlas/p20-span-final
```

- Before correction: 18 failed, 8 passed in 46.75s.
- After correction: 35 passed in 86.26s, including actual Chrome and Git-to-CLI workflows.
- Final additional span regression: 10 passed in 0.06s.

```powershell
$env:COVERAGE_FILE = (Join-Path (Get-Location) '.intentatlas/p20-coverage-resume')
.\.venv\Scripts\python.exe -m pytest --basetemp=.intentatlas/p20-complete-resume --cov=intentatlas --cov-branch --cov-report=term --cov-fail-under=80 --tb=short --junitxml=.intentatlas/p20-complete-resume.xml 2>&1 | Tee-Object -FilePath .intentatlas/p20-complete-resume.log
$phaseExit = $LASTEXITCODE
Set-Content -LiteralPath .intentatlas/p20-complete-resume.exit -Value $phaseExit
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m mypy
.\.venv\Scripts\python.exe -m bandit -q -r src tools
git diff --check
.\.venv\Scripts\python.exe .intentatlas/p20_verify_vault.py 2>&1 | Tee-Object -FilePath .intentatlas/p20-vault-final.log
```

- Full branch-coverage suite: **595 passed, 4 skipped in 522.84s**, **86.47%** total coverage
  with branch measurement enabled, **exit 0**. The first run's process connection was lost before
  its final result was retrieved; the resumed run persists log, JUnit report and exit code.
  Three link-dependent scenarios and one FIFO scenario were skipped because the local platform
  could not provide those facilities; they are not claimed as executed passes.
- Ruff: passed. Mypy: passed (50 source files). Bandit: passed. Diff integrity: passed.
- Final two scans: 1931 nodes / 4495 edges; graph identical except `generated_at`; all 1721 generated
  files byte-identical; all 212 durable files preserved; 264 current delivery wikilinks resolved;
  `status` reports zero durable orphans. The result is also retained in EVD-036.

## Acceptance decision and remaining risks

REQ-036's behavior, CLI/browser, vault and final quality criteria pass. **Phase 20 is complete**;
Phase 21 is the next queued delivery step. No regression expectation or frozen benchmark label
was weakened. This local closure does not declare a package ready for public release.

This is local source-tree verification, with pre-existing dirty work based on HEAD
`f407e496c6c0393e34921a17398666ee876cb41c`; it is not release provenance for that commit alone.
Six verified implementation/test file hashes are recorded in EVD-036. Exact-wheel installation,
source inventory, contribution/vault governance, supported-platform CI, and dependency audit remain
Phase 21/release gates. Human pilot and repeat-use evidence remain Phase 22 work. Public release
actions remain Phase 23/11C gates. No external publication or networked verification occurred.

Zero-count hunk consumers must retain uncertainty. Old-side code is not reconstructed, and
structural recommendations remain advisory. The historical generated-vault policy is retained
until the explicit Phase 21 governance review; no bulk untracking or deletion was performed.

## Links

The unchanged implementation and tests were subsequently recorded in local commit
`041069aeef79145535e693690c023983e25223af`:
[[Commits/Commit 041069a - fix- harden analysis reliability and change coverage]].
The source hashes in EVD-036 still match; commit creation does not replace the remaining release gates.

- [[Requirements/REQ-036 - Require complete change coverage before targeted advice]]
- [[Decisions/ADR-038 - Preserve uncovered change ranges and deletion uncertainty]]
- [[Issues/ISSUE-036 - Close partial hunk deletion and browser regressions]]
- [[Evidence/EVD-036 - Phase 20 change coverage verification]]
- [[Brain/Alpha Release Execution Plan]]
