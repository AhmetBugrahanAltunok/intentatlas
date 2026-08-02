---
id: EVD-026
type: evidence
status: verified
phase: 11A
---
# EVD-026 — Phase 11A release candidate and demo verification

## Scope

- proves:: [[Requirements/REQ-026 - Make the release candidate honest and immediately evaluable]]
- Decision: [[Decisions/ADR-026 - Separate scriptable demo evidence from interactive viewing and publication]]
- Release boundary: [[Decisions/ADR-025 - Layer offline verification before trusted publishing]]
- Delivery issue: [[Issues/ISSUE-024 - Implement the honest 0.3.0 release candidate demo]]
- Review: [[Reviews/Phase 11A Release Candidate and Demo Review]]
- proves:: [[Tests/tests - test_git_history.py]]
- proves:: [[Tests/tests - test_scanner.py]]
- proves:: [[Tests/tests - test_config.py]]
- proves:: [[Tests/tests - test_vault.py]]
- proves:: [[Tests/tests - test_evidence.py]]
- proves:: [[Tests/tests - test_delivery.py]]
- proves:: [[Tests/tests - test_security.py]]
- proves:: [[Tests/tests - test_real_world.py]]
- Prior release-candidate audit commit: [[Commits/Commit 0f9d6cb - fix- harden release candidate verification]]
- recorded-in:: [[Commits/Commit 7e8623a - fix- enforce private-safe analysis boundaries]]
- The exact follow-up implementation commit is
  `7e8623a6e87154b18c92918d1e61dff307083c5c`; the prior audit commit remains historical context
  and is not used as provenance for the follow-up tests.

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

## Follow-up hardening inventory and decisions

- Confirmed that Git log and patch output previously crossed the process boundary before the
  Private/configured-exclude filters and collection limits were applied. Git commands now carry
  case-insensitive literal exclusion pathspecs, patch collection is restricted to literal scanned
  symbol paths, and stdout is killed at the byte boundary. Synthetic Git history contains tracked
  mixed-case Private, configured generated, and nested excluded paths and proves none reaches the
  collector.
- Confirmed that Python module ownership previously used scalar overwrite semantics. Resolution
  now retains candidate sets, requires a unique owner at each direct/re-export hop, and abstains on
  repository-root/leading-`src/`, duplicate-init, or direct-plus-re-export collisions. It does not
  guess nested monorepo source roots.
- Confirmed the trust-contract mismatch: vault initialization created `Private/` despite REQ-002's
  absolute no-modification rule. Initialization no longer creates or inspects that user-provisioned
  boundary; literal and configured Private roots, linked generated components, and malformed or
  linked configuration fail closed. Imported JSON/XML and Git blobs share a bounded stable
  regular-file reader; non-blocking opens prevent FIFO stalls where the platform supports FIFOs.
- Fixed generated-area-prefixed wikilink aliases so the durable chain resolves to actual generated
  Code and Test nodes. REQ-026 -> ADR-026 -> ISSUE-024 -> Code and EVD-026 -> Test are present in
  the materialized graph. EVD-026 intentionally has no `recorded-in` edge for this uncommitted
  follow-up; after commit approval it must link to the exact generated note with
  `recorded-in:: [[Commits/Commit <new-short-sha> - <new-subject>]]`.
- A fresh extracted-sdist run first exposed Windows Git fixture paths beyond the default filename
  limit. The synthetic fixture repository now enables its own `core.longpaths`; the final fresh
  archive run passes without changing user or global Git configuration.

## Earlier focused and complete local verification

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

## Current focused and complete local verification

- Source-directed commands used `PYTHONPATH=D:\Projects\IntentAtlas\src`; installed-wheel commands
  removed it and resolved the package from the fresh audit environment.
- Focused trust-boundary, Git-history, resolution, report-import, CLI/change, cache, and
  conformance suite: `156 passed, 2 skipped` on Windows. The skips are the platform-unavailable
  real symlink/FIFO cases; simulated dangling-link, identity-swap, and link-path regressions pass.
- Complete source suite with `INTENTATLAS_REQUIRE_BROWSER=1` and branch-aware coverage:
  `399 passed, 2 skipped`, `87.46%`, above the required 80%.
- `python -m ruff check .`, `python -m mypy src`, `python -m bandit -q -r src tools`,
  `python -m pip check`, `node --check src/intentatlas/web/app.js`, and `git diff --check` passed.

## Earlier working-tree package verification

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

## Current working-tree package verification

- `build==1.3.0` with the locally installed fixed `hatchling==1.31.0` built the reviewed working
  tree twice without network or build isolation under `SOURCE_DATE_EPOCH=1704067200`.
  `tools/verify_release.py` accepted byte-identical artifacts with 46 wheel files and 144 sdist
  files:
  - `intentatlas-0.3.0rc1-py3-none-any.whl`: 129,778 bytes,
    SHA-256 `816636a7c468428fb6f14e77a5760dee29a75e929af9b5c7b37a1d20a97b8238`.
  - `intentatlas-0.3.0rc1.tar.gz`: 218,079 bytes,
    SHA-256 `14d51c5a591c90e48ac0f3d56034a08cbce87d83c2775c8c9195c0d2370cf427`.
- Rebuilding the verified sdist wheel with `--no-build-isolation` produced the exact direct-wheel
  SHA-256. A separate clean environment installed that wheel, reported `IntentAtlas 0.3.0rc1`, and
  returned the expected schema-1 rotation-test demo result.
- Extracted verified-sdist tests with a required Chrome-family browser: `393 passed, 8 skipped`.
  Six skips are repository-only workflow tests because `.github/` is intentionally excluded; the
  other two are the Windows platform skips described above.
- These hashes describe the current uncommitted working tree and are not source-revision-bound
  provenance.

## Follow-up implementation commit verification

- The roadmap handoff records were preserved separately in commit
  `14aaa0be2b43e9c24dbebdf31c453245d4265fdf` (`docs: add phase 11b-13 delivery roadmap`). The
  Phase 11A hardening source, tests, records, and generated vault outputs were committed as
  `7e8623a6e87154b18c92918d1e61dff307083c5c`
  (`fix: enforce private-safe analysis boundaries`) with commit epoch `1785664054`.
- Focused command:
  `.venv\Scripts\python.exe -m pytest tests/test_git_history.py tests/test_scanner.py
  tests/test_config.py tests/test_vault.py tests/test_evidence.py tests/test_delivery.py
  tests/test_security.py tests/test_real_world.py -ra` - `107 passed, 2 skipped`. The Windows
  skips are the unavailable real symlink and FIFO cases; their simulated fail-closed regressions
  pass.
- Complete source command with `INTENTATLAS_REQUIRE_BROWSER=1`:
  `.venv\Scripts\python.exe -m pytest --cov=intentatlas --cov-report=term-missing
  --cov-fail-under=80` - `399 passed, 2 skipped`; branch-aware coverage `87.46%`.
- `.venv\Scripts\python.exe -m ruff check .`, `.venv\Scripts\python.exe -m mypy`,
  `.venv\Scripts\python.exe -m bandit -q -r src tools`,
  `.venv\Scripts\python.exe -m pip check`, `node --check src/intentatlas/web/app.js`, and
  `git diff --check` passed. Mypy checked 39 maintained source files.
- Two offline, non-isolated builds under `SOURCE_DATE_EPOCH=1785664054` were byte-identical and
  `tools/verify_release.py` bound deterministic schema-1 provenance to the exact 40-character
  implementation revision. The verifier accepted 46 wheel files and 144 sdist files:
  - `intentatlas-0.3.0rc1-py3-none-any.whl`: 129,778 bytes,
    SHA-256 `73b97aee824b0fb59f99d3358e87d22d9b7e95b8fc937564892b1a6f6c97fb32`.
  - `intentatlas-0.3.0rc1.tar.gz`: 218,094 bytes,
    SHA-256 `8c0c916104ada128321b5da52c64a7562da1b835ca9d7b59193b0b12b0ed4c3c`.
- Rebuilding the verified sdist wheel with `--no-index --no-deps --no-build-isolation` reproduced
  the direct wheel SHA-256 exactly. A fresh environment installed that exact wheel with
  `--no-index --no-deps`, reported `IntentAtlas 0.3.0rc1`, and returned deterministic schema-1
  JSON plus byte-identical repeated text demo reports. Extracted-sdist tests with a required
  Chrome-family browser passed: `393 passed, 8 skipped`; six skips are repository-only workflow
  tests and two are the Windows platform skips above.
- `pip-audit 2.10.1` with `--skip-editable` reported no known vulnerabilities; only the expected
  unpublished editable IntentAtlas distribution was skipped. GitHub's official Commit API
  returned the exact configured SHA with `verification.verified=true` and reason `valid` for
  `actions/checkout`, `actions/setup-python`, `actions/upload-artifact`,
  `actions/download-artifact`, and `pypa/gh-action-pypi-publish` on 2026-08-02.
- The deterministic provenance JSON is a local ignored audit artifact under `var/`; it is not a
  signature, hosted attestation, release, or publication approval.

## First remote CI run and correction

- Push run `30742803481` for evidence commit
  `7f6fb4d9999be457f2a62e90826c9b088c3f840b` completed with 12 passing jobs and one failed
  `static-types` job. Security, Python 3.11/3.12/3.13 source tests, required browser E2E,
  reproducible package verification, and all six Linux/macOS/Windows installed-wheel jobs passed.
- The clean typing job installed only `.[typing]`, while the maintained
  `tools/verify_release.py` imports `packaging.metadata` and `packaging.requirements` from the
  release toolchain. Mypy therefore reported two `import-not-found` errors. This was an environment
  contract gap, not a suppression candidate.
- The workflow now installs `.[release,typing]` for the typing job, and
  `tests/test_action.py::test_static_type_job_installs_release_tool_imports` locks that semantic
  dependency contract. Focused verification reported `7 passed`; Ruff, mypy across 39 maintained
  source files, and `git diff --check` passed locally. The corrective remote run remains required.

## Exact committed candidate provenance

- Local audit commit `0f9d6cbc722c814d49abc26949b4be38c30a75b1`
  (`fix: harden release candidate verification`) was cleanly rebuilt twice with its recorded
  `SOURCE_DATE_EPOCH=1785624255` through `build==1.3.0` and isolated `hatchling==1.31.0`.
- Deterministic provenance schema 1 binds that exact source revision and epoch to:
  - `intentatlas-0.3.0rc1-py3-none-any.whl`: 125,896 bytes,
    SHA-256 `f6ee19a3f1f3d0a15abdfd18f557e6270f34f46fe913c857a8939c14713750c4`.
  - `intentatlas-0.3.0rc1.tar.gz`: 210,901 bytes,
    SHA-256 `dda498a0ee444950fcbcb0045091aa48a58c83d0692c07b07cb1705bdbed7b56`.
- The verifier accepted 45 exact wheel members and 143 exact sdist files and recorded Hatchling
  1.31.0 as generator. Rebuilding the committed sdist reproduced the wheel SHA-256 exactly.
- A fresh environment installed the committed wheel with `--no-deps`, reported
  `IntentAtlas 0.3.0rc1`, and returned the expected rotation-test demo result.
- The provenance JSON remains a local ignored audit artifact under `var/`; it describes verified
  bytes and is not represented as a signature, hosted attestation, tag, or publication approval.

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

## Prior committed audit vault verification

- The first final scan produced 1,144 nodes, 2,480 relationships, and 1,002 generated notes; two
  adapter fragments were reused and one was rebuilt. The immediate second scan reused all three
  fragments and rebuilt none while preserving the same graph and note counts.
- After the exact audit commit and provenance update, final materialization retained 1,144 nodes
  and 1,002 generated notes, incorporated the new commit evidence at 2,550 relationships, reused
  all three adapter fragments, and rebuilt none. Its immediate second scan was identical.
- Explicit snapshots covered 142 files in `Brain/`, `Requirements/`, `Decisions/`, `Issues/`,
  `Evidence/`, `Reviews/`, and `Sessions/`, never `Private/`. Hash, length, path, and UTC mtime were
  identical before/after the first scan and after the second scan.
- The 1,003-file generated snapshot across `Code/`, `Symbols/`, `Tests/`, `Commits/`, and
  `Dashboard/` was byte- and mtime-identical across the two scans.
- Final `intentatlas status` reported 2,550 relationships and zero durable orphans.

## Current follow-up vault verification

- The first follow-up scan produced 1,184 nodes, 2,663 relationships, and 1,042 generated notes;
  two adapter fragments were reused and one was rebuilt. The immediate second scan reused all
  three fragments and rebuilt none while preserving the same graph and note counts.
- Explicit snapshots covered 142 files in `Brain/`, `Requirements/`, `Decisions/`, `Issues/`,
  `Evidence/`, `Reviews/`, and `Sessions/`, never `Private/`. Hash, length, path, and UTC mtime were
  identical before/after the first scan and after the second scan.
- The 1,043-file generated snapshot across `Code/`, `Symbols/`, `Tests/`, `Commits/`, and
  `Dashboard/` was byte- and mtime-identical across the two scans.
- Final `intentatlas status` reported 2,663 relationships and zero durable orphans. Explicit graph
  assertions passed for REQ-026 -> ADR-026, ADR-026 -> ISSUE-024, ISSUE-024 ->
  `src/intentatlas/git_history.py`, and EVD-026 -> `tests/test_git_history.py`; the pending new
  implementation-commit edge is absent as required before commit approval.

## Commit-bound closure vault verification

- After materializing the exact implementation Commit note and `recorded-in` edge, two immediate
  source-directed scans each reported 1,201 nodes, 2,879 relationships, 1,042 generated notes,
  three adapter fragments reused, and zero rebuilt.
- Explicit snapshots covered 159 files in `Brain/`, `Requirements/`, `Decisions/`, `Issues/`,
  `Evidence/`, `Reviews/`, and `Sessions/`, never `Private/`. Path, length, SHA-256, and UTC mtime
  were unchanged by both scans.
- The 1,043-file generated snapshot across `Code/`, `Symbols/`, `Tests/`, `Commits/`, and
  `Dashboard/` was byte- and mtime-identical across the two scans.
- Final `intentatlas status` reported 2,879 relationships and zero durable orphans. Graph
  assertions passed for REQ-026 -> ADR-026, ADR-026 -> ISSUE-024, ISSUE-024 ->
  `src/intentatlas/git_history.py`, EVD-026 -> `tests/test_git_history.py`, and EVD-026
  `recorded-in` -> exact implementation commit `7e8623a6e87154b18c92918d1e61dff307083c5c`.

## Remote closure verification

- `main` was fetched before each push and advanced by ordinary fast-forward updates without force:
  `58590e0..7f6fb4d` for the roadmap, implementation, and commit-bound evidence commits, followed
  by `7f6fb4d..bfd0f1e` for the typing-environment correction.
- Corrective push run `30742936215` for commit
  `bfd0f1e775ba8637d0d4c4bb310ab81c181b0269` passed all 13 jobs: security, static typing,
  required browser E2E, reproducible package/sdist verification, Python 3.11/3.12/3.13 source
  suites, and six installed-wheel jobs across Linux, macOS, and Windows on Python 3.11 and 3.13.
- The successful run is recorded at
  `https://github.com/AhmetBugrahanAltunok/intentatlas/actions/runs/30742936215`.

## Final post-correction vault verification

- After the remote typing correction and final status updates, two immediate scans each reported
  1,202 nodes, 2,857 relationships, 1,043 generated notes, all three adapter fragments reused,
  zero rebuilt, and zero durable orphans.
- Snapshots of 159 user-owned files and 1,044 generated files were byte- and UTC-mtime-identical
  across the scans. The full REQ-026 -> ADR-026 -> ISSUE-024 -> Code/Test -> EVD-026 -> exact
  implementation Commit chain was asserted again.

## Remaining risks and later gates

- Vault synchronization rejects linked components present during validation, but it does not claim
  cross-platform protection against a separate hostile process replacing a verified generated
  directory while synchronization is running. Scans assume repository/vault directories remain
  under the invoking user's control for the duration of the operation.
- Before any later public launch, the owner must verify GitHub private vulnerability reporting and
  the external `pypi` environment's required reviewers/deployment-branch protection. These are
  Phase 11C/publication controls, not a substitute for the Phase 11A remote-CI gate.
- No tag, release, publication, deployment, or repository-visibility change is authorized.

## Final decision

Verified. The follow-up implementation is bound to an exact commit, deterministic provenance,
generated Commit note, passing local regression/package/browser gates, current authorized network
audits, fast-forward push, and a fully passing 13-job remote CI run. Phase 11A acceptance is
satisfied. Tagging, release creation, publication, deployment, visibility changes, hosted
attestation, and the external Phase 11C launch controls remain unapproved and outside this closure.
