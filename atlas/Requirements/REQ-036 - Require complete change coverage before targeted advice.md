---
id: REQ-036
type: requirement
status: accepted
phase: 20
---
# Require complete change coverage before targeted advice

## User outcome

A maintainer sees targeted-only advice only when every retained change range has trustworthy
current-side symbol coverage. Unmapped lines and deletion-only ranges retain uncertainty.

## Acceptance

- A partially overlapping hunk, including a gap between symbols, cannot be complete.
- A hunk touching both a parent body and a nested symbol preserves both changed owners;
  a child-only change does not spuriously mark its parent.
- Ownership depends on interval boundaries, not iteration over every source line; output is
  deterministic for reordered symbols and split/merged equivalent hunks.
- Deletion-only ranges in surviving files remain represented as zero-count hunks, including
  start zero. They never become exact current-side symbol evidence.
- A mixed modification/deletion file uses fallback and a full-suite strategy, while retaining
  independently justified positive-range symbol history. Whole-file deletion remains unknown.
- Actual local Git to CLI text/JSON reports exercise partial, mixed-deletion, nested, and
  child-only cases. Existing precise cases retain their behavior.
- A real browser displays the complete-snapshot evidence path after a single selection;
  delayed responses are awaited without repeatedly resetting the selection or weakening assertions.
- Focused tests, full branch-coverage suite (minimum 80%), Ruff, mypy, Bandit, and diff checks pass.
- Durable roadmap links resolve; generated scans are deterministic and preserve user-owned notes.

## Links

- drives:: [[Decisions/ADR-038 - Preserve uncovered change ranges and deletion uncertainty]]
- tracked-by:: [[Issues/ISSUE-036 - Close partial hunk deletion and browser regressions]]
- proven-by:: [[Evidence/EVD-036 - Phase 20 change coverage verification]]
- reviewed-by:: [[Reviews/Phase 20 Change Coverage Review]]
- extends:: [[Requirements/REQ-035 - Close audited trust and cross-language analysis gaps]]
- planned-in:: [[Brain/Alpha Release Execution Plan]]
