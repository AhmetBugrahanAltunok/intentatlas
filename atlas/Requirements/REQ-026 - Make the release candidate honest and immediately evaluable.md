---
id: REQ-026
type: requirement
status: accepted
phase: 11A
---
# Make the release candidate honest and immediately evaluable

A developer can verify the exact IntentAtlas release candidate and run one original, offline demo
that shows both a supported recommendation and an unpromoted same-file candidate through
interactive and deterministic machine-readable views.

## Acceptance

- The package has one canonical version source and identifies itself as `0.3.0rc1` consistently in
  runtime output, wheel metadata, source archive naming, provenance, and documentation.
- The original demo contains two requirements, two symbols, and two tests associated with the same
  source file; the example commit modifies only one symbol.
- Production recommendation logic selects the directly evidenced test and does not select the
  unrelated same-file test at the default confidence threshold.
- Text and schema-versioned JSON demo reports are deterministic, bounded, timestamp-free, exit
  without starting a listener, and state that omission is not proof of no impact or no test need.
- The default `intentatlas demo` experience remains the loopback production viewer and exposes the
  same graph and recommendation story.
- English, Turkish, guided-demo, changelog, and release documentation describe exact source
  installation, candidate status, the same-file scenario, and the publication boundary clearly.
- Focused and complete tests, coverage, lint, typing, security, package reproducibility, exact-wheel
  installation, CLI/UI, browser, provenance, deterministic vault, remote CI, Evidence, and Review
  gates pass before Phase 11A closes.

## Typed links

- drives:: [[Decisions/ADR-026 - Separate scriptable demo evidence from interactive viewing and publication]]

## Trace

- Strategy: [[Brain/Phase 11 Strategy]]
- Roadmap: [[Brain/Product Roadmap]]
- Delivery: [[Issues/ISSUE-024 - Implement the honest 0.3.0 release candidate demo]]
- Planned evidence: [[Evidence/EVD-026 - Phase 11A release candidate and demo verification]]
