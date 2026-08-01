---
id: REQ-019
type: requirement
status: accepted
phase: 7D
---
# Ship verifiable cross-platform releases

Maintainers can prepare a reviewable IntentAtlas release whose installed user workflow works on
supported operating systems and whose exact package contents can be reproduced and inspected
before any external publication.

## Acceptance

- A subprocess end-to-end test exercises initialization, scan, status, impact, test
  recommendation, and loopback viewer retrieval through the installed package.
- CI runs that workflow from a built wheel on Linux, Windows, and macOS with Python 3.11 and 3.13.
- Repeated wheel and source builds under one fixed timestamp are byte-identical.
- Release verification checks archive safety, wheel integrity and metadata, console entry point,
  bundled web assets, MIT license bytes, and source-distribution boundaries.
- The source distribution contains buildable source, tests, documentation, and release tooling but
  excludes the Obsidian vault, benchmarks, GitHub workflows, and local IntentAtlas configuration.
- Release instructions cover versioning, complete gates, fresh installation, artifact hashes, and
  the explicit approval boundary before tagging or publication.
- Focused and complete tests, coverage, lint, security, package, CLI/UI, determinism, attribution,
  remote CI, and Obsidian closure gates pass.

## Typed links

- drives:: [[Decisions/ADR-019 - Separate reproducible verification from publication]]

## Trace

- Roadmap: [[Brain/Product Roadmap]]
- Planned evidence: [[Evidence/EVD-019 - Phase 7D release readiness verification]]
