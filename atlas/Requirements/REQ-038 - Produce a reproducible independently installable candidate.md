---
id: REQ-038
type: requirement
status: accepted
phase: 21B
---
# Produce a reproducible independently installable candidate

## User outcome

A maintainer can rebuild the exact candidate artifacts from a recorded source revision, confirm
they are byte-identical, and install them into a clean environment that produces a useful result
without the development checkout present.

## Acceptance

- Two consecutive builds from one fixed `SOURCE_DATE_EPOCH` produce byte-identical wheel and
  source archives.
- `tools/verify_release.py` passes every archive, metadata, manifest, payload, and licence check
  and writes a deterministic provenance record bound to the exact 40-character source revision.
- Rebuilding the verified source archive under the same epoch reproduces the direct wheel
  byte-for-byte, with the build cache disabled so the comparison is an actual rebuild.
- A clean virtual environment installs the archive-derived wheel with no dependencies, reports the
  same version as the source module, and returns a schema-1 demo report.
- The extracted source archive runs its own test suite against its own `src` tree.
- Any gate that cannot run offline is recorded as unverified rather than assumed.

## Links

- proved-by:: [[Evidence/EVD-038 - Phase 21B reproducible candidate verification]]
- reviewed-by:: [[Reviews/Phase 21B Reproducible Candidate Review]]
- delivered-by:: [[Issues/ISSUE-038 - Close the network-gated release checks]]
- extends:: [[Requirements/REQ-037 - Prove which package and boundaries verification covers]]
- planned-in:: [[Brain/Alpha Release Execution Plan]]
