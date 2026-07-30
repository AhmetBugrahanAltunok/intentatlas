---
id: phase-completion-protocol
type: memory
status: active
---
# Phase Completion Protocol

This protocol prevents IntentAtlas from progressing on unverified assumptions. It applies to
every phase in [[Brain/Product Roadmap]].

## Required completion record

1. List every meaningful behavior, architecture, configuration, vault, and documentation change.
2. Trace each change back to its requirement and any applicable ADR.
3. Run focused regression tests for changed behavior.
4. Run the complete test, lint, and security suite.
5. Exercise affected CLI and graphical workflows end to end.
6. Confirm generated output is deterministic and user-owned notes remain untouched.
7. Record exact commands, results, limitations, and remaining risks in `Evidence/`.
8. Record a final pass, conditional pass, or fail decision in `Reviews/`.

Networked checks require explicit approval. If they cannot run, the Evidence note must identify
the unverified check instead of treating it as passed.

## Stop conditions

A phase stays open when any acceptance criterion is unmet, a regression is unexplained, a trust
boundary is uncertain, or implementation and documentation disagree. The next phase does not
start until the mismatch is corrected or explicitly re-scoped by the project owner.
