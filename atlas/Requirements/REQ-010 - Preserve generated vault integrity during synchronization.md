---
id: REQ-010
type: requirement
status: accepted
phase: 6B2A
---
# Preserve generated vault integrity during synchronization

When generated Obsidian notes are refreshed, a transient or persistent filesystem lock must not
leave the previously complete generated vault partially deleted. Unchanged generated files should
not be rewritten, and user-owned notes must remain untouched.

## Acceptance

- All desired generated content is rendered before existing generated output is mutated.
- A changed generated note is replaced atomically through a same-directory temporary file.
- Transient sharing and permission failures receive a small, bounded retry; persistent failures
  fail clearly without first deleting the existing target.
- Stale generated notes are removed only after every desired note is safely present.
- Byte-identical generated notes are left untouched.
- Temporary files are cleaned after both successful and failed replacement attempts.
- Manual notes without the IntentAtlas generated marker and all user-owned vault areas are
  preserved.
- Focused fault-injection tests and the complete test, lint, security, CLI, package,
  determinism, and user-interface gates pass before the phase is complete.

## Scope boundary

This phase provides failure-preserving per-file replacement, not a filesystem-wide transaction.
After a persistent error, some desired files may contain the new version and others the previous
version, but existing generated targets are not removed first and stale cleanup does not begin.

## Typed links

- drives:: [[Decisions/ADR-010 - Failure-preserving atomic vault synchronization]]

## Trace

- Roadmap: [[Brain/Product Roadmap]]
- Planned evidence: [[Evidence/EVD-010 - Phase 6B2A vault synchronization verification]]
