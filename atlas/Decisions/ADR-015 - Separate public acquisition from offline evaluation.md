---
id: ADR-015
type: decision
status: accepted
phase: 6B2B2B2B
---
# ADR-015 — Separate public acquisition from offline evaluation

## Context

Synthetic fixtures protect deterministic scoring behavior but cannot show that discovery, language
adapters, Git history, test classification, and recommendations compose on real repositories.
Bundling public repositories would add source, history, license, branding, size, freshness, and Git
noise to the product. Making the product command clone or execute those projects would also weaken
the offline and untrusted-input boundaries.

## Decision

Keep acquisition explicit and outside the evaluator. Store only a strict provenance manifest and
manually reviewed label files. Require local checkout directories named by manifest project ID and
verify their canonical origin, exact HEAD, clean state, reviewed license path, and SHA-256 before
scanning.

Run `scan_repository` in memory with a newly constructed default `ProjectConfig`, never a
checkout-owned configuration. Reuse the unchanged production `evaluate_corpus` path at all three
confidence thresholds. Persist no graph, vault, raw diff, commit subject, or source-derived output.
Keep checkouts and optional redirected reports below the already ignored `.intentatlas/` area.

## Consequences

- Public validation is reproducible without shipping third-party code or changing the MIT license
  boundary.
- The product command remains offline and never executes project dependencies, tests, or hooks.
- License and source drift fail closed through full commit and license-byte verification.
- Contributors must perform a separately approved clone step before evaluation.
- Nine small cases expose threshold behavior but cannot establish broad accuracy or false-positive
  rates across diverse repositories.

## Links

- Requirement: REQ-015 (available through the incoming `drives` relationship)
- tracked-by:: [[Issues/ISSUE-013 - Implement license-reviewed real-world validation]]
