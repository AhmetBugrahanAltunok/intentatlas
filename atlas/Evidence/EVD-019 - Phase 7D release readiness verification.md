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
  --cov-fail-under=80` — 161 passed; total branch-aware coverage 90.32%.
- `.venv\Scripts\python.exe -m ruff check .` — passed.
- `.venv\Scripts\python.exe -m bandit -q -r src` — passed.
- `.venv\Scripts\python.exe -m pip check` — no broken requirements.
- `.venv\Scripts\python.exe -m pip_audit` — no known vulnerabilities; the unpublished local
  `intentatlas` distribution was skipped because it is absent from PyPI.
- `node --check src/intentatlas/web/app.js` and `git diff --check` — passed.
- Two final fixed-timestamp builds were byte-identical. Wheel SHA-256:
  `837834775f34ce4ffb68bf7b26f0f346b92e479464f376f2ae50cbea550e24e5`; source archive SHA-256:
  `3207b43a51970e5a7f4912ea7b71a21ece26842a758d80c6fa907eb4f0d67bfb`. The verifier validated
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
  3.11/3.12/3.13 full tests, and Linux/Windows E2E. Both macOS E2E cells timed out while polling a
  preselected port without a positive server-readiness signal. A second run (`30691140214`) ruled
  out proxy interception. A third run (`30691236189`) used server-selected port 0 and unbuffered
  output, then proved the child stalled before reporting its bound address. This isolated the
  standard `HTTPServer.server_bind` reverse DNS lookup, which can block on the macOS runner before
  listening. `LoopbackHTTPServer` now binds through `TCPServer` and records the already validated
  numeric address without DNS. An independent regression fails any attempted `socket.getfqdn`
  call, and the local installed workflow still passes.
- Remote rerun after the reverse-DNS-free server correction: pending.

## Remaining risks

- The corrected cross-platform CI run has not yet completed.
- Reproducibility was demonstrated with the same source, timestamp, Python, Hatchling, and local
  environment; different build-tool or compression versions can produce different bytes.
- Publication is outside this phase and remains approval-gated.

## Decision

Pending. All local acceptance gates, including the approved network-backed dependency audit, pass.
Phase 7D remains open until the remote CI matrix passes on the implementation commit.
