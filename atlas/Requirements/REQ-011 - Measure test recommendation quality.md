---
id: REQ-011
type: requirement
status: accepted
phase: 6B2B1
---
# Measure test recommendation quality

A maintainer can compare IntentAtlas test recommendations with an explicitly exhaustive,
human-labeled test set and receive deterministic per-case and aggregate precision/recall results.

## Acceptance

- Evaluation labels are explicit local JSON input with a versioned, documented, closed-world
  `complete-test-set` policy.
- Label files remain project-local, avoid `atlas/Private/`, reject symbolic links, duplicate JSON
  keys, unknown fields, malformed types, excessive bytes/cases/tests, duplicate cases, and unsafe
  paths.
- Every target and expected test resolves exactly in the validated graph; stale or wrong-kind
  labels fail instead of being silently skipped.
- Evaluation reuses the production recommendation engine with selected confidence and result
  limits; it never executes tests, project code, language runtimes, or network requests.
- Results report ranked recommendations, true positives, false positives, false negatives,
  precision, and recall per case plus micro-aggregated totals.
- Undefined metrics are represented as `null`/`n/a`, never invented as perfect or zero scores.
- Text and schema-1 JSON are bounded, deterministic, timestamp-free, and explicitly warn that one
  benchmark cannot prove general accuracy.
- A committed IntentAtlas self-hosted label set establishes the first reviewed baseline without
  changing recommendation scores.
- Focused and complete test, lint, security, CLI, package, determinism, and UI gates pass before
  the phase is complete.

## Scope boundary

This phase measures the existing direct-evidence policy. It does not tune scores, add transitive
propagation, claim statistical generalization, or treat repository history as automatic ground
truth. More independently reviewed repositories remain Phase 6B2B2 and Phase 7 work.

## Typed links

- drives:: [[Decisions/ADR-011 - Closed-world recommendation evaluation]]

## Trace

- Roadmap: [[Brain/Product Roadmap]]
- Planned evidence: [[Evidence/EVD-011 - Phase 6B2B1 recommendation evaluation verification]]
