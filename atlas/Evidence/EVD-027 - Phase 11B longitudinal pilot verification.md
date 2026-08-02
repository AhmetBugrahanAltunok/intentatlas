---
id: EVD-027
type: evidence
status: verified
phase: 11B
---
# EVD-027 - Phase 11B longitudinal pilot verification

## Scope and durable chain

- proves:: [[Requirements/REQ-027 - Establish longitudinal recommendation evidence]]
- Decision: [[Decisions/ADR-027 - Freeze pilot evidence before recommendation tuning]]
- Delivery issue: [[Issues/ISSUE-025 - Implement longitudinal pilot and compatibility baseline]]
- implemented-by:: [[Code/src - intentatlas - longitudinal.py]]
- implemented-by:: [[Code/src - intentatlas - cli.py]]
- proves:: [[Tests/tests - test_longitudinal.py]]
- proves:: [[Tests/tests - test_compatibility_policy.py]]
- recorded-in:: [[Commits/Commit d84e545 - feat- add frozen longitudinal pilot baseline]]
- Supporting documentation commit: [[Commits/Commit 9557cb1 - docs- publish longitudinal baseline card]]
- Supporting package commit: [[Commits/Commit 9b54c06 - build- include frozen pilot metadata]]
- Review: [[Reviews/Phase 11B Longitudinal Pilot and Compatibility Review]]

## Exact provenance and ordering

- Phase 11A closed first at `b45ff0e93b8c53c7d9816dbbf14e92477ef74591`, timestamp
  `2026-08-02T13:06:36+03:00`; its final 13-job CI run `30743100374` passed.
- Phase 11B began from that exact revision. Before Phase 11B edits, the prior schema-1 real-world
  manifest SHA-256 and its six label hashes were recorded in ISSUE-025.
- The frozen unchanged production baseline was committed before any optional recommendation change
  as `d84e54588d56f2b0ec2c3f1768c12de00c1d138e`, epoch `1785670965`, timestamp
  `2026-08-02T14:42:45+03:00` (`feat: add frozen longitudinal pilot baseline`).
- The benchmark card and generated Code/Test/Commit materialization were committed as
  `9557cb1824de3c8ba1b4a4a5c6a6282f885b7b7d`, epoch `1785675240`, timestamp
  `2026-08-02T15:54:00+03:00`.
- Exact package inclusion and release allow-list verification were committed as
  `9b54c0663e81027bbf1ac301fea4607817158eb6`, epoch `1785675465`, timestamp
  `2026-08-02T15:57:45+03:00`. This is the exact pushed implementation/package revision used by
  the final build and remote-CI evidence below.
- No production recommendation score, traversal, resolver, confidence threshold, fallback, or
  full-suite behavior changed. The frozen results did not justify the optional refinement, so the
  evaluation partition was never used as tuning input and the original baseline was retained.

## Approved acquisition, identity, and license review

The user explicitly approved network acquisition of public Phase 11B pilot repositories, local
commits, push, and remote CI, subject to license/provenance review, no access to `atlas/Private/`,
no tag/release/publication, and no Phase 12 work before this Review. Acquisition cloned the public
repositories only into ignored `.intentatlas/real-world/checkouts/`, detached them at the manifest
revisions, and verified origin, clean checkout, revision, license bytes, and bounded history before
evaluation. No third-party source, patch body, repository commit message, or raw file content was
added to tracked project evidence.

| Project | Cohort / shape | Exact revision | SPDX | License SHA-256 |
| --- | --- | --- | --- | --- |
| antfu-utils | JavaScript/TypeScript / workspace | `91f8cf73bebddae8f7ebcac82e47c9bcba9805e2` | MIT | `157381f8592cbf45b6a1f7e8aa2ec9c676fafaed849726692eedf95adfac43e9` |
| axios | JavaScript/TypeScript / single | `c3f553c740ebf3dff5e22dae24e9caaafafddd2d` | MIT | `e8b48767d34116869c34cf31af9e77a37fdd6225f55a27166019dcf9bf439465` |
| cobra | Go / single | `61968e893eee2f27696c2fbc8e34fa5c4afaf7c4` | Apache-2.0 | `d7a18303ada5be476e66d11ed8c87149664c9fd15f5e7397829f059820d565e6` |
| match | Go / single | `9eab4b2d580b9e1c5ef6399492a09f5a2bdd286b` | MIT | `677524ffb56d765c88cd841ce04b8f2144e1e65816b084ecbc464463ef87a117` |
| p-limit | JavaScript/TypeScript / single | `ef37eb2f372d385883d113803c98ba0bf3828ad1` | MIT | `5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3` |
| schedule | Python / single | `2dcb5833cdf2b7d7a1bda90c19e2fb7e373e66df` | MIT | `49469f2d42facf357213ad2cda29da188fa418a16fccfe7c6bbb3e3fc07bf4ff` |
| yocto-queue | JavaScript/TypeScript / single | `b07eac099753833b29d06c614149904445739776` | MIT | `5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3` |
| zustand | JavaScript/TypeScript / workspace | `beca84e600e4e250f6b244d22878e72948f331c7` | MIT | `f0dcbb086850a46d51446679126b274b0752801d85ca1f6ddb067ed046ccc2e2` |

All license records were reviewed on `2026-08-02`. IntentAtlas's MIT license does not relicense
these third-party repositories.

## Frozen corpus and deterministic output

- Manifest schema: `1`; manifest SHA-256:
  `391015effa9b3759cfbf6a8d94eb0c8d58a7c2e27bbd538d6e2377c741543731`.
- Corpus: eight repositories, 64 globally unique chronological commit cases, eight cases per
  repository. The language cohorts contain 40 JavaScript/TypeScript cases, 16 Go cases, and eight
  Python cases; the two explicit pnpm workspace histories contain 16 cases.
- Calibration: 32 cases,
  `3a1a903f37ca7e2432007b0210494ea659c64fb3aa2d93f2490de92f09041320`.
- Evaluation: 32 cases,
  `edafea2e4225a271664c43b54e90b2987d4c1cf70f67e1ecc5a832d06efb72d5`.
- Two unchanged offline evaluations produced byte-identical repeated results. Canonical JSON
  SHA-256 was `dd90bd22ceefba5321e1a0fb2a762adee15f8f943807718b1bcf0117923d3cdd`;
  text SHA-256 was `0a0b9c530dcd57c9e6ca208e665c408da4d7376c0cc05c4463db8ccbf4aa887d`.
- The result contains 192 case/threshold rows and reports every project, language, workspace,
  partition, threshold, and overall cohort. Unknown numeric values remain JSON `null` and text
  `n/a`. `duration_evidence` is `null`; text reports duration/savings as unknown because no
  revision-aligned execution evidence was supplied.

## Evaluation results

All percentages below describe only these frozen reviewed cases and are not general accuracy or
population estimates. The CLI emits Wilson 95% intervals and denominators for every estimate.

### Overall evaluation partition

| Threshold | Cases | TP | FP | FN | Precision, Wilson 95% CI | Recall, Wilson 95% CI | Coverage, Wilson 95% CI | Abstention, Wilson 95% CI |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| low | 32 | 34 | 34 | 0 | 50.0000% [38.4381%, 61.5619%], n=68 | 100.0000% [89.8485%, 100%], n=34 | 90.6250% [75.7818%, 96.7598%], n=32 | 56.2500% [39.3256%, 71.8347%], n=32 |
| medium | 32 | 34 | 34 | 0 | 50.0000% [38.4381%, 61.5619%], n=68 | 100.0000% [89.8485%, 100%], n=34 | 90.6250% [75.7818%, 96.7598%], n=32 | 56.2500% [39.3256%, 71.8347%], n=32 |
| high | 32 | 27 | 0 | 7 | 100.0000% [87.5445%, 100%], n=27 | 79.4118% [63.2016%, 89.6505%], n=34 | 71.8750% [54.6255%, 84.4354%], n=32 | 56.2500% [39.3256%, 71.8347%], n=32 |

For all 64 cases, low/medium produced TP=72, FP=86, FN=0, precision 45.5696%, recall
100%, coverage 95.3125%, and abstention 71.875%; high produced TP=60, FP=0, FN=12, precision
100%, recall 83.3333%, coverage 78.125%, and abstention 71.875%.

### Evaluation language and workspace cohorts

| Cohort | Threshold | Projects / cases | TP / FP / FN | Precision | Recall | Coverage | Abstention |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| Python | low / medium / high | 1 / 4 | 4 / 0 / 0 | 100% | 100% | 100% | 75% |
| JavaScript/TypeScript | low / medium | 5 / 20 | 22 / 2 / 0 | 91.6667% | 100% | 85% | 55% |
| JavaScript/TypeScript | high | 5 / 20 | 19 / 0 / 3 | 100% | 86.3636% | 75% | 55% |
| Go | low / medium | 2 / 8 | 8 / 32 / 0 | 20% | 100% | 100% | 50% |
| Go | high | 2 / 8 | 4 / 0 / 4 | 100% | 50% | 50% | 50% |
| Workspace | low / medium | 2 / 8 | 7 / 0 / 0 | 100% | 100% | 75% | 37.5% |
| Workspace | high | 2 / 8 | 6 / 0 / 1 | 100% | 85.7143% | 62.5% | 37.5% |

### Per-project evaluation at medium confidence

| Project | Cases | TP | FP | FN | Precision | Recall | Coverage | Abstention |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| antfu-utils | 4 | 4 | 0 | 0 | 100% | 100% | 75% | 25% |
| axios | 4 | 8 | 2 | 0 | 80% | 100% | 100% | 75% |
| cobra | 4 | 4 | 32 | 0 | 11.1111% | 100% | 100% | 25% |
| match | 4 | 4 | 0 | 0 | 100% | 100% | 100% | 75% |
| p-limit | 4 | 4 | 0 | 0 | 100% | 100% | 100% | 75% |
| schedule | 4 | 4 | 0 | 0 | 100% | 100% | 100% | 75% |
| yocto-queue | 4 | 3 | 0 | 0 | 100% | 100% | 75% | 50% |
| zustand | 4 | 3 | 0 | 0 | 100% | 100% | 75% | 50% |

The exact JSON/text reports additionally contain low, medium, and high rows with Wilson intervals
for each project. No cohort is silently omitted.

### Analysis, freshness, and strategy safeguards

Each evaluation threshold has the same evidence-state distribution: analysis `fallback=14`,
`unknown=18`; freshness `aligned=14`, `stale=18`; strategy `abstain-and-full-suite=18`,
`full-suite-fallback=3`, `targeted-plus-full-suite=11`. Thus every unknown/stale case remains
advisory and retains a full-suite path; no result claims that a targeted subset is sufficient.

## Error review and limitations

- All 192 case/threshold rows have zero unclassified error paths.
- Calibration low and medium each classify 52 false-positive paths as `resolver-ambiguity`;
  evaluation low and medium each classify 34 false-positive paths the same way.
- Calibration high classifies five false-negative paths and evaluation high classifies seven as
  `recommendation-policy-gap`. Classification records bind canonical sorted path-set hashes and
  evaluation rejects missing, stale, or mismatched observations.
- Low/medium broad candidates are concentrated in Cobra and Axios. High confidence removes all
  observed false positives but misses seven evaluation labels; this tradeoff did not justify a
  production-policy change on the frozen corpus.
- Type-declaration checks named `*.test-d.ts` are not production scanner test nodes and are
  excluded from runtime-test labels. Click and itsdangerous were considered but rejected before
  baseline output because overload/platform definitions produce duplicate Python adapter symbol
  identities. No adapter expansion was made to admit them.
- The corpus is intentionally small, selected, and historical. It supports reproducibility and
  diagnosis, not ecosystem-wide accuracy, runtime savings, or causal performance claims.

## Compatibility and implementation inventory

- `src/intentatlas/longitudinal.py` adds strict schema-1 manifest, project, label, partition,
  classification, validation, cohort aggregation, uncertainty, deterministic JSON, and text
  rendering without executing project code.
- `src/intentatlas/cli.py` adds offline `evaluate-longitudinal MANIFEST CHECKOUTS [PATH]` with
  text/JSON formats while preserving the CLI's optional project-root contract.
- `benchmarks/longitudinal/` contains one manifest plus eight label and eight classification files;
  package verification requires exactly that approved metadata set in the sdist.
- `docs/longitudinal-pilot.md` and README publish the bounded benchmark card, acquisition boundary,
  exclusions, known misses, and no-generalization wording.
- `docs/compatibility-policy.md` classifies graph schema, CLI JSON, change/report, evidence import,
  adapters, and cache as stable, experimental, or internal and states pre-1.0 migration and
  deprecation rules. `tests/test_compatibility_policy.py` binds every declared contract and schema
  version; `tests/test_longitudinal.py` covers strict input, trust boundaries, determinism,
  uncertainty, fallback, classifications, metadata, card parity, and CLI operation.
- `pyproject.toml`, `tools/verify_release.py`, and `tests/test_release.py` include and exactly
  allow-list the frozen metadata in source distributions. The wheel intentionally contains code,
  not repository benchmark data.
- Generated vault material adds the longitudinal Code/Symbol/Test notes, refreshed dashboard and
  relationship data, and exact Commit notes. Generated history pruning removed only the prior
  bounded-history Commit note; no user-owned note was overwritten.

## Local verification

- Focused longitudinal/CLI/compatibility/release regressions and final complete local gates are
  recorded in the final closure section below.
- A complete browser-required source run before the package-only follow-up reported `411 passed,
  2 skipped` and branch-aware coverage `86.36%`.
- `python -m ruff check .`, `python -m mypy`, `python -m bandit -q -r src tools`,
  `python -m pip check`, `node --check src/intentatlas/web/app.js`, and `git diff --check` passed.
- Two commit-epoch builds from `9b54c0663e81027bbf1ac301fea4607817158eb6` passed
  `tools/verify_release.py` with identical bytes, 47 wheel files, and 166 sdist files:
  - wheel: 139,987 bytes, SHA-256
    `df1797f68ce397d0124566805d0766aacb5fcadf0411b95d1e9e2dada0c75d7e`;
  - sdist: 242,103 bytes, SHA-256
    `f7a7eac1d6f3ba803b3ebe29f9996b3b9f8a515bed46cfea10ae3b57e8484a9e`.
- A fresh environment installed the exact wheel with no dependencies, `pip check` passed,
  `IntentAtlas 0.3.0rc1` was reported, schema-1 demo JSON passed, and the installed longitudinal
  CLI evaluated eight projects/64 cases with zero classification gaps. The extracted verified
  sdist suite passed with nine expected skips visible (repository-only and Windows platform
  cases); the packaged benchmark directory was present.

## Network and remote verification

- `.venv\Scripts\python.exe -m pip_audit` (`pip-audit 2.10.1`) reported no known vulnerabilities;
  only the expected unpublished `intentatlas 0.3.0rc1` distribution could not be audited on PyPI.
- GitHub's official Commit API returned the exact configured SHA with
  `verification.verified=true`, reason `valid`, for `actions/checkout`, `actions/setup-python`,
  `actions/upload-artifact`, `actions/download-artifact`, and
  `pypa/gh-action-pypi-publish` on 2026-08-02.
- `main` was pushed by ordinary fast-forward from `b45ff0e` through `9b54c06`; no force push,
  tag, release, package publication, deployment, or visibility change occurred.
- CI run `30749058555` for exact head
  `9b54c0663e81027bbf1ac301fea4607817158eb6` passed all 13 jobs: security, static typing,
  required browser E2E, reproducible package/sdist verification, Python 3.11/3.12/3.13 source
  suites, and six installed-wheel E2E jobs across Linux, macOS, and Windows on Python 3.11/3.13.
  Run URL: `https://github.com/AhmetBugrahanAltunok/intentatlas/actions/runs/30749058555`.
- Network use was limited to approved public repository acquisition, dependency/Action audits,
  Git push, and CI observation. The evaluator and normal CLI remain offline and no telemetry,
  project source, graph, vault content, test output, or credentials were uploaded by IntentAtlas.

## Pre-closure vault verification

- Two immediate explicit-root scans reported 1,269 nodes, 2,995 relationships, 1,110 generated
  notes, and an identical second pass with all three adapter fragments reused and zero rebuilt.
- Explicit snapshots covered 159 user-owned files under `Brain/`, `Requirements/`, `Decisions/`,
  `Issues/`, `Evidence/`, `Reviews/`, and `Sessions/`; `atlas/Private/` was never enumerated, read,
  indexed, or modified. The generated snapshot covered 1,111 files under `Code/`, `Symbols/`,
  `Tests/`, `Commits/`, and `Dashboard/`. Path, length, SHA-256, and UTC mtime were unchanged across
  the immediate second scan.
- Final status counted commit=25, config=8, decision=29, document=26, evidence=29, file=40,
  issue=27, memory=7, requirement=29, review=29, session=9, symbol=943, test=68,
  relationships=2,995, and zero durable orphans.

## Final closure vault and regression verification

- Focused command:
  `.venv\Scripts\python.exe -m pytest tests\test_longitudinal.py
  tests\test_compatibility_policy.py tests\test_cli.py tests\test_release.py -ra` - `50 passed`.
- Final browser-required complete command:
  `.venv\Scripts\python.exe -m pytest --cov=intentatlas --cov-report=term-missing
  --cov-fail-under=80 -ra` with `INTENTATLAS_REQUIRE_BROWSER=1` - `411 passed, 2 skipped` in
  77.01 seconds; branch-aware coverage `86.36%`. The skips are the platform-unavailable real
  symlink and FIFO cases; simulated fail-closed coverage remains present.
- `.venv\Scripts\python.exe -m ruff check .`, `.venv\Scripts\python.exe -m mypy`,
  `.venv\Scripts\python.exe -m bandit -q -r src tools`,
  `.venv\Scripts\python.exe -m pip check`, `node --check src/intentatlas/web/app.js`, and
  `git diff --check` passed. Mypy checked 40 maintained source files.
- After materializing EVD-027 and all three exact Commit notes, two immediate scans each reported
  1,269 nodes, 2,926 relationships, and 1,110 generated notes. Both passes reused all three
  adapter fragments and rebuilt none.
- Snapshots of 159 explicitly selected user-owned files and 1,111 generated files were byte- and
  UTC-mtime-identical across the scans. The user snapshot enumerated only `Brain/`,
  `Requirements/`, `Decisions/`, `Issues/`, `Evidence/`, `Reviews/`, and `Sessions/`; the
  generated snapshot enumerated only `Code/`, `Symbols/`, `Tests/`, `Commits/`, and `Dashboard/`.
  `atlas/Private/` was never included in either enumeration.
- Final status reported commit=25, config=8, decision=29, document=26, evidence=29, file=40,
  issue=27, memory=7, requirement=29, review=29, session=9, symbol=943, test=68,
  relationships=2,926, and zero durable orphans.
- Exact graph assertions passed for REQ-027 `drives` ADR-027; ADR-027 `tracked-by` ISSUE-025;
  ISSUE-025 `implemented-by` `src/intentatlas/longitudinal.py`; EVD-027 `proves`
  `tests/test_longitudinal.py`; and EVD-027 `recorded-in` exact baseline commit
  `d84e54588d56f2b0ec2c3f1768c12de00c1d138e`.

## Remaining risks and exclusions

- Small, selected cohorts and wide Wilson intervals prevent general accuracy claims. The Go cohort
  exposes high low/medium resolver ambiguity; high confidence exposes recommendation-policy gaps.
- Historical analysis is frequently stale/unknown. Full-suite fallback and abstention therefore
  remain required; recommendations remain advisory and non-blocking.
- No duration/savings, real test execution, telemetry, hosted attestation, publication, or public
  launch claim is made. Phase 11C controls, tags, releases, deployments, and package publication
  remain owner-controlled and outside this phase.
- `atlas/Private/` was not accessed. No Phase 12 or Phase 13 implementation was begun.

## Decision

Verified. The frozen baseline, independent evaluation partition, complete cohort/error reporting,
compatibility policy, exact implementation/package provenance, deterministic local/package/vault
checks, approved network audits, fast-forward push, and 13-job exact-head remote CI all pass.
REQ-027 is satisfied without recommendation tuning. Phase 11B may close; this decision authorizes
no Phase 11C public action, tag, release, publication, deployment, or Phase 12 implementation.
