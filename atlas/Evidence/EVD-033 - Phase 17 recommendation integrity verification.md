---
id: EVD-033
type: evidence
status: in-progress
phase: 17
---
# EVD-033 - Phase 17 recommendation integrity verification

## Entry and frozen baseline

- Entry: clean `HEAD == main == origin/main == 174369afc56d603373de1443d7826c92fcec395a`;
  Phase 16 remains passed and closed.
- Longitudinal manifest SHA-256:
  `391015effa9b3759cfbf6a8d94eb0c8d58a7c2e27bbd538d6e2377c741543731`.
- Frozen partition hashes remain calibration
  `3a1a903f37ca7e2432007b0210494ea659c64fb3aa2d93f2490de92f09041320` and evaluation
  `edafea2e4225a271664c43b54e90b2987d4c1cf70f67e1ecc5a832d06efb72d5`.
- Two unchanged `evaluate-longitudinal ... --format json` runs were byte-identical, SHA-256
  `dd90bd22ceefba5321e1a0fb2a762adee15f8f943807718b1bcf0117923d3cdd`.
- Before-change overall medium results: calibration TP 38 / FP 52 / FN 0, precision `0.422222`,
  recall `1.0`; evaluation TP 34 / FP 34 / FN 0, precision `0.5`, recall `1.0`.

## Independent reproduction

- Public corpus: `https://github.com/pallets/click.git` exact revision
  `00e592cea702e0b2caa0dee42489fdb1c22cd845`, BSD-3-Clause `LICENSE.txt` SHA-256
  `757302fe7c41e7026fa46d3315ea8604ed5295fc95c2256d9b38adac43f6fbe5`.
- The exact worktree change produced analyzed/aligned ChangeReport state, medium threshold,
  targeted strategy, two selected/two candidates/zero filtered. It showed empty
  `tests/test_utils/__init__.py` at score 65 but confidence low, plus real
  `tests/test_formatting.py` at score 45 low.
- In-memory Click scan produced zero Python exact-symbol test edges. Default recommend-tests
  returned only the empty marker at 65 medium; low also returned test_formatting at 45.
- Self-scan produced only five Python exact-symbol test edges. Four tests from bulk commit
  `2f3d695` ranked 70 above six direct-dependent tests at 65; test_recommendations remained a 45
  filename fallback.
- Root cause: Flit/Hatchling/conventional pyprojects defaulted to `.` source-root, preventing the
  safe src-module normalization. The real qualified caller edge was absent. A re-export file's
  exact import then combined with a filename-only second hop and inherited score 65. Separate
  ChangeReport confidence and missing test filtering compounded the error.
- Pre-fix command `python -m pytest tests/test_phase17_recommendation_integrity.py -q` produced
  `7 failed`, covering confidence/filtering, weakest-hop scoring, empty markers, broad/narrow
  co-change, Flit/Hatch/conventional src layouts, qualified attributes, Click shape, and self-scan.

## Corrected corpus results

- Two post-fix Click ChangeReports were byte-identical, SHA-256
  `5aa5723abd30af73a5c29090e47fb1ed7a5e07c72de1eee1a3d45cb059417124`. Both were
  analyzed/aligned and selected only real caller `tests/test_formatting.py` at score 80 medium.
  The 38 package-re-export candidates remained low and were filtered before strategy; the empty
  marker was not a candidate.
- Self-scan found five exact `python-symbol-reference` test edges for `recommend_tests`, including
  `tests/test_recommendations.py`; all five ranked 80. Three structural one-hop dependents ranked
  65, filename-only paths stayed 45, and the former broad-commit score-70 noise was absent.
- Post-fix longitudinal output was deterministic at SHA-256
  `f27b777fc23a56cfb431c6e18e5b5f92727f6961a872fa6e73f77dfa25bc1099`.
  Frozen medium results were unchanged: calibration TP 38 / FP 52 / FN 0, precision `0.422222`,
  recall `1.0`; evaluation TP 34 / FP 34 / FN 0, precision `0.5`, recall `1.0`; all TP 72 / FP 86 /
  FN 0. Manifest, labels, and partition hashes were not changed.

## Behavior and surface verification

- `tests/test_phase17_recommendation_integrity.py` covers canonical 65 confidence, pre-limit
  filtering/counters/strategy, zero-byte eligibility, filename and package-re-export weakest hops,
  broad/narrow co-change, Flit/Hatchling/conventional roots, qualified attributes, root/src
  collision abstention, Click shape, and self-scan exact callers.
- Focused recommendation/change-report/workspace/scanner/diagnostic/guided/viewer suites passed.
  English and Turkish guided output retain the same canonical IDs/enums/commands and stale reports
  expose the clean exact-revision checkout action. JSON and viewer consume the same corrected
  schema-1 report selection and additive `revision_action`.
- `diagnose` now says detected roots are bounded readiness heuristics rather than proof of resolver
  abstention. Resolver ownership/module/symbol uniqueness remains independently fail-closed.
- A real redirected Windows matrix reproduced the appendix risk before correction: byte `0x97`
  rendered as mojibake under CP437/857 and replacement under a UTF-8 consumer. After changing only
  `status`/`impact` presentation separators to ASCII, CP437, CP857, CP1252, and UTF-8 runs all
  returned exit 0, ASCII-only output, and no replacement character.

## Complete local gates

- `INTENTATLAS_REQUIRE_BROWSER=1 python -m pytest --cov=intentatlas
  --cov-report=term-missing --cov-fail-under=80` passed `508` tests with `4` expected
  platform/browser capability skips and `85.75%` coverage.
- `python -m ruff check .`, `python -m mypy` (`47` source files),
  `python -m bandit -q -r src tools`, `node --check src/intentatlas/web/app.js`,
  `python -m pip check`, and `git diff --check` passed.
- Approved `python -m pip_audit --skip-editable` reported no known vulnerabilities; only the local
  editable IntentAtlas distribution was explicitly skipped.
- Implementation commit: `85a639fb91c3cce0e0ce9bee4c3242d46caa2935`; generated note
  [[Commits/Commit 85a639f - Implement Phase 17 recommendation integrity]].
- Two `SOURCE_DATE_EPOCH=1704067200 python -m build --sdist --wheel` runs were byte-identical.
  `tools/verify_release.py` validated wheel `53` files and sdist `191` files:
  - wheel SHA-256 `7d194ba7a56ea4fa34905dceee9395c8ed9e1506aca462cf866da6d3a462354d`;
  - sdist SHA-256 `70e79040df00d764f1559da93d7b811d4e684520d5b7de5a9c22899ab29d8c70`.
- Exact-wheel pipx install/reinstall/uninstall passed. With the same epoch, the sdist rebuilt the
  exact wheel hash; isolated version and JSON demo smoke checks passed, and the extracted source
  suite passed with only expected capability skips.

## Network and vault gates

- Approved `git ls-remote` resolved public Click HEAD to the pinned
  `00e592cea702e0b2caa0dee42489fdb1c22cd845`; cached origin and checkout matched. BSD-3-Clause
  `LICENSE.txt` SHA-256 remained
  `757302fe7c41e7026fa46d3315ea8604ed5295fc95c2256d9b38adac43f6fbe5`.
- Two post-verification scans each produced `1,673 nodes`, `3,837 relationships`, and `1,482`
  generated notes. The second reused all three adapter partitions. All `191` files in explicitly
  allowed user-owned folders retained identical bytes, sizes, and mtimes; `1,484` generated files
  were byte-identical across passes. `intentatlas status` reported `durable orphans 0`.
- Public corpus, package, provenance, coverage, and comparison artifacts remain ignored under
  `var/`; no third-party source or package artifact is committed.

## Remaining closure

- [x] 17B confidence/filter/counter/strategy parity.
- [x] 17C source-root/qualified-symbol/re-export precision.
- [x] 17D candidate eligibility and calibrated ranking.
- [x] 17E documentation, diagnostics, Windows encoding, local/package/network/vault gates.
- [ ] Local-verification/generated-note commit, push, final-head remote CI, and clean synchronized
      worktree.

## Remaining risks

- Frozen longitudinal precision/recall did not move because its current cases do not exercise the
  corrected Python scenarios; Click and self-scan are bounded regression corpora, not a claim of
  general recommendation accuracy.
- Package-initializer re-export candidates remain visible only at low confidence; ambiguity still
  prefers abstention and can reduce recall.
- Tracked generated vault outputs remain safe only under the single-writer governance in ADR-034;
  contributor intake requires a separate decision before Phase 11C.

## Links

- proves:: [[Requirements/REQ-033 - Preserve recommendation integrity across supported surfaces]]
- references:: [[Decisions/ADR-033 - Canonicalize confidence and conservative Python resolution]]
- references:: [[Decisions/ADR-034 - Retain generated vault outputs under single-writer governance]]
- delivered-by:: [[Issues/ISSUE-032 - Implement recommendation integrity and Python resolution]]
- reviewed-by:: [[Reviews/Phase 17 Recommendation Integrity and Python Resolution Review]]
