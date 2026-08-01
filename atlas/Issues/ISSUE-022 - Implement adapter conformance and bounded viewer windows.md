---
id: ISSUE-022
type: issue
status: closed
phase: 10C
---
# ISSUE-022 — Implement adapter conformance and bounded viewer windows

Implement [[Decisions/ADR-024 - Validate adapters and render bounded graph windows]] for
[[Requirements/REQ-024 - Keep adapters trustworthy and large graphs responsive]].

## Acceptance checklist

- [x] Shared adapter definition/fragment validation and public repeated-scan conformance helper.
- [x] Built-in adapters declare and pass the same evidence and structural contract.
- [x] Fresh and cached scan paths fail closed on malformed adapter output.
- [x] Viewer renders deterministic bounded overview/focus windows with indexed graph access.
- [x] Global search, linked navigation, overview restore, counts, and bounded details remain usable.
- [x] Contract documentation and large-graph viewer behavior are documented in both READMEs.
- [x] Focused/full tests, coverage, lint, security, CLI/UI E2E, determinism, and vault closure pass.

## Planned implementation links

- implemented-by:: [[src - intentatlas - adapters - conformance.py|src/intentatlas/adapters/conformance.py]]
- implemented-by:: [[src - intentatlas - scanner.py|src/intentatlas/scanner.py]]
- implemented-by:: [[src - intentatlas - web - app.js|src/intentatlas/web/app.js]]
- verified-by:: [[tests - test_adapter_conformance.py|tests/test_adapter_conformance.py]]
- verified-by:: [[tests - test_viewer.py|tests/test_viewer.py]]

## Context

- Strategy: [[Brain/Phase 8-10 Strategy]]
- Kickoff: [[Sessions/2026-08-01 - Phase 10C kickoff]]
