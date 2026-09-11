---
id: ISSUE-038
type: issue
status: open
phase: 21B
---
# Close the network-gated release checks

The owner granted network approval on 2026-09-11. Two of the three checks are now closed. The
remaining one needs a push to the public remote, which is a separate outward-facing action and
has not been approved.

- [x] Run `tools/verify_pipx_install.py` against the verified wheel with network available.
  Closed 2026-09-11: `Verified isolated pipx install, reinstall, and uninstall: IntentAtlas
  0.3.0rc1`, exit 0. The earlier offline failure was pipx's own shared-library bootstrap.
- [ ] **Open — needs a push, which the owner has not separately approved.** Run the remote CI
  matrix — Ubuntu, Windows, macOS across Python 3.11 and 3.13 — and bind the result to this
  source revision. Local verification covered Windows 11 and one interpreter.
- [x] Run `python -m pip_audit --skip-editable` against the combined development, release,
  security, typing, and build environment. Closed 2026-09-11: `No known vulnerabilities
  found`, exit 0; only the editable candidate itself was skipped.

When these run, re-verify rather than reuse: a new artifact build supersedes the recorded digests.

## Links

- implements:: [[Requirements/REQ-038 - Produce a reproducible independently installable candidate]]
- verified-by:: [[Evidence/EVD-038 - Phase 21B reproducible candidate verification]]
- reviewed-by:: [[Reviews/Phase 21B Reproducible Candidate Review]]
