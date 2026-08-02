# Installation status

IntentAtlas is currently an unpublished release candidate. A package-index command is therefore
not yet a public installation path. From a trusted checkout, create and install a local wheel:

```text
python -m build --wheel --outdir dist
python -m pipx install --pip-args=--no-deps dist/intentatlas-*.whl
intentatlas --version
```

This requires Python 3.11-3.13 and an already installed `pipx`. The exact wheel used for release
review is tested with temporary `PIPX_HOME`, `PIPX_BIN_DIR`, and `PIPX_MAN_DIR` values through
install, command discovery, help/version, reinstall, and uninstall. That verification does not
modify the real user PATH or pipx roots.

After a separately approved package publication, `pipx install intentatlas` can become the
canonical public command. Phase 15 does not publish a package, tag a release, or provide a
zero-prerequisite Windows installer; Git is also required for repository acquisition and guided
Git analysis.

