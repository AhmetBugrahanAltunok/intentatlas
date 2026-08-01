---
id: ADR-019
type: decision
status: accepted
phase: 7D
---
# ADR-019 — Separate reproducible verification from publication

## Context

Unit tests and one local wheel smoke check do not prove that a command-line package behaves on the
supported operating systems. A default source archive also included repository-only vault and
benchmark material that users do not need to install or inspect the Python package. Publishing
directly from CI would combine technical verification with a higher-risk external action.

## Decision

Exercise the installed wheel as a subprocess on Linux, Windows, and macOS using the oldest and
newest supported Python versions. Cover the user-visible chain from initialization and scan to
impact, recommendation, and loopback HTTP retrieval without executing scanned project code.

Create wheel and source artifacts twice under one fixed `SOURCE_DATE_EPOCH`. Require exact names
and byte-identical SHA-256 values. Validate wheel member safety, CRCs, `RECORD`, metadata, entry
point, web assets, and repository-matching MIT license bytes. Limit the source distribution to
source, tests, documentation, release tooling, and required project metadata; reject vault,
benchmark, workflow, and local configuration roots.

Keep the CI jobs verification-only. Tagging, release creation, and package-index upload remain
separate actions that require explicit approval of the recorded version and artifact hashes.

## Consequences

- Installation and viewer regressions become visible across supported operating-system families.
- Repeated-build comparison exposes accidental nondeterminism before a release is approved.
- The source archive is smaller and avoids shipping project-memory outputs unrelated to package
  installation, while retaining tests and the verifier needed for review.
- CI configuration establishes the intended matrix but the phase cannot close until those remote
  jobs actually pass after the commit is pushed.
- Fixed timestamps make artifacts reproducible for identical source and toolchain inputs; they do
  not promise equality across different build-backend versions or compression implementations.

## Links

- Requirement: REQ-019 (available through the incoming `drives` relationship)
- tracked-by:: [[Issues/ISSUE-017 - Implement open-source release gates]]
