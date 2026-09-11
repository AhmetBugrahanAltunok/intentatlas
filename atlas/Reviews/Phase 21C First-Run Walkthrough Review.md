---
id: review-phase-21c-first-run-walkthrough
type: review
status: passed
phase: 21C
---
# Phase 21C First-Run Walkthrough Review

Decision: **passed, 2026-09-11**, for what this sub-phase actually claims: the verified candidate,
installed alone in a clean environment, produces a useful first report on an ordinary repository
without writing anything into it. Acceptance mapping is in EVD-039. Phase 21 stays open.

## The result that matters

On a purpose-built billing repository with an uncommitted edit to `total`, the candidate reported
`analyzed / aligned / targeted` and ranked two tests. The first directly references the changed
symbol. The second, `tests/test_refund.py`, never mentions `total` at all and was reached through
`refund.py`'s import, with the route printed:

```text
symbol:src/billing/invoice.py::total -[imported-by]-> file:src/billing/refund.py
  -[tested-by]-> file:tests/test_refund.py
```

That is the product doing the thing it exists to do, from a packaged artifact, for a repository it
had never seen. It is the strongest evidence recorded so far that the candidate is worth putting
in front of a person.

## What was verified and what was not

Verified: the documented demo, `diagnose` readiness plus a **Next safe command** that works when
copied verbatim, exact symbol analysis rather than file fallback, text/JSON agreement, complete
absence of writes into the target repository, both documented refusal paths, and EN/TR parity for
installation and recovery commands.

Not verified, and not claimed: anything about other platforms or interpreters, JavaScript/
TypeScript or Go targets, the loopback viewer in this walkthrough, and — most importantly —
anything about a real newcomer. The walkthrough was performed by the implementer, who already
knows which command to run and what the output means. It establishes that the path works, not that
it is discoverable or interpretable. Phase 22 still requires actual independent participants, and
no part of this evidence may be counted toward that gate.

## Findings

The narrow Phase 21 checklist item on EN/TR installation and recovery commands **passes on
inspection** — the two READMEs already agree command for command, so no change was needed.

A wider documentation divergence was found instead and deliberately left uncorrected: the Turkish
README carries neither the capability list nor the command reference that the English one does.
Translating roughly 130 lines would resolve it, but would also work against the open question of
whether the 675-line English README should be split for the Phase 22 time target. Both, plus the
ADR-034 governance decision, are recorded together in ISSUE-039 as owner decisions.

## Remaining Phase 21 gates

The supported platform matrix (ISSUE-038, needs a push), the Phase 18/19/20 release inventory
reconciliation, and the three ISSUE-039 decisions.

## Links

- reviews:: [[Requirements/REQ-039 - Deliver a useful first report from a clean install]]
- reviews:: [[Issues/ISSUE-039 - Resolve the documentation divergence decisions]]
- based-on:: [[Evidence/EVD-039 - Phase 21C first-run walkthrough verification]]
- follows:: [[Reviews/Phase 21B Reproducible Candidate Review]]
- governed-by:: [[Brain/Phase Completion Protocol]]
