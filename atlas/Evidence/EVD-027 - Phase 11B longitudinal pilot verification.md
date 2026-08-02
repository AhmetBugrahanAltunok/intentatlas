---
id: EVD-027
type: evidence
status: pending
phase: 11B
---
# EVD-027 - Phase 11B longitudinal pilot verification

This is a verification plan, not evidence that Phase 11B has passed.

## Claim to verify

IntentAtlas can report recommendation quality, coverage, abstention, and compatibility limits over
a frozen longitudinal corpus without tuning on evaluation data, overstating accuracy, persisting
third-party source, weakening fallback safeguards, or adding a network requirement.

## Required evidence

- [ ] Exact starting and implementation revisions plus commit timestamps.
- [ ] Manifest/schema versions, corpus and partition hashes, project revisions, license records, and
      an explicit statement of which acquisition steps received network approval.
- [ ] Proof that the baseline production query was recorded before any recommendation change.
- [ ] Case/repository counts and separate Python, JavaScript/TypeScript, Go, workspace, threshold,
      and overall cohort tables.
- [ ] TP, FP, FN, precision, recall, recommendation coverage, abstention, analysis/freshness,
      execution-strategy, cohort-size, and uncertainty results with undefined values preserved.
- [ ] Reviewed classification for every FP/FN and a list of unsupported or excluded structures.
- [ ] Proof that duration/savings are either aligned to execution evidence or explicitly absent.
- [ ] Deterministic text/JSON output hashes from two clean evaluations.
- [ ] Compatibility matrix and migration/deprecation checks for every claimed stable contract.
- [ ] Focused regression commands and exact results.
- [ ] Complete test, coverage, lint, type, security, package, installed-CLI, and documentation
      command results.
- [ ] Two-pass vault bytes/mtime check, user-owned snapshot, zero-orphan result, and explicit
      Requirement -> Decision -> Issue -> Code -> Test -> Evidence -> Commit graph assertions.
- [ ] Approved network audit and complete remote CI results, or an explicit open gate.
- [ ] Comprehensive change inventory, remaining risks, and exact generated Commit-note link.

## Stop conditions

Keep the phase open if a partition was inspected before freezing, a cohort is silently omitted,
coverage/abstention is not reported beside precision, source or raw patches are persisted, a
fallback loses its full-suite safeguard, compatibility claims exceed tested behavior, or any
required local/remote gate is missing.

## Links

- proves:: [[Requirements/REQ-027 - Establish longitudinal recommendation evidence]]
- Decision: [[Decisions/ADR-027 - Freeze pilot evidence before recommendation tuning]]
- Delivery issue: [[Issues/ISSUE-025 - Implement longitudinal pilot and compatibility baseline]]
- Review: [[Reviews/Phase 11B Longitudinal Pilot and Compatibility Review]]
- Strategy: [[Brain/Phase 11B-13 Delivery Strategy]]
