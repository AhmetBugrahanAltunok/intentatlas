---
id: ADR-041
type: decision
status: accepted
phase: 21F
---
# Lead the change report with its answer

## Context

Phase 22 puts the product in front of five people who have never seen it. A technical walkthrough
in Phase 21C established that the path works; it said nothing about whether a newcomer can read the
result, because the implementer already knew what every line meant.

Read as a stranger would, the default report opened with nine lines of bookkeeping — scope,
revision SHAs, analysis state, minimum confidence, confidence bands, test strategy, analysis
coverage with two limit counts, requirement selection with four counts, test selection with four
more — before the first actionable line. Each ranked item then carried a raw graph identifier
(`file:tests/test_invoice.py`), a duplicated score (`80/100 (medium)` plus
`(symbol-structural-test, 80/100)`), a path in internal addressing
(`symbol:…::total -[tested-by]-> file:…`), internal evidence labels, and a pointer to a JSON field.

`intentatlas --help` listed eighteen commands, nine of which are maintainer or benchmark tools
that a first-time user has no reason to run.

None of this is wrong. All of it is precise, and the precision is the product. It is ordered for
someone who already knows the model.

## Decision

The default text rendering of a Change Report leads with the answer and keeps every boundary that
qualifies it. In order: what changed, which tests to run with a plain reason and a readable route,
the full-suite caveat when the strategy is not `targeted`, affected requirements or their explicit
absence, files that could not be analysed exactly, how many weaker candidates were hidden by the
threshold, the standing advisory, and a pointer to more.

Nothing is deleted. `--explain` renders exactly the previous output, byte for byte. `--format json`
is untouched, and a regression asserts the JSON is identical with and without `explain`.

Graph identifiers are rendered as the things they address in the default view only:
`symbol:src/billing/invoice.py::total` becomes `total (src/billing/invoice.py)` in the changed
line and `total` inside a route. The full identifiers remain in `--explain` and in JSON, which are
the surfaces tools and maintainers use.

Maintainer and benchmark commands — `cache`, `review`, `diff`, `benchmark-scale`, and the four
`evaluate-*` commands — are omitted from the help listing and named in its epilog instead. They
keep working unchanged.

## Consequences

- A first-time reader sees an answer on the first line instead of the ninth.
- The honesty survives the shortening: the advisory, the full-suite caveat, the
  could-not-be-analysed count, and the hidden-candidate count are all in the default view. A
  shortening that dropped them would have removed the reason to trust the answer.
- The default text output changed shape. Anything parsing it breaks, which is why `--format json`
  exists and is documented as the stable surface; the compatibility policy records the change.
- Tests that assert the detailed contract now pass `--explain`, which makes explicit which
  surface each one was actually testing.
- `--help` no longer advertises everything the CLI can do. The epilog keeps the rest discoverable
  rather than hidden.

## Links

- implements:: [[Requirements/REQ-042 - Make the first report readable by a newcomer]]
- refines:: [[Decisions/ADR-028 - Make the change report the primary product surface]]
- recorded-in:: [[Evidence/EVD-042 - Phase 21F readable first answer verification]]
