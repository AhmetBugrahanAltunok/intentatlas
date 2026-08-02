---
id: ISSUE-027
type: issue
status: in-progress
phase: 13
---
# Implement semantic monorepo foundation

Deliver explicit workspace ownership, revision-bound semantic evidence, partitioned derived state,
and bounded large-graph navigation without executing repository-controlled tooling.

## Entry condition

- [x] [[Reviews/Phase 12 Trust-First Onboarding Review]] records a final pass.
- [x] Phase 11B pilot evidence identifies the exact workspace structures and ambiguity failures to
      solve; unsupported structures are not added by speculation.
- [x] ADR-029 and the graph/schema compatibility boundary receive owner review before migration code.

## Work package 13A - workspace identity and ambiguity

- [x] Define versioned repository/project/package/source-root identities and typed relationships.
- [x] Parse only explicit bounded Python, JavaScript/TypeScript, and Go workspace metadata.
- [x] Move all applicable resolvers to project-scoped candidate sets and unique-only relationships.
- [x] Emit deterministic diagnostics for conflicting, unsupported, cyclic, or ambiguous ownership.
- [x] Add original fixtures and reviewed real-workspace cases for repeated names, aliases, namespace
      packages, nested modules, and cross-package tests.
- [x] Add deterministic old-schema migration and compatibility round-trip tests.

## Work package 13B - revision-bound semantic evidence

- [x] Define strict bounded SCIP symbol/occurrence/relation projection and compatibility metadata.
- [x] Require exact revision, artifact alignment, unique owner, safe range, and supported role before
      an imported observation becomes exact evidence.
- [x] Preserve stale/incomplete/unsafe/ambiguous inputs as rejected, fallback, or unknown without raw
      source/document persistence.
- [x] Prove that no indexer, compiler, package manager, plugin, hook, or project code is executed.
- [x] Exercise change -> symbol -> requirement -> test paths with aligned semantic evidence and with
      deliberately stale/ambiguous counterexamples.

## Work package 13C - partitioned scale and viewer queries

- [x] Partition adapter/cache inputs by declared project/package with dependency-aware invalidation.
- [x] Add repository file/byte/node/edge/report budgets before unbounded work and preserve last-good
      derived artifacts on failure.
- [x] Add bounded loopback graph search/neighborhood/path/report endpoints with snapshot identity,
      total counts, and omission counts.
- [x] Stop transferring or indexing the complete graph for the initial viewer window.
- [x] Record deterministic 100,000-node/500,000-edge work counters plus payload, query, browser, and
      peak-memory metrics on declared reference hardware.

## Closure

- [x] Add exact Code and Test links after implementation artifacts exist.
- [x] Run focused resolver/importer/migration/cache/scale/browser/security regressions.
- [ ] Run complete test, coverage, lint, type, security, package, installed-wheel, extracted-sdist,
      CLI/UI, deterministic-vault, approved network, and remote-CI gates.
- [ ] Complete EVD-029 with real-workspace licensing/provenance, exact artifact hashes, budget
      results, remaining limits, and full durable-chain assertions.
- [ ] Bind Evidence to the exact implementation commit and obtain final Review.

## Non-goals

- No new language adapter unless a separate requirement is justified by Phase 11B evidence.
- No external indexer execution or arbitrary adapter/plugin loader.
- No distributed build/test/cache system, hosted code-intelligence service, or mandatory network.
- No claim that static or imported semantic evidence proves behavioral completeness.

## Typed links

- implements:: [[Requirements/REQ-029 - Scale precise evidence across monorepos]]
- decided-by:: [[Decisions/ADR-029 - Model workspace boundaries and import semantic evidence]]
- planned-evidence:: [[Evidence/EVD-029 - Phase 13 semantic monorepo verification]]
- reviewed-by:: [[Reviews/Phase 13 Semantic Monorepo Foundation Review]]

## Planning links

- Strategy: [[Brain/Phase 11B-13 Delivery Strategy]]
- Handoff: [[Sessions/2026-08-02 - Phase 11B-13 roadmap handoff]]

## Implementation links

- implemented-by:: [[file:src/intentatlas/workspace.py]]
- implemented-by:: [[file:src/intentatlas/open_evidence.py]]
- implemented-by:: [[file:src/intentatlas/scan_cache.py]]
- implemented-by:: [[file:src/intentatlas/graph_query.py]]
- implemented-by:: [[file:src/intentatlas/viewer.py]]
- references:: [[file:tests/test_workspace.py]]
- references:: [[file:tests/test_open_evidence.py]]
- references:: [[file:tests/test_scan_cache.py]]
- references:: [[file:tests/test_graph_query.py]]
- references:: [[file:tests/test_browser_e2e.py]]
