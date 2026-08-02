---
id: ISSUE-028
type: issue
status: closed
phase: 14
---
# Implement one-command guided CLI onboarding

Deliver a dependency-free, zero-argument guided terminal route to the existing no-write diagnostic
and ChangeReport without changing recommendation semantics or automation contracts.

## Entry condition

- [x] [[Reviews/Phase 13 Semantic Monorepo Foundation Review]] records a final pass.
- [x] REQ-030 and ADR-030 define the interaction, safety, compatibility, and evidence boundary.
- [x] Confirm a clean synchronized starting revision and record it in EVD-030 before code changes.

## Work package 14A - guided contract and safe session engine

- [x] Add an isolated onboarding/session module with injected terminal I/O and centralized EN/TR
      human-copy catalogs; add no runtime dependency.
- [x] Add explicit `intentatlas guide [PATH]` and retain every existing parser route and output.
- [x] Resolve one explicit or nearest Git root without broad filesystem discovery, history, shell
      evaluation, unsafe symlink/junction traversal, or Private access.
- [x] Select conflict/worktree/staged/HEAD/unborn scopes deterministically from bounded Git metadata
      and expose alternate explicit scope selection without guessing a base branch.
- [x] Add line-oriented progress, cancellation, terminal sanitization, path normalization, narrow-
      terminal, encoding, `NO_COLOR`, `TERM=dumb`, EOF, and error recovery contracts.
- [x] Prove that no default guided operation writes, makes an external request, or executes project
      code, tests, hooks, tools, plugins, or indexers.

## Work package 14B - zero-argument progressive report

- [x] Route empty argv to the guide only for interactive stdin/stdout; preserve non-TTY/redirected/
      CI argparse stderr, exit 2, no-scan, no-read, and no-wait behavior.
- [x] Show canonical root, safe default scope, and trust statement before at most one Enter.
- [x] Build one production graph/ChangeReport context and render the concise guided answer without
      duplicate scoring, resolving, freshness, fallback, or omission logic.
- [x] Expose exact revision/scope, state/freshness, threshold, counts, score/confidence/reasons,
      omissions, strategy, advisory, and `tests executed: 0` with plain-language mappings.
- [x] Add progressive evidence paths, omitted-candidate reasons, alternate scopes, reproducible
      explicit text/JSON commands, language switching, and immediate safe exit.
- [x] Lock semantic parity for targeted, targeted-plus-full-suite, full-suite-fallback,
      abstain-and-full-suite, no-targets-found, no-changes, stale, ambiguous, and bounded failures.

## Work package 14C - exact viewer opt-in and release-quality closure

- [x] Open the already-created snapshot only after explicit selection, on IPv4 loopback and an
      ephemeral port, with existing Host/header/escaping/accessibility/bounded-query controls.
- [x] Keep persistent `init`, `scan`, `open`, test execution, shell evaluation, and automatic browser
      behavior out of the guide; provide commands only after the first answer.
- [x] Update README/README.tr, quick start, trust-first preview, observation guide, architecture,
      compatibility policy, changelog, and release/package inclusion checks.
- [x] Add focused transcripts, real PTY/non-TTY checks where available, clean-installed-wheel E2E,
      extracted-sdist, Windows/Linux/macOS, Python 3.11-3.13, real-browser, and hostile-input gates.
- [x] Complete full test/coverage/lint/type/security/package/vault/provenance/approved-network/remote-
      CI evidence without publishing or claiming human usability.

## Closure

- [x] Add exact Code and Test links only after implementation artifacts exist.
- [x] Record the complete behavior/document/config/test inventory and exact commands/results in
      EVD-030.
- [x] Prove two-pass generated-vault determinism, unchanged user-owned material, zero orphans, and
      REQ -> ADR -> ISSUE -> Code/Test -> EVD -> Commit links without Private access.
- [x] Bind evidence to exact implementation and closure commits and obtain a final Review decision.
- [x] Keep Phase 11C pending unless its independent human evidence is separately supplied.

## Non-goals

- No desktop application, full-screen TUI, editor integration, or shell-specific folder chooser.
- No automatic persistent setup, project/test/tool execution, recent-project history, or user
  preference file.
- No new language, evidence importer, scoring, resolver, recommendation, hosted, telemetry, AI/chat,
  or mandatory-network behavior.
- No tag, release, publication, deployment, visibility/settings change, announcement, or human-time
  claim.

## Typed links

- implements:: [[Requirements/REQ-030 - Make trustworthy analysis effortless from the CLI]]
- decided-by:: [[Decisions/ADR-030 - Layer a TTY-guided flow over deterministic contracts]]
- planned-evidence:: [[Evidence/EVD-030 - Phase 14 guided CLI verification]]
- reviewed-by:: [[Reviews/Phase 14 One-Command Guided CLI Review]]
- implemented-by:: [[Code/src - intentatlas - onboarding.py|src/intentatlas/onboarding.py]]
- implemented-by:: [[Code/src - intentatlas - cli.py|src/intentatlas/cli.py]]
- tested-by:: [[Tests/tests - test_guided_cli.py|tests/test_guided_cli.py]]
- tested-by:: [[Tests/tests - test_e2e.py|tests/test_e2e.py]]
- tested-by:: [[Tests/tests - test_release.py|tests/test_release.py]]

## Planning links

- Strategy: [[Brain/Phase 14 Guided CLI Strategy]]
- Handoff: [[Sessions/2026-08-02 - Phase 14 guided CLI handoff]]
