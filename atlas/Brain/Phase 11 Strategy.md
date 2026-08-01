---
id: phase-11-strategy
type: memory
status: active
---
# Phase 11 Strategy

Phase 10 completed the scale, open-evidence, browser, typing, and release-provenance foundation.
Phase 11 turns that capability into an honest, easy-to-evaluate release candidate without weakening
the local-first product contract or implying that impact analysis is perfect.

## Product target

A developer should be able to install one reviewed candidate, confirm its exact version, run one
offline command, and see both the useful recommendation and the deliberately excluded same-file
false positive. Interactive exploration and machine-readable evidence should tell the same story.

## Phase 11A — Honest release candidate and evaluable demo

1. Use one canonical package-version source and prepare `0.3.0rc1` without tagging or publishing.
2. Extend the original demo with two requirements, symbols, and tests sharing one source file.
3. Modify only one symbol and prove the unrelated same-file test is not recommended from the
   available evidence.
4. Add deterministic text and JSON demo reports that exit without starting a server; keep the
   current interactive viewer as the default experience.
5. Verify the exact built wheel, version, report, browser, provenance, and complete quality gates.

Delivery is governed by [[Requirements/REQ-026 - Make the release candidate honest and immediately evaluable]],
[[Decisions/ADR-026 - Separate scriptable demo evidence from interactive viewing and publication]],
and [[Issues/ISSUE-024 - Implement the honest 0.3.0 release candidate demo]].

## Phase 11B — Sustained pilot evidence and compatibility policy

Planned only after Phase 11A passes. Expand independently reviewed pilot histories, document graph
and adapter compatibility guarantees, and publish measured limitations. Do not tune against hidden
holdouts or turn advisory recommendations into blocking policy without evidence.

## Phase 11C — Public launch and feedback loop

Planned only after separate owner approval. Prepare public repository/release presentation,
contributor issue templates, signed or hosted attestations if justified, and a feedback loop that
does not add telemetry to the local CLI. Repository visibility, tags, releases, and package-index
publication are external actions and are not authorized by this strategy.

## Non-goals

- No claim that an omitted requirement or test is unaffected or unnecessary.
- No copied third-party demo, branding, source, vault, or repository history.
- No network requirement, telemetry, hosted account, model API, tag, release, or publication.
- No `1.0` compatibility promise before sustained pilot and extension-contract evidence exists.
