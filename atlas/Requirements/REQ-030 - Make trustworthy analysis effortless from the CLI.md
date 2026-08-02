---
id: REQ-030
type: requirement
status: accepted
phase: 14
---
# Make trustworthy analysis effortless from the CLI

## User outcome

A maintainer runs `intentatlas` in or below a trusted Git repository and reaches a correct,
explainable change-and-test answer without learning scope flags, revisions, confidence settings,
configuration, or graph concepts first. The common path remains local, no-write, and explicit
about uncertainty.

## Acceptance

- Phase 13 has a final passing Review before implementation begins.
- Empty argv starts guided analysis only when stdin and stdout are interactive terminals. An
  additive `intentatlas guide [PATH]` route exposes the same flow explicitly.
- The common repository path requires one command and at most one Enter before the report. Outside
  a repository, the only mandatory extra input is one project-directory path.
- The nearest enclosing or explicitly supplied Git root is resolved without scanning sibling,
  home, or drive locations, persisting recent projects, evaluating shell text, or escaping a safe
  canonical boundary.
- Scope selection is deterministic: conflicts or unstaged/untracked changes use worktree; staged-
  only changes use staged; a clean repository uses exact HEAD; an unborn repository uses worktree
  and never fabricates history. A base branch is not guessed.
- Before analysis the selected root and scope plus the local/no-write/no-execution/Private boundary
  are visible. Enter accepts the recommendation; scope change and exit are immediately available.
- Diagnostic and report collection reuse the production structured paths. The guide adds no
  recommendation, resolver, confidence, freshness, or fallback rules.
- Default analysis creates or changes no config, cache, graph, vault, report, Git, or project file;
  makes no external request; and runs no test, repository code, hook, build/package tool, plugin,
  compiler, or indexer.
- The concise answer exposes exact scope/revisions, analysis state, freshness, threshold, selected/
  candidate/filtered/omitted counts, confidence, selection reason, omission meaning, safe test
  strategy, advisory limits, and `tests executed: 0` in plain language.
- Complete details retain recorded evidence paths and distinguish below-threshold omission from
  result-limit omission. No wording turns omission into proof of no impact or no testing need.
- Terminal summary, complete details, JSON command recipe, and optional browser view refer to the
  same immutable graph/report snapshot. Browser opening is an explicit choice, loopback-only, and
  does not rescan or persist state.
- English and Turkish guided copy preserve the same safety semantics. Machine enums, IDs, commands,
  flags, and versioned JSON are not translated.
- The interface is line-oriented, keyboard-complete, screen-reader-friendly, usable in narrow or
  plain terminals, independent of color/animation/cursor control, and safe against repository-
  controlled ANSI/control/bidi/newline injection.
- Ctrl+C, EOF, invalid/quoted/spaced paths, Git absence, non-Git/unborn/detached/conflicted repos,
  invalid config, unsafe paths, unsupported languages, ambiguous workspaces, stale evidence,
  oversized/truncated input, budget failures, and browser failure yield actionable results without
  a traceback or partial persisted output.
- Empty-argv non-TTY, redirected, and CI use never prompts, scans, or consumes stdin; it retains the
  established argparse stderr and exit-2 behavior. Existing explicit command text/JSON meanings,
  flags, ordering rules, and exit semantics remain compatible.
- Guided prompt layout remains an experimental human interface while no-write, scope, revision,
  privacy, omission, fallback, and exit meanings remain protected. Automation continues to use
  explicit commands and versioned JSON.
- Clean-wheel and extracted-sdist flows, Python 3.11-3.13, Windows/Linux/macOS E2E, real-browser
  opt-in, full quality/security/package/vault/provenance/remote-CI gates, and focused transcript
  scenarios pass.
- Synthetic transcripts and an owner walkthrough are recorded only as technical evidence. Phase 14
  makes no human usability or elapsed-time claim and does not satisfy the Phase 11C five-person
  launch gate.

## Typed links

- drives:: [[Decisions/ADR-030 - Layer a TTY-guided flow over deterministic contracts]]

## Trace

- Strategy: [[Brain/Phase 14 Guided CLI Strategy]]
- Roadmap: [[Brain/Product Roadmap]]
- Delivery issue: [[Issues/ISSUE-028 - Implement one-command guided CLI onboarding]]
- Planned evidence: [[Evidence/EVD-030 - Phase 14 guided CLI verification]]
- Planned review: [[Reviews/Phase 14 One-Command Guided CLI Review]]
- Entry gate: [[Reviews/Phase 13 Semantic Monorepo Foundation Review]]
