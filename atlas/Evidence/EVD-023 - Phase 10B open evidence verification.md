---
id: EVD-023
type: evidence
status: verified
phase: 10B
---
# EVD-023 — Phase 10B open evidence verification

This evidence verifies
[[Requirements/REQ-023 - Import open evidence without overstating certainty]] through
[[Decisions/ADR-023 - Separate observations from aligned execution evidence]] and
[[Issues/ISSUE-021 - Implement bounded open evidence imports]].

## Change inventory

- `ProjectConfig` adds explicit `scip_reports`, `sarif_reports`, and `test_execution_reports` lists;
  absent lists preserve the prior offline default and no report is auto-discovered.
- A separate open-evidence parser rejects duplicate JSON keys, non-finite numbers, excessive depth,
  values, strings, files, locations, and records behind the existing 10 MiB, project-relative,
  link-safe, non-private report boundary.
- SCIP protobuf JSON produces one neutral per-file `code-index` summary with bounded occurrence,
  definition, reference, and diagnostic counts. Binary protobuf and raw symbols/content are not
  accepted or retained.
- SARIF 2.1.0 produces one neutral per-file `finding-summary` with fixed level counts and bounded
  rule IDs after safe percent-decoded URI resolution. Messages, snippets, fixes, flows, properties,
  raw results, and unsafe/absolute locations are not retained.
- SCIP/SARIF summaries use `references`, never causal, proof, history, or test relationships.
- Test Execution Map schema 1 validates an exact 40-character commit, fixed completeness policy,
  unique test records, and unique existing source paths. Summary nodes expose aligned/stale/unknown
  freshness without raw output.
- Fixed read-only Git calls require both report-commit equality and every mapped test/source path to
  be tracked and unchanged from HEAD. Only then are `test-execution-map` `tests` edges created;
  stale/unknown summaries cannot influence the existing recommendation engine.
- README, Turkish README, architecture, changelog, and `docs/open-evidence.md` document the format
  boundaries, configuration, aggregation, freshness, non-claims, and binary SCIP limitation.
- REQ-023, ADR-023, ISSUE-021, Roadmap, kickoff, Evidence, and Review preserve phase traceability in
  the canonical `atlas/` vault.

## Focused verification

Command:

`python -m pytest tests/test_open_evidence.py tests/test_evidence.py tests/test_config.py tests/test_git_history.py tests/test_recommendations.py -q`

Result: 31 passed. Coverage includes deterministic SCIP/SARIF aggregation, aligned runtime
recommendations, stale and unknown withholding, matching-commit dirty-worktree withholding,
clean/incremental equality, source/diagnostic non-retention, private report rejection, duplicate,
binary, excessive, malformed, wrong-version and wrong-contract rejection, existing XML behavior,
configuration, Git, and recommendation regressions.

## Complete quality and security verification

- `python -m pytest --cov=intentatlas --cov-report=term-missing` — 214 passed; 88% total branch
  coverage.
- `python -m ruff check .` — passed.
- `python -m bandit -q -r src` — passed.
- `python -m pip check` — passed with no broken requirements.
- `node --check src/intentatlas/web/app.js` — passed.
- `bash -n .github/actions/intentatlas-review/run.sh` — passed.
- `git diff --check` — passed.

No dependency was added. The networked `pip-audit` check was not rerun because networked audits
require separate explicit approval; this is recorded as unverified rather than passed.

## Installed CLI and graphical pilot

An ignored original temporary pilot contained one Python source, one independent test, one clean
Git commit, one SCIP JSON document, one SARIF result, and one aligned execution record.

- First installed-CLI scan: 8 nodes, 11 relationships, `0 reused, 3 rebuilt`.
- Second installed-CLI scan: 8 nodes, 11 relationships, `3 reused, 0 rebuilt`.
- `intentatlas status` exited 0.
- The graph contained exactly one `code-index`, one `finding-summary`, one `test-execution`, one
  aligned runtime test edge, and execution freshness `aligned`.
- The real local viewer displayed all three new graph layers. Keyboard activation opened the
  execution node with exact report, commit, freshness, completeness, observed-file count, and a
  bounded evidence path. Browser warning/error count was zero.
- The viewer listener returned to zero and the complete ignored pilot directory was removed.

## Repository determinism and default behavior

- Final two-pass repository closure produced 1,002 nodes, 2,335 relationships, and 879 generated
  notes. The first rebuilt only Python after final implementation changes; the second reported
  `3 reused, 0 rebuilt`.
- Semantic graph diff was zero, generated-note fingerprints matched, all 123 allowed user-owned
  notes stayed byte-identical, status exited 0, and zero durable orphans remained.
- With all new report lists absent from root configuration, the graph contained zero `code-index`,
  `finding-summary`, or `test-execution` nodes, proving opt-in default behavior.
- `atlas/Private/` was not enumerated or included. Root `.obsidian/` and `.intentatlas/` remained
  ignored derived/local state.

## Acceptance decision and remaining limits

All REQ-023 acceptance criteria pass. Phase 10B is verified.

- SCIP support is protobuf JSON aggregate import, not binary protobuf or a symbol dependency graph.
- SARIF supports direct project-relative and `%SRCROOT%` artifact URIs; other URI-base resolution is
  intentionally omitted rather than guessed.
- Execution schema 1 uses the product's current full 40-character SHA-1 convention; Git SHA-256
  repository support requires a future schema decision.
- Alignment verifies mapped artifacts, not whether the producer's runtime environment or coverage
  instrumentation was complete or correct.
- Networked audit and remote cross-platform CI were not triggered without approval/push.

## Links

- proves:: [[Requirements/REQ-023 - Import open evidence without overstating certainty]]
- reviewed-by:: [[Reviews/Phase 10B Open Evidence Review]]
