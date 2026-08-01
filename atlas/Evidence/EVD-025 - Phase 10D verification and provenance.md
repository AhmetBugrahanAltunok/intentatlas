---
id: EVD-025
type: evidence
status: partial
phase: 10D
---
# EVD-025 — Phase 10D verification and provenance

## Requirement and decision

- proves:: [[Requirements/REQ-025 - Harden verification and release provenance]]
- Decision: [[Decisions/ADR-025 - Layer offline verification before trusted publishing]]
- Delivery issue: [[Issues/ISSUE-023 - Implement verification and provenance hardening]]
- Review: [[Reviews/Phase 10D Verification and Release Provenance Review]]

## Interim change inventory

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

## Interim verification

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
- Official Git references resolved the pinned checkout `v4.2.2` to `11bd719...`, setup-python
  `v5.6.0` to `a26af69...`, and the PyPI trusted-publishing `release/v1` branch to immutable
  `dc37677...` on 2026-08-01. The local policy accepted every external reference.
- A no-change closure scan kept generated-note bytes and nanosecond modification times stable at
  SHA-256 `16e9cff43c3e044e62ed247599e83edef344e6663e09f5f932146ba22f1fbde6`;
  the explicit user-owned Brain/Requirement/Decision/Issue/Evidence/Review/Session areas were
  byte-stable across the same scan. `atlas/Private/` was not enumerated or read.

## Open gates

- Pinned Action revisions require remote CI execution before they can close the hosted gate.
- The trusted-publishing workflow requires the repository owner to configure protected `pypi`
  reviewers and matching package-index trust before first use. No workflow dispatch or package
  publication has occurred or is authorized by this evidence.
- Final deterministic vault, remote CI, dependency-audit, and Review closure remain pending.

## Interim decision

Phase 10D remains active. Local property/fuzz, browser, typing, policy, package, installed-wheel,
and committed-source provenance behavior passes, but the remote CI, dependency-audit, and final
Review gates prevent completion.
