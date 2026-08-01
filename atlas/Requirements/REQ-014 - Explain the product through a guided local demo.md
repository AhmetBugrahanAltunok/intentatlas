---
id: REQ-014
type: requirement
status: accepted
phase: 6B2B2B2A
---
# Explain the product through a guided local demo

A new user can understand IntentAtlas's Requirement → Decision → Issue → Code → Test → Evidence →
Commit value without preparing a repository, accessing the network, or reading implementation
documentation first.

## Acceptance

- `intentatlas demo` opens a small packaged graph without scanning the current directory.
- The graph is original first-party material and contains a coherent intent-to-proof chain using
  the production graph schema and relation vocabulary.
- Demo startup writes only to an automatically cleaned temporary directory, binds only to
  loopback, and uses no network service or project code.
- The viewer derives a bounded set of deterministic shortest evidence paths from the selected
  node using graph relationships, not hard-coded node IDs.
- Each path shows direction, relation, destination kind, and destination label and can focus the
  destination node.
- Path search has explicit depth, visited-node, and result limits and presents an honest empty
  state when no proof-oriented destination is reachable.
- Search, filters, direct relationships, keyboard navigation, mobile layout, and existing project
  viewer behavior remain intact.
- CLI, viewer assets, package installation, local UI, focused and complete tests, coverage, lint,
  security, determinism, and Obsidian phase gates pass.

## Scope boundary

This phase improves first-run understanding with an original local showcase. It does not claim
real-world accuracy, download public repositories, add telemetry, copy external project content,
or replace the normal `init` → `scan` → `open` workflow. Public-repository validation remains
Phase 6B2B2B2B and requires explicit network and license approval.

## Typed links

- drives:: [[Decisions/ADR-014 - Packaged first-party demo and bounded evidence paths]]

## Trace

- Roadmap: [[Brain/Product Roadmap]]
- Planned evidence: [[Evidence/EVD-014 - Phase 6B2B2B2A guided demo verification]]
