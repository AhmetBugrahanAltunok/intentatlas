---
id: EVD-039
type: evidence
status: verified
phase: 21C
---
# Phase 21C first-run walkthrough verification

Local decision: **verified, 2026-09-11**. Every command below ran from
`var/release-21b/sdist-install`, a clean virtual environment holding only the archive-derived
candidate wheel verified in EVD-038. The development checkout was never on its path.

This is a technical walkthrough performed by the implementer. It is **not** a human pilot
observation and does not contribute to the Phase 22 gate.

## Target repository

A purpose-built Git repository, not a fixture from this project: a `src/billing` package with
`invoice.py` (`subtotal`, `apply_tax`, `total`) and `refund.py` (`refund_amount`, importing
`total`), plus `tests/test_invoice.py` and `tests/test_refund.py`. Two commits, then an
uncommitted edit that guards `total` against an empty line list.

The interesting property is that `tests/test_refund.py` never mentions `total`. It reaches the
changed symbol only through `refund.py`'s import.

## Acceptance and verification

| Acceptance | Evidence | Result |
| --- | --- | --- |
| Documented demo from a clean install | `intentatlas demo --report text` and `--report json` both returned the `rotate_session` scenario; JSON reported `schema_version 1` | passed |
| Diagnose reports readiness and a next command | `diagnose PATH`: configuration `missing`, Git `ready`, 5 files, recommended scope `worktree`, exit 0 | passed |
| The printed next command works verbatim | `changes PATH --worktree --report`, copied exactly from the **Next safe command** line, exit 0 | passed |
| Exact symbol analysis, not file fallback | `Analysis state: analyzed; freshness aligned`, `Test strategy: targeted`, `1/1 artifacts analyzed` | passed |
| A directly referencing test is ranked with its path | `tests/test_invoice.py` 80/100 medium, path `symbol:src/billing/invoice.py::total -[tested-by]-> file:tests/test_invoice.py` | passed |
| An import-chain test is reached | `tests/test_refund.py` 65/100 medium, path `symbol:…::total -[imported-by]-> file:src/billing/refund.py -[tested-by]-> file:tests/test_refund.py` | passed |
| Text and JSON agree | JSON `schema_version 1`, `analysis.state analyzed`, `test_strategy targeted`, tests `[(test_invoice.py, 80, medium), (test_refund.py, 65, medium)]` | passed |
| Nothing written to the target repository | SHA-256 of every non-`.git` file before and after: identical; no new path of any kind; `git status` unchanged | passed |
| Documented refusals hold | empty argv non-interactive exit 2; `open` without a scan exit 2 with an actionable message naming the exact `scan` command and its write effects | passed |
| EN/TR installation and recovery parity | Compared directly; see below | passed |

## The result a first-time user actually sees

```text
Analysis state: analyzed; freshness aligned
Test strategy: targeted
- file:tests/test_invoice.py: 80/100 (medium)
  Why: The test directly references an exactly modified symbol.
  Path: symbol:src/billing/invoice.py::total -[tested-by]-> file:tests/test_invoice.py
- file:tests/test_refund.py: 65/100 (medium)
  Why: The test directly targets a file that imports the exact changed symbol.
  Path: symbol:src/billing/invoice.py::total -[imported-by]-> file:src/billing/refund.py
        -[tested-by]-> file:tests/test_refund.py
```

The second item is the product's actual claim working: a test with no textual link to the change
is surfaced, with the route shown rather than asserted.

## EN/TR parity

The narrow checklist item — installation and post-failure continuation commands — **passes**.
`README.md` and `README.tr.md` carry the same venv selection block, the same
`pip install .` and `demo --report text` commands, the same activation guidance, the same
macOS/Linux fallback, and the same non-interactive recovery instruction to run
`intentatlas diagnose PATH` and copy its **Next safe command**. Only example paths are localized
(`C:\path\to\your-project` against `C:\projenizin\yolu`), which is intended.

A wider divergence exists and is recorded rather than silently corrected: `README.tr.md` has no
equivalent of the English `## What works today` or `## Core commands` sections. A Turkish reader
therefore gets no capability list and no command reference, and never sees `status`, `diff`,
`review`, `benchmark-scale`, or the `evaluate-*` commands. That is tracked in ISSUE-039, because
closing it interacts with the open question of whether the 675-line English README should be split
at all; expanding the Turkish one by roughly 130 lines would move it in the opposite direction.

## Limitations

- One platform, one interpreter, one synthetic-but-realistic Python repository. No
  JavaScript/TypeScript or Go target was exercised in this walkthrough.
- The loopback viewer was not opened here; real-browser rendering is covered separately by
  `tests/test_browser_e2e.py`.
- The implementer already knows the product. Nothing here measures whether a newcomer would
  interpret the output correctly, choose the right command, or return a second time. Those remain
  Phase 22 questions and cannot be answered from this evidence.

## Links

- proves:: [[Requirements/REQ-039 - Deliver a useful first report from a clean install]]
- reviewed-in:: [[Reviews/Phase 21C First-Run Walkthrough Review]]
- verifies:: [[Issues/ISSUE-039 - Resolve the documentation divergence decisions]]
- follows:: [[Evidence/EVD-038 - Phase 21B reproducible candidate verification]]
