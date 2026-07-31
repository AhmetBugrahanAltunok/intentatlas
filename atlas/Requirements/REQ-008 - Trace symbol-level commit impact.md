---
id: REQ-008
type: requirement
status: accepted
phase: 6A
---
# Trace symbol-level commit impact

A developer can distinguish which supported source symbol a commit changed without losing the
existing conservative file-level history when the exact symbol cannot be established.

## Acceptance

- Python AST symbols expose deterministic inclusive start and end lines.
- The Git adapter reads bounded zero-context diff hunks with fixed read-only commands and never
  executes repository code.
- A hunk is eligible only when the current worktree file matches that commit's bounded raw Git
  blob after line-ending normalization, preventing stale historical line projection.
- Blob comparison candidates are limited to scanned paths with trusted source spans and a bounded
  commit/path budget; excluded paths are never opened for symbol analysis.
- A commit creates a typed `modifies` relationship only to the most-specific current symbol whose
  validated source span intersects changed new-side lines.
- Existing commit-to-file `changes` relationships remain available as the safe fallback.
- Pure deletions, module-level edits, malformed or oversized diff output, missing spans, and
  unsupported languages do not create guessed symbol relationships.
- A fixture with two functions in one file proves that changing one function does not mark the
  sibling function as directly modified.
- Cache migration, CLI traversal, Obsidian output, and the local viewer expose the new typed
  relationship deterministically.
- Focused regression tests and the complete test, lint, security, CLI, viewer, package, and
  determinism gates pass before the phase is complete.

## Scope boundary

This phase creates precise structural evidence. Confidence scoring, requirement-impact ranking,
per-test execution traces, and automatic test selection remain Phase 6B work.

## Typed links

- drives:: [[Decisions/ADR-008 - Conservative diff-to-symbol projection]]

## Trace

- Roadmap: [[Brain/Product Roadmap]]
- Planned evidence: [[Evidence/EVD-008 - Phase 6A symbol impact verification]]
