---
id: ISSUE-015
type: issue
status: closed
phase: 7B
---
# ISSUE-015 — Expand and refine real-world validation

Implement ADR-017 while preserving the external-source, license, and offline trust boundaries.

## Acceptance checklist

- [x] Click, Axios, and Cobra provenance and licenses are pinned and reviewed.
- [x] Nine new commit/file/symbol cases are independently labeled.
- [x] Source-only and multiple-test scenarios are represented.
- [x] Initial six-project metrics are recorded before code refinement.
- [x] Imported Go tests use qualified unique-symbol evidence instead of package-wide fan-out.
- [x] Cobra false positives fall from 18 to zero without changing labels or scores.
- [x] Complete quality, security, package, CLI/UI, determinism, attribution, and vault gates pass.
- [x] Evidence and final review record exact results and remaining risks.

## Planned implementation links

- implemented-by:: [[src - intentatlas - adapters - go.py|src/intentatlas/adapters/go.py]]
- implemented-by:: [[tests - test_adapters.py|tests/test_adapters.py]]
- implemented-by:: [[tests - test_scanner.py|tests/test_scanner.py]]
- implemented-by:: [[benchmarks - real-world - manifest.json|benchmarks/real-world/manifest.json]]

## Context

- Requirement: REQ-017 (linked through ADR-017)
- Decision: ADR-017 (available through the incoming `tracked-by` relationship)
- Evidence: [[Evidence/EVD-017 - Phase 7B broader validation verification]]
- Review: [[Reviews/Phase 7B Broader Validation Review]]
