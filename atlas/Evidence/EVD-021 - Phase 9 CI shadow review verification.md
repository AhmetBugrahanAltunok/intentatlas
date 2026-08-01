---
id: EVD-021
type: evidence
status: verified
phase: 9
---
# EVD-021 — Phase 9 CI shadow review verification

## Requirement and decision

- proves:: [[Requirements/REQ-021 - Review revision ranges in CI shadow mode]]
- Decision: [[Decisions/ADR-021 - Compose review formats over trustworthy change reports]]
- Delivery issue: [[Issues/ISSUE-019 - Implement CI shadow review loop]]
- Review: [[Reviews/Phase 9 CI Shadow Review Review]]

## Change inventory

- Review Report schema 1 composes the existing range ChangeSet, Change Analysis, and Change Report
  without adding another impact traversal. Resolved revisions, confidence, evidence, freshness,
  uncertainty, and full-suite fallback policy remain intact.
- `intentatlas review --base --head` emits deterministic Markdown, JSON, and bounded SARIF 2.1.0.
  Fixed rules distinguish unknown/fallback analysis, possible requirement impact, and full-suite
  fallback. SARIF paths are project-relative and encoded; source snippets and absolute paths are
  excluded.
- Valid findings remain non-blocking in fixed `shadow` mode. The command executes no project code
  or tests and performs no provider request, upload, comment, publication, or repository mutation.
- The opt-in composite Action accepts base, head, format, and an optional project-relative outcome
  sidecar. It requires no token or permission, writes only below `RUNNER_TEMP`, and exposes only the
  temporary local path. A calling workflow must explicitly choose any later upload or policy.
- Test Outcome schema 1 requires one full commit SHA, `complete-executed-set`, unique canonical
  project-relative paths, fixed statuses, and bounded optional durations. Unknown fields,
  duplicate JSON keys/paths, malformed or oversized input, unsafe paths, symbolic links, project
  escapes, and `atlas/Private/` locations fail closed.
- Outcome comparison occurs only when the sidecar commit exactly equals the resolved review head.
  Stale input is visible but creates no matched/missing comparison claims. Aligned sets describe one
  execution and are not labeled necessity, sufficiency, precision, recall, false positive, or false
  negative.
- `review --open` serves the exact fresh in-memory graph and Review Report through the loopback-only
  viewer. The panel shows scope, strategy, requirements, test candidates, outcome freshness, and
  selected-versus-executed evidence without a second scan or cache fallback.
- README, Turkish README, architecture, changelog, CI review documentation, pilot documentation,
  ADR, issue, session, roadmap, tests, Action metadata, and generated vault notes describe the same
  trust boundary.

## Acceptance and adversarial verification

- Markdown escapes untrusted labels. JSON and SARIF are byte-stable for identical inputs.
- Traversal, POSIX absolute, and Windows absolute paths are omitted from SARIF locations. Safe paths
  are URL-encoded, empty deletion hunks do not create invalid regions, and output is capped at 1,000
  results.
- A real Git range CLI fixture produces aligned exact-symbol analysis, selects the directly linked
  test, and preserves successful shadow exit status. Its stale sidecar exposes freshness but no
  comparison sets. A configured `atlas/Private/` sidecar is rejected before loading.
- The composite Action's exact Bash runner succeeds locally with no credential. Invalid
  traversal-shaped format input exits 2 before creating a file; an aligned HEAD sidecar is carried
  into the produced shadow report.
- The representative pilots cover exact+aligned targeted selection, stale-outcome comparison
  withholding, and unsupported TOML fallback with `IA101`, `IA300`, and full-suite policy. These
  fixtures are regression evidence, not general accuracy claims.
- Installed CLI E2E starts `review --open`, retrieves `/review.json`, and verifies aligned failed-test
  evidence. Real browser interaction opens the Revision review panel, displays the exact commit and
  `failed · 11 ms`, and reports no browser console warning or error. Visual review identified and
  corrected an accidental CSS case transformation of SHA and duration units.

## Verification commands and results

- `.venv\Scripts\python.exe -m pytest tests/test_review.py tests/test_test_outcomes.py
  tests/test_review_pilots.py tests/test_viewer.py -q` — 26 passed after interruption recovery.
- `.venv\Scripts\python.exe -m pytest tests/test_e2e.py::
  test_installed_revision_review_viewer_serves_commit_keyed_outcomes -q` — 1 passed.
- `.venv\Scripts\python.exe -m pytest --cov=intentatlas --cov-report=term-missing` — 199 passed;
  total branch-aware coverage 88%.
- `.venv\Scripts\python.exe -m ruff check .` — passed.
- `.venv\Scripts\python.exe -m bandit -q -r src` — passed.
- `.venv\Scripts\python.exe -m pip check` — no broken requirements.
- `node --check src/intentatlas/web/app.js` — passed.
- `bash -n .github/actions/intentatlas-review/run.sh` — passed with Git Bash.
- `git diff --check` — passed.
- No dependency declaration changed. A network-backed dependency audit was not rerun because
  networked audits require explicit approval; this is not represented as a new network result.

## Remaining risks

- Shadow mode deliberately does not prove behavioral impact, test necessity, or sufficient
  coverage and does not block CI.
- Outcome sidecars depend on the caller accurately reporting the complete executed-path set for the
  declared commit. They are observations, not ground truth for recommendation accuracy.
- Exact current-change spans remain strongest for Python. Unsupported languages, generated code,
  reflection, runtime configuration, deletions, and stale worktrees can require fallback or
  abstention.
- Requirements still depend on explicit, correct human-authored links. Missing intent cannot be
  reconstructed with certainty.
- The three pilots and existing public corpus are bounded regression evidence, not a universal
  precision/recall guarantee.

## Vault and repository closure

- Two final closure scans each produced 928 nodes, 2,155
  relationships, and 817 scanner-generated notes. All 111 explicitly enumerated user-owned files
  under `Brain/`, `Requirements/`, `Decisions/`, `Issues/`, `Evidence/`, `Reviews/`, and `Sessions/`
  remained byte-identical; `atlas/Private/` was never enumerated.
- The timestamp-normalized semantic graph was stable with SHA-256
  `aef2d5992f90e620782d124219bdf3066f06379d73203c6bbd57efa27d1317cd`.
- The 818 explicitly enumerated generated files, including the dashboard, were stable with
  content fingerprint `6fc79c2693cc199c5f82f4282d0bd2cd304407c2317f1a2260118a005e2fdd43`;
  `atlas/Home.md` was also unchanged. The scanner's 817-note count excludes one dashboard-level
  file included by the explicit fingerprint.
- `python -m intentatlas status .` reported 2,155 relationships and zero durable orphans.
- The graph contains no `atlas/Private/` path. Git tracks neither `atlas/Private/` nor the ignored
  root `.obsidian/` directory.
- Changed-line scans found zero prohibited tool-authorship statements and zero ProjectOS or
  Obsidian Mind source references. Legitimate MIT and existing third-party attribution remain.
- `git diff --check` passed. No network, push, publication, provider mutation, or deployment was
  performed.

## Decision

REQ-021 acceptance criteria are satisfied. Phase 9 passes locally with one shared uncertainty
model across CLI, SARIF, composite Action, commit-keyed outcome evidence, and the local viewer.
Findings remain shadow-only and non-blocking; stale or incomplete evidence cannot become a stronger
claim than its provenance supports.
