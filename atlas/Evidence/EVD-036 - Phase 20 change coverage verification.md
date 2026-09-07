---
id: EVD-036
type: evidence
status: verified
phase: 20
---
# Phase 20 change coverage verification

Final local decision: **verified, 2026-09-07**. Complete resumed suite: **595 passed, 4 skipped**,
exit **0**, branch-enabled total coverage **86.47%**, duration **522.84s**.

## Baseline — 2026-09-07

Source-tree full suite: 569 passed, 1 failed, 4 skipped in 316.60s. The failing
`test_real_browser_renders_same_file_demo_story` failed again in isolation (12.47s).
Ruff, Bandit, mypy (50 files), CLI help and text demo passed. Separate in-memory examples
returned `targeted` and `analysis_coverage_complete=True` for partial and mixed-deletion changes.

The default system Python lacks pytest/Ruff/Bandit. `.venv` has the tools but imports an older
installed package unless the source path is set explicitly. Source verification uses
`$env:PYTHONPATH = (Join-Path (Get-Location) 'src')` with `.venv/Scripts/python.exe`.
This is not exact-wheel release verification.

## Acceptance and verification

| Acceptance | Evidence | Result |
| --- | --- | --- |
| Partial intervals and gaps never claim complete coverage | Parameterized leading/trailing/gap span tests; actual Git/CLI partial-hunk cases | passed |
| Parent/child ownership is preserved without false parent changes | Equivalent merged/split hunks and reversed symbol order; parent+child and child-only CLI cases | passed |
| No per-line expansion | Two adjacent spans cover a billion-line synthetic range | passed |
| Deletion-only ranges remain uncertain | Git parser start-zero and nonzero-zero-count tests; shared mapping emits no exact deletion symbol | passed |
| Mixed changes retain positive evidence and require fallback | Shared positive+deletion regression; CLI staged/worktree/commit/range cases | passed |
| CLI text/JSON agree and do not create project state | 16 actual Git-to-CLI parameter combinations; no config/vault/graph output directories | passed |
| Browser paths survive delayed response after one selection | Existing real Chrome demo check now waits for readiness, selects once, delays actual path fetch by 150ms, asserts one request and rendered test path | passed |
| Full quality suite | 595 passed / 4 platform skips, 86.47% branch-enabled total coverage; Ruff, mypy, Bandit and diff checks passed | passed |
| Durable memory and generated integrity | Final two scans; 264 wikilinks resolved; 212 durable files preserved; 1721 generated files byte-identical; no durable orphans | passed |

## Change inventory

- `src/intentatlas/symbol_spans.py`: interval-union completeness, segment-specific ownership,
  parent retention outside descendant intervals, and explicit zero-count rejection for symbol mapping.
- `src/intentatlas/git_history.py`: preserve valid zero-count hunks in surviving files, including
  deletion at the beginning, under the existing path/byte/line/hunk limits.
- `tests/test_symbol_spans.py`: eight additional cases for partial/gap/deletion ranges, nested
  ownership invariance, large ranges, and independently valid positive evidence.
- `tests/test_git_history.py`: one regression for mixed positive/deletion ranges and start zero.
- `tests/test_change_coverage.py`: 16 actual Git-to-CLI cases across four scopes and four edit
  patterns, checking artifacts, coverage, strategy, text/JSON parity, and no-write behavior.
- `tests/test_browser_e2e.py`: correct the observer to await page readiness and one selection;
  intentionally delay the real path fetch and assert exactly one request. Production viewer code
  was not changed in this phase. The original failure was reproduced twice before this correction.
- `CHANGELOG.md`, `docs/compatibility-policy.md`, `docs/trust-first-preview.md`: record the
  correctness correction, count-zero consumer handling, nested coverage, and conservative strategy.
- `AGENTS.md`: add delivery continuity references while preserving the untrusted-vault boundary.
- `atlas/Brain/Product Roadmap.md`: reconcile existing Phase 18/19 closure links; add Phase 20–23
  sequence with explicit human and release gates.
- `atlas/Brain/Alpha Release Execution Plan.md`: record product focus, milestones, measurable
  acceptance, first-run protocol, release limitations, risks, and continuation discipline.
- `atlas/Home.md`: add direct links to plan, checkpoint, and active issue.
- REQ-036, ADR-038, ISSUE-036, this evidence, Phase 20 Review, and the 2026-09-07 Sessions
  checkpoint form the durable delivery chain.
- Rebuilt scanner-owned Code/Symbols/Tests/Commits/dashboard output in two deterministic passes.
  Pre-existing Phase 18/19 source and vault changes were preserved, not attributed to Phase 20.

## Exact commands and results

All commands run from `D:\Projects\IntentAtlas` with repository-local temporary output.

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
.\.venv\Scripts\python.exe -c "import intentatlas; from pathlib import Path; print(Path(intentatlas.__file__).resolve())"
```

Import identity: `D:\Projects\IntentAtlas\src\intentatlas\__init__.py`.
Current Git HEAD is `f407e496c6c0393e34921a17398666ee876cb41c`; verification applies to the dirty
working tree including prior work and this correction, not to that commit alone or a release artifact.

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_symbol_spans.py tests/test_git_history.py::test_parse_git_diffs_preserves_deletion_uncertainty_in_surviving_files tests/test_change_coverage.py --basetemp=.intentatlas/p20-red --tb=short
```

Before correction: **18 failed, 8 passed in 46.75s**. Failures expose actual coverage/ownership
defects; existing child-only behavior remained green.

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_symbol_spans.py tests/test_git_history.py tests/test_change_coverage.py tests/test_browser_e2e.py --basetemp=.intentatlas/p20-focused --tb=short
.\.venv\Scripts\python.exe -m pytest tests/test_symbol_spans.py --basetemp=.intentatlas/p20-span-final
```

After correction: **35 passed in 86.26s**, including Chrome. After adding the final independent
positive+deletion assertion: **10 span tests passed in 0.06s**.

```powershell
$env:COVERAGE_FILE = (Join-Path (Get-Location) '.intentatlas/p20-coverage')
.\.venv\Scripts\python.exe -m pytest --basetemp=.intentatlas/p20-complete --cov=intentatlas --cov-branch --cov-report=term --cov-fail-under=80 --tb=short
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m mypy
.\.venv\Scripts\python.exe -m bandit -q -r src tools
git diff --check
```

The original complete-run process connection was lost before the final result could be retrieved.
No pass was inferred from its cache. The final resumed command persisted its outcome:

```powershell
$env:COVERAGE_FILE = (Join-Path (Get-Location) '.intentatlas/p20-coverage-resume')
.\.venv\Scripts\python.exe -m pytest --basetemp=.intentatlas/p20-complete-resume --cov=intentatlas --cov-branch --cov-report=term --cov-fail-under=80 --tb=short --junitxml=.intentatlas/p20-complete-resume.xml 2>&1 | Tee-Object -FilePath .intentatlas/p20-complete-resume.log
$phaseExit = $LASTEXITCODE
Set-Content -LiteralPath .intentatlas/p20-complete-resume.exit -Value $phaseExit
```

Final result: **595 passed, 4 skipped in 522.84s**, exit **0**, **86.47%** total coverage with
branch measurement enabled (80% required). Ruff passed; mypy passed for 50 source files;
Bandit passed; diff integrity passed. Windows skipped three tests requiring unavailable symbolic
or directory links and one requiring unavailable FIFO support. These platform skips are not
represented as successful executions of those scenarios.

```powershell
.\.venv\Scripts\python.exe .intentatlas/p20_verify_vault.py
.\.venv\Scripts\python.exe .intentatlas/p20_verify_vault.py 2>&1 | Tee-Object -FilePath .intentatlas/p20-vault-final.log
```

The local verification helper hashes Markdown under the explicit seven user-owned areas plus
Home, runs `intentatlas scan` twice, compares graph JSON excluding only `generated_at`, compares
generated-note hashes, invokes `intentatlas status`, and resolves wikilinks in the current delivery
documents. It excludes linked directories and never traverses Private. Result:
**1931 nodes, 4495 edges, 0 durable orphans, 264 resolved links, 212 preserved durable files,
1721 identical generated files** in the final closure passes; both reused all 3 adapter caches.
The initial passes had 4493 edges / 262 links and rebuilt one adapter. Closure added two direct
plan-to-evidence/review links, so the final two passes were verified again after those additions.
The helper/result are disposable `.intentatlas` files; this note retains the accepted results.

## Source/test identity

SHA-256 for the six behavior and regression files at verification:

| File | SHA-256 |
| --- | --- |
| src/intentatlas/symbol_spans.py | 89a18422a03e0fe3d84603df146f5497d331de973d7328b1637c41c4e4daa8bd |
| src/intentatlas/git_history.py | b54f9f46d47686b94b6eff922bcb10764cf0cfc7ec42054dcd2b889f6af8430f |
| tests/test_symbol_spans.py | b309c1bd91689c9220e30432d1d58accd7d4cff8e79dccc10d5b38c7e057d171 |
| tests/test_git_history.py | 1baf2faf7012946399e6e952344652ea217fe0ab4105013aa7143fc2e346d8fb |
| tests/test_change_coverage.py | 5278a08c47bd06e82a471ecb3ead3bdf3ace005259572216fd67d815aaf7b515 |
| tests/test_browser_e2e.py | 17c3bbd25c34e75f5beceb163c698645c0e19eea0ef9878dad9a7841ec44d35c |

## Remaining risks and release boundary

### Local commit checkpoint

After verification, the unchanged source/test/product-documentation tree was recorded in local
commit `041069aeef79145535e693690c023983e25223af`:
[[Commits/Commit 041069a - fix- harden analysis reliability and change coverage]].
The six file hashes above remain unchanged. The earlier dirty-tree description is the state in
which the tests ran; this commit captures those same source bytes. The following documentation
commit retains Phase 18/19/20 durable records and the refreshed vault snapshot. These local commits
do not constitute remote CI, release provenance, a push, or publication.

The post-source-commit graph snapshot is refreshed separately because the newly recorded Git
history legitimately changes graph counts. The phase-closure counts above remain historical
verification of the pre-commit snapshot, not an assertion that later snapshots have identical counts.

Post-source-commit verification used
`PYTHONPATH=src .venv/Scripts/python.exe .intentatlas/p20_verify_vault.py`
(PowerShell sets `PYTHONPATH` as in the commands above), with output retained in
`.intentatlas/commit-vault-verification.log`. Both passes reused all 3 adapters and produced
**1932 nodes / 4747 edges**, **267 resolved wikilinks**, **212 preserved durable files**,
**1722 byte-identical generated files**, and **0 durable orphans**. The new commit and its
verified change relationships explain the increased graph population; source/test bytes did not change.

### Open release work

- Windows/Python 3.13 source-tree evidence does not replace remote supported-platform CI or
  clean-wheel installation. Those belong to Phase 21; no package, network audit, push, tag,
  release upload, or announcement was executed.
- Old-side code is not reconstructed; deletion-only ranges deliberately fall back. Structural
  evidence is not proof of complete behavioral impact or test sufficiency.
- Downstream code assuming every hunk has positive count must handle preserved zero-count ranges.
- Frozen benchmark labels were not changed to fit the correction. Human usability and repeat-use
  evidence remain open Phase 22 work; technical tests cannot satisfy those gates.
- Tracked generated vault output and pre-existing dirty changes still need the Phase 21 source
  inventory and ADR-034 contribution-governance review before release intake.

## Links

- proves:: [[Requirements/REQ-036 - Require complete change coverage before targeted advice]]
- follows:: [[Decisions/ADR-038 - Preserve uncovered change ranges and deletion uncertainty]]
- delivered-by:: [[Issues/ISSUE-036 - Close partial hunk deletion and browser regressions]]
- reviewed-by:: [[Reviews/Phase 20 Change Coverage Review]]
