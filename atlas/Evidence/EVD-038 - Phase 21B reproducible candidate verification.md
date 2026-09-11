---
id: EVD-038
type: evidence
status: verified
phase: 21B
---
# Phase 21B reproducible candidate verification

Local decision: **verified for the offline gates, 2026-09-11**. Three network-dependent gates
could not run and are recorded as unverified, not as passed.

Source revision under verification: `ecbcc8ca0c112336ba8a11b3ac06e46c1610b160`.
Fixed build epoch: `1789136856` (the HEAD commit time, per `RELEASING.md`).
Toolchain: `hatchling 1.31.0`, `build 1.3.0` — both exactly the pinned `[release]` versions, so
the local build backend matches the one CI uses.

## Verified artifacts

| Artifact | SHA-256 | Bytes |
| --- | --- | --- |
| `intentatlas-0.3.0rc1-py3-none-any.whl` | `54d38e1110979c3ac0a07a9eb59ce0711878151b81e1cb818c704194bef0db5c` | 206630 |
| `intentatlas-0.3.0rc1.tar.gz` | `d028f36bbe97a8dbbce2652e5bf708e2bb669eaec9447c8edbe5d2198bb0289c` | 3206657 |

Wheel members 56; source-archive members 203; generator `hatchling 1.31.0`. The provenance record
is at `var/release-21b/release-provenance.json` and is not tracked, because `var/` is ignored.

## Acceptance and verification

| Acceptance | Evidence | Result |
| --- | --- | --- |
| Repeated builds are byte-identical | Two `python -m build` runs under one epoch; verifier reports `repeated_builds_byte_identical: true` | passed |
| Full release verification and provenance | `tools/verify_release.py` exit 0 with 13 recorded checks bound to the exact revision and epoch | passed |
| Source archive rebuilds the direct wheel | `pip wheel --no-cache-dir` from the sdist; `cmp` identical and both digests `54d38e11…` | passed |
| Clean environment install | Fresh venv, `--no-deps --no-index`; `intentatlas --version` equals the source module version | passed |
| Useful result without the checkout | `intentatlas demo --report json` from that venv returned `schema_version 1` and the `rotate_session` changed symbol | passed |
| Extracted archive tests itself | 607 passed, 11 skipped, exit 0, run from the extracted tree with its own `src` on `PYTHONPATH` | passed |
| Environment consistency | `python -m pip check`: no broken requirements | passed |
| Isolated pipx lifecycle | Not run offline; see below | **unverified** |
| Supported platform matrix | Not run; see below | **unverified** |
| Dependency audit | Not run; see below | **unverified** |

## Commands

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

`--no-isolation` was used deliberately so the build stayed offline. It is safe here only because
the installed backend is exactly the pinned `hatchling==1.31.0`; the documented isolated command
remains the CI form. This is a documented deviation, not an equivalent substitution.

One early comparison failed before the epoch was applied to the rebuild step: the direct and
archive-derived wheels differed at byte 11, the zip timestamp. The CI job sets the epoch at job
scope, which covers that step. The corrected run is the recorded result, and the cache was
disabled so the comparison could not be satisfied by a stored wheel.

## Unverified checks

- **Isolated pipx lifecycle.** `tools/verify_pipx_install.py` was attempted with `PIP_NO_INDEX=1`
  and failed while pipx upgraded its own shared libraries: `Could not find a version that
  satisfies the requirement pip>=23.1`. The failure is in pipx's environment bootstrap, not in the
  candidate wheel. The gate needs network approval to run.
- **Supported platform matrix.** Verified on Windows 11 with one Python only. The declared
  matrix — Ubuntu, Windows and macOS across Python 3.11 and 3.13 — needs remote CI.
- **Dependency audit.** `pip_audit --skip-editable` needs network approval.

Nothing was published, uploaded, or pushed. The artifacts exist only under the ignored `var/`
tree and carry no release approval.

## Links

- proves:: [[Requirements/REQ-038 - Produce a reproducible independently installable candidate]]
- reviewed-in:: [[Reviews/Phase 21B Reproducible Candidate Review]]
- verifies:: [[Issues/ISSUE-038 - Close the network-gated release checks]]
- follows:: [[Evidence/EVD-037 - Phase 21A verification integrity verification]]
