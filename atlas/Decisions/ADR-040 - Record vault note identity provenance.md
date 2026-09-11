---
id: ADR-040
type: decision
status: accepted
phase: 21E
---
# Record vault note identity provenance

## Context

A user-owned vault note gets its graph identity one of two ways. If its frontmatter declares
`id:`, the scanner validates and uses that value. If it does not, the scanner mints
`note:<vault-relative-path-without-.md>` so the note still has a stable identity.

Change analysis emitted the evidence label `vault-frontmatter-id` for both cases. For a note with
no frontmatter that label described an identity the author never declared. The product's whole
claim is that it does not overstate its evidence, so an evidence label that overstates is a defect
in the thing being sold, not a cosmetic issue. It was found in Phase 21A and recorded rather than
fixed, because correcting it changes a published label.

The obvious cheap fix — infer provenance from the `note:` prefix — is unreliable. `note:` is not
in `RESERVED_USER_ID_PREFIXES`, so a frontmatter `id:` may legitimately start with it. Provenance
has to be recorded where it is known rather than reconstructed downstream.

## Decision

The scanner records identity provenance on every user-owned vault node as
`metadata["identity"]`, valued `frontmatter` or `path`.

Change analysis emits `vault-frontmatter-id` only when every durable node matched for that file
declares `frontmatter` provenance, and `vault-path-identity` otherwise. A graph carrying no
`identity` metadata — an older cache, or any node the scanner did not produce — resolves to
`vault-path-identity`, the weaker claim, rather than the stronger one.

`durable-intent-artifact` continues to accompany both. It is the label that answers "is this a
durable vault note", and it is unchanged, so a consumer asking that question needs no update.

State, freshness, confidence, and artifact identity are unchanged in both cases. The correction is
to the description of the evidence, not to what the analysis concluded.

## Consequences

- `vault-frontmatter-id` now means what it says. It appears strictly less often than before.
- A consumer that keyed off `vault-frontmatter-id` to detect durable vault notes was already
  relying on an imprecise signal and should key off `durable-intent-artifact` instead. This is
  recorded in the compatibility policy as a narrowed label rather than shipped silently.
- `metadata["identity"]` is an additive field under the existing schema boundary and needs no
  stored-data migration. Absence resolves to the conservative value by construction.
- Reconstructing provenance from an ID prefix stays rejected; if `note:` is ever reserved, that is
  a separate decision about user-authored IDs, not a way to reintroduce the inference.

## Links

- implements:: [[Requirements/REQ-041 - Describe vault identity evidence accurately]]
- refines:: [[Decisions/ADR-037 - Bound trust claims and abstain on uncertain structure]]
- recorded-in:: [[Evidence/EVD-041 - Phase 21E vault identity evidence verification]]
