---
id: REQ-002
type: requirement
status: accepted
phase: 1
---
# Harden trust boundaries

IntentAtlas must be safe to run on an untrusted repository while preserving the user's private
and durable vault material.

## Acceptance

- Discovery prunes configured excluded directories before descending into them.
- `atlas/Private/` is never created, read, enumerated, indexed, or modified; users provision that
  local-only boundary themselves when they need it.
- Tests prove non-access to private and excluded directories, not only absence from the graph.
- User note IDs cannot silently replace or merge with scanner-owned graph nodes.
- Untrusted labels and metadata cannot alter the structure of generated Markdown notes.
- The local graph viewer supports both pointer and keyboard node selection.
- Focused regressions and the full phase completion suite pass and are recorded as evidence.

## Links

- Roadmap: [[Brain/Product Roadmap]]
- Protocol: [[Brain/Phase Completion Protocol]]
- Decision: [[Decisions/ADR-002 - Pruned trust-boundary traversal]]
- Evidence: [[Evidence/EVD-002 - Phase 1 foundation verification]]
- Review: [[Reviews/Phase 1 Foundation Review]]
- Prior requirement: [[Requirements/REQ-001 - Explain change impact]]
