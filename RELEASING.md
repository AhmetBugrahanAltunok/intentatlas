# Releasing IntentAtlas

Releases are deliberate, reviewable, and local-first. The CI workflow verifies supported Python
versions, operating-system smoke tests, archive contents, and repeated-build reproducibility; it
does not publish a package.

## 1. Prepare the release

- Start from a clean, reviewed commit on `main`.
- Update the version in `pyproject.toml` and `src/intentatlas/__init__.py` together.
- Move the relevant `CHANGELOG.md` entries from `Unreleased` into a dated version section.
- Confirm that README, security, contribution, license, attribution, requirement, evidence, and
  review records describe the release accurately.

## 2. Run the complete local gates

```powershell
python -m pytest --cov=intentatlas --cov-report=term-missing --cov-fail-under=80
python -m ruff check .
python -m bandit -q -r src
python -m pip check
```

Run the actual CLI and local viewer workflows as described in the phase review. A release is not
ready while a required gate is failing.

## 3. Build and compare artifacts

Install the release tools with `python -m pip install -e ".[release]"`. Use one fixed timestamp for
both builds so archive metadata is reproducible:

```powershell
$releaseEpoch = git show -s --format=%ct HEAD
$env:SOURCE_DATE_EPOCH = $releaseEpoch
python -m build --sdist --wheel --outdir var/release-a
python -m build --sdist --wheel --outdir var/release-b
python tools/verify_release.py var/release-a var/release-b
```

The verifier requires byte-identical repeated artifacts, validates wheel `RECORD` hashes and
metadata, checks the console entry point and bundled web assets, confirms the MIT license bytes,
and rejects project-only vault, benchmark, workflow, and local configuration data from the source
distribution.

## 4. Install the exact candidate

Create a fresh virtual environment, install the wheel from `var/release-a` with `--no-deps`, then
verify `intentatlas --version`, `intentatlas demo`, and the init/scan/status/impact workflow on a
temporary example repository. Record the artifact hashes and results in the release evidence.

## 5. Publish only after approval

Tagging, creating a public release, and uploading to a package index are separate external actions.
Perform them only after the recorded review passes and the release owner explicitly approves the
exact version and artifact hashes. Never rebuild between approval and publication.
