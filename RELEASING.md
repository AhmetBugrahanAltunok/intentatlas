# Releasing IntentAtlas

Releases are deliberate, reviewable, and local-first. The CI workflow verifies supported Python
versions, operating-system smoke tests, archive contents, and repeated-build reproducibility; it
does not publish a package.

## 1. Prepare the release

- Start from a clean, reviewed commit on `main`.
- Update `__version__` in `src/intentatlas/__init__.py`; Hatchling reads this canonical value
  through `[tool.hatch.version]`, so `pyproject.toml` must not contain a second static version.
- Run `intentatlas --version` and the version-consistency regression before building.
- Move the relevant `CHANGELOG.md` entries from `Unreleased` into a dated version section.
- Confirm that README, security, contribution, license, attribution, requirement, evidence, and
  review records describe the release accurately.

## 2. Run the complete local gates

```powershell
python -m pytest --cov=intentatlas --cov-report=term-missing --cov-fail-under=80
python -m ruff check .
python -m bandit -q -r src
python -m pip check
python -m mypy
```

Run the actual CLI and local viewer workflows as described in the phase review. A release is not
ready while a required gate is failing.

## 3. Build and compare artifacts

Install the release tools with `python -m pip install -e ".[release]"`. Use one fixed timestamp for
both builds so archive metadata is reproducible:

```powershell
$releaseEpoch = git show -s --format=%ct HEAD
$sourceRevision = git rev-parse HEAD
$env:SOURCE_DATE_EPOCH = $releaseEpoch
python -m build --sdist --wheel --outdir var/release-a
python -m build --sdist --wheel --outdir var/release-b
python tools/verify_release.py var/release-a var/release-b `
  --write-provenance var/release-provenance.json `
  --source-revision $sourceRevision `
  --source-date-epoch $releaseEpoch
```

The verifier requires byte-identical repeated artifacts, validates wheel `RECORD` hashes and
metadata, checks the console entry point and bundled web assets, confirms the MIT license bytes,
and rejects project-only vault, benchmark, workflow, and local configuration data from the source
distribution. The canonical provenance record binds those verified artifact names, sizes, and
SHA-256 digests to the exact 40-character source revision and fixed build epoch. It describes the
reviewed bytes but is not a signature or hosted attestation.

## 4. Install the exact candidate

Create a fresh virtual environment, install the wheel from `var/release-a` with `--no-deps`, then
verify `intentatlas --version`, deterministic `intentatlas demo --report text` and `--report json`,
interactive `intentatlas demo`, and the init/scan/status/impact workflow on a temporary example
repository. Run the real-browser E2E gate with
`INTENTATLAS_REQUIRE_BROWSER=1`. Record the provenance file and results in the release evidence.

## 5. Publish only after approval

An `rc` version only identifies reviewed candidate bytes; it is not release approval. Tagging,
creating a public release, changing repository visibility, and uploading to a package index are
separate external actions.
Perform them only after the recorded review passes and the release owner explicitly approves the
exact version and artifact hashes. Never rebuild between approval and publication.

The default CI workflow is verification-only. The separate `Publish approved release` workflow is
manual and inert until a maintainer dispatches it. Before first use, the repository owner must
configure required reviewers on the fixed `pypi` environment and configure the matching PyPI
Trusted Publisher; neither external setting is created by this repository.

Dispatch only after approving the exact source revision, fixed epoch, wheel SHA-256, source archive
SHA-256, and required confirmation phrase. The protected job checks out that full revision without
persisted credentials, builds twice, rejects any byte or approved-hash mismatch, writes provenance,
and gives only the already verified `release-a` bytes to the immutable trusted-publishing Action.
It receives no long-lived package token. The presence of this workflow is not release approval,
and it must not be dispatched while any recorded gate remains open.
