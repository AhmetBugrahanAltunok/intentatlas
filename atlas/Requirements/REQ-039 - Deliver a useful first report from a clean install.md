---
id: REQ-039
type: requirement
status: accepted
phase: 21C
---
# Deliver a useful first report from a clean install

## User outcome

Someone who installs the candidate and has never used IntentAtlas can point it at their own
repository and get a report they can act on, without the development checkout, without writing
anything into their project, and without having to guess the next command.

## Acceptance

- A clean environment holding only the candidate wheel runs the documented two-minute demo.
- `diagnose PATH` on an unconfigured repository reports readiness and prints an exact
  **Next safe command** that runs successfully when copied verbatim.
- That command produces exact changed-symbol analysis and ranked tests with visible evidence
  paths, not just a file-level fallback, on an ordinary repository with real history.
- The report reaches a test that is only connected through an import chain, since that is the
  relationship a person cannot easily see for themselves.
- Text and JSON renderings of the same report agree on state, strategy, and every ranked test.
- After the full walkthrough the target repository is byte-identical, with no configuration,
  vault, graph, or cache path created anywhere in it.
- Documented refusals hold from the same install: non-interactive empty argv exits 2, and `open`
  without a prior scan refuses with an actionable message and a non-zero exit.
- Installation and post-failure recovery instructions are identical in English and Turkish.

## Links

- proven-by:: [[Evidence/EVD-039 - Phase 21C first-run walkthrough verification]]
- reviewed-by:: [[Reviews/Phase 21C First-Run Walkthrough Review]]
- tracked-by:: [[Issues/ISSUE-039 - Resolve the documentation divergence decisions]]
- extends:: [[Requirements/REQ-038 - Produce a reproducible independently installable candidate]]
- planned-in:: [[Brain/Alpha Release Execution Plan]]
