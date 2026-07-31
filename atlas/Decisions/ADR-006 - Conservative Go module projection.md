---
id: ADR-006
type: decision
status: accepted
phase: 5A
---
# ADR-006 — Conservative Go module projection

## Context

Go imports identify packages rather than individual files, while the current IntentAtlas
structural graph connects file nodes directly. Go projects may also contain nested modules with
independent module paths. A Go adapter must preserve truthful relationships without invoking the
Go toolchain, downloading modules, or choosing an arbitrary package file.

## Decision

Implement Go through the existing immutable, bounded language-adapter contract using a small
dependency-free structural lexer. It recognizes explicit top-level named types, functions, and
methods after masking comments and literals. It tokenizes import declarations so import-looking
text inside comments, interpreted strings, runes, and raw strings cannot become relationships.

Discover `go.mod` as a configuration file and read only its module declaration. A module-local
package import is projected onto every discovered non-test `.go` file in the matched package.
Matching uses the longest discovered module-path prefix, so nested modules resolve independently.
External imports, unresolved packages, unclosed import blocks, and files above the shared parse
limit are omitted rather than guessed.

Test files use the existing `tests` relation. In addition, `name_test.go` links to `name.go` only
when that exact non-test sibling exists. The adapter emits stable file/symbol edges and structural
metadata only; it never executes Go or persists source contents.

## Consequences

- Go support remains offline, deterministic, zero-dependency, and compatible with the current
  graph schema, CLI, vault, and viewer.
- Projecting an imported package onto all its non-test files is more truthful than selecting an
  arbitrary representative, but packages with many files create denser graphs.
- The parser intentionally favors precision over full Go syntax coverage. Unicode identifiers,
  build-constraint evaluation, generated-code detection, dot semantics, and package-level nodes
  remain possible future refinements.

## Links

- Requirement: REQ-006 (available through the incoming `drives` relationship)
- tracked-by:: [[Issues/ISSUE-004 - Implement Go language adapter]]
- Strategy: [[Brain/Language Adapter Strategy]]
