---
id: ADR-030
type: decision
status: accepted
phase: 14
---
# ADR-030 - Layer a TTY-guided flow over deterministic contracts

## Context

Phase 12 made a no-write ChangeReport the primary real-repository answer, and Phase 13 made that
answer more precise and bounded for workspaces and large graphs. Reaching it still requires a new
user to combine `diagnose`, a path, one of four Git scopes, `--report`, and optionally `--open` or
`--format json`. Empty `intentatlas` currently produces a required-subcommand error.

The package has no runtime dependency and supports Windows, Linux, and macOS. A full-screen TUI,
GUI, or prompt framework would enlarge the dependency and terminal-compatibility boundary without
improving the underlying evidence. Automatically initializing, scanning, running tests, or opening
the browser would weaken the trust-first first-run contract.

## Decision

Add a small guided session in a separate onboarding module. Before argparse parsing, route empty
argv to that session only when both stdin and stdout are real interactive terminals. Retain the
existing required-subcommand parser for every non-interactive or explicit invocation. Add
`intentatlas guide [PATH]` as an explicit interactive route.

Use a line-oriented, dependency-free terminal adapter with injected input/output for tests. Do not
use curses, full-screen redraws, cursor addressing, mandatory color, arrow-only selection, or a new
runtime package. Provide English and Turkish human-copy catalogs while retaining canonical enums,
IDs, flags, commands, and JSON names.

Resolve only the explicit path or nearest enclosing Git root. Derive the default scope from bounded
Git metadata: conflicts and unstaged/untracked changes select worktree, staged-only changes select
staged, clean repositories select exact HEAD, and unborn repositories select worktree. Show the
root and scope before one Enter accepts analysis. Never guess a merge base or branch comparison.

Call the existing structured diagnostic, ChangeSet, and `collect_change_report_context` paths.
Hold one graph and ChangeReport snapshot for the session. Render the concise terminal answer,
complete details, and optional loopback viewer bytes from that snapshot. Do not execute a
diagnostic command string or re-run analysis when the viewer is selected.

The first result is a progressive projection, not a replacement schema. It foregrounds revision,
scope, state, freshness, threshold, counts, selection/omission meaning, strategy, advisory, and the
fact that zero tests were run. Details preserve every REQ-028 trust field and evidence path.

Browser use requires an explicit post-result selection, binds to IPv4 loopback with an ephemeral
port, and keeps the existing Host/header/escaping/bounded-query controls. Persistent adoption is
shown only as reproducible command recipes. The guide does not execute `init`, `scan`, persistent
`open`, tests, or any shell text.

Classify the stable explicit command/JSON contracts separately from the guided presentation. The
no-write, privacy, scope, revision, omission, fallback, and exit meanings are protected. Prompt
copy, wrapping, and menu order remain experimental until external human observation justifies
stabilizing them. Scripts must use explicit commands rather than interactive transcripts.

## Consequences

- A new maintainer reaches the product's primary answer with one memorable command and minimal
  domain knowledge.
- Existing automation and explicit CLI consumers retain their stable interface and do not hang on
  prompts.
- Standard-library, line-oriented output reduces packaging, accessibility, screen-reader, terminal,
  and supply-chain risk compared with a full TUI.
- Scope selection becomes convenient without becoming implicit: the selected root and scope remain
  visible and changeable before analysis.
- A dedicated onboarding state machine, message catalog, terminal sanitizer, and PTY/non-TTY tests
  add code and documentation that must remain semantically aligned with ChangeReport.
- Guided persistent setup is deliberately deferred; observed demand can justify it without putting
  writes on the first-value path.
- Technical walkthroughs can close Phase 14, but only independent human observations can validate
  usability or the Phase 11C time claim.

## Links

- Requirement: REQ-030 (available through the incoming `drives` relationship)
- tracked-by:: [[Issues/ISSUE-028 - Implement one-command guided CLI onboarding]]
- Trust-first decision: [[Decisions/ADR-028 - Make the change report the primary product surface]]
- Strategy: [[Brain/Phase 14 Guided CLI Strategy]]
