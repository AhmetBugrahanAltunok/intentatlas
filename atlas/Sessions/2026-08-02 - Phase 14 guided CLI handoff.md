---
id: session-2026-08-02-phase-14-guided-cli-handoff
type: session
status: active
phase: 14
---
# Phase 14 guided CLI handoff

## Baseline

- Planning began from clean synchronized `main` at
  `6679150554a513b7ab11f59e2fd1074bd9282f24` after the Phase 13 Review passed.
- No Phase 14 implementation code or test exists at this planning handoff.
- No tag, release, publication, deployment, visibility/settings change, announcement, or Phase 11C
  action is authorized by these notes.
- `atlas/Private/` was not accessed.

## Product handoff

The user-facing target is one memorable command, one visible root/scope confirmation, and at most
one Enter before the existing trustworthy report. The guide is a line-oriented progressive layer,
not a GUI, full-screen TUI, or new analysis engine.

Open these records before implementation:

- [[Brain/Phase 14 Guided CLI Strategy]]
- [[Requirements/REQ-030 - Make trustworthy analysis effortless from the CLI]]
- [[Decisions/ADR-030 - Layer a TTY-guided flow over deterministic contracts]]
- [[Issues/ISSUE-028 - Implement one-command guided CLI onboarding]]
- [[Evidence/EVD-030 - Phase 14 guided CLI verification]]
- [[Reviews/Phase 14 One-Command Guided CLI Review]]

## Architectural handoff

- Preserve `argparse`, existing explicit commands, and the no-runtime-dependency package.
- Pre-parse dispatch only empty argv plus real interactive stdin/stdout; every other path retains
  the existing parser.
- Add a separate testable onboarding module and an explicit `intentatlas guide [PATH]` route.
- Reuse structured diagnostic, ChangeSet, and `collect_change_report_context` functions directly.
  Never execute the diagnostic's display command as shell text.
- Keep one graph/ChangeReport snapshot for terminal details and optional loopback browser output.
- Do not call persistent `open` when its graph is absent; that path scans and writes.
- Do not add a TUI framework or other runtime dependency.

## Delivery order

1. 14A: session/TTY/root/scope/no-write/security foundation plus focused tests.
2. 14B: zero-argument progressive EN/TR report and semantic-parity scenarios.
3. 14C: exact-snapshot viewer opt-in, documentation, package/cross-platform/full gates, Evidence,
   Review, push, and remote CI when separately authorized.

Do not close one work package by weakening a later trust requirement. Do not mark Phase 14 passed
until EVD-030 and the Review are complete. Do not count technical transcripts or an owner dry run
as external human evidence.

## Installation and launch boundary

Current verification must use a trusted exact wheel or source checkout and remain unpublished. A
future separately approved public package may use an isolated CLI-tool installer and then the same
`intentatlas` entry point. Phase 14 adds no downloader, self-updater, or network requirement.

## Typed links

- plans:: [[Issues/ISSUE-028 - Implement one-command guided CLI onboarding]]
- strategy:: [[Brain/Phase 14 Guided CLI Strategy]]
- entry-review:: [[Reviews/Phase 13 Semantic Monorepo Foundation Review]]
