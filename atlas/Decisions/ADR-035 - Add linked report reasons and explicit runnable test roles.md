---
id: ADR-035
type: decision
status: accepted
phase: 17F
---
# Add linked report reasons and explicit runnable test roles

## Context

ChangeReport schema 1 aggregated recommendation summaries, paths, and evidence into three separately
sorted collections. That preserved values but destroyed their relationship and could display a weak
re-export path beside an 80-point direct-reference score. Separately, file location made every
Python file below `tests/` a graph test and therefore a runnable recommendation, including typing
fixtures and support modules.

## Decision

Add bounded `reason_details` and `primary_reason` records with linked `signal`, `score`, `summary`,
`path`, and `evidence`. The primary record is deterministically first and its score equals the
candidate score. Retain schema-1 `reasons`, `paths`, and `evidence` as deprecated aggregate views;
do not remove or reinterpret them. Omitted candidates retain legacy `reason` as the selection
reason, add explicit `selection_reason`, and carry ranking reason records separately. These changes
are additive and require no schema bump or migration.

Keep Python files in test-shaped locations as graph test artifacts, but annotate a separate role.
Default pytest-compatible runnable filenames are bounded patterns; a safely parsed project
`python_files` declaration may replace them. `conftest.py`, package markers, and unmatched Python
files are support artifacts and are not direct runnable recommendations. Existing graphs without
role metadata and non-Python adapters retain their prior behavior. Ambiguous or unsupported custom
patterns abstain rather than guessing.

Low confidence remains an explicit discovery surface that can have high fan-out and low precision.
Medium or higher is recommended for automated CI selection. High remains reserved for stronger
evidence such as a test directly present in the changed set; an exact static symbol reference
remains 80/medium.

## Consequences

- ChangeReport schema 1 gains only additive fields; legacy consumers continue to work.
- Human surfaces can no longer detach the displayed path/evidence from the score-producing reason.
- Python support files remain inspectable in the graph without being presented as commands to run.
- Custom runner semantics outside safely supported filename declarations remain an explicit recall
  boundary.

## Links

- requirement:: [[Requirements/REQ-033 - Preserve recommendation integrity across supported surfaces]]
- tracked-by:: [[Issues/ISSUE-033 - Correct evidence presentation and runnable test integrity]]
- evidence:: [[Evidence/EVD-033 - Phase 17 recommendation integrity verification]]
