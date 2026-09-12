---
id: EVD-042
type: evidence
status: verified
phase: 21F
---
# Phase 21F readable first answer verification

Local decision: **verified, 2026-09-12**. Complete suite: **683 passed, 4 skipped**, exit **0**,
branch-enabled total coverage **88.07%**. Ruff, mypy (50 source files) and Bandit passed.

## The measurement that prompted this

The Phase 21C walkthrough proved the path works. It could not show whether the result is readable,
because the implementer already knew the model. Read as a stranger would, against the same billing
repository:

```text
Change report: worktree
Revision: base cb5023f4107d492379a0aefd180b0e7cc22d9add; head worktree
Analysis state: analyzed; freshness aligned
Minimum confidence: medium
Confidence bands: low 0-64; medium 65-84; high 85-100
Test strategy: targeted
Analysis coverage: 1/1 artifacts analyzed; 0 omitted by the 200-artifact limit; 1/1 test signals…
Requirement impacts: 0 selected / 0 candidates; 0 filtered; 0 omitted by limit; 0/0 omission…
Recommended tests: 2 selected / 2 candidates; 0 filtered; 0 omitted by limit; 0/0 omission…
- file:tests/test_invoice.py: 80/100 (medium); selected from 1 changed artifacts
  Why: The test directly references an exactly modified symbol. (symbol-structural-test, 80/100)
  Path: symbol:src/billing/invoice.py::total -[tested-by]-> file:tests/test_invoice.py
  Evidence: python-ast, python-symbol-reference
  Additional signals: 1 (inspect `tests[].reason_details` in `--format json`)
```

Nine lines of bookkeeping before anything actionable; graph addressing as the primary explanation;
the score stated twice. `intentatlas --help` listed eighteen commands, nine of them maintainer or
benchmark tools.

## The same report now

```text
Changed: total (src/billing/invoice.py)
Run 2 tests:

  tests/test_invoice.py   [medium confidence]
    The test directly references an exactly modified symbol.
    total -> tests/test_invoice.py

  tests/test_refund.py   [medium confidence]
    The test directly targets a file that imports the exact changed symbol.
    total -> src/billing/refund.py -> tests/test_refund.py

No requirement is linked to this change.

Impact and test recommendations are bounded structural evidence, not proof that an
omitted requirement is unaffected or that a suggested test is sufficient.
Full detail: --explain    Machine-readable: --format json
```

The second entry still shows what only this product can: a test with no textual link to the change,
reached through an import, with the route printed.

`intentatlas --help` now lists ten commands and names the other eight in its epilog.

## Acceptance and verification

| Acceptance | Evidence | Result |
| --- | --- | --- |
| Answer first | Regression asserts line 1 is `Changed: login (auth.py)` and line 2 is `Run 1 test:` | passed |
| No machinery in the default view | Regression asserts eleven markers are absent, including `Confidence bands:`, `80/100`, `symbol:auth.py::login`, `file:test_auth.py`, `-[tested-by]->` | passed |
| Every boundary retained | Regression asserts the advisory prose, the hidden-candidate count, and the `--explain` pointer are present | passed |
| Terminal wrapping | Regression asserts no default line exceeds 100 characters | passed |
| `--explain` reproduces the previous rendering | Regression asserts the old header, the bands line, the full identifier path, and the advisory ending | passed |
| JSON untouched | Regression asserts `render(..., "json")` is identical with and without `explain` | passed |
| Hidden commands still run | `diff --help`, `cache list`, `benchmark-scale --help` all execute | passed |
| Both languages match the output | `README.md` and `README.tr.md` examples replaced | passed |
| Quality gates | 683 passed / 4 skips, 88.07%; Ruff, mypy, Bandit | passed |

## Change inventory

- `src/intentatlas/change_report.py`: `render_change_report(..., explain=False)` dispatches to a
  new `_render_plain_text` or the unchanged rendering, now `_render_detailed_text`. Adds
  `_plain_node`, `_plain_path_text`, `_plain_symbol_location`, `_wrapped`, and `_STRATEGY_NOTE`.
- `src/intentatlas/cli.py`: `changes --explain`; `explain` threaded through `_changes`; maintainer
  commands omitted from the help listing; `COMMAND` metavar; an epilog naming the hidden commands
  and the two starting commands.
- `tests/test_change_report.py`: five regressions for the plain view, `--explain` fidelity, and
  JSON equality; three existing detail assertions now request `--explain`.
- `tests/test_change_coverage.py`, `tests/test_phase17f_evidence_integrity.py`,
  `tests/test_onboarding_walkthroughs.py`: detail assertions now request `--explain`.
- `tests/test_trust_first.py`: covers both views — the default for what a reader sees, `--explain`
  for the machinery.
- `tests/test_e2e.py`, `tests/test_guided_cli.py`: the empty-argv assertion now checks the stable
  contract rather than the metavar noun.
- `README.md`, `README.tr.md`, `docs/compatibility-policy.md`, `CHANGELOG.md`.

## A user-visible side effect

The `COMMAND` metavar changed argparse's empty-argv message from `the following arguments are
required: command` to `...: COMMAND`. Exit 2 and argparse's stderr behaviour — the documented
contract — are unchanged. Two tests asserted the exact noun; they now assert the stable part.

## Limitations

- This is a readability change measured by the implementer, not by a reader. Whether a newcomer
  now interprets the output correctly is exactly the Phase 22 question and cannot be answered here.
- The guided CLI has its own terminal projection and is untouched by this phase.
- `recommend-tests`, `impact`, `status` and `diagnose` keep their existing output shapes.

## Links

- proves:: [[Requirements/REQ-042 - Make the first report readable by a newcomer]]
- follows:: [[Decisions/ADR-041 - Lead the change report with its answer]]
- reviewed-in:: [[Reviews/Phase 21F Readable First Answer Review]]
- follows:: [[Evidence/EVD-039 - Phase 21C first-run walkthrough verification]]
