---
id: ADR-036
type: decision
status: accepted
phase: 18
---
# ADR-036 - Use repository-state-aware first-run guidance

## Context

First-run walkthroughs confirmed that installation and the packaged demo were fast, but exposed a
gap between demo evidence and a minimal real Python project. An explicit
`from src.auth import rotate_session` test did not form the exact symbol-to-test link shown by the
demo, so the relevant and unrelated tests could be presented with the same weak co-change score.
The same walkthroughs found that a new user could accidentally stage generated state, could not
always tell which project a graph command used, and received insufficient guidance for Git scope,
missing artifacts, `diff --check`, or a non-interactive terminal.

The README also described individual commands without giving a beginner one clear decision table
for demo, local preview, public acquisition, and persistent adoption. Raw readiness labels could
be read as proof that semantic links were complete or fresh when they were only bounded checks.

## Decision

Keep the trust-first, offline-first architecture and improve its guidance rather than introducing
automatic execution or hidden state changes.

- Derive the diagnostic's recommended change scope from bounded Git metadata. Ignore generated
  IntentAtlas state and `atlas/Private/`; prefer worktree when inspection is incomplete.
- Report project identity and saved-graph symbol-to-test health separately from readiness and
  freshness. Exact-link health is an observation about the saved graph, not proof of completeness.
- For uniquely owned markerless Python `src/` layouts, register both the stripped module identity
  and explicit `src.` identity. Keep owner/module/symbol ambiguity fail-closed.
- When recommending tests for a changed file, prefer an exact file-to-defined-symbol-to-test edge
  over file-level convention or co-change evidence and retain its bounded path.
- Make `init` append a deterministic, idempotent `.gitignore` block for local generated state while
  preserving existing user content and line endings.
- Make command failures actionable: include the project, distinguish missing graph from missing
  baseline, explain exit status 1 from `diff --check`, and provide explicit non-TTY commands.
- Treat the README as the primary beginner contract: show the original demo GIF, shortest install,
  plain-language boundaries, a real example and expected output, and a command-choice table.
- Preserve schema versions and stable explicit CLI contracts; additions to diagnostic and
  recommendation JSON are additive.

## Consequences

- First-run advice follows the repository's actual Git state without executing project code.
- Markerless projects using either `auth` or `src.auth` can form exact links when ownership is
  unique, while ambiguity still reduces recall rather than inventing evidence.
- Persistent initialization writes one additional user-visible file, `.gitignore`, but only with
  missing safe defaults and only after the user explicitly chooses `init`.
- Diagnostic output becomes more useful but remains explicitly limited: saved graph freshness and
  full test coverage are not established.
- Documentation and tests must remain portable across Windows command quoting and POSIX shell
  quoting.

## Links

- driven-by:: [[Requirements/REQ-034 - Harden the first-run experience from observed use]]
- tracked-by:: [[Issues/ISSUE-034 - Apply first-run observation fixes]]
- verifies-with:: [[Evidence/EVD-034 - Phase 18 first-run experience hardening verification]]
- extends:: [[Decisions/ADR-028 - Make the change report the primary product surface]]
- extends:: [[Decisions/ADR-030 - Layer a TTY-guided flow over deterministic contracts]]
- preserves:: [[Decisions/ADR-033 - Canonicalize confidence and conservative Python resolution]]
