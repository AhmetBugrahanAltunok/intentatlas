---
id: review-phase-21e-vault-identity-evidence
type: review
status: passed
phase: 21E
---
# Phase 21E Vault Identity Evidence Review

Decision: **passed, 2026-09-11**. 643 passed, 4 platform skips, exit 0, 87.72% branch-enabled total
coverage. Ruff, mypy and Bandit passed. Two scans stayed deterministic with 0 durable orphans.

## What this corrects

Phase 21A found that `vault-frontmatter-id` was emitted for durable vault notes whose identity the
scanner had derived from their path, and deferred the fix because correcting a published label is
not a silent change. This phase makes the label mean what it says.

The correction is small in code and specific in kind: it removes an overclaim. Nothing about any
analysis conclusion changed — the same files remain `analyzed / aligned / high` with the same
artifact identities and the same `durable-intent-artifact` label. Only the description of the
evidence is now true.

That distinction matters for a product whose entire proposition is that it does not overstate what
it knows. An evidence label that describes an identity the author never declared is a defect in the
thing being sold, not a cosmetic one.

## The rejected shortcut

Inferring provenance from the `note:` ID prefix would have avoided touching the scanner. It is
wrong, because `note:` is not in `RESERVED_USER_ID_PREFIXES` and a frontmatter `id:` may
legitimately use it. A regression now pins exactly that case. Provenance is recorded where it is
known instead of reconstructed downstream, and a graph without it resolves to the weaker claim
rather than the stronger one.

## Honest scope

This repository was never affected. All 233 of its user-owned notes declare frontmatter
identities, so every label here was already correct and the live report is unchanged. The defect
only appeared in vaults containing notes without frontmatter — other people's projects. The
regressions construct that condition deliberately, because the shipping project cannot reproduce
its own bug.

The narrowed label is recorded in the compatibility policy rather than shipped quietly. A consumer
detecting durable vault notes should key off `durable-intent-artifact`; one keying off
`vault-frontmatter-id` was relying on a signal that did not mean what it said.

## Limits

The label now describes where an identity came from. It still says nothing about whether that
identity is meaningful, unique across projects, or intended. No prior analysis result is
invalidated or improved by this phase.

## Links

- reviews:: [[Requirements/REQ-041 - Describe vault identity evidence accurately]]
- reviews:: [[Decisions/ADR-040 - Record vault note identity provenance]]
- based-on:: [[Evidence/EVD-041 - Phase 21E vault identity evidence verification]]
- follows:: [[Reviews/Phase 21D Fail-Closed Branch Review]]
- governed-by:: [[Brain/Phase Completion Protocol]]
