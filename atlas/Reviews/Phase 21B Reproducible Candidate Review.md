---
id: review-phase-21b-reproducible-candidate
type: review
status: conditional
phase: 21B
---
# Phase 21B Reproducible Candidate Review

Decision: **conditional pass, 2026-09-11**, with the condition substantially narrowed the same
day. Every offline gate passed for the candidate built from
`ecbcc8ca0c112336ba8a11b3ac06e46c1610b160`. The owner then granted network approval, which closed
the pipx lifecycle and the dependency audit and retired the recorded build deviation. One
condition remains: the supported platform matrix, which needs a push that has not been approved.
ISSUE-038 stays open on that single item; Phase 21 stays open.

## What this sub-phase establishes

The candidate is reproducible and independently installable. Two builds under one fixed epoch were
byte-identical, the full release verifier passed all thirteen recorded checks and wrote provenance
bound to the exact revision, the source archive rebuilt the direct wheel byte-for-byte with the
cache disabled, a clean environment installed the archive-derived wheel and produced a schema-1
demo report without the development checkout, and the extracted archive ran its own suite green.

No source, test, or documentation file changed in this sub-phase. It is verification only, so the
Phase 21A result carries forward unchanged.

After network approval, three more gates closed: the isolated pipx install, reinstall and
uninstall lifecycle passed against the verified wheel; `pip_audit --skip-editable` found no known
vulnerabilities across the whole environment; and two runs of the documented isolated
`python -m build` reproduced the offline digests exactly, which retires the deviation recorded
earlier rather than leaving it as an argument.

A side result worth keeping: the same digests hold at `ecbcc8ca` and `06701d3`, revisions that
differ only under `atlas/`. Because the source archive excludes the vault, vault-only commits are
demonstrably unable to change the candidate bytes.

## What it does not establish

- Nothing about other operating systems or Python versions. One platform and one interpreter were
  exercised. The declared support matrix is a claim only the remote CI run can substantiate, and
  that run needs a push.
- Nothing about release approval. The artifacts live under the ignored `var/` tree. No upload,
  publication, tag, or push occurred, and the version remains an unpublished candidate.
- Nothing about real first-run usability. Installing a wheel and reading `--version` is not the
  same as a person getting a useful report; that is the remaining Phase 21 work and Phase 22.

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
