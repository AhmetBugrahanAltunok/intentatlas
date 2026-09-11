---
id: review-phase-21b-reproducible-candidate
type: review
status: passed
phase: 21B
---
# Phase 21B Reproducible Candidate Review

Decision: **passed, 2026-09-11**. Recorded first as a conditional pass at `0.3.0rc1`; every
condition has since been discharged and the whole chain was re-verified at `0.3.0b1`.

The sequence matters, so it is recorded rather than flattened. Offline gates passed first. Network
approval then closed the pipx lifecycle and the dependency audit and retired the recorded
`--no-isolation` deviation. A beta version change arrived from the remote, invalidating the `rc1`
digests, so the chain was re-run at merged revision `ac2f2402` rather than carried forward. Push
approval then produced the remote matrix result, closing the last open item. ISSUE-038 is closed;
Phase 21 itself stays open on its remaining items.

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

- The supported matrix is now substantiated rather than claimed: run
  [34635166633](https://github.com/AhmetBugrahanAltunok/intentatlas/actions/runs/34635166633)
  at `a6e60d1` passed 13 of 13 jobs, including all six `cross-platform-e2e` combinations and
  `reproducible-package`. That is the first remote evidence that the Phase 21A package-identity
  gate behaves on Linux and macOS, not only on the Windows host it was written on. It describes
  `a6e60d1` and no later revision.
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
