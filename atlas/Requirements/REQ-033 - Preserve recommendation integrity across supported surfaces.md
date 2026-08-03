---
id: REQ-033
type: requirement
status: accepted
phase: 17
---
# Preserve recommendation integrity across supported surfaces

## User outcome

A developer sees the same bounded test selection, confidence, reasons, omissions, and execution
strategy in ChangeReport, recommend-tests, guided CLI, JSON, and viewer output, while supported
Python src-layout imports resolve real callers without promoting weak or non-runnable candidates.

## Acceptance

- Scores map canonically to high `85+`, medium `65-84`, and low `0-64` on every surface.
- `minimum_confidence` filters test candidates before limiting and strategy selection; selected,
  filtered, limit-omitted, and shown-omission counts remain exact.
- Setuptools, Hatchling, Flit, and uniquely evidenced conventional src layouts map import module
  names without executing project tooling.
- Unique `import pkg; pkg.submodule.symbol` chains and bounded re-exports resolve the actual symbol;
  ambiguous owners, roots, modules, bindings, or symbols abstain.
- Empty package markers remain graph nodes but are not runnable recommendations.
- A filename-only or package-initializer re-export second hop stays low confidence, a single broad
  commit produces no co-change recommendation, and bounded co-change never outranks direct
  structural evidence.
- Reasons describe only resolved graph evidence and never claim source-level absence as fact.
- Historical stale analysis recommends a clean revision-matched checkout; diagnostic ambiguity is
  explicitly a heuristic warning rather than proof that the resolver abstained.
- Frozen before/after evaluation, focused/full/static/security/package/network/browser/CLI/vault
  gates, final pushed-head CI, and comprehensive Evidence/Review all pass.
- Phase 11C, tag, release, publication, deployment, third-party execution, and Private access do
  not occur.

## Links

- drives:: [[Decisions/ADR-033 - Canonicalize confidence and conservative Python resolution]]
- delivered-by:: [[Issues/ISSUE-032 - Implement recommendation integrity and Python resolution]]
- proved-by:: [[Evidence/EVD-033 - Phase 17 recommendation integrity verification]]
