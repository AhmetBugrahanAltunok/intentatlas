---
id: EVD-010
type: evidence
status: verified
phase: 6B2A
---
# EVD-010 — Phase 6B2A vault synchronization verification

## Requirement and decision

- proves:: [[Requirements/REQ-010 - Preserve generated vault integrity during synchronization]]
- Decision: [[Decisions/ADR-010 - Failure-preserving atomic vault synchronization]]
- Delivery issue: [[Issues/ISSUE-008 - Implement resilient generated vault synchronization]]
- Review: [[Reviews/Phase 6B2A Vault Synchronization Review]]

## Change inventory

- Replaced purge-before-write synchronization with an in-memory prepare, atomic replace, then
  stale-prune pipeline.
- Every desired generated node and dashboard document is rendered before filesystem mutation.
- Byte-identical UTF-8 output is detected with exact byte comparison and left untouched.
- Changed notes are written to dot-prefixed same-directory temporary files and installed with
  `os.replace`, so an existing symlink is replaced rather than followed and readers do not see a
  truncated target.
- Temporary files are cleaned in a `finally` path after successful replacement, retry exhaustion,
  missing-source errors, non-transient I/O errors, and write failures.
- Recognized permission and Windows sharing failures retry after fixed delays of 20, 50, and 100
  milliseconds. Missing replace sources and non-transient errors fail immediately.
- Stale enumeration starts only after every desired replacement succeeds. Marked stale notes use
  the same bounded retry for reading and deletion; manual notes and symlinks are skipped.
- The CLI generated-note count retains its prior meaning: total desired generated notes, not the
  number physically rewritten during that scan.
- English and Turkish READMEs, architecture, security, changelog, roadmap, requirement, ADR, and
  issue records document the behavior and its explicit per-file transaction boundary.

## Focused fault-injection verification

Command:

`python -m pytest tests/test_vault.py -q`

Result: 14 passed.

The suite covers user and Private note preservation, marked-only stale cleanup, exact byte
identity, CRLF/LF byte differences, transient replacement locks, persistent replacement locks,
missing replace sources, non-transient I/O failures, temporary-file write failure, temporary-file
cleanup, transient stale-read locks, transient stale-delete locks, symlink skipping, render-before-
mutation ordering, deterministic output, and untrusted Markdown escaping.

## Complete quality suite

- `python -m pytest --cov=intentatlas --cov-report=term
  --cov-report=json:.intentatlas/coverage-phase6b2a-final.json` — 78 passed.
- Coverage — total 88.6951%; `vault.py` 90.0%.
- `python -m ruff check .` — passed.
- `python -m bandit -q -r src` — passed.
- `python -m pip check` — no broken requirements.
- `python -m pip_audit` — no known vulnerabilities; the local unpublished
  `intentatlas==0.1.0` package was skipped because it is not on PyPI.
- `node --check src/intentatlas/web/app.js` — passed.

## Real Windows lock and recovery

A marked stale probe was created in the generated `atlas/Code/` area and held open with Windows
sharing flags that permit reading but deny deletion. The locked scan exited 2 with the expected
WinError 32 after bounded retries. The SHA-256 manifest of all 457 desired generated notes was
identical before and after the failure:
`083614be0e8cd4b3debe389d7b5b670fb6fb48299692ffdfbd4cf5e47d1c1bea`.

The probe remained present while locked, proving the failure was explicit rather than silently
ignored. After closing the handle, the next scan passed, removed only the stale probe, restored
the accepted 457-note view, and left no `.intentatlas.tmp` file.

## Real vault stability

Two consecutive accepted scans before the final fault-injection additions each produced 508
nodes, 1,020 relationships, 457 generated notes, and zero durable orphans. The normalized graph
hash, allowed user-area hash, and a manifest containing every generated file's bytes and UTC
modification ticks were identical across both scans. The identical modification-time manifest
proves the second scan did not rewrite unchanged generated notes. `atlas/Private/` was not
enumerated or read.

After the final tests were added, the UI acceptance scan produced 514 nodes, 1,026 relationships,
and 463 generated notes. Final closure counts are recorded below after adding this Evidence and
Review.

## Local viewer

The loopback viewer returned HTTP 200 and rendered the 514-node/1,026-link graph. Search accepted
`REQ-010`; keyboard selection opened its requirement detail with three relationships; graph
metrics, layers, metadata, and relationship cards rendered correctly; and the browser console had
no warnings or errors. The temporary viewer process was stopped.

## Package verification

- `python -m pip wheel . --no-deps --no-build-isolation` produced
  `intentatlas-0.1.0-py3-none-any.whl` with SHA-256
  `954b5b68fe97f43576ffa47e10a6573b92c680002ffa9703cbc5205ced45dbe7`.
- The wheel installed with `--no-deps` into a new virtual environment.
- The installed CLI initialized a clean fixture, completed two consecutive scans, and reported
  six durable nodes, nine relationships, and zero durable orphans.

## Corrections made during verification

- Temporary-path assignment was moved before writing so a disk-full error cannot leak the newly
  created temporary file.
- `FileNotFoundError` is accepted only for idempotent cleanup; a missing atomic-replace source now
  fails immediately instead of being mistaken for success.
- Text decoding was replaced with byte comparison so CRLF and LF files are not falsely treated as
  byte-identical.
- Stale-note reads gained the same bounded retry and explicit persistent-error behavior as
  replacement and deletion; inaccessible stale output is no longer silently ignored.
- A loop variable used by the stale-delete callback was bound explicitly after lint identified the
  closure ambiguity.

## Remaining risks and boundaries

- Atomicity is per file, not across the complete vault. A persistent error may leave some desired
  notes at the new version and others at the previous version, but it does not delete desired
  targets first and it prevents stale cleanup from starting.
- Same-directory `os.replace` semantics depend on the local filesystem. Network shares or unusual
  filesystems may provide weaker guarantees than tested local Windows and normal CI filesystems.
- The bounded retry window totals 170 milliseconds. Longer locks fail clearly and require a later
  scan after the external process releases the file.
- Generated-note churn from real graph changes remains expected. Content-addressed manifests or
  versioned directory swaps could provide stronger cross-file transactions in a future phase.

## Final closure verification

After this Evidence and Review entered the graph, two final scans each produced 516 nodes, 1,039
relationships, 463 generated notes, and zero durable orphans. Their normalized graph SHA-256 was
identical at `bfa5cd6f3aa0729f7baaae55a98f02afce13af59202220466b94a42e2a3874ea`.
Allowed user-area aggregates were identical to each other, and generated bytes plus UTC
modification ticks were identical at
`3bc34bbd1222b88ab176306bc57a22594d03199e61a7af5bf2dce353b4a8bbc4`.

## Decision

REQ-010 acceptance criteria are satisfied. Phase 6B2A passes with failure-preserving generated
output, bounded lock recovery, exact unchanged-file preservation, and explicit residual limits.
