---
id: EVD-026
type: evidence
status: partial
phase: 11A
---
# EVD-026 — Phase 11A release candidate and demo verification

## Scope

- proves:: [[Requirements/REQ-026 - Make the release candidate honest and immediately evaluable]]
- Decision: [[Decisions/ADR-026 - Separate scriptable demo evidence from interactive viewing and publication]]
- Delivery issue: [[Issues/ISSUE-024 - Implement the honest 0.3.0 release candidate demo]]
- Review: [[Reviews/Phase 11A Release Candidate and Demo Review]]

## Interim change inventory

- Replaced duplicated static package-version configuration with Hatchling dynamic versioning from
  `src/intentatlas/__init__.py` and prepared `0.3.0rc1` without a tag or publication.
- Expanded the original demo from 9 nodes/13 relationships to 12 nodes/16 relationships with two
  requirements, two symbols, and two tests sharing `src/auth.py`; the example commit modifies only
  `rotate_session`.
- Added deterministic schema-1 text and JSON reports derived from graph indexes and the production
  recommendation engine. The report selects `tests/test_auth_rotation.py`, leaves
  `tests/test_auth_audit.py` unpromoted at the default threshold, and explicitly rejects an
  “unaffected” or “unnecessary” interpretation.
- Preserved `intentatlas demo` as the production loopback viewer default and added report mode as an
  immediate no-listener path.
- Extended source and exact-wheel CLI E2E, real Chrome-family rendering, version consistency,
  release-verifier fixtures, English/Turkish onboarding, guided demo, architecture, changelog, and
  release instructions.
- Added the Phase 11 strategy and linked REQ-026, ADR-026, ISSUE-024, kickoff, Evidence, Review, and
  Product Roadmap records.

## Interim local verification

- `.venv\Scripts\python.exe -m pytest tests/test_demo.py tests/test_version.py
  tests/test_release.py tests/test_e2e.py tests/test_browser_e2e.py -q` with
  `INTENTATLAS_REQUIRE_BROWSER=1` — 17 passed.
- `.venv\Scripts\python.exe -m pytest --cov=intentatlas --cov-report=term-missing
  --cov-fail-under=80` — 346 passed; total branch-aware coverage 88.00%.
- `.venv\Scripts\python.exe -m ruff check .` — passed.
- `.venv\Scripts\python.exe -m mypy` — success, no issues in 38 maintained source files.
- `.venv\Scripts\python.exe -m bandit -q -r src` — passed.
- `.venv\Scripts\python.exe -m pip check` — no broken requirements.
- `node --check src/intentatlas/web/app.js` and `git diff --check` — passed.
- Two Hatchling builds under epoch `1704067200` were byte-identical and passed the release
  verifier: wheel SHA-256 `de660a8d63eb834bf06b69e91c5015199ca3bd7279ccd71901f8e0b75089343a`,
  sdist SHA-256 `ac1ab1e23c5e1ab6c84bc6376a7b4f39ff42a7e4da99a5b8cb2d8eecb5754925`,
  with 45 wheel and 136 source files. These are working-tree verification artifacts, not yet the
  source-bound final candidate.
- A new environment installed that exact wheel with `--no-deps`, reported
  `IntentAtlas 0.3.0rc1`, and rendered both text and valid JSON reports without using the source
  tree.
- Clean implementation commit `1c640192410c35b7287b2aaddeae6b8cdadcc75d` was rebuilt twice under
  its own commit epoch `1785613103`. Exact source-bound provenance and approved-hash matching
  passed: wheel SHA-256 `44a8f7ec7a9c880fecdf605c9ba6ffde4c6a48986c8a99636281a6485dae496a`
  at 124,511 bytes and sdist SHA-256
  `c8aaa0ac3486fbab41921e2bc97bf763680a00e212d9a1c86712d0e841fad758` at 192,167 bytes, with 45
  wheel and 136 source files. A new environment installed the exact committed wheel, reported the
  candidate version, and parsed its JSON demo report successfully.
- Final local vault materialization produced 1,096 nodes, 2,422 relationships, 954 generated notes,
  `3 reused, 0 rebuilt`, and zero durable orphans. A subsequent no-change scan kept generated
  bytes, lengths, and mtimes stable at SHA-256
  `875153455001f8da8ddb18088e696bbc842d3f93a7f7091c050d09c2ee562fc7`; explicit user-owned areas
  were byte-and-mtime stable. `atlas/Private/` was not enumerated or read.

## Open gates

- Re-run the complete local gates after final Evidence/Review materialization.
- Network dependency audit, push, remote CI, final Review, and acceptance remain pending and need
  separate authorization where required.
- No tag, release, package publication, deployment, or repository-visibility change is authorized.

## Interim decision

Phase 11A remains active. All implemented behavior and current local gates pass, but exact committed
provenance, remote closure, and final Review prevent acceptance.
