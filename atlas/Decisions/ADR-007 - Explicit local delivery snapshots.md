---
id: ADR-007
type: decision
status: accepted
phase: 5B
---
# ADR-007 — Explicit local delivery snapshots

## Context

Direct issue-tracker connectors introduce credentials, network availability, rate limits,
provider coupling, and changing remote state. IntentAtlas needs a trustworthy offline foundation.

## Decision

Import only explicitly configured project-local JSON snapshots through a versioned,
vendor-neutral schema. Reports contain a source/repository namespace and bounded issue and pull
request records, intentionally excluding bodies, comments, review text, authors, and raw payloads.

Issue intent IDs create `tracked-by` edges. Pull requests link same-snapshot issues, exact
discovered file paths, and exact known commit SHAs through `addressed-by`, `changes`, and safe
`references` edges. Unknown references are skipped rather than guessed.

Scanner-owned notes live below `Commits/Issues/` and `Commits/Pull Requests/`, remaining inside the
generated `Commits/` area. Relation schema 2 adds invertible `addressed-by`/`addresses` semantics
and broadens `changes` to version-control delivery records.

## Consequences

- The feature is deterministic, offline, provider-neutral, testable, and credential-free.
- Users or CI remain responsible for producing the snapshot.
- Later network connectors can translate APIs into this stable schema only after separate approval.
- Relation-schema-1 graph caches require rebuilding with `intentatlas scan`.

## Links

- Requirement: REQ-007 (available through the incoming `drives` relationship)
- tracked-by:: [[Issues/ISSUE-005 - Implement local delivery imports]]
