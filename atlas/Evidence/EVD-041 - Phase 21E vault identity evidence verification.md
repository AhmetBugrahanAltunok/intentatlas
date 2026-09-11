---
id: EVD-041
type: evidence
status: verified
phase: 21E
---
# Phase 21E vault identity evidence verification

Local decision: **verified, 2026-09-11**. Complete suite: **643 passed, 4 skipped**, exit **0**,
branch-enabled total coverage **87.72%**. Ruff, mypy (50 source files) and Bandit passed.

This closes the defect identified and deliberately deferred in EVD-037: change analysis emitted
`vault-frontmatter-id` for durable vault notes whose identity the scanner had derived from their
path because no `id:` frontmatter existed.

## Why the cheap fix was rejected

Inferring provenance from the `note:` ID prefix would have needed no schema change. It is wrong:
`RESERVED_USER_ID_PREFIXES` is `("commit:", "file:", "symbol:")`, so `note:` is not reserved and a
frontmatter `id:` may legitimately start with it. A regression now pins that case — a note
declaring `id: note:chosen-by-the-author` is recorded as `frontmatter` provenance, which the prefix
heuristic would have misclassified.

Provenance is therefore recorded where it is known, in the scanner, rather than reconstructed
downstream.

## Acceptance and verification

| Acceptance | Evidence | Result |
| --- | --- | --- |
| Identity provenance is recorded on user vault nodes | `metadata["identity"]` is `frontmatter` or `path`; scanner regression asserts both | passed |
| A declared identity yields the frontmatter label only | Actual Git-to-analysis case on `REQ-900`: `vault-frontmatter-id` present, `vault-path-identity` absent | passed |
| A derived identity yields the path label only | Actual case on `Brain/Loose note.md`: `vault-path-identity` present, `vault-frontmatter-id` absent, artifact ID still `note:Brain/Loose note` | passed |
| Missing provenance resolves to the weaker claim | `all(... == FRONTMATTER_IDENTITY)` over matched nodes; absence yields `vault-path-identity` by construction | passed |
| Analysis conclusions unchanged | Both cases remain `analyzed / aligned / high` carrying `durable-intent-artifact` | passed |
| Provenance is not inferred from the ID text | Regression for a declared `note:`-prefixed identity | passed |
| The narrowed label is documented | `docs/compatibility-policy.md` records it as a narrowed label with the migration note | passed |
| Quality gates and deterministic scans | 643 passed / 4 skips, 87.72%; Ruff, mypy, Bandit; two scans identical, 0 durable orphans | passed |

## Effect on this repository

None, and that is worth stating. All 233 user-owned notes in this vault declare frontmatter
identities, so every one was already labelled correctly and the live report still reads
`change-set-schema-1, fresh-worktree-scan, vault-frontmatter-id, durable-intent-artifact` for
REQ-041. The defect only ever surfaced in a vault containing notes without frontmatter — that is,
in someone else's project rather than in the one that shipped the bug. The regressions construct
that condition explicitly because this repository cannot reproduce it.

## Change inventory

- `src/intentatlas/scanner.py`: `FRONTMATTER_IDENTITY` and `PATH_IDENTITY` constants; user vault
  nodes carry `metadata["identity"]`.
- `src/intentatlas/change_analysis.py`: `_vault_artifact` selects the evidence label from recorded
  provenance across all matched durable nodes and abstains to the weaker label when absent.
- `tests/test_scanner.py`: two regressions for recorded provenance, including a declared
  `note:`-prefixed identity.
- `tests/test_change_analysis.py`: both vault cases now assert the exact label and the absence of
  the other.
- `docs/compatibility-policy.md`, `CHANGELOG.md`: record the narrowed label and the additive
  metadata field.
- REQ-041 / ADR-040 / this evidence / Phase 21E Review: the durable chain.

## Limitations

- The label is now accurate about where an identity came from. It still says nothing about whether
  the declared identity is meaningful, unique across projects, or intended by the author.
- No behavioural conclusion changed, so no existing analysis result is invalidated or improved by
  this phase; only its description is now truthful.

## Links

- proves:: [[Requirements/REQ-041 - Describe vault identity evidence accurately]]
- follows:: [[Decisions/ADR-040 - Record vault note identity provenance]]
- reviewed-in:: [[Reviews/Phase 21E Vault Identity Evidence Review]]
- corrects:: [[Evidence/EVD-037 - Phase 21A verification integrity verification]]
