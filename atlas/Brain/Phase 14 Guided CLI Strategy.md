---
id: phase-14-guided-cli-strategy
type: memory
status: proposed
phase: 14
---
# Phase 14 Guided CLI Strategy

## Product decision

Phase 14 makes the existing trust-first change report reachable through one memorable command:

```text
intentatlas
```

This is a guided terminal flow, not a desktop application and not a full-screen TUI. It layers a
small, line-oriented interaction over the existing deterministic diagnostic, ChangeSet,
ChangeReport, and loopback-viewer contracts. It does not create a second recommendation engine.

The normal path is one command and at most one Enter before the answer. A maintainer is not asked
to know Git scope flags, revisions, confidence thresholds, graph terminology, configuration, or
vault layout before seeing value.

## Primary user job

The first job is:

> Tell me what this change may affect, which tests are supported by evidence, why, and what the
> safe test strategy is, without changing my repository or making me learn the CLI first.

The guided flow is successful only when the user can answer:

1. What repository, scope, base, and head were examined?
2. Is the result aligned, fallback, stale, or unknown?
3. Why was a requirement or test selected or omitted?
4. What test strategy should be followed?
5. What did IntentAtlas actually do: no test execution, no write, no external network, and no
   human-usability guarantee?

## Non-negotiable boundaries

- The default guided path is local, offline, bounded, and no-write.
- It never runs tests, repository code, hooks, package managers, build tools, compilers, plugins,
  or external indexers.
- It never reads, lists, records, or offers content under `atlas/Private/` or a configured Private
  boundary.
- It never opens a browser, listener, or persistent setup automatically.
- It never initializes, scans persistently, writes config/cache/graph/vault output, or stores recent
  repositories or preferences.
- It never fetches refs or guesses a base branch. Explicit range analysis remains an optional
  user choice.
- It never lowers confidence, hides ambiguity, or translates omission into “unaffected” or “test
  unnecessary.”
- It does not change the existing explicit CLI text/JSON commands or their exit meanings.
- It does not close Phase 11C or claim human usability, elapsed user time, or adoption.

## Interaction budget

### Common path

- From a repository root or nested directory: one command, one displayed project/scope
  confirmation, at most one Enter, then the report.
- From outside a repository: one project-directory question, then the same confirmation and report.
- No language, revision, confidence, output-format, browser, or setup question appears on the
  common path.

### Progressive disclosure

The first answer shows the minimum complete trust surface. Deeper evidence, omitted candidates,
another scope, JSON, the exact local browser snapshot, and existing advanced commands appear only
after the answer. Enter or `Q` exits; the user is not trapped in a menu.

## Canonical state flow

```text
TTY gate
  -> resolve one explicit or nearest Git root
  -> bounded read-only diagnostic
  -> derive a safe default scope
  -> show root, scope, and trust boundary
  -> Enter / change scope / quit
  -> collect one in-memory graph + ChangeReport snapshot
  -> render a concise truthful answer
  -> optional details / another scope / exact local viewer / command recipes / exit
```

No diagnostic `next_safe_command` string is executed as a shell command. The guide calls the
existing structured Python functions directly.

## Repository selection

1. `intentatlas` inside a Git worktree resolves only the nearest enclosing Git root.
2. `intentatlas guide PATH` accepts an explicit directory or nested directory and displays the
   canonical root it resolved.
3. If no enclosing repository exists, the guide asks for one path. It does not scan siblings,
   drives, the home directory, or a recent-project history.
4. Pasted quoted Windows paths and paths with spaces are normalized without shell evaluation.
5. A file path, missing directory, unsafe `.git`, symlink/junction escape, Private target, or
   permission failure produces an actionable retry/exit result before project scanning.
6. A non-Git directory offers another path, the original safe demo, or exit. It does not initialize
   Git or pretend that a revision-scoped report exists.

## Deterministic scope selection

The guide uses bounded Git metadata and the existing ChangeSet implementation:

1. An unmerged/conflicted worktree selects `worktree` and prominently requires the conservative
   full-suite path.
2. Any unstaged or untracked change selects `worktree`.
3. Staged changes with no unstaged or untracked change select `staged`.
4. A clean repository with a valid HEAD selects `commit HEAD`.
5. An unborn repository selects `worktree`; if it is empty, the result says that no analyzable
   change exists and offers another repository or the demo.
6. Detached HEAD is valid when the exact resolved revision is shown.
7. Monorepos keep the complete selected change set. The guide does not ask for one package and
   thereby hide possible cross-workspace effects.

The confirmation is intentionally small:

```text
Enter  Analyze the recommended scope
S      Select another scope
Q      Exit
```

The alternate-scope menu supports worktree, staged, last commit, one explicit commit, and an
explicit base/head range. It never invents a base branch.

## First screen contract

The first screen must identify the selected root and scope before expensive analysis, then state:

- local and no external network request;
- no configuration, cache, graph, vault, report file, or Git/project write;
- no project code, test, hook, plugin, or indexer execution;
- `atlas/Private/` exclusion;
- safe cancellation with Ctrl+C.

It uses plain lines, not a spinner, cursor movement, screen clearing, or a fake percentage. Long
work emits stable stages such as “checking repository,” “selecting scope,” “building local
evidence,” and “ranking requirements and tests.”

## Primary result contract

The concise result is a projection of the same immutable ChangeReport used by explicit text/JSON
and the optional viewer. It must show:

- project and selected scope;
- exact base/head revisions, with short forms only as an additional convenience;
- machine enum and plain-language meaning for analysis state and freshness;
- minimum confidence;
- changed-file count;
- selected/total/filtered/result-limit-omitted requirement counts;
- selected/total/result-limit-omitted test counts;
- selected requirement/test ID or label, score, confidence, and a concise evidence-backed reason;
- omission count and the distinction between below-threshold and result-limit omission;
- the exact test-strategy enum and a plain-language safe action;
- `Tests executed: 0`;
- the advisory that recommendations are not proof of completeness or sufficiency.

The default screen may show only the leading selected items when the result is long, but counts and
the presence of hidden/omitted items are always visible. “Details” renders every REQ-028 trust
field, including recorded evidence paths and omission reasons.

## Human-language mapping

| Canonical state/strategy | Guided meaning |
| --- | --- |
| `analyzed` + `aligned` + `targeted` | Exact structural evidence supports the listed targets; it does not prove that the subset is sufficient. |
| `fallback` + `targeted-plus-full-suite` | Start with the listed targets, then run the full suite because some links are not exact. |
| `fallback` + `full-suite-fallback` | No safe targeted set was proven; run the full suite. |
| `unknown` + `abstain-and-full-suite` | IntentAtlas abstains from targeted ranking; run the full suite. |
| `stale` | Evidence does not match the selected revision; targeted sufficiency is unavailable. |
| `no-targets-found` | No linked test was proven; never phrase this as “no tests needed.” |
| `no-changes` | The selected scope contains no changes; choose another scope or exit. |

The canonical English enum remains visible beside localized prose so users can compare terminal,
JSON, documentation, and viewer output without semantic drift.

## Post-result actions

After the answer:

```text
1  Why were these requirements and tests selected?
2  Show omitted candidates and reasons
3  Show complete scope, freshness, evidence paths, and fallback detail
4  Open this exact report in the local browser
5  Analyze another scope
6  Show reproducible text/JSON and persistent-setup commands
L  Language / Dil
Enter or Q  Exit
```

- Action 4 is itself explicit browser consent. It binds only to IPv4 loopback on an ephemeral port
  and serves the already-created snapshot; it does not rescan or write files.
- If a browser cannot be opened, the loopback URL is shown without losing the terminal result.
- Action 6 displays commands; it does not execute `init`, `scan`, `open`, a test command, or a shell
  string. Guided persistent adoption can be considered only after observed user need.

## Language and accessibility

- The initial guided copy is English and Turkish. `intentatlas guide --language en|tr` provides an
  explicit override; otherwise a supported OS locale may select the language and English is the
  fallback. No preference is persisted.
- Commands, flags, JSON fields, IDs, evidence tags, and canonical enums are never translated.
- Human copy comes from one tested message catalog so English and Turkish retain the same safety
  meaning.
- The interface is line-oriented and works with numbers/letters plus Enter. It does not require
  arrow keys, mouse input, cursor addressing, or a full-screen terminal.
- Color and symbols are optional decoration and never the only status channel. `NO_COLOR`,
  `TERM=dumb`, narrow terminals, screen readers, and non-Unicode output receive readable text.
- Repository-controlled labels, paths, revisions, and commit text are stripped or escaped for
  terminal control, ANSI, bidi-control, and newline injection before display.
- Ctrl+C cancels analysis with exit 130 and a no-write statement. `Q` or EOF exits without a stack
  trace or partial persisted result.

## TTY and automation boundary

The no-argument route starts only when argv is empty and both stdin and stdout are real interactive
terminal streams. In non-TTY, redirected, or CI use it must not consume input, scan the repository,
or wait. It preserves the existing argparse stderr and exit-2 behavior and points automation to
explicit versioned commands.

`intentatlas guide [PATH]` is the explicit interactive entry point for help, support, testing, and
language selection. It also refuses to prompt without an interactive terminal unless a narrowly
scoped test harness injects an internal terminal adapter; no public “force TTY” escape weakens CI
safety.

Explicit subcommands and versioned JSON remain the scripting interface. Guided prompt wording and
menu order are experimental before external observations; no-write, scope, revision, strategy,
omission, privacy, and exit meanings are protected compatibility semantics.

## Failure and recovery matrix

| Condition | Required behavior |
| --- | --- |
| Git unavailable | No real-repository report; show prerequisite, demo, or exit. |
| Invalid config/unsafe vault | Stop before report instead of silently replacing the config with defaults. |
| Unsupported language | Show the limitation and retain fallback/full-suite semantics. |
| Ambiguous workspace ownership | Keep the whole scope, expose ambiguity, and abstain where uniqueness is not proven. |
| Oversized/truncated/budgeted input | Show the exact bounded limitation; never silently claim complete coverage. |
| Repository changes during analysis | Mark stale/unknown and remove targeted-sufficiency wording. |
| Merge conflict | Keep worktree scope, expose conflict, and require the conservative strategy. |
| No selected test | Say that no target was proven and retain the project's normal/full test policy. |
| Port occupied | Use an ephemeral loopback port rather than asking the user to troubleshoot a default port. |
| Browser launch failure | Print the local URL and preserve the terminal report. |
| UNC/network-backed path | Do not claim the operating-system filesystem access is network-free; only claim that IntentAtlas makes no external request. |
| Hostile terminal text | Escape it before display; never emit repository-controlled control sequences. |
| Ctrl+C/EOF | Exit predictably with no partial persistent output. |

## Technical integration boundary

- Keep `argparse` and the zero-runtime-dependency package.
- Dispatch empty argv to a new `onboarding.py` only after the TTY gate; leave
  `subparsers(required=True)` and existing parser behavior intact for all other invocations.
- Add `intentatlas guide [PATH]` as an additive explicit route.
- Reuse `diagnose_repository`, `collect_change_set`, and `collect_change_report_context`.
- Hold the graph and ChangeReport as one session snapshot. Render the summary and optional browser
  bytes from that object; do not run a second scan.
- Use a small injected terminal I/O boundary so prompts, cancellation, localization, TTY behavior,
  and transcripts are testable without patching business logic.
- Do not call the current persistent `open` path when no graph exists because it scans and writes.
- Do not add Rich, curses, prompt-toolkit, questionary, a GUI toolkit, or another runtime dependency.

## Installation boundary

Phase 14 verifies a clean wheel installation but does not publish it. A trusted pilot receives one
exact wheel-install command and then runs `intentatlas`. After separately approved publication,
the intended durable installation path is an isolated CLI-tool install such as
`pipx install intentatlas`; a temporary `pipx run intentatlas` evaluation necessarily uses network
and is not the offline runtime contract. No updater or downloader is added to IntentAtlas.

## Work packages

### Phase 14A - guided contract and safe session engine

- Record REQ-030, ADR-030, ISSUE-028, EVD-030, Review, and compatibility classification.
- Add an isolated testable terminal I/O/session boundary and explicit `guide` entry point.
- Resolve safe project roots and deterministic scopes without broad discovery or writes.
- Cover TTY/non-TTY, path, Private, hostile terminal, cancellation, and no-write invariants.

### Phase 14B - zero-argument progressive answer

- Gate empty argv on real TTY while retaining every explicit command contract.
- Produce the concise bilingual answer from the existing immutable ChangeReport.
- Add strategy mappings, omissions, evidence drill-down, alternate scopes, command recipes, and
  stable line-based progress.
- Verify parity across targeted, fallback, unknown, stale, no-target, no-change, ambiguous, and
  bounded-failure cases.

### Phase 14C - exact viewer opt-in and release-quality verification

- Serve the same snapshot on explicit loopback/browser choice with an ephemeral port.
- Update English/Turkish onboarding, architecture, compatibility, observation, and release-candidate
  documentation without claiming publication.
- Run focused, full, browser, package, cross-platform, deterministic-vault, approved network, and
  remote-CI gates.
- Leave the Phase 11C five-person observation and real-time median open.

## Deliberately deferred

- Desktop application, full-screen TUI, editor integration, and shell-specific folder picker.
- Automatic `init`, `scan`, user-note creation, test execution, or persistent recent-project list.
- Hosted account, telemetry, analytics, AI/chat, self-update, or mandatory network access.
- New language, scoring, resolver, indexer, or recommendation semantics.
- Public tag, release, package publication, deployment, visibility change, or announcement.
- Any human-usability or time-to-value claim without five independent consented observations.

## Delivery links

- Requirement: [[Requirements/REQ-030 - Make trustworthy analysis effortless from the CLI]]
- Decision: [[Decisions/ADR-030 - Layer a TTY-guided flow over deterministic contracts]]
- Issue: [[Issues/ISSUE-028 - Implement one-command guided CLI onboarding]]
- Evidence: [[Evidence/EVD-030 - Phase 14 guided CLI verification]]
- Review: [[Reviews/Phase 14 One-Command Guided CLI Review]]
- Roadmap: [[Brain/Product Roadmap]]
- Entry review: [[Reviews/Phase 13 Semantic Monorepo Foundation Review]]
- Human launch gate: [[Brain/Phase 11 Strategy]]
