---
id: session-2026-09-11-phase-21c
type: session
status: active
---
# Phase 21C first-run walkthrough

## Objective

The owner granted network approval and asked for continued autonomous delivery. This session
closed the network-gated checks from ISSUE-038, retired the Phase 21B build deviation, and then
verified the first-run path end to end from the packaged candidate.

## Current state

**Phase 21C is complete. Phase 21B's condition is down to one item. Phase 21 remains open.**
`atlas/Private/` was not read, indexed, or modified.

Phase 21 checklist: five of nine items closed. Remaining are the Phase 18/19/20 inventory split,
the supported platform matrix, the ADR-034 governance decision, and the final release-candidate
inventory record.

## Completed this session

- **pipx lifecycle** — `verify_pipx_install.py` exit 0 against the verified wheel. The earlier
  offline failure was pipx bootstrapping its own shared libraries, exactly as suspected.
- **Dependency audit** — `pip_audit --skip-editable`: no known vulnerabilities, exit 0.
- **Build deviation retired** — two runs of the documented isolated `python -m build` produced
  digests identical to the earlier `--no-isolation` pair. The shortcut is now confirmed
  equivalent for this toolchain rather than merely argued to be. The same digests also hold at
  `ecbcc8ca` and `06701d3`, which differ only under `atlas/`, so vault-only commits provably
  cannot change the candidate bytes.
- **First-run walkthrough** — from `var/release-21b/sdist-install`, a clean environment holding
  only the candidate wheel, against a purpose-built billing repository it had never seen:

```text
diagnose  -> configuration missing, Git ready, recommended scope worktree, exit 0
            Next safe command: intentatlas changes PATH --worktree --report
changes   -> analyzed / aligned / targeted
            tests/test_invoice.py 80 medium  (direct symbol reference)
            tests/test_refund.py  65 medium  (reached only through refund.py's import)
after     -> every file byte-identical; no config, vault, graph or cache path created
```

- **EN/TR parity** — verified by inspection; installation and recovery commands already matched
  exactly, so no change was needed.

## Findings recorded, not corrected

- `README.tr.md` lacks the English `## What works today` and `## Core commands` sections, so a
  Turkish reader gets no capability list or command reference. Translating roughly 130 lines would
  fix it but would work against the open question of splitting the 675-line English README.
- Both, plus the ADR-034 generated-vault governance choice, are grouped in
  [[Issues/ISSUE-039 - Resolve the documentation divergence decisions]] because deciding them
  separately would create work that has to be undone.

## Next action

The highest-value remaining work is no longer technical. Phase 21's open items are one push away
(platform matrix), one bookkeeping pass (release inventory), and three owner decisions. The
product itself has now demonstrated its core claim from a packaged artifact on an unseen
repository.

Concretely, in order:

1. Owner decides ISSUE-039. Nothing else should touch the READMEs until then.
2. Owner approves a push, which unblocks the platform matrix and with it the last Phase 21B
   condition.
3. Reconcile the Phase 18/19/20 change inventory and record the release-candidate inventory,
   closing Phase 21.
4. Phase 22 needs five independent people. No technical work substitutes for it, and nothing
   recorded in Phase 21A-C may be counted toward it.

No push, publication, upload, or human pilot result is claimed.

## Links

- [[Requirements/REQ-039 - Deliver a useful first report from a clean install]]
- [[Issues/ISSUE-039 - Resolve the documentation divergence decisions]]
- [[Evidence/EVD-039 - Phase 21C first-run walkthrough verification]]
- [[Reviews/Phase 21C First-Run Walkthrough Review]]
- [[Issues/ISSUE-038 - Close the network-gated release checks]]
- [[Sessions/2026-09-11 - Phase 21B reproducible candidate]]
- [[Brain/Alpha Release Execution Plan]]
