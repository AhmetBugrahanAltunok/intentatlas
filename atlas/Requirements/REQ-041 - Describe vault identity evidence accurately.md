---
id: REQ-041
type: requirement
status: accepted
phase: 21E
---
# Describe vault identity evidence accurately

## User outcome

When a change report says a vault note's identity came from its frontmatter, it did. A maintainer
reading the evidence for a durable intent artifact can tell whether the author declared that
identity or whether IntentAtlas derived it from the file's location.

## Acceptance

- A user-owned vault node records where its identity came from, as `frontmatter` or `path`.
- A note with a declared `id:` yields `vault-frontmatter-id` and never `vault-path-identity`.
- A note without frontmatter yields `vault-path-identity` and never `vault-frontmatter-id`,
  while still resolving to its stable path-derived artifact identity.
- A graph carrying no identity provenance resolves to the weaker claim, not the stronger one.
- `durable-intent-artifact`, state, freshness, confidence, and artifact identity are unchanged in
  every case; only the description of the evidence changes.
- Provenance is never reconstructed from an ID prefix, because `note:` is not a reserved
  user-identity prefix and a declared identity may legitimately use it.
- The narrowed label is recorded in the compatibility policy rather than shipped silently.
- The full suite, Ruff, mypy, and Bandit pass, and two scans stay deterministic.

## Links

- drives:: [[Decisions/ADR-040 - Record vault note identity provenance]]
- proved-by:: [[Evidence/EVD-041 - Phase 21E vault identity evidence verification]]
- reviewed-by:: [[Reviews/Phase 21E Vault Identity Evidence Review]]
- extends:: [[Requirements/REQ-040 - Prove the fail-closed branches rather than assert them]]
