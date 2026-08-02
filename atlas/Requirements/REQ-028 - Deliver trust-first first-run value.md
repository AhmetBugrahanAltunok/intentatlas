---
id: REQ-028
type: requirement
status: proposed
phase: 12
---
# Deliver trust-first first-run value

A maintainer can obtain an honest, explainable result from a real repository in the first ten
minutes without initializing a vault, modifying the repository, starting a hosted service, or
mistaking a generic graph for proof of impact.

## User outcome

The first-run path answers what changed, which intent and test paths are supported, what evidence
is stale or ambiguous, which candidates were selected or omitted, and what the safe next action is.
The graph is available for bounded evidence navigation after the report establishes that context.

## Acceptance

- Phase 11B has a final passing Review before Phase 12 implementation begins.
- A deterministic read-only diagnostic reports repository/config readiness, supported and
  experimental language capabilities, detected project/source-root ambiguity, evidence freshness,
  graph/report availability, and the next safe command in text and JSON.
- Diagnostic and zero-footprint change-report paths do not create or modify configuration, cache,
  graph, vault, generated notes, Git state, or project files.
- The real-repository quick start promotes the existing aligned change-report pipeline before
  `init`, `scan`, or generic graph exploration.
- Every recommendation surface shows exact revision/scope, analysis state, freshness, threshold,
  score/confidence, selected and total candidate counts, evidence types, bounded paths, fallback
  strategy, and advisory wording.
- Selected, filtered, and omitted candidates are distinguishable. Omission means only that the
  available evidence did not meet the shown threshold; it never means unaffected or unnecessary.
- Terminal text, JSON, and the loopback viewer derive from the same report snapshot and preserve the
  same selection, ordering, reason, evidence, and fallback semantics.
- The viewer opens only through an explicit user action, remains loopback-only and Host-validated,
  escapes untrusted content, supports keyboard navigation, and renders bounded windows.
- The synthetic demo and real-repository preview are clearly separated; the demo does not imply
  that discovery, Git alignment, or user-authored intent was exercised.
- English and Turkish onboarding, an indexed documentation landing page, one original example, and
  one deterministic trust-first screenshot/report artifact follow the same command sequence.
- At least five independent first-run observations are recorded; median time from a trusted
  checkout to the first correctly interpreted explainable result is below ten minutes, with
  confusion and failed steps retained in Evidence.
- No telemetry, hosted account, model/API key, automatic user-note edits, or network requirement is
  added to the CLI.
- Focused/no-write/browser/accessibility/docs regressions and the complete local, package,
  deterministic-vault, approved network, remote-CI, Evidence, durable-chain, and Review gates pass.

## Typed links

- drives:: [[Decisions/ADR-028 - Make the change report the primary product surface]]

## Trace

- Strategy: [[Brain/Phase 11B-13 Delivery Strategy]]
- Roadmap: [[Brain/Product Roadmap]]
- Delivery issue: [[Issues/ISSUE-026 - Implement zero-footprint onboarding and trust-first reporting]]
- Planned evidence: [[Evidence/EVD-028 - Phase 12 trust-first onboarding verification]]
- Planned review: [[Reviews/Phase 12 Trust-First Onboarding Review]]
- Entry gate: [[Reviews/Phase 11B Longitudinal Pilot and Compatibility Review]]
