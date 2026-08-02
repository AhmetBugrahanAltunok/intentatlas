---
id: phase-11b-13-delivery-strategy
type: memory
status: active
---
# Phase 11B-13 Delivery Strategy

This strategy converts the release-candidate audit into a sequenced product plan. It keeps the
vault-first and offline contracts intact while moving the product from a locally credible release
candidate to measured recommendation trust, technically ready onboarding, and a bounded monorepo
foundation.

## Product thesis

IntentAtlas is a vault-first verification layer that connects human-authored requirements and
decisions to local, reproducible code, test, evidence, and commit records. For each change it should
produce an explainable and conservative impact/test recommendation without presenting an inference
as proof.

The graph is an evidence drill-down surface, not the primary product outcome. The first product
questions are:

1. What changed?
2. Which requirement and decision paths are supported by aligned evidence?
3. Which tests are recommended, which were omitted, and why?
4. Where is the evidence incomplete, stale, ambiguous, or unsupported?

The initial user is a maintainer, reviewer, or technical lead working in an established repository
and willing to keep durable project intent in Markdown. IntentAtlas is not initially a replacement
for a build system, issue tracker, requirements editor, developer portal, or compiler indexer.

## Entry gate

At roadmap creation, [[Reviews/Phase 11A Release Candidate and Demo Review]] is pending. Its
follow-up hardening is locally verified in
[[Evidence/EVD-026 - Phase 11A release candidate and demo verification]] but remains uncommitted and
lacks exact source-bound provenance, an authorized network audit, push, and remote CI. This is a
dated entry condition, not a permanent status statement: the implementation conversation must read
the linked live Review. None of the delivery phases below starts until Phase 11A records a final
pass.

The existing Phase 11C publication idea is a conditional owner-controlled checkpoint, not an
automatic sequential engineering phase. It may be deferred until Phase 12 completes and does not
block Phase 12 once Phase 11B passes. Repository visibility, tags, releases, package publication,
and hosted attestations always require separate approval.

## Priority order

Benefit scores use `5` for highest benefit. Cost scores use `5` for highest cost. Net priority is
the five benefit scores minus implementation and maintenance cost.

| Order | Phase | User value | Risk reduction | OSS interest | Implementation cost | Maintenance cost | FP reduction | Trust | Net |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 11B - longitudinal pilot evidence | 5 | 5 | 4 | 3 | 3 | 5 | 5 | 18 |
| 2 | 12 - trust-first first-run value | 5 | 3 | 5 | 3 | 3 | 2 | 5 | 14 |
| 3 | 13 - semantic monorepo foundation | 4 | 5 | 5 | 5 | 5 | 5 | 4 | 13 |

## Shared delivery rules

- Every phase follows [[Brain/Phase Completion Protocol]] and remains open on a failed or
  unverified gate.
- Recommendation evaluation is frozen before tuning. Hidden holdouts must not become tuning data.
- Precision, recall, recommendation coverage, abstention, and execution strategy are reported
  together; precision cannot be improved cosmetically by abstaining on nearly everything.
- No omitted requirement or test is described as unaffected or unnecessary.
- Inputs remain explicit, local, bounded, symlink-safe, Private-safe, deterministic, and
  source-free in persisted output.
- Acquisition of public pilot repositories is approval-gated and separate from the offline
  evaluator. Third-party source, branding, vaults, and history are never copied into the product.
- Schema and compatibility claims are scoped explicitly before `1.0`; no accidental permanent
  contract is inferred from an internal cache or experimental adapter.
- Each Evidence note links the exact requirement, decision, issue, changed Code/Test notes, and
  implementation commit. Zero durable orphans is necessary but not sufficient; the full durable
  chain must be asserted.

## Phase 11B - sustained pilot evidence and compatibility policy

The existential question is whether advisory recommendations remain useful outside the small
reviewed corpus. Phase 11B therefore measures before adding capability. It freezes chronological
held-out histories, reports language/cohort results and uncertainty, records abstention and full-
suite behavior, and publishes an honest compatibility matrix for graph, report, evidence, and
adapter contracts.

Delivery records:

- [[Requirements/REQ-027 - Establish longitudinal recommendation evidence]]
- [[Decisions/ADR-027 - Freeze pilot evidence before recommendation tuning]]
- [[Issues/ISSUE-025 - Implement longitudinal pilot and compatibility baseline]]
- [[Evidence/EVD-027 - Phase 11B longitudinal pilot verification]]
- [[Reviews/Phase 11B Longitudinal Pilot and Compatibility Review]]

Phase 11B does not add a language, execute tests, block CI, or promise general accuracy. Its exit
gate is a frozen, reproducible, independently reviewed baseline and an explicit compatibility
policy. Any scoring refinement is a later change within the same phase only after the baseline is
committed and must be measured against untouched evaluation data.

## Phase 12 - trust-first first-run value

Phase 12 makes the change report, not the generic graph, the first real-repository outcome. A user
can inspect support, ambiguity, freshness, and next actions without initializing or modifying the
repository. The CLI and viewer show the same selection, omission, threshold, evidence, and fallback
semantics. The graph remains available as bounded evidence navigation.

Delivery records:

- [[Requirements/REQ-028 - Deliver trust-first first-run value]]
- [[Decisions/ADR-028 - Make the change report the primary product surface]]
- [[Issues/ISSUE-026 - Implement zero-footprint onboarding and trust-first reporting]]
- [[Evidence/EVD-028 - Phase 12 trust-first onboarding verification]]
- [[Reviews/Phase 12 Trust-First Onboarding Review]]

Phase 12 does not add hosted accounts, telemetry, automatic edits to user notes, an editor plugin,
or graph cosmetics without a measured usability need. Its exit gate is a no-write first-run path,
complete trust information in text/JSON/UI, real-browser keyboard/accessibility verification,
clean-install verification, and at least five distinct task-based synthetic/cognitive walkthroughs.
These walkthroughs are technical checks, not human observations, and produce no user-time median.

## Conditional Phase 11C - public launch checkpoint

The owner may approve public launch only after Phase 11B; the recommended point is after Phase 12
so the public repository presents a trustworthy first-run experience. The checkpoint verifies
repository security reporting, protected publishing environments, exact release provenance,
public benchmark wording, contributor intake, and the absence of telemetry. It is not permission
embedded in this roadmap and it does not alter local CLI behavior.

Before public launch or any real user-time claim, Phase 11C also requires at least five independent
human first-run observations and a below-ten-minute median. Automated or synthetic Phase 12
walkthroughs cannot satisfy that external usability gate.

## Phase 13 - semantic monorepo foundation

Phase 13 addresses false certainty and scale in multi-source-root and workspace repositories. It
introduces explicit project/package/source-root boundaries, abstains on ambiguous ownership,
imports revision-bound semantic evidence such as SCIP rather than executing compiler indexers,
partitions invalidation work, and avoids transferring the complete graph for the first viewer
window.

Delivery records:

- [[Requirements/REQ-029 - Scale precise evidence across monorepos]]
- [[Decisions/ADR-029 - Model workspace boundaries and import semantic evidence]]
- [[Issues/ISSUE-027 - Implement semantic monorepo foundation]]
- [[Evidence/EVD-029 - Phase 13 semantic monorepo verification]]
- [[Reviews/Phase 13 Semantic Monorepo Foundation Review]]

Phase 13 does not execute third-party indexers, load arbitrary repository plugins, create a remote
code-intelligence service, implement a distributed cache, or add languages without pilot demand.
Its exit gate is ambiguity-safe behavior on real workspace structures, revision/freshness-bound
semantic evidence, deterministic schema migration, and declared large-graph budgets.

Delivery status on 2026-08-02: Phase 13A-13C implementation is recorded at
`7f45361005163a4951f9afaa18b20e892057fa6f`, with the handoff checkpoint at
`d3e4e56ebdb3cdd8dc4ae1be7082584da3f78ab0`. Focused, complete, coverage, browser, scale,
package, installed-wheel, extracted-sdist, lint, type, security, and approved network-audit gates
passed locally. Phase 13 remains open until deterministic vault/durable-chain verification,
EVD-029 completion, push, complete remote CI, and the final Review decision pass.

## Work deliberately deferred

1. Public tag, package publication, or broad production/monorepo claims before their gates pass.
2. New languages and scoring heuristics that are not justified by frozen pilot evidence.
3. Hosted SaaS, mandatory telemetry, AI chat, test execution, distributed caching, full project
   management, or drag-and-drop graph editing.

## Handoff discipline

The implementation conversation should open the requirement, ADR, issue, pending Evidence, and
pending Review for exactly one phase. It should update the issue checklist during delivery, add
Code/Test links only after those artifacts exist, record exact commands and results in Evidence,
and keep the Review pending until every local and remote gate in that phase passes. It must not
start the next phase merely because implementation appears complete.

## Links

- North star: [[Brain/North Star]]
- Roadmap: [[Brain/Product Roadmap]]
- Phase 11 context: [[Brain/Phase 11 Strategy]]
- Completion protocol: [[Brain/Phase Completion Protocol]]
- Handoff session: [[Sessions/2026-08-02 - Phase 11B-13 roadmap handoff]]
