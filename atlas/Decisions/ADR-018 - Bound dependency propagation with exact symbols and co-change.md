---
id: ADR-018
type: decision
status: accepted
phase: 7C
---
# ADR-018 — Bound dependency propagation with exact symbols and co-change

## Context

Phase 7B measured five Axios false negatives behind root-module, dynamic-import, and indirect
paths, plus three Click false positives caused by treating imports from a large Python file as
evidence for every declaration in that file. Blind reverse import traversal recovered Axios tests
but also reached dozens of unrelated tests, so a depth limit alone was not a sufficient precision
boundary.

## Decision

Record exact Python test-to-symbol relationships for explicit imported names and qualified module
attributes. Resolve local package re-exports for at most eight hops with cycle rejection. For a
nested changed method, inspect the exact symbol and its owners in order. If an owner-named test is
present, prefer that focused test over unrelated users of the same owner.

Record exact JavaScript/TypeScript named and default static-import relationships when the target
declaration is discovered unambiguously. Recommendation propagation may reverse only one such
exact-symbol import into a production file, then select only tests already linked directly to that
file. Cap direct dependents at 1,000.

For selected files and symbols, admit separate recent co-change evidence from at most five commits
on the latest analyzed date for that file. If the latest dated file change contains exact modified
symbols, use those symbols to scope the file query. Keep the evidence type, path, and fixed score
visible. Do not traverse arbitrary file-level import chains or claim that co-change proves runtime
dependency.

## Consequences

- Click no longer promotes unrelated declarations from `core.py` when the latest change and test
  both focus on `Context`.
- Axios can use exact one-hop normalization evidence and recent changed-test evidence without
  recommending every test importing the package root.
- Owner-name focus may omit relevant differently named tests; recent co-change may miss unchanged
  tests or include broad-commit tests. These are precision-first advisory heuristics, not proof.
- Dynamic loading, registry dispatch, reflection, hidden tests, and longer dependency paths remain
  unresolved unless another explicit evidence source supports them.

## Links

- Requirement: REQ-018 (available through the incoming `drives` relationship)
- tracked-by:: [[Issues/ISSUE-016 - Implement bounded symbol-aware test evidence]]
