---
id: EVD-015
type: evidence
status: verified
phase: 6B2B2B2B
---
# EVD-015 — Phase 6B2B2B2B real-world verification

## Requirement and decision

- proves:: [[Requirements/REQ-015 - Validate recommendations on pinned public projects]]
- Decision: [[Decisions/ADR-015 - Separate public acquisition from offline evaluation]]
- Delivery issue: [[Issues/ISSUE-013 - Implement license-reviewed real-world validation]]
- Review: [[Reviews/Phase 6B2B2B2B Real-World Validation Review]]

## Change inventory

- Added `evaluate-real-world`, an offline command that reads a strict provenance manifest and scans
  verified local checkouts in memory through the production scanner and corpus evaluator.
- Added bounded manifest parsing for canonical GitHub URLs, exact commits, safe project-relative
  labels, safe checkout-relative licenses, SPDX identifiers, SHA-256 digests, duplicate keys,
  unknown fields, project counts, text, and path shapes.
- Added fail-closed origin, HEAD, worktree cleanliness, license presence, license size, and license
  byte verification with fixed read-only Git argument lists and no shell execution.
- Constructed a fixed default `ProjectConfig` for external scanning so checkout-owned configuration
  cannot select reports, outputs, exclusions, or other inputs.
- Added three license-reviewed public-project records: `dbader/schedule` at `2dcb5833cdf2`,
  `sindresorhus/p-limit` at `ef37eb2f372d`, and `tidwall/match` at `9eab4b2d580b`, all MIT.
- Added nine manually reviewed complete-test-set cases: a pinned commit, changed file, and changed
  symbol for each Python, JavaScript, and Go project.
- Defined an `ephemeral-only` policy. Checkouts and optional redirected results remain below ignored
  `.intentatlas/`; no third-party source, history, logo, branding asset, generated graph, raw diff,
  or commit subject is tracked.
- Recognized root-level `test.js` and `tests.js` as test files after the p-limit scan exposed the
  missing common naming convention.
- Added focused parser, provenance, dirty-state, license, Git, label, offline CLI, deterministic
  rendering, in-memory scanning, and root-test classification regressions.
- Updated English/Turkish READMEs, architecture, security, changelog, protocol, roadmap,
  requirement, decision, issue, Evidence, and Review records.

## Public source and license review

Network approval was explicitly received before repository research and cloning. The validated
manifest records these license bytes:

- `dbader/schedule`, `LICENSE.txt`, MIT, SHA-256
  `49469f2d42facf357213ad2cda29da188fa418a16fccfe7c6bbb3e3fc07bf4ff`.
- `sindresorhus/p-limit`, `license`, MIT, SHA-256
  `5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3`.
- `tidwall/match`, `LICENSE`, MIT, SHA-256
  `677524ffb56d765c88cd841ce04b8f2144e1e65816b084ecbc464463ef87a117`.

The evaluator rechecked each exact origin, commit, clean state, and digest before every measurement.
It made no network request and executed no third-party code, test, dependency, hook, or runtime.

## Focused verification

- `.venv\Scripts\python.exe -m pytest tests/test_real_world.py tests/test_corpus.py
  tests/test_scanner.py --cov=intentatlas.real_world --cov=intentatlas.corpus
  --cov=intentatlas.scanner --cov-report=term-missing` — 51 passed; selected modules total 90%,
  with `real_world.py` at 90%.
- Focused real-world, scanner, and CLI regressions passed before the complete suite.
- `.venv\Scripts\python.exe -m ruff check .` and `git diff --check` passed after focused changes.

Focused tests cover deterministic text/JSON, exact in-memory recommendations, absence of generated
checkout output, malformed and duplicate manifests, unsafe paths, missing Git, wrong origin/HEAD,
dirty trees, missing or changed licenses, stale labels, missing checkout roots, bounded input, CLI
path validation, and root `test.js` structural relationships.

## Real-world measurements

`intentatlas evaluate-real-world benchmarks/real-world/manifest.json
.intentatlas/real-world/checkouts` completed for 3 projects and 9 cases:

- Low confidence — TP 9, FP 0, FN 0, precision 100%, recall 100%.
- Medium confidence — TP 8, FP 0, FN 1, precision 100%, recall 88.89%.
- High confidence — TP 3, FP 0, FN 6, precision 100%, recall 33.33%.

At medium confidence, the Go file-only case is omitted because it has only a filename-convention
relationship. At high confidence, only the three directly changed test files remain. Two complete
JSON runs were byte-identical with SHA-256
`02359a64e45f77a899c373c3f0f4c5d600317ce7cc97691dae47506024c98a07`; all checkouts remained
clean. These results apply only to the nine reviewed cases and do not prove general accuracy.

## Complete quality and security suite

- `.venv\Scripts\python.exe -m pytest --cov=intentatlas --cov-report=term-missing` — 153 passed.
- Coverage — total 90%; `real_world.py` 90%; `cli.py` 90%; `scanner.py` 91%.
- `.venv\Scripts\python.exe -m ruff check .` — passed.
- `.venv\Scripts\python.exe -m bandit -q -r src` — passed.
- `.venv\Scripts\python.exe -m pip check` — no broken requirements.
- `.venv\Scripts\python.exe -m pip_audit` — no known vulnerabilities; the local unpublished
  `intentatlas` package was explicitly skipped because it is not on PyPI.
- `node --check src/intentatlas/web/app.js` — passed.
- `git diff --check` — passed.

## CLI, package, and local viewer

- The source CLI exposed `evaluate-real-world` and produced the exact nine-case text and JSON
  reports without modifying any checkout.
- `pip wheel . --no-deps --no-build-isolation` produced
  `intentatlas-0.1.0-py3-none-any.whl` with SHA-256
  `41cf34e88442484e9cea5cd3471aa26988f9bb6944dc3686b761cf03500825cd`.
- The wheel installed with `--no-deps` in a clean virtual environment, reported version 0.1.0, and
  its installed CLI returned `case_count: 9` plus `generated_output_policy: ephemeral-only`.
- The actual loopback demo rendered 9 nodes and 13 links in a browser. Enter-key activation selected
  the requirement, exposed four bounded evidence paths, and followed the test path to
  `tests/test_auth.py`; the server returned HTTP 200 and was stopped after verification.

## Recommendation and vault compatibility

The self-hosted complete-test-set baseline now includes `tests/test_real_world.py` because it calls
the production recommendation path through the real-world evaluator. At medium confidence the two
cases total TP 11, FP 3, FN 0, precision 78.57%, and recall 100%. The original three-project corpus
remains medium precision 66.67%/recall 100% and high precision 100%/recall 50%.

Two final closure scans each produced 688 nodes, 1,421 relationships, 610 generated notes, and zero
durable orphans. Explicitly enumerated user-owned areas were byte-identical before, between, and
after both scans; `atlas/Private/` was not enumerated or read. The normalized graph SHA-256 was
identical at
`da9cd16800ef7d6708e78325ec566fa86caaa523ad9b89994cf54ed0b35f9b06`. Generated-note bytes plus
UTC modification ticks were identical at
`b5c56aa576b0812678ffda52f787f877a2ff419b1b886ba11ae80928b2a0dc5f`, proving the second scan did
not rewrite unchanged generated notes.

## Corrections made during verification

- The first p-limit scan produced no candidate because root `test.js` was classified as a normal
  file. The scanner now recognizes exact `test` and `tests` stems, and a focused JavaScript
  structural-link regression protects the behavior.
- Initial commit-only cases all scored high because the chosen changes directly modified their
  test files. File and symbol cases were added so the benchmark measures structural and
  filename-only confidence behavior. Expected test sets were re-reviewed from each pinned diff,
  implementation, and test layout rather than copied from evaluator output.
- The generic corpus advisory referred only to fixtures even when reused by the real-world wrapper.
  It now states the correct shared boundary: results do not prove accuracy beyond evaluated cases.

## Remaining risks and boundaries

- Three small projects with one relevant test file each do not meaningfully stress false positives,
  monorepos, generated code, integration suites, indirect dependencies, or multiple relevant tests.
- Labels are bounded manual judgments. They do not include hidden, downstream, platform-specific,
  type-checking, or external integration tests and can still contain reviewer error.
- Third-party tests were deliberately not executed, so this phase validates structural selection,
  not whether selected tests pass or dynamically cover the changed behavior.
- Only canonical GitHub HTTPS origins are accepted in schema 1. Other forges and signed provenance
  are deferred until demand justifies a broader trust contract.
- A directly changed test is high confidence by design. Larger future benchmarks need source-only
  commits and negative cases to estimate real false-positive rates.

## Decision

REQ-015 acceptance criteria are satisfied. Phase 6B2B2B2B passes as a reproducible, license-aware,
offline real-world validation gate with explicit limits and no bundled third-party repository data.
