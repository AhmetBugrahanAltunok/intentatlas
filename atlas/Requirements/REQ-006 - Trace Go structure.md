---
id: REQ-006
type: requirement
status: accepted
phase: 5A
---
# Trace Go structure

A developer can trace Go files, named types, functions, methods, module-local imports, and tests in
the same language-neutral graph used for Python and TypeScript/JavaScript, without running Go,
project code, network access, or an API key.

## Acceptance

- `.go` files and `go.mod` manifests are discovered with correct file kinds and language metadata.
- Explicit top-level named types, functions, generic functions, and methods expose deterministic
  symbol nodes with source lines.
- Imports matching a discovered `go.mod` module resolve only to non-test files in that local
  package; external imports and string/comment lookalikes do not create internal relationships.
- Nested modules use their own longest matching module path instead of being confused with a
  repository-root module.
- Go test imports create `tests` relationships, and `name_test.go` links conservatively to a unique
  sibling `name.go` through the filename convention.
- Oversized input is skipped, malformed import blocks fail closed without invented links, and no
  language runtime or project code runs.
- Repeated scans produce identical nodes and relationships.
- CLI output, generated Obsidian notes, and the local viewer can navigate Go nodes and edges.

## Typed links

- drives:: [[Decisions/ADR-006 - Conservative Go module projection]]

## Trace

- Roadmap: [[Brain/Product Roadmap]]
- Strategy: [[Brain/Language Adapter Strategy]]
- Planned evidence: [[Evidence/EVD-006 - Phase 5A Go adapter verification]]
