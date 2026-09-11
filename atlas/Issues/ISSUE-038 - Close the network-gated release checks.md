---
id: ISSUE-038
type: issue
status: open
phase: 21B
---
# Close the network-gated release checks

Every offline gate for the candidate at `ecbcc8ca0c112336ba8a11b3ac06e46c1610b160` passed. The
three items below need explicit network approval from the project owner and cannot be inferred
from the local results.

- [ ] Run `tools/verify_pipx_install.py` against the verified wheel with network available. The
  offline attempt failed inside pipx's own shared-library bootstrap, not in the candidate.
- [ ] Run the remote CI matrix — Ubuntu, Windows, macOS across Python 3.11 and 3.13 — and bind the
  result to this source revision. Local verification covered Windows 11 and one interpreter.
- [ ] Run `python -m pip_audit --skip-editable` against the combined development, release,
  security, typing, and build environment.

When these run, re-verify rather than reuse: a new artifact build supersedes the recorded digests.

## Links

- implements:: [[Requirements/REQ-038 - Produce a reproducible independently installable candidate]]
- verified-by:: [[Evidence/EVD-038 - Phase 21B reproducible candidate verification]]
- reviewed-by:: [[Reviews/Phase 21B Reproducible Candidate Review]]
