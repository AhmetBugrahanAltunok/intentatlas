---
id: REQ-034
type: requirement
status: accepted
phase: 18
---
# Harden the first-run experience from observed use

## User outcome

A first-time maintainer can understand what IntentAtlas does, install it, choose a safe analysis
scope, see which project is being analyzed, and interpret the result without reading source code or
mistaking missing evidence for proof of no impact.

## Acceptance

- The English and Turkish README openings explain the product in plain language, show the demo,
  distinguish what IntentAtlas is and is not, provide a real-repository example with expected
  output, and present the shortest supported installation path.
- Demo, read-only real-repository preview, and persistent `init`/`scan` adoption are visibly
  separate workflows with their write, network, and cache effects stated before use.
- `diagnose` selects worktree for unstaged, untracked, or conflicted changes; staged for staged-only
  changes; exact HEAD for a clean repository; and worktree for an unborn repository.
- The diagnostic shows the resolved project, recommended scope, and saved-graph Python
  symbol-to-test health without claiming that graph freshness or complete coverage was proved.
- A uniquely owned markerless Python `src/` project resolves both conventional imports and an
  explicit `src.package` import, while ambiguous ownership, modules, or symbols continue to
  abstain.
- A test that directly imports a symbol defined by a changed file outranks weak co-change evidence
  and exposes the exact file-to-symbol-to-test explanation.
- `init` adds only missing local generated-state rules to `.gitignore`, preserves existing content,
  and prevents `.intentatlas/`, `.venv-intentatlas/`, and Obsidian machine state from being added by
  a normal `git add -A`.
- `impact` and `recommend-tests` identify the project being queried; missing graph/baseline errors,
  `diff --check` exit status 1, and non-TTY guide rejection provide a concrete safe next action.
- Confidence bands, selection/omission meaning, traversal indentation, cache identifiers, saved
  artifact freshness, and command differences are documented without overstating evidence.
- Focused regressions, the complete test suite, lint, typing, security, cross-platform/package
  checks, and final pushed-head CI pass.
- Raw evaluator reports remain disposable input; accepted findings and their verification are
  retained in durable Evidence and Review notes. They are not represented as human usability
  validation.
- No telemetry, API key, hosted account, release, publication, deployment, or access to
  `atlas/Private/` is introduced.

## Links

- drives:: [[Decisions/ADR-036 - Use repository-state-aware first-run guidance]]
- tracked-by:: [[Issues/ISSUE-034 - Apply first-run observation fixes]]
- proven-by:: [[Evidence/EVD-034 - Phase 18 first-run experience hardening verification]]
- reviewed-by:: [[Reviews/Phase 18 First-Run Experience Hardening Review]]
- extends:: [[Requirements/REQ-028 - Deliver trust-first first-run value]]
- preserves:: [[Requirements/REQ-033 - Preserve recommendation integrity across supported surfaces]]
