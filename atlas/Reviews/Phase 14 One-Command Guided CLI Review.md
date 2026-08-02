---
id: review-phase-14-one-command-guided-cli
type: review
status: pending
phase: 14
---
# Phase 14 One-Command Guided CLI Review

## Acceptance review

- [ ] Phase 13 passed before Phase 14 implementation and the exact entry revision is recorded.
- [ ] REQ-030 is linked to ADR-030 and ISSUE-028.
- [ ] Interactive empty argv and explicit `guide` deliver the production ChangeReport within the
      declared interaction budget without a new recommendation path.
- [ ] Root and scope selection are deterministic, visible, changeable, ambiguity-safe, and never
      guess a base branch or scan unrelated filesystem locations.
- [ ] The common flow is demonstrably no-write, offline, Private-safe, execution-free, bounded, and
      cancellable; browser/listener behavior requires explicit selection.
- [ ] Concise and complete terminal surfaces preserve all revision/scope/state/freshness/threshold/
      count/evidence/omission/strategy/advisory meanings and state that zero tests were executed.
- [ ] Terminal and browser consume the same immutable snapshot; no second scan creates drift.
- [ ] EN/TR, accessibility, narrow/plain terminal, hostile text, error, and recovery gates pass.
- [ ] Non-TTY/redirected/CI calls cannot prompt, wait, scan, or corrupt machine output, and every
      existing explicit CLI/JSON and exit contract passes.
- [ ] Focused/full/browser/package/cross-platform/deterministic-vault/approved-network/remote-CI
      gates and exact provenance pass.
- [ ] EVD-030 contains the complete inventory, commands, results, limitations, links, and risks.
- [ ] No persistent setup execution, test execution, new runtime dependency, product-semantic
      expansion, Phase 11C closure, human-time claim, tag, release, publication, or deployment
      occurred.

## Evidence to examine

- [[Evidence/EVD-030 - Phase 14 guided CLI verification]]
- [[Requirements/REQ-030 - Make trustworthy analysis effortless from the CLI]]
- [[Decisions/ADR-030 - Layer a TTY-guided flow over deterministic contracts]]
- [[Issues/ISSUE-028 - Implement one-command guided CLI onboarding]]

## Review decision

Pending. This Review must remain pending until every applicable acceptance item and EVD-030 gate is
complete at an exact pushed revision with passing remote CI. A technical Phase 14 pass will not
close the separate Phase 11C human-observation gate.
