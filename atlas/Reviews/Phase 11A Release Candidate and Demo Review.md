---
id: review-phase-11a-release-candidate-demo
type: review
status: pass
phase: 11A
---
# Phase 11A Release Candidate and Demo Review

## Acceptance review

- [x] REQ-026 is linked to ADR-026 and ISSUE-024.
- [x] One canonical version source produces `0.3.0rc1` in source, installed runtime, wheel, sdist,
      and metadata.
- [x] The prebuilt demo demonstrates downstream exact-symbol selection without promoting
      same-file ambiguity or claiming end-to-end analysis accuracy.
- [x] Deterministic text/JSON reports and the interactive viewer use the same graph snapshot,
      selected test, evidence boundary, and complete visible advisory.
- [x] Documentation and changelog describe candidate installation, prebuilt-demo limits, explicit
      target paths, repository-only benchmarks, reconstruction, publication controls, and
      attribution accurately.
- [x] Focused/full source, coverage, lint, typing, Bandit, package, installed-wheel, sdist rebuild,
      CLI/UI, loopback-security, and required real-browser local gates pass.
- [x] Release verification binds exact wheel/sdist manifests, complete metadata, fixed hook-free
      build configuration, and runtime bytes to the reviewed checkout.
- [x] Publishing identity is isolated from source/build execution; semantic workflow tests bind
      the exact protected-main revision, three-file transfer, hash recheck, and three-step OIDC job.
- [x] Third-party dependency audit and official Action-SHA identity/signature checks pass.
- [x] Final vault materialization, zero-orphan health, user-owned-area preservation, and generated
      byte/mtime determinism pass.
- [x] Exact committed source revision, commit-epoch repeated builds, deterministic provenance,
      sdist-to-wheel equality, and clean candidate installation pass.
- [x] Git-history Private boundary, bounded Git output, Python ambiguous-module abstention,
      strict configuration, no-touch vault initialization, stable bounded input reads, focused and
      complete local regression, package/browser, and deterministic-vault gates pass.
- [x] The follow-up is bound to an exact implementation commit, generated Commit-note link, and
      source-revision-bound deterministic provenance.
- [x] Push and remote CI pass.
- [ ] Before the later public-launch phase, GitHub private vulnerability reporting and protected
      `pypi` environment controls are externally verified (not a Phase 11A closure gate).

## Evidence examined

- [[Evidence/EVD-026 - Phase 11A release candidate and demo verification]]
- [[Requirements/REQ-026 - Make the release candidate honest and immediately evaluable]]
- [[Decisions/ADR-025 - Layer offline verification before trusted publishing]]
- [[Decisions/ADR-026 - Separate scriptable demo evidence from interactive viewing and publication]]
- [[Issues/ISSUE-024 - Implement the honest 0.3.0 release candidate demo]]

## Final change inventory

- Release-candidate demo, version, local viewer, workflow separation, artifact manifests,
  deterministic provenance, documentation, and release-boundary hardening from the Phase 11A
  implementation and deep audit.
- Git metadata pathspec exclusion and streaming byte limits, Python ambiguous-module abstention,
  strict bounded configuration/report reads, literal Private protection, and no-touch vault
  initialization in exact implementation commit
  `7e8623a6e87154b18c92918d1e61dff307083c5c`.
- Synthetic trust-boundary, resolver, configuration, stable-read, package, workflow, browser, and
  deterministic-vault regressions, with generated Code/Test/Commit/Dashboard materialization.
- Commit-bound evidence/provenance and exact `recorded-in` relationship in evidence commit
  `7f6fb4d9999be457f2a62e90826c9b088c3f840b`.
- Clean typing-environment dependency correction and semantic workflow regression in
  `bfd0f1e775ba8637d0d4c4bb310ab81c181b0269`.
- Phase 11B-13 roadmap records were preserved separately in
  `14aaa0be2b43e9c24dbebdf31c453245d4265fdf`; no Phase 11B, 12, or 13 implementation was included.

## Exact verification and results

- `.venv\Scripts\python.exe -m pytest tests/test_git_history.py tests/test_scanner.py
  tests/test_config.py tests/test_vault.py tests/test_evidence.py tests/test_delivery.py
  tests/test_security.py tests/test_real_world.py -ra` - `107 passed, 2 skipped`.
- With `INTENTATLAS_REQUIRE_BROWSER=1`, `.venv\Scripts\python.exe -m pytest
  --cov=intentatlas --cov-report=term-missing --cov-fail-under=80` - `399 passed, 2 skipped`,
  coverage `87.46%`.
- `.venv\Scripts\python.exe -m ruff check .`, `.venv\Scripts\python.exe -m mypy`,
  `.venv\Scripts\python.exe -m bandit -q -r src tools`,
  `.venv\Scripts\python.exe -m pip check`, `node --check src/intentatlas/web/app.js`, and
  `git diff --check` passed.
- Two offline commit-epoch wheel/sdist builds passed `tools/verify_release.py`; the wheel and
  sdist SHA-256 values are recorded in EVD-026. The sdist-rebuilt wheel matched exactly, a clean
  install reported `IntentAtlas 0.3.0rc1`, and extracted-sdist browser-required tests passed
  `393 passed, 8 skipped`.
- `.venv\Scripts\python.exe -m pip_audit --skip-editable` found no known vulnerabilities. GitHub's
  official Commit API returned the exact five Action SHAs with valid verified signatures.
- Two immediate final scans reported 1,202 nodes, 2,857 relationships, 1,043 generated notes,
  zero adapter rebuilds, and zero durable orphans; 159 user-owned and 1,044 generated files were
  byte/mtime stable. The exact implementation Commit edge and full durable chain were asserted.
- Initial remote run `30742803481` exposed the clean typing dependency gap while its other 12 jobs
  passed. Corrective run `30742936215` passed all 13 jobs, including six cross-platform wheel jobs,
  reproducible package verification, browser, security, typing, and three Python source suites.

## Remaining risks

- Generated-vault synchronization assumes repository directories are not replaced concurrently by
  another hostile process after validation.
- Public vulnerability-reporting settings, protected `pypi` environment controls, tags, releases,
  publication, deployment, visibility changes, and hosted attestations remain separate Phase 11C
  owner-controlled gates. They are not authorized by this review.

## Review decision

Pass. REQ-026 acceptance is satisfied by the exact implementation/evidence chain, deterministic
local and package verification, current network audits, fast-forward push, and fully passing remote
CI. Phase 11A is complete. This decision authorizes no tag, release, publication, deployment,
repository-visibility change, or hosted attestation.
