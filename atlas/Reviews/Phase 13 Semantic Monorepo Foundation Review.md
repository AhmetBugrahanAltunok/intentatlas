---
id: review-phase-13-semantic-monorepo-foundation
type: review
status: pending
phase: 13
---
# Phase 13 Semantic Monorepo Foundation Review

## Acceptance review

- [ ] Phase 12 passed and Phase 11B evidence justified the selected workspace scope.
- [ ] REQ-029 is linked to ADR-029 and ISSUE-027.
- [ ] Workspace/project/source-root identities and relation semantics are versioned and documented.
- [ ] All applicable resolvers retain candidates and abstain instead of guessing ambiguous owners.
- [ ] Existing supported graph documents migrate deterministically without changing durable
      Markdown identities or silently changing meaning.
- [ ] Imported semantic evidence is local, strict, bounded, source-free, producer/revision-bound,
      uniquely owned, range-valid, and artifact-aligned before supporting exact claims.
- [ ] No repository-controlled compiler, indexer, build tool, package manager, hook, or plugin runs.
- [ ] Partitioned cache invalidation avoids unrelated rehash/rebuild and preserves last-good output.
- [ ] File/byte/node/edge/report budgets fail closed before unbounded work.
- [ ] Initial viewer navigation is bounded independently of total graph size and does not transfer
      or index the complete graph.
- [ ] Declared 100,000-node/500,000-edge deterministic and real-hardware scale budgets pass.
- [ ] Reviewed workspace cases preserve exact/fallback/unknown, omission, and full-suite safeguards.
- [ ] No new language, arbitrary plugin system, hosted service, telemetry, or distributed executor
      was introduced.
- [ ] Focused/full local quality, package, browser, deterministic-vault, and approved network gates
      pass.
- [ ] Exact implementation provenance, durable-chain assertions, push, and full remote CI pass.
- [ ] EVD-029 contains the complete inventory, exact commands/results, limitations, and risks.

## Evidence to examine

- [[Evidence/EVD-029 - Phase 13 semantic monorepo verification]]
- [[Requirements/REQ-029 - Scale precise evidence across monorepos]]
- [[Decisions/ADR-029 - Model workspace boundaries and import semantic evidence]]
- [[Issues/ISSUE-027 - Implement semantic monorepo foundation]]

## Review decision

Pending. Do not claim general monorepo or semantic-language completeness until every acceptance
item passes; retain an explicit capability matrix after closure.
