---
id: ADR-021
type: decision
status: accepted
phase: 9
---
# ADR-021 — Compose review formats over trustworthy change reports

## Context

Phase 8 established bounded revision input, explicit freshness, exact/fallback/unknown analysis,
and advisory requirement/test output. A pull-request review that independently reimplements those
rules would drift and could present contradictory confidence.

CI output also has different consumers: people need readable Markdown, automation needs stable
JSON, and code-scanning systems need SARIF. None of these formats should imply that a structural
candidate is a proven defect.

## Decision

Build Review Report schema 1 as a pure presentation layer over a range ChangeSet and its Change
Report schema 1. Resolve base/head through the existing Git boundary, scan once, and retain the
resolved revisions and all existing uncertainty. Do not add another impact traversal.

Emit deterministic Markdown, JSON, and SARIF 2.1.0 without timestamps. Markdown summarizes scope,
strategy, possible requirements, candidate tests, and analysis gaps. JSON contains the review
schema plus the complete nested change report. SARIF uses fixed first-party rule IDs, bounded
results, safe project-relative URIs and hunk regions, and no source excerpts. Requirement-impact
results are informational; fallback and unknown analysis are explicit analysis-gap findings.

The first CI integration is shadow mode only. The command exits successfully when it produces a
valid report regardless of findings. It does not post comments, upload artifacts, call provider
APIs, execute tests, read credentials, or change repository state. Blocking policy requires a
separate future decision backed by pilot evidence.

Later test-outcome comparison must require a full commit identity and explicit freshness. A stale
or unkeyed JUnit result remains an observation and cannot validate or invalidate a prediction.

Use a separate, strict vendor-neutral JSON sidecar for that comparison rather than inferring commit
identity from JUnit names or file timestamps. Schema 1 contains one full 40-character Git commit,
an explicit `complete-executed-set` policy, and a bounded unique list of safe project-relative test
paths with `passed`, `failed`, `error`, or `skipped` status. It contains no console output, source
content, environment data, or absolute paths. The review command accepts the sidecar only through
an explicit project-relative option outside `atlas/Private/`.

Compare outcomes with predictions only when the sidecar commit exactly equals the resolved review
head. An unequal commit is reported as `stale` but produces no matched/missing prediction claims.
An aligned sidecar may show predicted-and-executed, predicted-not-executed, and executed-not-
predicted paths as observational coverage of that run; none of those sets is labeled accuracy,
necessity, sufficiency, false positive, or false negative.

## Consequences

- CLI, CI, and viewer consumers share one evidence and confidence model.
- SARIF annotations remain useful without being mislabeled as certain defects.
- Shadow-mode adoption can gather false-positive/false-negative evidence safely before policy.
- Provider comments, network access, and blocking checks remain out of scope for the first slice.

## Links

- Requirement: REQ-021 (available through the incoming `drives` relationship)
- tracked-by:: [[Issues/ISSUE-019 - Implement CI shadow review loop]]
- Strategy: [[Brain/Phase 8-10 Strategy]]
