---
id: REQ-004
type: requirement
status: accepted
phase: 3
---
# Trace TypeScript and JavaScript structure

A developer can trace TypeScript and JavaScript files, named symbols, local imports, and tests in
the same language-neutral graph used for Python, without running project code or requiring Node,
network access, or an API key.

## Acceptance

- Built-in language analysis uses one explicit adapter contract and deterministic graph fragments.
- Existing Python file, symbol, import, and test behavior remains unchanged behind that contract.
- TypeScript, JavaScript, TSX, and JSX files expose named classes, functions, interfaces, types,
  enums, and arrow-function declarations when they can be identified conservatively.
- Static local imports and re-exports resolve extensionless paths and directory index modules.
- Test files create `tests` relationships while application files create `imports` relationships.
- Bare package imports, malformed input, unsupported syntax, and files above the parse limit do not
  create invented internal relationships or execute code.
- Focused fixtures prove deterministic output across repeated scans.
- Existing CLI, generated Obsidian notes, and the local viewer can navigate the new nodes and edges.

## Typed links

- drives:: [[Decisions/ADR-004 - Built-in language adapter contract]]

## Trace

- Roadmap: [[Brain/Product Roadmap]]
- Strategy: [[Brain/Language Adapter Strategy]]
- Planned evidence: [[Evidence/EVD-004 - Phase 3 TypeScript and JavaScript verification]]
