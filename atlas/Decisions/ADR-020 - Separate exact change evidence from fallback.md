---
id: ADR-020
type: decision
status: accepted
phase: 8
---
# ADR-020 — Separate exact change evidence from fallback

## Context

A changed file may implement several unrelated requirements and define several unrelated symbols.
Promoting a file-level relationship to exact symbol evidence creates credible-looking false
positives. Dynamic behavior also means general-purpose static analysis cannot prove completeness.

## Decision

Normalize revision inputs into a bounded change set, then retain evidence granularity throughout
impact and recommendation traversal. Exact symbol references, exact coverage, and validated spans
may support direct claims. File relationships, naming conventions, ambiguous declarations, and
unsupported constructs remain explicitly labeled fallback evidence and cannot silently become
medium- or high-confidence symbol claims.

Every result carries analysis state, provenance, revision scope, confidence, and freshness. When
the relevant analyzer is incomplete or evidence is stale, report `fallback` or `unknown` and either
abstain or offer a clearly labeled full-test option.

Keep deterministic static analysis as the offline foundation. Coverage, execution traces, and
optional semantic interpretation may add evidence later, but they never erase provenance or turn
inference into fact.

ChangeSet schema 1 represents commit, endpoint range, staged, and worktree scopes with the same
deterministic structure. Resolve supplied revisions to full commit IDs before invoking a diff.
Store only file status, safe current/previous project-relative paths, and bounded current-side hunk
ranges. Do not retain raw patch lines. Worktree collection may enumerate ignored-aware untracked
paths but must not read their contents. Disable external diff drivers, text conversion, color, and
submodule traversal; reject unsafe revisions/paths and over-limit output rather than truncating it.

When analysis is requested, build a fresh read-only graph of the current worktree. Worktree scope
is aligned to that scan. For commit, range, and staged scopes, compare bounded normalized worktree
bytes with the resolved head or index blob; never infer symbols from a mismatch. Classify each file
as `analyzed`, `fallback`, or `unknown`, and expose `aligned`, `stale`, or `unknown` freshness plus
confidence, artifact IDs, and provenance. Require every current-side hunk to intersect a validated
symbol span before claiming exact analysis. Existing files without complete spans remain file
fallbacks; deleted, unavailable, private, unmerged, and stale artifacts remain unknown.

Map durable vault notes through their frontmatter identity and recognize generated vault notes as
derived outputs. Exclude the configured `Private/` path at the Git pathspec boundary before
collecting metadata. The base ChangeSet never reads untracked contents; the explicit analysis mode
may read supported worktree files through the normal bounded scanner but never executes them or
persists raw source.

Build requirement and test reports only from aligned artifact identities. Traverse requirement
intent through bounded `implemented-by`, `tracked-by`, and `drives` paths. A route that starts at a
file or crosses a file-to-symbol `defines` boundary remains low confidence even if it later reaches
a durable requirement; it must not become a default exact-symbol impact claim. Reuse the existing
test recommendation query, but cap candidates discovered by expanding an uncertain file and pair
them with a mandatory full-suite fallback. If any changed artifact is `unknown`, abstain from
ranked claims. Report schema 1 is deterministic and exposes candidate counts, paths, evidence,
analysis coverage, and one of the explicit execution strategies.

For Go, retain exact test-to-symbol edges as well as separate file navigation edges. Add a
`calls`/`called-by` edge only when a lexical call name resolves to one function or method in the
same package. Recommendation traversal may follow one such caller hop only when the test has exact
evidence for that caller; ambiguous declarations and broader transitive calls remain unlinked.

For Python, module identity is a module-to-candidate-set mapping. The existing repository-root and
leading-`src/` interpretations remain supported, but a module, symbol, or re-export relationship is
emitted only when the applicable module has one physical candidate. A collision such as
`pkg/a.py` with `src/pkg/a.py` abstains instead of selecting one by traversal order. Nested custom
source roots are not guessed without an explicit future source-root contract.

## Consequences

- Precision is favored over recall at the default confidence threshold.
- Low-confidence candidates remain inspectable without becoming default warnings.
- Language adapters must expose exact symbol evidence where they can and honest incompleteness
  where they cannot.
- No algorithm can guarantee complete behavior for reflection, runtime configuration, generated
  code, native boundaries, external systems, or undocumented intent.

## Links

- Requirement: REQ-020 (available through the incoming `drives` relationship)
- tracked-by:: [[Issues/ISSUE-018 - Implement trustworthy change intelligence]]
- Strategy: [[Brain/Phase 8-10 Strategy]]
