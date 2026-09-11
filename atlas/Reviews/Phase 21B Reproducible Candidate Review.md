---
id: review-phase-21b-reproducible-candidate
type: review
status: conditional
phase: 21B
---
# Phase 21B Reproducible Candidate Review

Decision: **conditional pass, 2026-09-11**. Every gate that can run without network passed for the
candidate built from `ecbcc8ca0c112336ba8a11b3ac06e46c1610b160`. Three gates need network approval
and are recorded as unverified in EVD-038. The condition is ISSUE-038; Phase 21 stays open.

## What this sub-phase establishes

The candidate is reproducible and independently installable. Two builds under one fixed epoch were
byte-identical, the full release verifier passed all thirteen recorded checks and wrote provenance
bound to the exact revision, the source archive rebuilt the direct wheel byte-for-byte with the
cache disabled, a clean environment installed the archive-derived wheel and produced a schema-1
demo report without the development checkout, and the extracted archive ran its own suite green.

No source, test, or documentation file changed in this sub-phase. It is verification only, so the
Phase 21A result carries forward unchanged.

## What it does not establish

- Nothing about other operating systems or Python versions. One platform and one interpreter were
  exercised. The declared support matrix is a claim the remote CI run has to substantiate.
- Nothing about third-party dependency vulnerabilities.
- Nothing about the pipx installation path a real user might take. The offline attempt failed in
  pipx's own bootstrap before reaching the candidate, which is informative about the environment
  and says nothing either way about the wheel.
- Nothing about release approval. The artifacts live under the ignored `var/` tree. No upload,
  publication, tag, or push occurred, and the version remains an unpublished candidate.

## Recorded deviation

The documented procedure uses isolated `python -m build`. This run used `--no-isolation` to stay
offline. That is sound only because the installed backend is exactly the pinned
`hatchling==1.31.0` that isolation would have fetched, and the provenance record confirms the
generator. It is still a deviation from the documented command and is recorded as one rather than
presented as equivalent. The next networked run should use the documented isolated form and
confirm the same digests.

## Remaining Phase 21 gates

Untouched by this sub-phase: the EN/TR first-run instruction reconciliation, the
clean-environment first-run walkthrough as a user would perform it, the Phase 18/19/20 release
inventory reconciliation, and the ADR-034 generated-vault governance decision before contributor
intake.

## Links

- reviews:: [[Requirements/REQ-038 - Produce a reproducible independently installable candidate]]
- reviews:: [[Issues/ISSUE-038 - Close the network-gated release checks]]
- based-on:: [[Evidence/EVD-038 - Phase 21B reproducible candidate verification]]
- follows:: [[Reviews/Phase 21A Verification Integrity Review]]
- governed-by:: [[Brain/Phase Completion Protocol]]
