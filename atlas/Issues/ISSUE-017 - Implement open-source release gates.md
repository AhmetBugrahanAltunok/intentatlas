---
id: ISSUE-017
type: issue
status: in-progress
phase: 7D
---
# ISSUE-017 — Implement open-source release gates

Implement ADR-019 without publishing, deploying, or executing scanned repository code.

## Acceptance checklist

- [x] Installed-package subprocess E2E covers the core CLI and loopback viewer workflow.
- [x] CI builds and installs a wheel on Linux, Windows, and macOS for Python 3.11 and 3.13.
- [x] Repeated wheel and source builds use a fixed timestamp and must be byte-identical.
- [x] The local verifier checks integrity, metadata, entry point, web assets, MIT license, safe
  archive paths, and source-package exclusions.
- [x] Source-distribution configuration omits project-only vault, benchmark, workflow, and local
  configuration data.
- [x] English/Turkish setup context, architecture, security, changelog, contribution, and release
  documentation are updated.
- [x] Complete local quality gates pass and are recorded.
- [ ] Remote quality gates pass and are recorded.
- [ ] Evidence and final review record exact results, hashes, CI run, and remaining risks.

## Planned implementation links

- implemented-by:: [[tools - verify_release.py|tools/verify_release.py]]
- implemented-by:: [[tests - test_e2e.py|tests/test_e2e.py]]
- implemented-by:: [[tests - test_release.py|tests/test_release.py]]
- implemented-by:: [[github - workflows - ci.yml|.github/workflows/ci.yml]]
- implemented-by:: [[pyproject.toml]]

## Context

- Requirement: REQ-019 (linked through ADR-019)
- Decision: ADR-019 (available through the incoming `tracked-by` relationship)
- Planned evidence: [[Evidence/EVD-019 - Phase 7D release readiness verification]]
- Planned review: [[Reviews/Phase 7D Open-Source Release Readiness Review]]
