---
id: ISSUE-034
type: issue
status: complete
phase: 18
---
# Apply first-run observation fixes

## Observation intake

- [x] Retain the measured first meaningful result (`41 seconds`) and full README walkthrough
      (`7 minutes 52 seconds`) as evaluator observations, not human usability proof.
- [x] Reproduce the markerless `src.auth` symbol-to-test failure in a minimal Python project.
- [x] Classify generated-state staging, unclear project context, missing-artifact guidance,
      `diff --check`, non-TTY, command-selection, and freshness-language findings.
- [x] Remove the disposable raw report files after transferring accepted findings to durable notes.

## Documentation and onboarding

- [x] Rewrite the English and Turkish README openings in plain language.
- [x] Add `docs/assets/intentatlas-demo.gif`, shortest installation, product boundaries, a real
      example with expected output, and demo/preview/adoption command tables.
- [x] Explain network and managed-cache effects, cache IDs, scan/init writes, graph/report
      freshness, confidence bands, omissions, and command differences.
- [x] Update installation, guided CLI, trust-first preview, evaluation, benchmark, and docs-index
      guidance consistently.

## Behavior fixes

- [x] Resolve unique explicit `src.` imports in markerless Python layouts and increment the adapter
      cache version.
- [x] Prefer exact file-to-symbol-to-test evidence in file recommendations.
- [x] Add diagnostic project identity, repository-state-aware scope selection, and saved-graph
      exact Python symbol-test health.
- [x] Add idempotent `.gitignore` initialization rules for local generated state.
- [x] Show project identity in impact/recommendation output and improve missing graph/baseline,
      traversal, evaluation target, viewer flush, threshold, TTY, and `diff --check` guidance.
- [x] Preserve UTF-8 BOM reading and bounded oversized-file freshness checks.

## Verification and closure

- [x] Add regressions for markerless imports, ranking, diagnostic scopes/health, `.gitignore`, CLI
      guidance, viewer output, and platform-native command quoting.
- [x] Pass focused and complete local tests, Ruff, mypy, Bandit, and `git diff --check`.
- [x] Push the implementation and cross-platform test correction to private `main`.
- [x] Pass all final-head GitHub Actions jobs on Python 3.11/3.12/3.13, Windows, macOS, Linux,
      browser E2E, static typing, security/audit, and reproducible source-package verification.

## Links

- implements:: [[Requirements/REQ-034 - Harden the first-run experience from observed use]]
- decided-by:: [[Decisions/ADR-036 - Use repository-state-aware first-run guidance]]
- implemented-by:: [[Code/src - intentatlas - adapters - python.py]]
- implemented-by:: [[Code/src - intentatlas - diagnostic.py]]
- implemented-by:: [[Code/src - intentatlas - recommendations.py]]
- implemented-by:: [[Code/src - intentatlas - onboarding.py]]
- verified-by:: [[Tests/tests - test_diagnostic.py]]
- verified-by:: [[Tests/tests - test_trust_first.py]]
- verified-by:: [[Tests/tests - test_scanner.py]]
- verified-by:: [[Tests/tests - test_recommendations.py]]
- evidence:: [[Evidence/EVD-034 - Phase 18 first-run experience hardening verification]]
- reviewed-by:: [[Reviews/Phase 18 First-Run Experience Hardening Review]]
