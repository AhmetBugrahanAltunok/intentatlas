---
id: REQ-007
type: requirement
status: accepted
phase: 5B
---
# Import local delivery context

A developer can connect explicitly exported issue and pull-request metadata to project intent,
files, and known commits without granting network access or persisting discussion bodies.

## Acceptance

- Configuration accepts a bounded list of project-relative delivery JSON reports.
- A versioned vendor-neutral schema creates deterministic delivery-issue and pull-request nodes.
- Requirement/decision IDs link to issues, issues link to pull requests, pull requests link to
  exact discovered files, and exact known commit SHAs link when present.
- Missing or ambiguous references are omitted instead of guessed.
- Reports outside the project, under `atlas/Private/`, symbolic links, oversized inputs, duplicate
  keys, unknown fields, unsafe URLs, invalid records, and excessive records/links fail safely.
- Only bounded titles, states, labels, safe URLs, identifiers, source/repository names, draft state,
  and relative report provenance are retained; bodies, comments, authors, logs, and tokens are not.
- Generated Obsidian notes, CLI traversal, and the local viewer expose delivery context.
- Repeated scans are deterministic and require no network access or API key.

## Typed links

- drives:: [[Decisions/ADR-007 - Explicit local delivery snapshots]]

## Trace

- Roadmap: [[Brain/Product Roadmap]]
- Planned evidence: [[Evidence/EVD-007 - Phase 5B local delivery verification]]
