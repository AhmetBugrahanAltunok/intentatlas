---
id: REQ-005
type: requirement
status: accepted
phase: 4
---
# Import verification evidence and compare graph changes

A developer can attach existing coverage and test-result reports to the intent graph and compare
the current graph with a baseline in CI, without IntentAtlas executing project code or requiring
network access.

## Acceptance

- Only explicitly configured, project-local Cobertura coverage XML and JUnit XML reports are read.
- Report paths remain inside the project and never enter `atlas/Private/`; missing, oversized,
  entity-bearing, or malformed reports fail safely with clear errors.
- Coverage and test results are aggregated per existing repository file and persist only bounded
  counts, status, duration, relative source path, and format metadata.
- Raw failure output, test output, source contents, secrets, and absolute paths are never persisted.
- Imported evidence uses deterministic IDs and typed `proves` relationships with explicit
  provenance.
- A versioned, timestamp-free graph diff reports sorted node additions, removals, changes, and edge
  additions/removals.
- The CLI can print or safely write the diff and optionally return a non-zero CI check result when
  changes exist.
- Repeated imports and diffs over identical inputs are byte-for-byte deterministic.
- CLI, generated Obsidian notes, packaged installation, and local viewer expose the new evidence.

## Typed links

- drives:: [[Decisions/ADR-005 - Bounded evidence imports and canonical graph diff]]

## Trace

- Roadmap: [[Brain/Product Roadmap]]
- Planned evidence: [[Evidence/EVD-005 - Phase 4 evidence import and graph diff verification]]
