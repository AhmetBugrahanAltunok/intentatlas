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
- Release boundary: [[Decisions/ADR-025 - Layer offline verification before trusted publishing]]
- Delivery issue: [[Issues/ISSUE-024 - Implement the honest 0.3.0 release candidate demo]]
- Review: [[Reviews/Phase 11A Release Candidate and Demo Review]]

## Deep-audit change inventory

- Retained one Hatchling-backed version source at `src/intentatlas/__init__.py` and candidate
  identity `0.3.0rc1`; no tag, release, publication, deployment, visibility change, or push
  occurred.
- Expanded the original prebuilt demo from 9 nodes/13 relationships to 12 nodes/18 relationships.
  Two requirements, two symbols, and two tests share `src/auth.py`; broad test-to-file fallback
  edges remain present, while the example commit has one canonical `modifies` edge to
  `symbol:src/auth.py::rotate_session`.
- Derived the demo's changed symbol and defining file from graph edges, then exercised production
  recommendation and Change Report contracts. `tests/test_auth_rotation.py` is selected;
  `tests/test_auth_audit.py` stays visible but is not ranked from the supplied exact-symbol
  evidence. Removing the exact `modifies` edge restores both file-fallback candidates, showing
  that the holdout is evidence-sensitive rather than graph-sparse.
- Served the production-shaped Change Report from the same graph snapshot as the interactive demo
  and rendered the complete advisory: omission is not proof that a requirement is unaffected or a
  test unnecessary.
- Hardened the local viewer boundary by normalizing `localhost` to numeric IPv4, rejecting `::1`
  and non-loopback binds, rejecting foreign `Host` headers, and returning CSP, anti-framing,
  no-sniff, no-referrer, same-origin-resource, and no-store response policies.
- Bound release artifacts to reviewed checkout bytes with exact wheel and positive sdist
  manifests, package-payload parity, complete Core Metadata 2.4 validation, fixed project fields,
  fixed base/extra dependencies, a hook-free Hatch configuration, one declarative version source,
  exact WHEEL fields/generator, complete `RECORD`, MIT license bytes, and bounded archives.
- Rejected encrypted and non-regular wheel members, undeclared dist-info files, duplicate or
  Unicode/case-colliding paths, Win32 trailing-dot/reserved paths, unsafe tar links, local-state
  roots, injected dependencies, conflicting metadata, indirect runtime version mutation,
  `backend-path`, and custom build hooks. Deterministic fixtures prevent timestamp-flaky negative
  tests.
- Split publishing into an OIDC-free source/build/verification job and a three-step protected OIDC
  job that only downloads, rechecks, and publishes the approved bytes. Semantic YAML tests bind
  the dispatch revision to protected `main`, exact checkout settings, approval commands, artifact
  paths, hash rechecks, permissions, job shape, and immutable Action identities.
- Extended the security gate to `src` plus `tools`, made editable-package exclusion explicit for
  third-party dependency auditing, and documented fresh per-run release/sdist directories so stale
  local artifacts cannot mask an incomplete package.
- Corrected English/Turkish onboarding, prebuilt-demo limits, repository-only benchmark commands,
  candidate-versus-release status, source reconstruction, protected-environment requirements,
  MIT/third-party attribution, and original open-source positioning. Active roadmap links remain
  the deliberate absolute exception because `atlas/` is excluded from the source archive.

## Focused and complete local verification

- Source-directed commands used absolute `PYTHONPATH=D:\Projects\IntentAtlas\src`; installed-wheel
  commands removed it and resolved `intentatlas` from
  `.venv\Lib\site-packages\intentatlas\__init__.py`.
- Focused release, workflow, demo, viewer, version, and required real-browser suite: `53 passed`.
- Complete source suite with `INTENTATLAS_REQUIRE_BROWSER=1`:
  `.venv\Scripts\python.exe -m pytest --cov=intentatlas --cov-report=term-missing
  --cov-fail-under=80` — `376 passed`; branch-aware coverage `87.92%`.
- `.venv\Scripts\python.exe -m ruff check .` — passed.
- `.venv\Scripts\python.exe -m mypy` — no issues in 38 maintained source files.
- `.venv\Scripts\python.exe -m bandit -q -r src tools` — passed.
- `.venv\Scripts\python.exe -m pip check` — no broken requirements.
- `node --check src/intentatlas/web/app.js` — passed.
- All four PowerShell blocks in `RELEASING.md` parsed as script blocks; semantic workflow tests and
  `git diff --check` passed.
- Installed-wheel CLI and real-browser E2E: `4 passed`. Coverage includes version, demo JSON,
  init/scan/status/changes/impact/recommendation, Change Report retrieval, commit-keyed review,
  loopback security headers/foreign-Host rejection, the 320-node bounded viewer, and the
  12-node/18-link same-file demo.

## Working-tree package verification

- `build==1.3.0` with isolated `hatchling==1.31.0` built the reviewed working tree twice under
  `SOURCE_DATE_EPOCH=1704067200`. `tools/verify_release.py` accepted byte-identical artifacts with
  45 wheel files and 143 sdist files:
  - `intentatlas-0.3.0rc1-py3-none-any.whl`: 125,896 bytes,
    SHA-256 `5ecd54fac264d068419c92451676b3cb3c8e704fe6ba791e63a60500f58d9347`.
  - `intentatlas-0.3.0rc1.tar.gz`: 210,899 bytes,
    SHA-256 `7ee2a8f453ce6e8215375fe0d8b13f53eafd47eb831b39734071b872719ebb0c`.
- Rebuilding the verified sdist wheel with `--no-build-isolation` produced the exact direct-wheel
  SHA-256. A separate clean environment installed that wheel, reported `IntentAtlas 0.3.0rc1`, and
  returned the expected schema-1 rotation-test demo result.
- Extracted verified-sdist tests with a required Chrome-family browser: `370 passed, 6 skipped`.
  The six skips are repository-only workflow tests because `.github/` is intentionally excluded.
- These hashes describe the final pre-commit working tree, not yet a Git source identity. A clean
  local implementation commit and source-revision-bound provenance are still required.

## Network and immutable-dependency verification

- The combined development/release/security/typing environment installed the fixed
  `build==1.3.0`; `pip check` passed.
- `.venv\Scripts\python.exe -m pip_audit --skip-editable` reported no known vulnerabilities. The
  unpublished editable IntentAtlas distribution was the only explicit skip; all installed
  third-party dependencies were audited.
- GitHub's commit API resolved all five configured Action SHAs in their declared official
  repositories on 2026-08-02. Checkout, setup-python, upload-artifact, download-artifact, and the
  PyPI publishing Action all returned the exact requested SHA with a valid verified signature.
- Network use was limited to package resolution/audit and these Action identity checks. No project
  source, graph, vault content, artifact, or telemetry was uploaded.

## Safety and boundary observations

- `atlas/Private/` was not enumerated, read, indexed, or modified. The ignored root `.obsidian/`
  directory was not treated as a vault or package source; `atlas/` remains the only project vault.
- No old ProjectOS content or history and no Obsidian Mind code, logo, or file was imported. The
  existing MIT and legitimate inspiration/third-party attribution boundaries remain intact.
- Commit metadata and tracked project files preserve the existing tool-neutral authorship and
  attribution boundary; IntentAtlas's own generated-note marker remains unaffected.
- No secrets, environment values, raw source bodies, package credentials, deployment, tag,
  release, visibility change, or push were introduced.

## Vault verification

- The first final scan produced 1,144 nodes, 2,480 relationships, and 1,002 generated notes; two
  adapter fragments were reused and one was rebuilt. The immediate second scan reused all three
  fragments and rebuilt none while preserving the same graph and note counts.
- Explicit snapshots covered 142 files in `Brain/`, `Requirements/`, `Decisions/`, `Issues/`,
  `Evidence/`, `Reviews/`, and `Sessions/`, never `Private/`. Hash, length, path, and UTC mtime were
  identical before/after the first scan and after the second scan.
- The 1,003-file generated snapshot across `Code/`, `Symbols/`, `Tests/`, `Commits/`, and
  `Dashboard/` was byte- and mtime-identical across the two scans.
- `intentatlas status` reported 2,480 relationships and zero durable orphans.

## Open gates

- Create a clean local audit-fix commit, rebuild it twice under a fixed recorded epoch, bind
  provenance to that exact source revision, and record the resulting hashes here.
- Push and remote CI remain pending by explicit instruction; Phase 11A cannot close before they
  pass.
- Before any public launch, the owner must verify GitHub private vulnerability reporting and the
  external `pypi` environment's required reviewers/deployment-branch protection. These remote
  settings cannot be proven from local files.
- No tag, release, publication, deployment, or repository-visibility change is authorized.

## Interim decision

All currently executable source, browser, security, dependency, package, install, sdist, and vault
gates pass. Phase 11A remains active until exact committed provenance, push/remote CI, and the
external launch controls above are verified.
