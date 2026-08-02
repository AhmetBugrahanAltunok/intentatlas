---
id: REQ-027
type: requirement
status: proposed
phase: 11B
---
# Establish longitudinal recommendation evidence

Maintainers can judge whether IntentAtlas recommendations are useful across independent repository
histories from frozen, reproducible, cohort-specific evidence instead of a small curated demo or a
single aggregate accuracy number.

## User outcome

A maintainer sees how often the product recommends, abstains, falls back to the full suite, includes
an irrelevant test, or misses a labeled relevant test. Results identify their repository, language,
revision, evidence state, and limitations without persisting third-party source.

## Acceptance

- Phase 11A has a final passing Review before any Phase 11B implementation begins.
- A strict versioned pilot manifest identifies every repository by license-reviewed metadata and
  immutable revision; acquisition remains a separate approval-gated operation.
- The evaluated corpus contains at least eight independently reviewed repositories and sixty
  chronologically ordered change cases, with Python, JavaScript/TypeScript, and Go reported as
  separate non-empty cohorts and at least two workspace/monorepo-shaped histories represented.
- Cohort membership, case labels, thresholds, and manifest hashes are frozen before a production
  score or traversal rule is changed.
- Calibration and evaluation partitions are explicit. Evaluation cases never become tuning input
  in the same phase.
- Text and JSON output report TP, FP, FN, precision, recall, recommendation coverage, abstention,
  analysis/freshness state, and targeted/full-suite strategy per threshold and cohort.
- Undefined metrics remain undefined rather than becoming zero. Statistical uncertainty and cohort
  size are shown next to point estimates; no result is presented as general accuracy.
- Duration or savings claims appear only when supplied by aligned, revision-bound execution
  evidence. Otherwise they are omitted or explicitly unknown.
- Every observed FP and FN has a reviewed classification such as label defect, unsupported
  construct, stale evidence, resolver ambiguity, or recommendation-policy gap.
- `fallback` and `unknown` cases never claim that a targeted subset is sufficient; full-suite and
  abstention safeguards retain their current meaning.
- A pre-`1.0` compatibility policy identifies stable, experimental, and internal graph, CLI JSON,
  change/report, evidence-import, and adapter/cache contracts, with explicit migration and
  deprecation rules.
- Focused and complete local gates, deterministic corpus output, package/CLI checks, approved
  remote CI, complete Evidence, durable-chain assertions, and final Review pass before closure.

## Typed links

- drives:: [[Decisions/ADR-027 - Freeze pilot evidence before recommendation tuning]]

## Trace

- Strategy: [[Brain/Phase 11B-13 Delivery Strategy]]
- Roadmap: [[Brain/Product Roadmap]]
- Delivery issue: [[Issues/ISSUE-025 - Implement longitudinal pilot and compatibility baseline]]
- Planned evidence: [[Evidence/EVD-027 - Phase 11B longitudinal pilot verification]]
- Planned review: [[Reviews/Phase 11B Longitudinal Pilot and Compatibility Review]]
- Entry gate: [[Reviews/Phase 11A Release Candidate and Demo Review]]
