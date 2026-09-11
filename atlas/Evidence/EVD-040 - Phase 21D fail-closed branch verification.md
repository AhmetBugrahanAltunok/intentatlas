---
id: EVD-040
type: evidence
status: verified
phase: 21D
---
# Phase 21D fail-closed branch verification

Local decision: **verified, 2026-09-11**. Complete suite: **641 passed, 4 skipped**, exit **0**,
branch-enabled total coverage **87.70%**, duration **165.62s**. Ruff, mypy (50 source files) and
Bandit over `src` and `tools` passed. No runtime module was modified.

## Why these modules

The 2026-09-11 review observed that the least-covered modules were also the ones carrying the
product's safety claims, and that the uncovered lines were concentrated in bound, error, and
abstention branches rather than in ordinary paths. A high aggregate percentage was therefore
hiding the fact that the fail-closed behaviour itself was the least proven part of the system.

## Coverage movement

| Module | Before | After |
| --- | --- | --- |
| `viewer.py` | 62% | 99% |
| `bounded_process.py` | 79% | 87% |
| `change_set.py` | 78% | 86% |
| `change_analysis.py` (Phase 21A) | 66% | 84% |
| `acquisition.py` | 76% | 78% |
| Project total | 86.47% | 87.70% |

Suite size moved from 612 to 641 collected passes; the 29 additions are the regressions listed
below. The remaining `bounded_process.py` gap is platform-gated: the POSIX process-group kill is
unreachable on Windows and the Windows Job Object and thread-resume ctypes paths are unreachable
on POSIX. Neither can be covered on one platform without mocking the operating system, which
would prove the mock rather than the behaviour.

## Regressions added

**Viewer, 8 cases.** An in-process loopback server fixture serves a small connected graph and
issues real HTTP requests, so the handler is exercised rather than imported. Covered: every
`/api/graph/*` route against the served snapshot; `/graph.json` returning the exact served bytes;
optional report endpoints present when supplied and 404 when not; packaged assets; unknown routes;
seven malformed queries each returning a bounded schema-1 error with no traceback text; and an
unparsable or non-UTF-8 graph document refused before any server starts.

The malformed-query set deliberately includes a percent-encoded Arabic-Indic digit three, because
`str.isdigit()` accepts it while `int()` semantics and the ASCII check do not. That case pins the
`isascii()` guard rather than assuming it.

**Bounded process, 8 cases.** Negative allowance refused before any process starts, verified by
asserting `Popen` is never reached. Unstartable command, containment failure, missing stdout pipe,
unreadable pipe, uncollectable child, and a zero allowance that both refuses output and still
accepts a silent success. The containment-failure case additionally polls the started child to
prove it did not outlive the failure.

The most valuable case is new: a parent that spawns a descendant inheriting stdout and then exits
cleanly. Collection must fail closed instead of blocking on a reader that can never reach end of
file, and the test asserts it returns in under six seconds rather than waiting out the descendant.
This is the only path through that branch, and it had no coverage.

**ChangeSet, 9 cases.** Text rendering directly, including absent revisions, rename provenance and
hunk ranges; unknown output format refused; JSON and text agreement; unknown scope and
non-repository refusals; missing Git refused; commit scope requiring exactly one revision across
three malformed argument combinations; and freshness abstention for unmerged, missing,
unresolvable-head and Git-less cases, with deletion freshness depending on the artifact actually
being absent.

**Acquisition, 4 cases.** The intended work was to cover the clone path. It cannot be covered
offline, and the reason is itself the finding: `_safe_git_command` sets
`protocol.file.allow=never`, `protocol.ext.allow=never`, and `http.followRedirects=false`, so the
transport refuses local and `file://` sources entirely. An attempt to clone a real on-disk
repository — both as a path and as a URI — was refused in both forms, leaving no `.git` directory
and no working-tree file behind.

That control had no test. It now has one, phrased as the security property rather than as a
coverage exercise: a reachable on-disk repository must remain unacquirable, because otherwise a
crafted source argument could make the transport read an arbitrary local repository. Also covered:
an unreachable origin, a refusal when Git is absent with no destination created, and a direct
assertion that the three protocol settings are present in the fixed argument list.

`acquisition.py` therefore moved only 76% to 78%. The residual gap is the clone success path and
its post-clone sparse-checkout and size accounting, which require a real remote over HTTPS.
Covering it offline would mean relaxing `protocol.file.allow`, which would test a weakened
configuration rather than the shipped one. It is left uncovered deliberately; the honest way to
exercise it is the networked acquisition path against a real public repository.

## A test that initially passed for the wrong reason

The uncollectable-child case was written against what looked like the process-wait failure block
and passed immediately. Coverage still reported that block uncovered, which prompted a direct
probe: the exception cause was `SubprocessError` and `wait` had been called twice, so the intended
path was in fact exercised — the still-uncovered lines were a different branch, the
reader-still-alive cleanup. That branch needed the surviving-pipe-holder scenario described above.
Recorded because a passing assertion was not by itself evidence that the intended path ran.

## Limitations

- Coverage is not correctness. These tests pin current behaviour at the boundaries; they do not
  establish that the chosen boundaries are the right ones.
- `longitudinal.py` at 75% was not addressed. `acquisition.py`'s residual gap is structural,
  as described above, rather than a matter of missing effort.
- One platform and one interpreter. The platform-gated branches above need the remote matrix.

## Links

- proves:: [[Requirements/REQ-040 - Prove the fail-closed branches rather than assert them]]
- reviewed-in:: [[Reviews/Phase 21D Fail-Closed Branch Review]]
- follows:: [[Evidence/EVD-039 - Phase 21C first-run walkthrough verification]]
