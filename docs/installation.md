# Installation

IntentAtlas requires Python 3.11, 3.12, or 3.13. It is currently an unpublished release candidate,
so `pipx install intentatlas` is not yet a valid public installation path.

## Fastest current path

From a trusted checkout, create an isolated environment, install the checkout, and run the offline
demo.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install .
.\.venv\Scripts\intentatlas.exe demo --report text
```

macOS or Linux:

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install .
./.venv/bin/intentatlas demo --report text
```

The final command does not scan the checkout, start a listener, or access the network. A successful
installation prints the built-in `rotate_session` scenario and recommends
`tests/test_auth_rotation.py` with its evidence path.

## Analyze a repository

Use the installed executable with an explicit local Git repository:

```powershell
.\.venv\Scripts\intentatlas.exe guide C:\path\to\your-project
```

Or use `./.venv/bin/intentatlas guide /path/to/your-project` on macOS or Linux. The guided flow
shows the selected Git root, revision scope, safety limits, and write behavior before it asks for
confirmation.

Public GitHub repository onboarding additionally requires Git and explicit approval of the shown
network and managed-cache effects:

```powershell
.\.venv\Scripts\intentatlas.exe guide https://github.com/OWNER/REPOSITORY
```

## Release-review installation

Release review builds an exact local wheel and installs that artifact with pipx:

```text
python -m build --wheel --outdir dist
python -m pipx install --pip-args=--no-deps dist/intentatlas-*.whl
intentatlas --version
```

The exact candidate wheel is tested with temporary `PIPX_HOME`, `PIPX_BIN_DIR`, and
`PIPX_MAN_DIR` values through install, command discovery, help/version, reinstall, and uninstall.
That verification does not modify the real user PATH or pipx roots. See the complete
[release process](../RELEASING.md).

After separately approved package publication, `pipx install intentatlas` can become the canonical
public command. No package, tag, or zero-prerequisite Windows installer is currently claimed.
