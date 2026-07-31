---
id: ADR-005
type: decision
status: accepted
phase: 4
---
# Bounded evidence imports and canonical graph diff

## Decision

IntentAtlas will import verification reports during `scan` only from explicit paths in
`intentatlas.json`. The first built-in formats are Cobertura-compatible coverage XML and JUnit XML.
Parsing uses the Python standard library with fixed file-size and record-count limits, rejects DTD
and entity declarations, and never invokes a test runner, language runtime, shell, or network.

Evidence is aggregated per graph file rather than storing raw test cases or failure payloads.
Generated `coverage` and `test-result` nodes live in the scanner-owned `Tests/` vault area and point
to the verified file with the existing typed `proves` relation. Inputs that cannot be mapped
conservatively to one discovered project file do not create relationships.

Graph comparison is a separate pure operation over two validated graph caches. Diff schema 1 has
no generation timestamp and sorts every collection, so the same inputs produce identical JSON.
The CLI prints JSON by default, may write only below the project root, and changes its exit status
only when the caller explicitly supplies `--check`.

## Consequences

- CI systems can generate reports with their existing tools, then let IntentAtlas ingest them
  offline.
- The graph records verification facts without becoming a test execution framework.
- Aggregate evidence minimizes sensitive-data exposure and keeps graph growth bounded.
- Compiler/runtime-specific coverage formats and semantic test discovery remain future adapters.

## Trace

- driven-by:: [[Requirements/REQ-005 - Import verification evidence and compare graph changes]]
- tracked-by:: [[Issues/ISSUE-003 - Implement evidence imports and graph diff]]
