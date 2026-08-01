---
id: EVD-017
type: evidence
status: verified
phase: 7B
---
# EVD-017 — Phase 7B broader validation verification

## Requirement and decision

- proves:: [[Requirements/REQ-017 - Validate recommendations on broader project structures]]
- Decision: [[Decisions/ADR-017 - Use broader benchmarks to drive conservative refinements]]
- Delivery issue: [[Issues/ISSUE-015 - Expand and refine real-world validation]]
- Review: [[Reviews/Phase 7B Broader Validation Review]]

## Change inventory

- Expanded the strict real-world manifest from three to six projects and from nine to 18 reviewed
  cases, adding Pallets Click, Axios, and Cobra.
- Added source-only Click and Cobra changes plus an Axios change with three relevant test layers.
- Recorded BSD-3-Clause, MIT, and Apache-2.0 license provenance without tracking third-party source,
  history, logos, branding, or generated graphs.
- Replaced package-wide Go test-import relationships with qualified unique-export references for
  default and named aliases, plus unique unqualified references for dot imports.
- Blank imports, ambiguous packages, and ambiguous exported declaration names now produce no direct
  imported-test relationship. Non-test imports retain package-level structural edges.
- Added regressions for named, default, dot, and blank imports; unrelated files in an imported Go
  package are explicitly rejected.
- Updated English/Turkish READMEs, architecture, security, changelog, validation protocol, roadmap,
  requirement, decision, issue, Evidence, and Review records.

## Independent case review

- Click `555fa9b` changes only `src/click/core.py`: `tests/test_context.py` owns Context resource and
  close behavior. `tests/test_shell_completion.py` imports other declarations from the same large
  file but does not exercise exception forwarding and is intentionally not labeled relevant.
- Axios `c3f553c` changes XHR status-zero handling and extracts URL preprocessing. The reviewed set
  includes browser request coverage, XHR adapter coverage, and the existing `buildFullPath` URL
  normalization suite. File and symbol cases retain only the layers relevant to their behavior.
- Cobra `61968e8` changes only Fish completion generation. `fish_completions_test.go` exercises that
  generator; six `doc/*_test.go` files import Cobra but do not exercise Fish completion output.

## Before-and-after measurement

The first six-project run used unchanged labels and scores but the previous package-wide Go test
import behavior:

- Low/medium — TP 18, FP 21, FN 5, precision 46.15%, recall 78.26%.
- High — TP 5, FP 0, FN 18, precision 100%, recall 21.74%.
- Cobra contributed 18 false positives: six unrelated documentation tests in each of its three
  cases.

After qualified imported-package symbol matching:

- Low/medium — TP 18, FP 3, FN 5, precision 85.71%, recall 78.26%.
- High — TP 5, FP 0, FN 18, precision 100%, recall 21.74%.
- Cobra moved from precision 14.29% to 100% with TP 3, FP 0, and FN 0.

No score or expected label changed between these two runs. The remaining three false positives are
Click's file-level `test_shell_completion.py` relationship across three targets. The remaining five
false negatives are Axios file/symbol cases hidden behind root-module and transitive imports.

## Focused, complete, package, UI, and closure verification

### Focused and deterministic checks

- `.venv\Scripts\python.exe -m pytest tests/test_adapters.py tests/test_scanner.py
  tests/test_real_world.py tests/test_recommendations.py tests/test_evaluation.py
  --cov=intentatlas.adapters.go --cov=intentatlas.real_world
  --cov=intentatlas.recommendations --cov-report=term-missing` — 58 passed; selected modules 88%
  total, with `go.py` at 87% and `real_world.py` at 90%.
- Two complete six-project JSON runs were byte-identical at SHA-256
  `ec069cf581e758493151515abc334e294192f45de64ddae2732f92df2c990125`.
- All six checkouts remained clean after repeated evaluation. No project code, dependency, test,
  hook, or runtime was executed and no checkout-owned configuration was loaded.

### Complete quality and security suite

- `.venv\Scripts\python.exe -m pytest --cov=intentatlas --cov-report=term-missing` — 154 passed.
- Coverage — total 90%; `go.py` 87%; `real_world.py` 90%; `recommendations.py` 88%.
- `.venv\Scripts\python.exe -m ruff check .` — passed.
- `.venv\Scripts\python.exe -m bandit -q -r src` — passed.
- `.venv\Scripts\python.exe -m pip check` — no broken requirements.
- `.venv\Scripts\python.exe -m pip_audit` — no known vulnerabilities; the unpublished local
  `intentatlas` distribution was skipped because it is absent from PyPI.
- `node --check src/intentatlas/web/app.js` and `git diff --check` — passed.

### Package, installed CLI, and local viewer

- `pip wheel . --no-deps --no-build-isolation` produced
  `intentatlas-0.1.0-py3-none-any.whl` with SHA-256
  `69aea9284391ae5a16a84ab8d5db485c7f89db8132c6e0acfbd3778d9cf2162b`.
- The wheel installed with `--no-deps` in a new virtual environment, reported version 0.1.0, and
  its installed CLI returned 18 cases with `ephemeral-only` output policy.
- The actual loopback demo rendered 9 nodes and 13 links. Enter-key activation selected the
  requirement, and its test evidence path navigated to `tests/test_auth.py`. The browser tab and
  local server were closed after verification.

### Existing benchmark compatibility

The reviewed self-hosted baseline remains TP 12, FP 3, FN 0, precision 80%, and recall 100% at
medium confidence. The original saved three-project corpus also remains medium precision
66.67%/recall 100% and high precision 100%/recall 50%. The Go import refinement therefore changes
the newly exposed package fan-out behavior without altering either earlier regression baseline.

### Obsidian closure

Two final closure scans each produced 706 nodes, 1,512 relationships, 618 generated notes, and zero
durable orphans. The normalized graph SHA-256 was identical at
`14261abea3aae1c27b8cece073b1f57636e08f9f6017b50ae8db5e6c10d0e97d`. Explicitly enumerated
user-owned areas were byte-identical across the scans; `atlas/Private/` was not enumerated or read.
Generated-note bytes plus nanosecond modification times were identical at
`f73481d4d47311e53447294105ea9aa6297bb7c56d004381966767956db4ba81`, proving the second scan did
not rewrite unchanged generated notes.

## Remaining risks and boundaries

- Static file-level Python links cannot yet distinguish which imported declarations a test uses.
- JavaScript barrel imports and transitive dependency paths are not traversed, causing the five
  recorded Axios false negatives.
- Go blank imports, unexported helpers, interface dispatch, reflection, and build-tag behavior may
  be omitted by the precision-first rule.
- Manual complete-test-set labels can contain reviewer error and exclude hidden, downstream,
  platform-specific, or runtime-only tests.
- Six projects and 18 cases improve diversity but remain far too small for a general accuracy claim.

## Decision

REQ-017 acceptance criteria are satisfied subject to the recorded deterministic closure values.
Phase 7B passes as an honest breadth expansion and precision correction: it materially improves
the observed false-positive rate while preserving the unresolved indirect-dependency gap.
