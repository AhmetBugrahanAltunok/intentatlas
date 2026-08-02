---
id: phase-15-source-to-atlas-strategy
type: memory
status: active
phase: 15
---
# Phase 15 Source-to-Atlas Strategy

## Outcome

After an isolated CLI-tool installation, one guided source input opens the existing trustworthy
IntentAtlas analysis for either a local Git directory or an explicit public GitHub repository URL.
The terminal keeps ChangeReport as the trust answer and makes the same immutable graph/report
snapshot's existing loopback viewer the prominent exploration action.

## Delivery order

1. **15A — isolated global-command readiness:** validate exact-wheel install, reinstall/upgrade,
   clean-shell command discovery, help/version/guide, and uninstall in temporary pipx roots.
2. **15B — safe public acquisition:** strictly normalize one GitHub repository URL, acquire it with
   inert Git settings into a bounded atomic managed cache, and expose safe cache inspection/removal.
3. **15C — source-to-atlas integration:** connect local and acquired roots to the existing
   diagnostic, scanner, ChangeReport, terminal projection, and viewer snapshot.

## Trust boundaries

- Local sources stay offline and no-write.
- Remote acquisition requires one explicit consent that names network and managed-cache writes.
- Only `https://github.com/<owner>/<repo>[.git]` is accepted. No authentication, token, API,
  private repository, redirect, submodule, LFS smudge, hook, filter, plugin, package manager,
  compiler, project code, or interactive Git prompt is allowed.
- A validated full revision, shallow-history boundary, file/byte/disk/output/time budgets, cache
  identity, cache hit/freshness, and omissions remain visible.
- `atlas/Private/` is never checked out, read, listed, scanned, indexed, cached as metadata, or
  served. Repository text is untrusted and passes the Phase 14 terminal sanitizer.
- Intent layers are reported only when present. Missing Requirement/Decision/Issue/Evidence layers
  remain explicit zeros; they are never inferred from code or Git history.
- No new scanner, graph, resolver, score, recommendation, viewer, runtime dependency, updater,
  telemetry, hosted service, or publication channel is introduced.

## Installation truth

`pipx install intentatlas` is the canonical future public command only after a package publication
exists and pipx is already installed. Phase 15 verifies exact local candidate wheels in isolated
temporary pipx roots; it does not publish to PyPI, winget, Homebrew, or any other channel and does
not provide a zero-prerequisite Windows installer.

## Human-validation boundary

Automated transcripts, owner walkthroughs, clean-shell tests, and public-repository smoke tests are
technical evidence only. Phase 11C remains owner-controlled and unopened.

## Delivery links

- Requirement: [[Requirements/REQ-031 - Open a trustworthy atlas from a local path or public GitHub URL]]
- Decision: [[Decisions/ADR-031 - Acquire explicit public repositories into a managed local cache]]
- Issue: [[Issues/ISSUE-029 - Implement frictionless source-to-atlas onboarding]]
- Evidence: [[Evidence/EVD-031 - Phase 15 source-to-atlas verification]]
- Review: [[Reviews/Phase 15 Source-to-Atlas Review]]
- Session: [[Sessions/2026-08-03 - Phase 15 source-to-atlas handoff]]
