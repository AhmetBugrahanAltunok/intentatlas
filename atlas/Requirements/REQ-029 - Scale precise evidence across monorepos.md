---
id: REQ-029
type: requirement
status: proposed
phase: 13
---
# Scale precise evidence across monorepos

Maintainers of multi-source-root and workspace repositories receive deterministic impact and test
evidence that respects explicit project/package boundaries, abstains on ambiguous ownership, and
remains usable at large graph sizes without executing repository-controlled tooling.

## User outcome

A change in one workspace is attributed only to projects, symbols, requirements, and tests supported
by aligned evidence. Conflicting module/package ownership is visible rather than silently resolved.
Precise external semantic evidence can strengthen supported paths when it matches the revision; a
stale or incomplete index becomes fallback/unknown. Large graphs open through a bounded initial
view instead of requiring the complete graph transfer.

## Acceptance

- Phase 12 has a final passing Review and Phase 11B pilot evidence justifies the selected workspace
  structures before Phase 13 implementation begins.
- A versioned graph model represents repository, project/package, and declared source-root/workspace
  boundaries without inferring arbitrary nested roots from directory names.
- Python project metadata/source roots, JavaScript/TypeScript package workspaces and configured
  aliases, and Go workspace/module boundaries are either resolved through explicit supported
  declarations or reported as unsupported/ambiguous; no last-writer or traversal-order guess occurs.
- Resolver state retains all candidates. A symbol/import/test relationship requiring one owner is
  emitted only when exactly one aligned candidate satisfies the declared boundary.
- Existing graph documents migrate deterministically through a documented schema boundary; older
  supported input either migrates exactly or fails with an actionable version error.
- Strict local semantic-evidence import can project SCIP symbols/occurrences and relationships with
  source path, revision, producer/schema identity, freshness, and confidence. It does not execute an
  indexer, compiler, build tool, plugin, or repository code.
- Semantic evidence aligned to another revision, an unavailable artifact, an unsafe/private path,
  an ambiguous owner, or an incomplete range cannot create exact impact or test claims.
- Scan/cache invalidation is partitioned by declared project/package and adapter inputs so one local
  change does not require byte-hashing and rebuilding every unrelated language fragment.
- Repository file/byte/node/edge/report budgets reject excessive input before unbounded parser,
  serialization, or browser work. Failure retains the last complete derived artifacts.
- The viewer's initial response and render window are bounded independently of total graph size;
  initial navigation does not transfer or index the complete graph.
- Deterministic scale evidence covers at least 100,000 nodes and 500,000 edges with declared work-
  counter, payload, query-latency, and peak-memory budgets on recorded reference hardware.
- At least one reviewed Python workspace and one JavaScript/TypeScript workspace exercise the full
  change -> intent -> test path; Go workspace behavior has a real or original fixture gate. Known
  unsupported structures remain visible and abstain safely.
- No new language, arbitrary adapter loader, distributed build/test cache, hosted cross-repository
  service, or mandatory network dependency is introduced.
- Focused resolver/importer/migration/cache/scale/browser/security regressions and complete local,
  package, deterministic-vault, approved network, remote-CI, Evidence, durable-chain, and Review
  gates pass.

## Typed links

- drives:: [[Decisions/ADR-029 - Model workspace boundaries and import semantic evidence]]

## Trace

- Strategy: [[Brain/Phase 11B-13 Delivery Strategy]]
- Roadmap: [[Brain/Product Roadmap]]
- Delivery issue: [[Issues/ISSUE-027 - Implement semantic monorepo foundation]]
- Planned evidence: [[Evidence/EVD-029 - Phase 13 semantic monorepo verification]]
- Planned review: [[Reviews/Phase 13 Semantic Monorepo Foundation Review]]
- Entry gate: [[Reviews/Phase 12 Trust-First Onboarding Review]]
