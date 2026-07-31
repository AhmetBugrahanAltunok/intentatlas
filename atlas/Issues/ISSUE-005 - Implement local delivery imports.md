---
id: ISSUE-005
type: issue
status: complete
phase: 5B
---
# ISSUE-005 — Implement local delivery imports

Implement ADR-007 without adding network access, credentials, dependencies, or raw discussion
content.

## Acceptance checklist

- [x] Bounded report configuration and path confinement implemented.
- [x] Vendor-neutral issue/PR schema and deterministic import implemented.
- [x] Typed intent, issue, PR, file, and known-commit relationships implemented.
- [x] Generated vault routing, viewer layers, fixture, and focused tests implemented.
- [x] Complete CLI/UI, package, determinism, Evidence, and Review gates pass.

## Planned implementation links

- implemented-by:: [[src - intentatlas - delivery.py|src/intentatlas/delivery.py]]
- implemented-by:: [[src - intentatlas - config.py|src/intentatlas/config.py]]
- implemented-by:: [[src - intentatlas - scanner.py|src/intentatlas/scanner.py]]
- implemented-by:: [[src - intentatlas - relations.py|src/intentatlas/relations.py]]
- implemented-by:: [[src - intentatlas - vault.py|src/intentatlas/vault.py]]
- implemented-by:: [[src - intentatlas - web - app.js|src/intentatlas/web/app.js]]
- implemented-by:: [[tests - test_delivery.py|tests/test_delivery.py]]

## Context

- Requirement: REQ-007 (linked through ADR-007)
- Decision: ADR-007 (available through the incoming `tracked-by` relationship)
- Evidence: [[Evidence/EVD-007 - Phase 5B local delivery verification]]
- Review: [[Reviews/Phase 5B Local Delivery Review]]
