---
id: ADR-043
type: decision
status: accepted
phase: 21H
---
# Split the READMEs at the first-run boundary

## Context

ISSUE-039 held two interacting documentation questions. `README.md` was 696 lines, of which 500
were reference material competing with the first-run path; the Phase 22 gate counts reading time
against a newcomer. `README.tr.md` was 559 lines and lacked the English capability list, so a
Turkish reader got less. Expanding the Turkish file before deciding the split would have had to be
undone, which is why they were held together.

A third fact shaped the answer: the Turkish README carried 393 lines of its own detail — workflows
and a capability inventory — that the English README kept in different sections. Moving only the
English detail to `docs/` would have silently cost Turkish readers content they already had.

## Decision

Both READMEs stop at the first-run boundary and carry the same seven sections: what it is, the
two-minute demo, a real-repository example, what it is and is not, what works today, beta status,
and choosing your first command — then a documentation table.

Reference material moves to `docs/`:

- `commands.md` — the full command reference, including the maintainer and benchmark commands that
  `intentatlas --help` no longer lists.
- `workflows.md` / `workflows.tr.md` — the guided flow, public GitHub analysis, the packaged demo,
  the zero-footprint expert preview, and adopting the persistent vault.
- `capabilities.md` / `capabilities.tr.md` — what each adapter and importer covers and where it
  abstains.

The Turkish detail is relocated, not dropped. `workflows.tr.md` and `capabilities.tr.md` are the
existing Turkish text moved verbatim, so no translation debt is created and no reader loses
material. The command reference stays English-only and says so; it is the one surface where
duplication would cost more than it returns.

`README.tr.md` gains a translated `Bugün ne çalışıyor`, which closes the original divergence.

Two things stay in both READMEs because a first-time reader needs them where the output is:
the confidence legend, since the example output shows `[medium confidence]` and a reader cannot
interpret it otherwise, and the safe command order — demo before diagnose before changes before
init — which the trust-first regression checks.

## Consequences

- `README.md` 696 to 242 lines, `README.tr.md` 559 to 238. Both now have identical structure.
- Turkish and English parity is a maintenance commitment for `workflows` and `capabilities`. A
  change to one must change the other or the pair diverges again, which is the failure this
  decision was made to correct.
- Three regressions that asserted on README content needed attention. Two were location changes
  and now read the file the content moved to; the third caught a real regression — the confidence
  legend had left the READMEs — and was fixed by restoring it rather than by moving the assertion.
- GitHub's landing page no longer shows the full capability inventory. That was a deliberate
  trade for the Phase 22 reading-time target.

## Links

- implements:: [[Requirements/REQ-044 - Stop both READMEs at the first-run boundary]]
- recorded-in:: [[Evidence/EVD-044 - Phase 21H documentation split verification]]
- refines:: [[Decisions/ADR-041 - Lead the change report with its answer]]
