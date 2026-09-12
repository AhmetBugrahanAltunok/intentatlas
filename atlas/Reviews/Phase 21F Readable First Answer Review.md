---
id: review-phase-21f-readable-first-answer
type: review
status: passed
phase: 21F
---
# Phase 21F Readable First Answer Review

Decision: **passed, 2026-09-12**. 683 passed, 4 platform skips, exit 0, 88.07% branch-enabled total
coverage. Ruff, mypy and Bandit passed.

## What this changes and what it refuses to change

The default text report now opens with what changed and which tests to run. Nine lines of
bookkeeping moved behind `--explain`, which reproduces the previous rendering exactly. `--format
json` is byte-identical with and without the flag, and a regression asserts it.

The tempting version of this change was to shorten the output by dropping qualifiers. That was
refused. The advisory, the full-suite caveat, the count of files that could not be analysed
exactly, and the count of weaker candidates hidden by the threshold are all in the default view.
A shortening that removed them would have produced something easier to read and less safe to
believe — and for Phase 22 the dangerous failure is not a participant who gives up, it is one who
trusts a result more than the evidence supports.

## The judgement inside it

Graph identifiers are now rendered as the things they address, but only in the default view.
`symbol:src/billing/invoice.py::total` reads as `total (src/billing/invoice.py)` in the changed
line and `total` inside a route; the full identifiers stay in `--explain` and in JSON, which are
the surfaces tools and maintainers use. This is a presentation boundary, not a data change.

Eight maintainer and benchmark commands left the help listing and are named in its epilog. They
still run. Hiding them entirely would have been dishonest about what the CLI does.

## Preserved

The second ranked item in the worked example still demonstrates the product's actual claim: a test
with no textual link to the change, reached through an import, with the route printed. The
shortening did not cost the thing worth showing.

## Limits of this evidence

This is a readability change measured by the person who wrote it. It cannot establish that a
newcomer reads the output correctly — that is the Phase 22 question, and nothing here counts
toward it. The guided CLI keeps its own projection and was not touched. `recommend-tests`,
`impact`, `status` and `diagnose` keep their existing shapes, so the CLI is not yet uniform.

The `COMMAND` metavar changed argparse's empty-argv message noun. Exit 2 and argparse's stderr
behaviour are unchanged, and the two tests that asserted the exact noun now assert the contract.

## Links

- reviews:: [[Requirements/REQ-042 - Make the first report readable by a newcomer]]
- reviews:: [[Decisions/ADR-041 - Lead the change report with its answer]]
- based-on:: [[Evidence/EVD-042 - Phase 21F readable first answer verification]]
- follows:: [[Reviews/Phase 21E Vault Identity Evidence Review]]
- governed-by:: [[Brain/Phase Completion Protocol]]
