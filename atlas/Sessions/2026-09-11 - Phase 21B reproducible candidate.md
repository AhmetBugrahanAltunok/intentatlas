---
id: session-2026-09-11-phase-21b
type: session
status: active
---
# Phase 21B reproducible candidate

## Objective

Continue Phase 21 from the action recorded in
[[Sessions/2026-09-11 - Phase 21A verification integrity]]: produce two artifact pairs under one
fixed `SOURCE_DATE_EPOCH`, run the release verifier, and bind artifact identity to a source
revision. Phase 21A had removed the import-identity ambiguity that would otherwise make a clean
candidate install unverifiable.

## Current state

**Phase 21B holds a conditional pass. Phase 21 remains open.** Everything that can run offline
passed for the candidate at `ecbcc8ca0c112336ba8a11b3ac06e46c1610b160`. Three gates need network
approval and are tracked in [[Issues/ISSUE-038 - Close the network-gated release checks]].

Verified artifacts:

```text
intentatlas-0.3.0rc1-py3-none-any.whl  sha256 54d38e11...  206630 bytes
intentatlas-0.3.0rc1.tar.gz            sha256 d028f36b...  3206657 bytes
epoch 1789136856   generator hatchling 1.31.0   wheel members 56   sdist members 203
```

Results: repeated builds byte-identical; `verify_release.py` exit 0 with 13 checks and provenance
written; sdist rebuild reproduced the direct wheel byte-for-byte with the cache disabled; clean
venv install matched the source version and returned a schema-1 demo report; the extracted archive
ran 607 passed / 11 skipped, exit 0; `pip check` clean.

Artifacts are under the ignored `var/release-21b/` tree. They are not tracked, not uploaded, and
carry no release approval.

## Open gates and one recorded deviation

- pipx lifecycle, platform matrix, and `pip_audit` all need network approval — ISSUE-038.
- The build used `--no-isolation` to stay offline. That is sound only because the installed
  backend is exactly the pinned `hatchling==1.31.0`, and it is recorded as a deviation from the
  documented isolated command rather than presented as equivalent. The next networked run should
  use the documented form and confirm the same digests.

## Next action

Two paths, and the owner's decision selects which:

1. **With network approval** — run the three ISSUE-038 checks against this revision, then move to
   the remaining Phase 21 items.
2. **Without it** — continue with the offline Phase 21 work: the clean-environment first-run
   walkthrough as a user would actually perform it (`diagnose`, change report, viewer, not just
   `--version` and the demo), verifying a first repository report without writing user notes or
   configuration, and reconciling the EN/TR installation and post-failure instructions.

Two Phase 21 items remain owner decisions rather than implementation work: the ADR-034
generated-vault governance choice before contributor intake, and whether to split the 675-line
README so the first-run path matches the Phase 22 ten-minute target.

No push, publication, upload, or human pilot result is claimed.

## Links

- [[Requirements/REQ-038 - Produce a reproducible independently installable candidate]]
- [[Issues/ISSUE-038 - Close the network-gated release checks]]
- [[Evidence/EVD-038 - Phase 21B reproducible candidate verification]]
- [[Reviews/Phase 21B Reproducible Candidate Review]]
- [[Sessions/2026-09-11 - Phase 21A verification integrity]]
- [[Brain/Alpha Release Execution Plan]]
