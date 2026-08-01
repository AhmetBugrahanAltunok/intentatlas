---
id: ISSUE-012
type: issue
status: closed
phase: 6B2B2B2A
---
# ISSUE-012 — Implement guided demo and viewer evidence paths

Implement ADR-014 without weakening the offline, loopback-only, or vault-first boundaries.

## Acceptance checklist

- [x] Original demo graph covers the complete intent-to-proof story with typed relationships.
- [x] `intentatlas demo` uses temporary storage and the existing loopback viewer.
- [x] Evidence-path traversal is deterministic and explicitly bounded.
- [x] Path cards preserve edge direction and typed forward/inverse labels.
- [x] Existing search, relationship, filter, keyboard, and responsive viewer workflows regress cleanly.
- [x] README, architecture, security, changelog, roadmap, Evidence, and Review are updated.
- [x] Focused and complete CLI/UI, package, determinism, attribution, and security gates pass.

## Planned implementation links

- implemented-by:: [[src - intentatlas - demo.py|src/intentatlas/demo.py]]
- implemented-by:: [[src - intentatlas - cli.py|src/intentatlas/cli.py]]
- implemented-by:: [[src - intentatlas - web - app.js|src/intentatlas/web/app.js]]
- implemented-by:: [[tests - test_demo.py|tests/test_demo.py]]

## Context

- Requirement: REQ-014 (linked through ADR-014)
- Decision: ADR-014 (available through the incoming `tracked-by` relationship)
- Evidence: [[Evidence/EVD-014 - Phase 6B2B2B2A guided demo verification]]
- Review: [[Reviews/Phase 6B2B2B2A Guided Demo Review]]
