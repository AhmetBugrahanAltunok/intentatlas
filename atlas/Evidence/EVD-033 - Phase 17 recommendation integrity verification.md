---
id: EVD-033
type: evidence
status: in-progress
phase: 17
---
# EVD-033 - Phase 17 recommendation integrity verification

## 17F reopen

External retest evidence at final head `6e187143a9362cdd24d3985b11d3089a05fbc839` reopened
Phase 17 for evidence-presentation and runnable-test integrity. The prior implementation and CI
results remain historical evidence, not proof that the new 17F gates pass.

## 17F entry and independent decisions

- Entry was independently verified before edits as clean
  `HEAD == main == origin/main == 6e187143a9362cdd24d3985b11d3089a05fbc839`. Phase 16 stayed
  closed; no Phase 11C, tag, release, publication, or deployment action occurred.
- **R1 — confirmed contract defect.** ChangeReport kept summaries, paths, and evidence in three
  independently sorted aggregates, so the displayed path could be detached from the score-producing
  reason.
- **R2 — confirmed contract defect.** The weak package re-export summary sorted before Click's
  direct exact-symbol reason even though the final score came from the direct reason.
- **R3 — confirmed bounded-presentation defect.** JSON counters were correct, but text, guided CLI,
  and viewer did not disclose that only 20 of 38 filtered Click details were rendered.
- **R4 — intentional behavior.** Static exact-symbol evidence remains `80/medium`; `100/high` is
  reserved for stronger evidence such as a test directly in the changed set. No score changed.
- **R5 — confirmed correctness defect.** Graph-visible Python support/fixture files had no separate
  runnable role and could become direct medium-confidence command targets.
- **R6 — intentional behavior with missing risk copy.** Low remains exploratory weak-evidence
  discovery with possible high fan-out and low precision; medium or higher is recommended for CI.

## 17F before/after corpus evidence

- The inert Click checkout remained pinned at
  `00e592cea702e0b2caa0dee42489fdb1c22cd845`; only the intentional
  `src/click/formatting.py` worktree edit was present and no Click code was executed.
- Before 17F, Click selected `tests/test_formatting.py` at `80/medium`, but its aggregate presentation
  put the package-reexport fallback first and separately aggregated
  `package-reexport-fallback`, `python-ast`, and `python-symbol-reference`. Selection was 1 of 39
  candidates, with 38 filtered and only 20 omission records shown.
- Two final post-fix Click reports were byte-identical, SHA-256
  `14ca82eadd390e5424354e9876c890a72d06de223481a09262135a859d881749`.
  `tests/test_formatting.py` remains `80/medium`; its primary signal is
  `symbol-structural-test`, its own path is exactly
  `wrap_text -> tests/test_formatting.py`, and its evidence is exactly
  `python-ast, python-symbol-reference`. The re-export route remains one additional low signal.
  Selection is 1 of 29 runnable candidates, 28 are filtered, and 20/28 omission details are shown.
- Click's safely read pytest discovery policy records root `tests`. The support file
  `tests/typing/typing_aliased_group.py` retains its exact graph edge but is neither selected nor an
  omitted runnable candidate. `conftest.py`, package markers, unmatched support, and files outside
  declared test roots follow the same general policy.
- The persisted entry self-graph had 1,673 nodes / 3,837 edges, SHA-256
  `62f1b3bf4ad0a49b5f8c64ebdcb11ff1851db6138bc93eb276abb2b47c325d41`, and no role metadata.
  Two fresh post-implementation self-scans, before this evidence paragraph was recorded, were
  identical at 1,714 nodes / 3,893 edges, SHA-256
  `90d90be55e635a40aedcb70d9406252c5d10554913a6a7ecad1f5f21231df949`.
  Their medium recommendation for `recommend_tests` had nine selected linked reasons; Python role
  counts were 46 runnable and 5 support, while legacy/non-Python behavior remained present.

## 17F implementation and compatibility

- `ReportReason` preserves `{signal, score, summary, path, evidence}` as one immutable record.
  `primary_reason` is deterministically strongest and its score must equal the candidate score.
  Text, JSON, guided CLI, and viewer consume that linked record; weaker routes are additional
  signals.
- Omitted records keep `selection_reason` separate from their linked ranking reason. Requirement
  and test summaries expose selected, total candidate, filtered, limit-omitted, and shown/total
  omission counts on all official surfaces.
- ADR-035 retains ChangeReport schema 1 and graph schema 4. `primary_reason`, `reason_details`,
  `selection_reason`, and Python role metadata are additive. Legacy `reasons`, `paths`, `evidence`,
  and omission `reason` remain readable aggregate/selection fields and are deprecated only for
  consumers that require a linked explanation; no migration is required.
- Bounded static pytest `python_files` and `testpaths` declarations are read without importing or
  executing project code. Invalid patterns/paths abstain. Python support, fixture, and package
  graph artifacts are not executable candidates; older graphs without role metadata and existing
  JavaScript/TypeScript and Go candidates retain their behavior.

## 17F local verification

- The new red regression file initially failed five independent behaviors: linked reason records,
  selection/ranking separation, fixture/support eligibility, custom discovery policy, and low-mode
  guidance. The completed focused matrix, including real-browser-required viewer tests, passed;
  `tests/test_phase17f_evidence_integrity.py` covers all four accepted pytest configuration sources,
  invalid-path abstention, test-root exclusion, JS/Go preservation, and EN/TR guidance.
- Final browser-required full command
  `python -m pytest --cov=intentatlas --cov-report=term
  --cov-report=json:var/phase17f-coverage-final.json --cov-fail-under=80 -ra` passed `518` tests with
  `4` Windows-unavailable symlink/FIFO capability skips and `85.86%` branch coverage.
- Final `ruff`, `mypy` (46 source files), `bandit -q -r src tools`, Node syntax, pip-check,
  diff-check, and approved pip-audit passed. Pip-audit reported no known vulnerabilities and only
  identified the unpublished local IntentAtlas distribution as unavailable on PyPI.
- Implementation commits are `41811e5226676c235e806de91eb5f14a4681ac3e` and
  `8b38c15c7fab68f546457ceca6237fc0daa09011`. The first generated durable note is
  [[Commits/Commit 41811e5 - Implement Phase 17F evidence integrity]]; the second is generated by
  the final local vault pass.
- Two fixed-epoch final builds were byte-identical. `tools/verify_release.py` bound provenance to
  exact source `8b38c15c7fab68f546457ceca6237fc0daa09011`, validated 54 wheel and 193 sdist files, and recorded:
  - wheel SHA-256 `17bb3a69a4b5a7e509c1945b9289a3551a81ce59e03fb55b8a7d5691b445162c`;
  - sdist SHA-256 `4f9513ecdcca85f8e96ba3416b8fdec11d5223ce8195459e90da99e42cdcd167`.
- Exact-wheel pipx install/reinstall/uninstall passed. The verified sdist rebuilt the same wheel,
  and isolated version plus JSON demo schema-1 smokes passed. Its extracted source passed `511`
  tests with `11` expected platform/repository-only capability skips.
- Approved `git ls-remote` resolved Click HEAD/main to the pinned revision. Its BSD-3-Clause
  `LICENSE.txt` SHA-256 remained
  `757302fe7c41e7026fa46d3315ea8604ed5295fc95c2256d9b38adac43f6fbe5`.
- Final two-pass vault scans each produced 1,714 nodes, 3,894 relationships, and 1,520 generated
  notes; pass two reused all three adapter partitions. All 194 files in the explicitly enumerated
  user-owned areas retained identical bytes, sizes, and mtimes. All 1,521 generated files retained
  identical bytes, sizes, and mtimes across the second pass. `intentatlas status` reported
  `durable orphans 0`. No public corpus, package, provenance, or coverage artifact is tracked.

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
- [x] Local-verification/generated-note commit, push, verification-head remote CI, and clean
      synchronized worktree. Final documentation head remains subject to the mandatory CI check.

## Remote closure

- Local verification and generated snapshot commit:
  `e6aa7c52773912447694ca4e70141ee173f277a8`.
- GitHub Actions run
  `https://github.com/AhmetBugrahanAltunok/intentatlas/actions/runs/30856167453` passed all `13/13`
  jobs at that exact head: three Python test matrices, six cross-platform installed-wheel E2E jobs,
  real Chrome, static typing, security/pip-audit, and reproducible package/pipx/extracted-sdist.
- The immediate documentation closure commit must remain clean and receive green final-head CI;
  any failure reopens this Evidence and Review.

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
