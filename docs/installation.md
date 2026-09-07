# Installation

IntentAtlas requires Python 3.11, 3.12, or 3.13. Git is required for repository analysis but not
for the built-in demo. It is currently an unpublished beta, so
`pipx install intentatlas` is not yet a valid public installation path. Installing this checkout
may contact the configured Python package index for build dependencies.

## Fastest current path

From a trusted checkout, create an isolated environment, install the checkout, and run the offline
demo.

Windows PowerShell:

```powershell
$IntentAtlasVenv = ".venv" # Use ".venv-intentatlas" if .venv already belongs to another setup.
python -m venv $IntentAtlasVenv
& "$IntentAtlasVenv\Scripts\python.exe" -m pip install .
& "$IntentAtlasVenv\Scripts\intentatlas.exe" demo --report text
```

macOS or Linux:

```bash
IntentAtlasVenv=.venv # Choose another name if needed.
python3 -m venv "$IntentAtlasVenv"
"$IntentAtlasVenv/bin/python" -m pip install .
"$IntentAtlasVenv/bin/intentatlas" demo --report text
```

The final command does not scan the checkout, start a listener, or access the network. A successful
installation prints the built-in `rotate_session` scenario and recommends
`tests/test_auth_rotation.py` with its evidence path.

Python reuses an existing environment folder. To use the shorter commands in the rest of the
documentation, activate the exact folder selected above:

```powershell
& "$IntentAtlasVenv\Scripts\Activate.ps1"
```

On macOS or Linux, run `source "$IntentAtlasVenv/bin/activate"`. If activation is blocked or
undesirable, use the selected environment folder's full executable path in every command.

## Analyze a repository

Run the next commands in a real interactive terminal; the guide intentionally rejects pipes,
redirects, CI, and other non-TTY contexts. Use the installed executable with an explicit local Git
repository:

```powershell
intentatlas guide C:\path\to\your-project
```

The guided flow shows the selected Git root, revision scope, safety limits, and write behavior
before it asks for confirmation.

Public GitHub repository onboarding additionally requires Git and explicit approval of the shown
network and managed-cache effects:

```powershell
intentatlas guide https://github.com/OWNER/REPOSITORY
```

Choose Quit to leave the guide. If you opt into the local viewer, stop the terminal process with
Ctrl+C. Persistent graph commands such as `status`, `impact`, `recommend-tests`, and `diff` require
`init` and `scan` first; `diagnose`, `guide`, and `changes --report` do not.

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
