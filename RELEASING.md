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

Create the release environment with every maintained gate and the fixed build toolchain:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,release,security,typing]"
```

On macOS or Linux, run `python -m venv .venv` followed by `source .venv/bin/activate`; the Python
commands below are otherwise the same.

```powershell
python -m pytest --cov=intentatlas --cov-report=term-missing --cov-fail-under=80
python -m ruff check .
python -m bandit -q -r src tools
python -m pip check
python -m mypy
```

After explicit network approval, run `python -m pip_audit --skip-editable` against that combined
environment so development, release, security, typing, build-backend, and runtime dependencies are
covered. The unpublished editable IntentAtlas candidate is intentionally skipped; its third-party
environment is still audited in full.

Run the actual CLI and local viewer workflows as described in the phase review. A release is not
ready while a required gate is failing.

## 3. Build and compare artifacts

Use one fixed timestamp for both builds so archive metadata is reproducible:

```powershell
$releaseEpoch = git show -s --format=%ct HEAD
$sourceRevision = git rev-parse HEAD
$env:SOURCE_DATE_EPOCH = $releaseEpoch
$varRoot = Join-Path (Resolve-Path .) "var"
New-Item -ItemType Directory -Force $varRoot | Out-Null
$releaseRoot = Join-Path $varRoot ("release-" + [guid]::NewGuid().ToString("N"))
$releaseA = Join-Path $releaseRoot "a"
$releaseB = Join-Path $releaseRoot "b"
New-Item -ItemType Directory $releaseRoot | Out-Null
New-Item -ItemType Directory $releaseA, $releaseB | Out-Null
python -m build --sdist --wheel --outdir $releaseA
python -m build --sdist --wheel --outdir $releaseB
python tools/verify_release.py $releaseA $releaseB `
  --write-provenance (Join-Path $releaseRoot "release-provenance.json") `
  --source-revision $sourceRevision `
  --source-date-epoch $releaseEpoch
```

The verifier requires byte-identical repeated artifacts; exact version-derived outer names and
dist-info identity; bounded, collision-free archive paths; valid wheel/source metadata; all wheel
`RECORD` hashes; the console entry point, pure-Python tag, bundled web assets, and dependency
metadata derived from the reviewed `pyproject.toml`. Every source-archive file and both runtime
payloads must match the reviewed checkout byte-for-byte; generated `PKG-INFO` is validated against
the same metadata contract. The source archive includes only the checked-in source, tests, docs,
release files, and small original corpus required by its tests; vault, real-world benchmark,
workflow, local state, and undeclared roots remain excluded. The canonical provenance record also
records the wheel generator and binds verified names, sizes, and SHA-256 digests to the exact
40-character source revision and fixed build epoch. It describes candidate bytes but is not a
signature or hosted attestation.

## 4. Install the exact candidate

Create a fresh virtual environment, install the wheel from `$releaseA` with `--no-deps`, then
verify `intentatlas --version`, deterministic `intentatlas demo --report text` and `--report json`,
interactive `intentatlas demo`, and the init/scan/status/impact workflow on a temporary example
repository. Run the real-browser E2E gate with
`INTENTATLAS_REQUIRE_BROWSER=1`. Record the provenance file and results in the release evidence.

Also build a wheel from the verified source archive with the fixed backend and
`--no-build-isolation`, install that rebuilt wheel into another clean environment, and repeat the
version plus deterministic demo checks. Under the same `SOURCE_DATE_EPOCH`, the rebuilt wheel must
be byte-identical to the directly built wheel. Extracted source-archive tests must pass; this
prevents an installable wheel from masking an incomplete source release.

One PowerShell sequence is:

```powershell
$sdistAuditRoot = Join-Path $varRoot ("sdist-" + [guid]::NewGuid().ToString("N"))
$sdistWheelDir = Join-Path $sdistAuditRoot "wheel"
$sdistSourceDir = Join-Path $sdistAuditRoot "source"
$sdistInstallDir = Join-Path $sdistAuditRoot "install"
New-Item -ItemType Directory $sdistAuditRoot | Out-Null
New-Item -ItemType Directory $sdistWheelDir, $sdistSourceDir | Out-Null
$sdist = (Get-ChildItem (Join-Path $releaseA "*.tar.gz")).FullName
python -m pip wheel --no-deps --no-build-isolation $sdist --wheel-dir $sdistWheelDir
$directWheel = (Get-ChildItem (Join-Path $releaseA "*.whl")).FullName
$sdistWheel = (Get-ChildItem (Join-Path $sdistWheelDir "*.whl")).FullName
if ((Get-FileHash $directWheel).Hash -ne (Get-FileHash $sdistWheel).Hash) {
  throw "The sdist-rebuilt wheel differs from the directly built wheel"
}
python -m venv $sdistInstallDir
& (Join-Path $sdistInstallDir "Scripts/python.exe") -m pip install --no-deps $sdistWheel
& (Join-Path $sdistInstallDir "Scripts/intentatlas.exe") --version
& (Join-Path $sdistInstallDir "Scripts/intentatlas.exe") demo --report json
tar -xzf $sdist -C $sdistSourceDir
$sdistRoot = (Get-ChildItem $sdistSourceDir -Directory -Force).FullName
Push-Location $sdistRoot
$previousPythonPath = $env:PYTHONPATH
try {
  $env:PYTHONPATH = (Resolve-Path src).Path
  python -m pytest -q
  if ($LASTEXITCODE -ne 0) { throw "Extracted sdist tests failed" }
} finally {
  if ($null -eq $previousPythonPath) {
    Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
  } else {
    $env:PYTHONPATH = $previousPythonPath
  }
  Pop-Location
}
```

On macOS or Linux, use the `bin/python` and `bin/intentatlas` paths below the fresh sdist install
directory; the CI workflow contains the equivalent POSIX extraction and test sequence.

## 5. Publish only after approval

An `rc` version only identifies candidate bytes; it is not release approval. Tagging,
creating a public release, changing repository visibility, and uploading to a package index are
separate external actions.
Perform them only after the recorded review passes and the release owner explicitly approves the
exact version and artifact hashes. Never substitute or publish a rebuild unless its bytes match the
approved hashes exactly.

The default CI workflow is verification-only. The separate `Publish approved release` workflow is
manual and inert until a maintainer dispatches it. Before first use, the repository owner must
configure required reviewers on the fixed `pypi` environment and configure the matching PyPI
Trusted Publisher. Restrict that environment's deployment branches/tags to protected `main` or an
explicitly approved release ref so a branch-modified workflow cannot request the publishing
identity. None of these external settings is created by this repository. Public visibility is also
blocked until GitHub private vulnerability reporting has been enabled and verified.

Dispatch the workflow from protected `main` only after approving that dispatch commit's exact
revision, fixed epoch, wheel SHA-256, source archive SHA-256, and required confirmation phrase. The
workflow rejects a supplied source revision that differs from its own `main` dispatch revision. An
unprivileged job checks out that exact revision without persisted credentials, builds twice,
rejects any byte or approved-hash mismatch, and transfers the verified artifacts plus provenance.
A separate protected `pypi` job receives OIDC
permission, runs no checkout, build backend, package installation, or project code, rechecks the
transferred hashes, and gives only those bytes to the immutable trusted-publishing Action. It
receives no long-lived package token. The presence of this workflow is not release approval, and
it must not be dispatched while any recorded gate remains open.
