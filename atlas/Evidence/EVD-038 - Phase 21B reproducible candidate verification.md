---
id: EVD-038
type: evidence
status: verified
phase: 21B
---
# Phase 21B reproducible candidate verification

Local decision: **verified, 2026-09-11**, at version `0.3.0b1` and revision
`ac2f24025d3cd3d5801a7b3c0f829e103c56afa5`.

This note was first written against `0.3.0rc1`. The remote then supplied a beta version change,
and the entire chain was re-run rather than carried forward; the re-verification section at the end
is the authoritative result and the earlier `rc1` sections are retained as superseded history.

Toolchain: `hatchling 1.31.0`, `build 1.3.0` — both exactly the pinned `[release]` versions, so
the local build backend matches the one CI uses. The remote platform matrix remains the only
unverified gate.

## Verified artifacts — current, `0.3.0b1`

| Artifact | SHA-256 | Bytes |
| --- | --- | --- |
| `intentatlas-0.3.0b1-py3-none-any.whl` | `f74a2700f461b942bf1383e8f42b19c719fc6e3a1315f812dda04996387de5bc` | 207397 |
| `intentatlas-0.3.0b1.tar.gz` | `1e77138732bc0b2d39dda7edc3ae453c1c196b99b860129aad82f434c6e55853` | 3215661 |

Source revision `ac2f24025d3cd3d5801a7b3c0f829e103c56afa5`, epoch `1789151641`, generator
`hatchling 1.31.0`, wheel members 56, source-archive members 203, 13 recorded checks, repeated
builds byte-identical. Provenance at `var/release-b1/release-provenance.json`, untracked.

## Superseded artifacts — `0.3.0rc1`

| Artifact | SHA-256 | Bytes |
| --- | --- | --- |
| `intentatlas-0.3.0rc1-py3-none-any.whl` | `54d38e1110979c3ac0a07a9eb59ce0711878151b81e1cb818c704194bef0db5c` | 206630 |
| `intentatlas-0.3.0rc1.tar.gz` | `d028f36bbe97a8dbbce2652e5bf708e2bb669eaec9447c8edbe5d2198bb0289c` | 3206657 |

These were verified at revisions `ecbcc8ca` and `06701d3` and remain valid descriptions of that
state. They are **not** evidence for the current source: the repository no longer builds
`0.3.0rc1`. See the re-verification section below.

## Acceptance and verification — as first recorded at `0.3.0rc1`

| Acceptance | Evidence | Result |
| --- | --- | --- |
| Repeated builds are byte-identical | Two `python -m build` runs under one epoch; verifier reports `repeated_builds_byte_identical: true` | passed |
| Full release verification and provenance | `tools/verify_release.py` exit 0 with 13 recorded checks bound to the exact revision and epoch | passed |
| Source archive rebuilds the direct wheel | `pip wheel --no-cache-dir` from the sdist; `cmp` identical and both digests `54d38e11…` | passed |
| Clean environment install | Fresh venv, `--no-deps --no-index`; `intentatlas --version` equals the source module version | passed |
| Useful result without the checkout | `intentatlas demo --report json` from that venv returned `schema_version 1` and the `rotate_session` changed symbol | passed |
| Extracted archive tests itself | 607 passed, 11 skipped, exit 0, run from the extracted tree with its own `src` on `PYTHONPATH` | passed |
| Environment consistency | `python -m pip check`: no broken requirements | passed |
| Isolated pipx lifecycle | `verify_pipx_install.py` exit 0 after network approval | passed |
| Dependency audit | `pip_audit --skip-editable`: no known vulnerabilities, exit 0 | passed |
| Documented isolated build reproduces the same bytes | Two isolated `python -m build` runs; digests identical to the offline pair | passed |
| Supported platform matrix | Not run; needs a push; see below | **unverified** |

## Commands — as first recorded at `0.3.0rc1`

```text
EPOCH=$(git show -s --format=%ct HEAD)        -> 1789136856
REV=$(git rev-parse HEAD)                     -> ecbcc8ca...
SOURCE_DATE_EPOCH=$EPOCH python -m build --no-isolation --sdist --wheel --outdir var/release-21b/a
SOURCE_DATE_EPOCH=$EPOCH python -m build --no-isolation --sdist --wheel --outdir var/release-21b/b
python tools/verify_release.py var/release-21b/a var/release-21b/b \
  --write-provenance var/release-21b/release-provenance.json \
  --source-revision $REV --source-date-epoch $EPOCH
SOURCE_DATE_EPOCH=$EPOCH python -m pip wheel --no-deps --no-build-isolation --no-index \
  --no-cache-dir var/release-21b/a/*.tar.gz --wheel-dir var/release-21b/sdist-wheel
cmp var/release-21b/a/*.whl var/release-21b/sdist-wheel/*.whl
python -m venv var/release-21b/sdist-install && install the archive-derived wheel
(extracted root) PYTHONPATH="$PWD/src" python -m pytest -q
```

`--no-isolation` was used deliberately so the offline run could stay offline. At the time it was
recorded as a deviation rather than an equivalent substitution, because the argument for it rested
on the installed backend being exactly the pinned `hatchling==1.31.0`. The networked section below
retires that caveat: the documented isolated command produced the same bytes.

One early comparison failed before the epoch was applied to the rebuild step: the direct and
archive-derived wheels differed at byte 11, the zip timestamp. The CI job sets the epoch at job
scope, which covers that step. The corrected run is the recorded result, and the cache was
disabled so the comparison could not be satisfied by a stored wheel.

## Networked verification — 2026-09-11

The owner granted network approval after the offline gates were recorded. Three things then ran.

- **Isolated pipx lifecycle.** `python tools/verify_pipx_install.py var/release-21b/a/*.whl` ->
  `Verified isolated pipx install, reinstall, and uninstall: IntentAtlas 0.3.0rc1`, exit 0. The
  earlier offline failure was pipx bootstrapping its own shared libraries, as suspected.
- **Dependency audit.** `python -m pip_audit --skip-editable` -> `No known vulnerabilities found`,
  exit 0, across the combined development, release, security, typing, and build environment. Only
  the editable candidate itself was skipped.
- **The recorded build deviation is closed.** Two isolated `python -m build` runs, the documented
  command, produced digests identical to the earlier `--no-isolation` pair:
  wheel `54d38e11...`, sdist `d028f36b...`. `verify_release.py` passed again and wrote provenance
  bound to `06701d36874e125ab5b0de5cc1ce08ca6fd01092`. The `--no-isolation` shortcut is therefore
  confirmed equivalent for this toolchain rather than merely argued to be.

Those digests also hold across two different source revisions, `ecbcc8ca` and `06701d3`, which
differ only in `atlas/`. The source archive excludes the vault, so vault-only commits provably do
not alter the candidate bytes.

## Still unverified

- **Supported platform matrix.** Verified on Windows 11 with one Python only. The declared matrix
  — Ubuntu, Windows and macOS across Python 3.11 and 3.13 — needs remote CI. The owner approved a
  push on 2026-09-11, so that run is expected to follow this record; until its result is bound to
  `ac2f2402`, the matrix claim stays open.

No package was uploaded or published. The artifacts exist only under the ignored `var/` tree and
carry no release approval; pushing source is not publishing a distribution.

## Re-verification after the beta version change — 2026-09-11

The remote `main` had diverged with four commits, one of which changed the version from
`0.3.0rc1` to `0.3.0b1` and added a beta badge. Merging them made every digest recorded above for
`rc1` describe a version the repository no longer produces. Reusing that evidence would have been
exactly the failure mode the execution plan's risk table names: green evidence from an older source
presented as current.

The whole chain was therefore re-run at the merged revision rather than carried forward:

| Check | Result at `0.3.0b1` |
| --- | --- |
| Full suite | 678 passed, 4 skipped, exit 0, 88.08% branch-enabled coverage |
| Ruff, mypy, Bandit, `pip check` | all passed |
| Repeated builds byte-identical | yes, both artifacts |
| `verify_release.py` with provenance | exit 0, 13 checks, bound to `ac2f2402` |
| Source archive rebuilds the direct wheel | identical, cache disabled |
| Clean environment install | `IntentAtlas 0.3.0b1` |
| Isolated pipx lifecycle | `Verified isolated pipx install, reinstall, and uninstall: IntentAtlas 0.3.0b1` |
| `pip_audit --skip-editable` | no known vulnerabilities |

The documented isolated `python -m build` was used throughout, so the earlier `--no-isolation`
deviation does not apply to these artifacts at all.

## Links

- proves:: [[Requirements/REQ-038 - Produce a reproducible independently installable candidate]]
- reviewed-in:: [[Reviews/Phase 21B Reproducible Candidate Review]]
- verifies:: [[Issues/ISSUE-038 - Close the network-gated release checks]]
- follows:: [[Evidence/EVD-037 - Phase 21A verification integrity verification]]
