---
id: session-2026-09-11-beta-merge
type: session
status: active
---
# Beta merge and re-verification

## Objective

The owner approved pushing the local Phase 21A-21E work. Before pushing, the remote turned out to
have diverged.

## What was found

`origin/main` held four commits from 2026-09-07 that were not local. One of them changed the
version from `0.3.0rc1` to `0.3.0b1`; the others added a beta badge, a Dependabot policy, and a
Windows long-path note. Every local commit was built on `0.3.0rc1`.

The mechanical merge was clean — `git merge-tree` reported no conflicts, and the three
both-sides files (`CHANGELOG.md`, `README.md`, `tests/test_e2e.py`) merged without intervention.
The real problem was evidential: the Phase 21B artifact digests describe `0.3.0rc1`, a version the
repository would no longer build. Pushing that record unchanged would have presented green
evidence from an older source as current, which the execution plan's risk table names explicitly.

## Merge, not rebase

The history was strictly linear, so rebase would normally be the natural choice. It was rejected
here because the durable notes cite exact commit SHAs as evidence — `f0e6719` in EVD-037,
`ecbcc8ca` and `06701d3` in EVD-038, `041069a` in the inventory. A rebase rewrites all of them and
leaves recorded evidence pointing at commits that no longer exist. In this project a commit SHA is
durable evidence, and that outranks the shape of the history.

## Re-verification at 0.3.0b1

The whole chain was re-run at merged revision `ac2f24025d3cd3d5801a7b3c0f829e103c56afa5`:

```text
full suite      678 passed, 4 skipped, exit 0, 88.08% branch-enabled coverage
gates           Ruff, mypy (50 files), Bandit, pip check — all passed
builds          two isolated python -m build runs, byte-identical
verifier        verify_release.py exit 0, 13 checks, provenance bound to ac2f2402
sdist rebuild   reproduces the direct wheel byte-for-byte, cache disabled
clean install   IntentAtlas 0.3.0b1
pipx lifecycle  install, reinstall, uninstall verified
pip_audit       no known vulnerabilities

intentatlas-0.3.0b1-py3-none-any.whl  f74a2700f461b942…  207397
intentatlas-0.3.0b1.tar.gz            1e77138732bc0b2d…  3215661
```

The documented isolated build command was used throughout, so the earlier `--no-isolation`
deviation does not apply to these artifacts at all. The `rc1` digests are retained in EVD-038 as
superseded history rather than deleted.

## Current state

Phase 21 checklist: six of nine closed. Remaining are the supported platform matrix, the ADR-034
governance decision, and the final release-candidate inventory record. ISSUE-039 carries four open
owner decisions: English README length, Turkish README scope, ADR-034 governance, and the durable
relation vocabulary.

## Push and the remote matrix

Pushed `ee5ff92..a6e60d1`, 13 commits. CI run
[34635166633](https://github.com/AhmetBugrahanAltunok/intentatlas/actions/runs/34635166633)
succeeded on **13 of 13 jobs** at `a6e60d1`, closing ISSUE-038 and turning the Phase 21B review
from a conditional pass into a full pass.

The matrix confirmed something local work could not: the Phase 21A package-identity gate, written
and exercised only on Windows, behaves on Linux and macOS across Python 3.11 and 3.13, and the
`reproducible-package` job corroborated the local build chain on Ubuntu.

## Next action

Phase 21 now has no remaining technical work. What is left is the owner's: the four decisions in
ISSUE-039 — English README length, Turkish README scope, ADR-034 generated-vault governance, and
the durable relation vocabulary — then the final release-candidate inventory record that closes
the phase. Phase 22 needs five independent people and nothing technical substitutes for it.

No package upload is authorised and none has occurred. Pushing source is not publishing a
distribution.

## Links

- [[Evidence/EVD-038 - Phase 21B reproducible candidate verification]]
- [[Brain/Release Candidate Inventory]]
- [[Issues/ISSUE-038 - Close the network-gated release checks]]
- [[Issues/ISSUE-039 - Resolve the documentation divergence decisions]]
- [[Sessions/2026-09-11 - Phase 21C first-run walkthrough]]
- [[Brain/Alpha Release Execution Plan]]
