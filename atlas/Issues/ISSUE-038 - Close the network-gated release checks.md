---
id: ISSUE-038
type: issue
status: closed
phase: 21B
---
# Close the network-gated release checks

Closed 2026-09-11. The owner granted network approval, then approved a push. All three checks
passed against `a6e60d10fd0e1a8e402878b62fd02c10747f5a8c`.

- [x] Run `tools/verify_pipx_install.py` against the verified wheel with network available.
  Closed 2026-09-11: `Verified isolated pipx install, reinstall, and uninstall: IntentAtlas
  0.3.0rc1`, exit 0. The earlier offline failure was pipx's own shared-library bootstrap.
- [x] Run the remote CI matrix — Ubuntu, Windows, macOS across Python 3.11 and 3.13 — and bind
  the result to this source revision. Closed 2026-09-11: run
  [34635166633](https://github.com/AhmetBugrahanAltunok/intentatlas/actions/runs/34635166633)
  at `a6e60d1`, **13 of 13 jobs succeeded**. All six `cross-platform-e2e` combinations passed,
  which is the first remote confirmation that the Phase 21A package-identity gate behaves on
  Linux and macOS and not only on the Windows host it was written on. `reproducible-package`
  also passed, corroborating the local dual-build, verifier, pipx and sdist-suite results on
  Ubuntu.
- [x] Run `python -m pip_audit --skip-editable` against the combined development, release,
  security, typing, and build environment. Closed 2026-09-11: `No known vulnerabilities
  found`, exit 0; only the editable candidate itself was skipped.

This result describes `a6e60d1`. A later revision needs its own run; these results must not be
reused as evidence for source they were not taken against.

## Links

- implements:: [[Requirements/REQ-038 - Produce a reproducible independently installable candidate]]
- verified-by:: [[Evidence/EVD-038 - Phase 21B reproducible candidate verification]]
- reviewed-by:: [[Reviews/Phase 21B Reproducible Candidate Review]]
