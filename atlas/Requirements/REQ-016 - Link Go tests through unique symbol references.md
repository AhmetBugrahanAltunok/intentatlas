---
id: REQ-016
type: requirement
status: accepted
phase: 7A
---
# Link Go tests through unique symbol references

Contributors can distinguish a Go test's direct lexical use of production declarations from a
weak same-filename convention without resolving or executing Go code.

## Acceptance

- Same-directory Go tests gain a structural `tests` relationship only when their package is the
  production package or its conventional external `_test` package.
- A referenced declaration must be exported and resolve to exactly one production file in that
  package; ambiguous names produce no structural relationship.
- Comments, quoted strings, raw strings, and rune literals cannot create symbol-reference links.
- The existing filename-convention relationship remains as an explicit low-confidence fallback.
- Results are deterministic, bounded by the shared parse-size limit, offline, and never execute the
  Go toolchain or project code.
- The pinned `tidwall/match` file case moves from low-only evidence to medium confidence without
  changing recommendation scores or labels.
- Focused and complete tests, coverage, lint, security, CLI, UI, package, determinism, attribution,
  and Obsidian closure gates pass.

## Scope boundary

The relationship is lexical evidence, not proof that a test executes a declaration. Unexported,
ambiguous, generated, build-tag-dependent, reflection-driven, and indirect behavior remains
unresolved unless another evidence source covers it.

## Typed links

- drives:: [[Decisions/ADR-016 - Prefer unique Go symbol evidence over filename convention]]

## Trace

- Roadmap: [[Brain/Product Roadmap]]
- Planned evidence: [[Evidence/EVD-016 - Phase 7A Go symbol-reference verification]]
