---
id: EVD-029
type: evidence
status: pending
phase: 13
---
# EVD-029 - Phase 13 semantic monorepo verification

This is a verification plan, not evidence that Phase 13 has passed.

## Claim to verify

IntentAtlas can preserve conservative, explainable change and test evidence across declared
workspace boundaries and large graphs, strengthen aligned paths with imported semantic evidence,
and abstain on ambiguity or staleness without executing repository-controlled tooling.

## Required evidence

- [ ] Exact starting/implementation revisions and the Phase 11B pilot cases that justify scope.
- [ ] Graph/schema/diagnostic/cache/viewer API versions, migration inventory, and compatibility
      classification.
- [ ] Original and license-reviewed real-workspace fixtures for supported Python, JavaScript/
      TypeScript, and Go boundary behavior.
- [ ] Candidate-set results proving unique resolution and abstention for repeated names, aliases,
      namespace packages, nested modules, re-exports, and cross-package test paths.
- [ ] Old-schema migration round trips, deterministic bytes, unsupported-version failures, and
      durable Markdown identity preservation.
- [ ] SCIP producer/schema/revision/input hashes and exact counts for accepted, stale, ambiguous,
      unsupported, unsafe, Private, excessive, and malformed observations.
- [ ] Proof that imported exact evidence requires aligned revision/artifact/range/owner/role and
      that no source/raw document is persisted.
- [ ] Process/command audit proving no compiler, indexer, build tool, package manager, plugin, hook,
      or repository code execution.
- [ ] Cache partition reuse/rebuild/rejection diagnostics and tests proving unrelated partitions are
      neither rehashed nor rebuilt after a local change.
- [ ] Pre-work repository budgets and failure-preserving last-good graph/cache behavior.
- [ ] Deterministic 100,000-node/500,000-edge work counters and recorded reference hardware, OS,
      Python/browser versions, wall time, payload bytes, query latency, and peak RSS.
- [ ] Real-browser proof that initial graph navigation does not transfer/index the complete graph
      and remains searchable, keyboard-accessible, Host-safe, and explicitly bounded.
- [ ] Focused regression commands and complete test/coverage/lint/type/security/package/installed-
      wheel/extracted-sdist/CLI/UI results.
- [ ] Two-pass vault bytes/mtime check, user-owned snapshot, zero-orphan result, and explicit full
      durable-chain assertions.
- [ ] Approved network audit, complete remote CI, exact generated Commit-note link, comprehensive
      change inventory, and remaining limits.

## Stop conditions

Keep the phase open if a resolver guesses one of multiple owners, semantic evidence is exact without
revision/artifact alignment, repository tooling executes, raw semantic/source content persists, an
old graph changes meaning silently, one partition change rebuilds the complete repository, initial
viewer navigation transfers the complete graph, a budget is exceeded without fail-closed behavior,
or any required local/remote gate is absent.

## Links

- proves:: [[Requirements/REQ-029 - Scale precise evidence across monorepos]]
- Decision: [[Decisions/ADR-029 - Model workspace boundaries and import semantic evidence]]
- Delivery issue: [[Issues/ISSUE-027 - Implement semantic monorepo foundation]]
- Review: [[Reviews/Phase 13 Semantic Monorepo Foundation Review]]
- Strategy: [[Brain/Phase 11B-13 Delivery Strategy]]
