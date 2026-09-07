---
id: ADR-037
type: decision
status: accepted
phase: 19
---
# ADR-037 - Bound trust claims and abstain on uncertain structure

## Context

A complete static audit found that the primary architecture remained sound, but several boundary
implementations did not fully match IntentAtlas's trust language. High-fan-out Change Reports could
count only the first 100 returned tests, some Git helpers checked output size after collection,
delivery strings could persist secret-shaped content, and the viewer searched only its current
render window. Go and JavaScript/TypeScript had useful symbol relationships but no conservative
source spans, so exact change analysis always fell back for those languages.

## Decision

- Separate result limits from analysis limits. When bounded work prevents an exact population
  count, publish a lower-bound/truncation state rather than inventing an exact omission count.
- Redact every untrusted delivery string at the persistence boundary while retaining raw validated
  IDs only for in-memory relationship resolution. Reject identity collisions after redaction.
- Use streaming subprocess collection with byte and time bounds for Git inspection. Contain the
  child process tree with a kill-on-close Windows Job Object or POSIX process group; convert
  timeout, overflow, and process errors into conservative product states.
- Treat staged deletion plus same-path recreation as a visible worktree modification while keeping
  staged scope as deletion.
- Recover cache locks only when their exact directory shape and bounded owner metadata are safe and
  the lock is older than every protected operation budget and its local owner PID is not live.
- Query evidence paths from the immutable server snapshot. Rendering windows remain projections.
- Bound saved graph input before parsing and model construction.
- Extend exact span capability without claiming parser completeness: emit Go and
  JavaScript/TypeScript end lines only when dependency-free masked structural parsing proves a
  balanced declaration boundary. Otherwise omit the span and fall back.
- Treat a proven `typing` overload group as one implementation symbol only when declarations and
  exactly one unconditional implementation are direct siblings; ambiguous groups abstain.

## Consequences

- Large reports degrade honestly instead of failing or undercounting.
- Persistence and subprocess boundaries better match the product's local-trust contract.
- Cross-language exact analysis improves for common balanced declarations while malformed,
  regex-sensitive, bodyless, and otherwise ambiguous forms continue to abstain.
- Change Report schema 1 gains additive coverage metadata; strict consumers must allow it.
- Graph-query path omission values may be `null` when bounded traversal cannot know an exact count.

## Links

- driven-by:: [[Requirements/REQ-035 - Close audited trust and cross-language analysis gaps]]
- tracked-by:: [[Issues/ISSUE-035 - Apply audited reliability fixes]]
- verifies-with:: [[Evidence/EVD-035 - Phase 19 audited reliability verification]]
- preserves:: [[Decisions/ADR-033 - Canonicalize confidence and conservative Python resolution]]
