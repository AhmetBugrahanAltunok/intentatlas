---
id: EVD-025
type: evidence
status: verified
phase: 10D
---
# EVD-025 — Phase 10D verification and provenance

## Requirement and decision

- proves:: [[Requirements/REQ-025 - Harden verification and release provenance]]
- Decision: [[Decisions/ADR-025 - Layer offline verification before trusted publishing]]
- Delivery issue: [[Issues/ISSUE-023 - Implement verification and provenance hardening]]
- Review: [[Reviews/Phase 10D Verification and Release Provenance Review]]

## Change inventory

- Added 32 fixed-seed generated-graph round trips, 32 deterministic graph-document mutations, 32
  generated untrusted-JSON trees, and a hostile JSON corpus. Accepted mutations must retain graph
  invariants; rejected inputs must fail through bounded `ValueError` validation.
- Added a real Chrome-family browser E2E that serves a 320-node/319-edge graph through the packaged
  loopback viewer and observes JavaScript-rendered DOM with exactly 240 shown nodes and 80 globally
  available omitted nodes.
- Added a full-SHA external Action policy and changed every current CI Action reference from a
  mutable release tag to an immutable 40-character revision.
- Added maintained-source Mypy configuration and an isolated CI job without adding a runtime
  dependency.
- Resolved all strict typing findings through explicit type narrowing and loop-local names; no
  runtime algorithm or confidence rule changed.
- Extended repeated-build verification with a deterministic provenance schema containing exact
  source revision, fixed epoch, artifact names, sizes, hashes, file counts, and completed checks.
- Added a separately dispatched `pypi`-environment workflow that requires an approval phrase,
  exact source/epoch/two hashes, repeated byte equality, short-lived OIDC identity, and the same
  verified artifact directory at publication. It has not been dispatched.
- Updated release, contribution, architecture, security, changelog, and English/Turkish product
  documentation. Default CI remains verification-only.

## Verification

- `.venv\Scripts\python.exe -m pytest tests/test_action.py tests/test_property_fuzz.py
  tests/test_browser_e2e.py tests/test_release.py -q` — 111 passed.
- `.venv\Scripts\python.exe -m pytest --cov=intentatlas --cov-report=term-missing
  --cov-fail-under=80` — 343 passed; total branch-aware coverage 87.91%.
- `.venv\Scripts\python.exe -m mypy` — success, no issues in 38 maintained source files.
- `.venv\Scripts\python.exe -m ruff check .` — passed.
- `.venv\Scripts\python.exe -m bandit -q -r src` — passed.
- `.venv\Scripts\python.exe -m pip check` — no broken requirements.
- `node --check src/intentatlas/web/app.js`, composite Action Bash syntax, and
  `git diff --check` — passed.
- Focused scanner, vault, browser, release, Action-policy, and property/fuzz regression — 139
  passed after materializing the updated project graph.
- Two consecutive repository scans after the final local implementation produced 1,076 nodes,
  2,473 relationships, 941 generated
  notes, and zero durable orphans. The first scan reused two adapters and rebuilt the changed
  Python fragment; the second reused all three adapters with zero rebuilds.
- Two final local Hatchling builds under epoch `1704067200` were byte-identical and matched both
  explicitly approved-hash inputs. The functional provenance fixture used a deliberately
  non-release all-`c` revision: wheel SHA-256
  `8c557cf1874490aacbcc511575e3db1de895a23306fe3beaa695a04828ec4f8b`; source SHA-256
  `2b684f71311c1a779003209ca0a6ffa53712f89e19befa918fc14f5f3462e58e`; 45 wheel and 135 source
  files validated. This proves deterministic record and approval matching, not source-bound
  release closure.
- A fresh environment imported IntentAtlas from the exact final wheel, not the editable source,
  and passed both installed CLI/review E2E cases plus the real Chrome large-graph E2E — 3 passed.
- Clean implementation commit `2f3d69542b0877174529470335a4e7e22bd3632a` was rebuilt twice
  under its own commit epoch `1785610201`. Exact source-bound provenance passed with wheel SHA-256
  `87d9f221a7e79925c73229637a23834f3c8b35cbb20f92ec447ca9e134930a4b` and source SHA-256
  `9f32b351850576f6414b785dcb83da3b827f0505484ee7ed94d758a843a73199`; both approved-hash
  checks matched, with 45 wheel and 135 source files validated.
- Official GitHub releases resolved checkout `v7.0.1` to `3d3c42e...` and setup-python `v7.0.0`
  to `5fda3b95...`; both declare the Node 24 runtime. The PyPI trusted-publishing `release/v1`
  branch resolved to immutable `dc37677...`. Every external reference is full-SHA pinned and the
  local policy accepted all of them on 2026-08-01.
- The post-CI closure materialization before the final record commit produced 1,076 nodes, 2,444
  relationships, 941 generated notes, `3 reused, 0 rebuilt`, and zero durable orphans. A
  subsequent no-change scan kept
  generated-note bytes, lengths, and modification times stable at SHA-256
  `f28acff89fce76184d892038eaaec2a2052ee8ed438c41499c3c4b1eb25e2c29`; the explicit user-owned
  Brain/Requirement/Decision/Issue/Evidence/Review/Session snapshot remained byte-and-mtime stable
  across the same scan. `atlas/Private/` was not enumerated or read.
- The separately approved network audit, `.venv\Scripts\python.exe -m pip_audit`, reported no
  known vulnerabilities. The unpublished local `intentatlas` distribution was the only skipped
  item because it is not available from PyPI; the hosted security job independently passed its
  Bandit and dependency-audit steps.
- Implementation and local-evidence commits through `583bf932f0a975c30afc311e903c3d86e47388ec`
  were pushed to `origin/main`. GitHub Actions run
  [30714014834](https://github.com/AhmetBugrahanAltunok/intentatlas/actions/runs/30714014834)
  completed successfully on 2026-08-01. All 13 jobs passed: Python 3.11/3.12/3.13 tests, the six
  Windows/Linux/macOS installed-wheel E2E combinations, reproducible package/provenance, real
  browser E2E, static typing, and security.

## Remaining operational limits

- The trusted-publishing workflow requires the repository owner to configure protected `pypi`
  reviewers and matching package-index trust before first use. No workflow dispatch or package
  publication has occurred or is authorized by this evidence.
- Property and mutation tests explore deterministic bounded samples; they do not prove the absence
  of every parser or graph defect.
- Passing dependency audits only cover vulnerabilities known to the audit database at execution
  time and must be repeated for future releases.

## Acceptance decision

All REQ-025 acceptance criteria pass. Phase 10D is verified. Publication remains a separately
authorized release operation and was not performed.

## Links

- proves:: [[Requirements/REQ-025 - Harden verification and release provenance]]
- reviewed-by:: [[Reviews/Phase 10D Verification and Release Provenance Review]]
