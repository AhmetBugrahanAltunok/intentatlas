---
id: REQ-042
type: requirement
status: accepted
phase: 21F
---
# Make the first report readable by a newcomer

## User outcome

Someone who has never seen IntentAtlas runs one command against their repository and, from the
first line, knows what changed and which tests to run — without having learned the vocabulary
first, and without losing any of the limits that make the answer trustworthy.

## Acceptance

- The default text report opens with the changed symbol and the tests to run, not with scope,
  revisions, bands, or counts.
- Each ranked test shows a readable path, a plain-language reason, and a confidence word, with no
  graph identifier, duplicated score, signal slug, or evidence label in the default view.
- Every boundary survives the shortening: the standing advisory, the full-suite caveat when the
  strategy is not `targeted`, the count of files that could not be analysed exactly, and the count
  of weaker candidates hidden by the threshold.
- Prose wraps for a terminal; no default line exceeds 100 characters.
- `--explain` reproduces the previous detailed rendering exactly.
- `--format json` is byte-identical with and without `explain`, so no tool is affected.
- `intentatlas --help` lists only the commands a first-time user needs, and names the maintainer
  and benchmark commands in its epilog; each still runs.
- READMEs in both languages show the output the command now produces.
- The full suite, Ruff, mypy, and Bandit pass.

## Links

- drives:: [[Decisions/ADR-041 - Lead the change report with its answer]]
- proved-by:: [[Evidence/EVD-042 - Phase 21F readable first answer verification]]
- reviewed-by:: [[Reviews/Phase 21F Readable First Answer Review]]
- planned-in:: [[Brain/Alpha Release Execution Plan]]
