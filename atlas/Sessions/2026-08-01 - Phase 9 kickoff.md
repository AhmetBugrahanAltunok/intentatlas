---
id: SESSION-2026-08-01-PHASE-9-KICKOFF
type: session
status: complete
phase: 9
---
# 2026-08-01 — Phase 9 kickoff

Phase 9 begins after the verified local Phase 8 commit `c4414dd`. The working tree was clean before
this kickoff and no push, network, publication, or deployment action was performed.

The phase is tracked by [[Issues/ISSUE-019 - Implement CI shadow review loop]], must satisfy
[[Requirements/REQ-021 - Review revision ranges in CI shadow mode]], and follows
[[Decisions/ADR-021 - Compose review formats over trustworthy change reports]].

## First implementation slice

1. Add a pure Review Report schema over the existing range ChangeSet and Change Report.
2. Provide deterministic Markdown, JSON, and bounded SARIF 2.1.0.
3. Add `intentatlas review --base <revision> --head <revision>` as a read-only shadow command.
4. Preserve successful exit status for valid findings; do not add provider APIs or blocking policy.
5. Run focused regressions, then the complete quality/security and affected CLI workflow gates.

Phase 9 remains open until commit-keyed test outcomes, the opt-in CI workflow, change-centric
viewer, pilots, and the complete [[Brain/Phase Completion Protocol]] pass.

## First-slice progress

- Added Review Report schema 1 and deterministic Markdown, JSON, and bounded SARIF 2.1.0 renderers.
- Added the read-only `review --base --head` CLI path with a fixed non-blocking `shadow` contract.
- Added path traversal, absolute-path, encoded-path, empty-hunk, format, schema, determinism, and
  real Git range regressions.
- Focused verification: `python -m pytest tests/test_review.py tests/test_cli.py -q` — 12 passed.
- Complete verification: `python -m pytest --cov=intentatlas --cov-report=term-missing` — 182
  passed, 88% total coverage.
- `python -m ruff check .`, `python -m bandit -q -r src`, and `python -m pip check` all passed.
- A real `HEAD^..HEAD` repository review produced deterministic JSON plus valid Markdown and SARIF;
  every format returned 0, SARIF reported `blocking=false`, and the stale revision correctly caused
  `unknown` analysis with `abstain-and-full-suite` rather than an unsafe targeted claim.
- No network, provider API, credential, publication, push, project-code execution, or test execution
  was introduced by the review command.

The first two [[Issues/ISSUE-019 - Implement CI shadow review loop|delivery checks]] are complete.
Phase 9 remains open for the opt-in workflow, commit-keyed test outcomes, viewer work, pilots, and
final phase closure.

## Second-slice progress

- Added an explicit local composite Action under `.github/actions/intentatlas-review/`; no workflow
  is enabled merely by installing or checking out the project.
- The Action accepts only base, head, and a validated report format. It loads the local package,
  calls the public review CLI, writes below `RUNNER_TEMP`, and exposes only that local path.
- It accepts no credential, requests no permission, calls no provider API, uploads nothing, writes
  no job summary, modifies no pull request, and does not introduce blocking policy.
- Manifest contract and forbidden-capability regression passed; `bash -n` passed.
- The exact Action runner succeeded against the real repository under Git Bash with exit 0 and a
  `shadow` JSON report. A traversal-shaped invalid format exited 2 before creating any file.

The first three [[Issues/ISSUE-019 - Implement CI shadow review loop|delivery checks]] are complete.
Phase 9 remains open for commit-keyed test outcomes, change-centric viewer work, representative
pilots, and final phase closure.

## Third-slice progress

- Added strict Test Outcome schema 1 with one full commit SHA, the `complete-executed-set` policy,
  unique canonical project-relative paths, four fixed statuses, and bounded optional durations.
- Unknown fields, duplicate keys/paths, malformed roots, oversized input, unsafe paths, symbolic
  links, project escapes, and `atlas/Private/` locations fail closed. Raw output, source content,
  environment values, timestamps, and absolute paths remain outside the schema.
- The Review Report compares selected and executed paths only when the sidecar commit exactly equals
  the resolved head. Stale evidence is visible but all comparison sets are withheld.
- Markdown, JSON, and SARIF expose the same outcome evidence without labeling it accuracy,
  necessity, sufficiency, false-positive, or false-negative proof.
- CLI and composite Action accept the optional project-relative sidecar. A real Action run against
  `c4414dd` produced an aligned shadow report; an invalid traversal-shaped format still failed before
  creating output.
- Focused verification: review/outcome/action/CLI package — 26 passed.
- Complete verification: `python -m pytest --cov=intentatlas --cov-report=term-missing` — 197
  passed, 88% total coverage.
- Ruff, Bandit, pip dependency checks, Bash syntax, and Git whitespace checks all passed.

The first four [[Issues/ISSUE-019 - Implement CI shadow review loop|delivery checks]] are complete.
Phase 9 remains open for the change-centric viewer, representative pilots, and the final Evidence
and Review closure gates.

## Closure

The change-centric viewer, exact/aligned, stale, and fallback pilots, 199-test full suite, 88%
coverage, quality/security gates, real browser interaction, two-pass vault determinism, zero-orphan
health, attribution privacy, and repository-boundary checks passed. Final records are
[[Evidence/EVD-021 - Phase 9 CI shadow review verification]] and
[[Reviews/Phase 9 CI Shadow Review Review]]. No commit, push, publication, or network action was
performed during closure.
