---
id: EVD-019
type: evidence
status: pending
phase: 7D
---
# EVD-019 — Phase 7D release readiness verification

## Requirement and decision

- proves:: [[Requirements/REQ-019 - Ship verifiable cross-platform releases]]
- Decision: [[Decisions/ADR-019 - Separate reproducible verification from publication]]
- Delivery issue: [[Issues/ISSUE-017 - Implement open-source release gates]]
- Review: [[Reviews/Phase 7D Open-Source Release Readiness Review]]

## Change inventory

- Added a subprocess end-to-end test that creates a project in a path containing spaces and uses
  the installed module for init, scan, status, impact, recommendation, and loopback viewer HTTP
  retrieval. A source file that raises at module load confirms scanning does not execute it.
- Added a six-cell Linux/Windows/macOS and Python 3.11/3.13 CI matrix. Each cell builds and installs
  the wheel, verifies the console entry point, and runs the installed-package E2E test.
- Added a separate package job that builds wheel and source archives twice under a fixed
  `SOURCE_DATE_EPOCH` and requires the local release verifier to pass.
- The verifier requires byte-identical artifact names and SHA-256 values; validates safe wheel
  members, CRCs, metadata, console entry point, web assets, MIT license bytes, and every `RECORD`
  hash and size; and validates safe source members and package boundaries.
- The source distribution now includes source, tests, documentation, release tooling, and required
  root metadata while excluding the vault, benchmarks, GitHub workflows, and local configuration.
- Added independent verifier regressions for valid repeated archives and a non-reproducible wheel.
- Added `RELEASING.md` and updated English/Turkish README, architecture, security, changelog,
  contribution, roadmap, requirement, decision, issue, Evidence, and Review records.

## Verification

- `.venv\Scripts\python.exe -m pytest tests\test_e2e.py tests\test_release.py -q` — 3 passed.
- `.venv\Scripts\python.exe -m pytest --cov=intentatlas --cov-report=term-missing
  --cov-fail-under=80` — 160 passed; total branch-aware coverage 90.31%.
- `.venv\Scripts\python.exe -m ruff check .` — passed.
- `.venv\Scripts\python.exe -m bandit -q -r src` — passed.
- `.venv\Scripts\python.exe -m pip check` — no broken requirements.
- `.venv\Scripts\python.exe -m pip_audit` — no known vulnerabilities; the unpublished local
  `intentatlas` distribution was skipped because it is absent from PyPI.
- `node --check src/intentatlas/web/app.js` and `git diff --check` — passed.
- Two final fixed-timestamp builds were byte-identical. Wheel SHA-256:
  `5662bd344e7b82268517cc8943335f6fff84d460f15bdefaa27ab71b36daf40c`; source archive SHA-256:
  `ec91ea4ce9ea24ddcaecc594f50993513713cce8505963d35e3b3e8a7a3e4e96`. The verifier validated
  36 wheel files and 109 source files.
- A fresh virtual environment installed the exact wheel with `--no-deps`, reported IntentAtlas
  0.1.0, and completed init, scan, zero-orphan status, and advisory test recommendation commands.
- The installed wheel's real viewer loaded 8 nodes and 10 links. Keyboard selection of `app.py`
  displayed the `test_app.py` evidence path, and the browser console contained no errors. The tab
  and loopback server were closed after verification.
- Two closure scans each produced 759 nodes, 1,765 relationships, 661 generated notes, and zero
  durable orphans. The normalized graph SHA-256 was stable at
  `01e01b464afb4d25a305171ea7b7c6d853ab8ce1b4f483a5083de2567b778a38`; generated-note bytes plus
  nanosecond modification times were stable at
  `e51fa68d8c116eb71224926d872a61de3d31593d8a6c4d49a5f7723d2bf93d4a`. Explicit user-owned areas
  were byte-stable, and `atlas/Private/` was not enumerated or read.
- Network-backed dependency audit: passed after explicit approval.
- The first remote run (`30691033738`) passed security, reproducible package, Python
  3.11/3.12/3.13 full tests, and Linux/Windows E2E. Both macOS E2E cells exposed that runner proxy
  variables could intercept the test's loopback `urllib` request. The product server remained
  running, but the request timed out. The regression now uses an explicit no-proxy opener for
  `127.0.0.1`; a local run with deliberately invalid proxy variables passed.
- Remote rerun after the macOS regression correction: pending.

## Remaining risks

- The corrected cross-platform CI run has not yet completed.
- Reproducibility was demonstrated with the same source, timestamp, Python, Hatchling, and local
  environment; different build-tool or compression versions can produce different bytes.
- Publication is outside this phase and remains approval-gated.

## Decision

Pending. All local acceptance gates, including the approved network-backed dependency audit, pass.
Phase 7D remains open until the remote CI matrix passes on the implementation commit.
