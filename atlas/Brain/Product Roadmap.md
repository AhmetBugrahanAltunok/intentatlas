---
id: product-roadmap
type: memory
status: active
---
# Product Roadmap

> **Canonical roadmap:** this is the active source for delivery phases and their completion
> status. The repository-root [Legacy Technical Roadmap](../../ROADMAP.md) is retained only as
> a historical 0.1–0.3 planning snapshot.

IntentAtlas is developed in independently verifiable phases. A phase is complete only after
the [[Brain/Phase Completion Protocol]] is satisfied and its evidence and review are linked.

The product continues to serve [[Requirements/REQ-001 - Explain change impact]] while remaining
independent, MIT-licensed, local-first, and vault-first.

## Phase 1 — Trustworthy foundation

Status: complete (2026-07-30)

- Requirement: [[Requirements/REQ-002 - Harden trust boundaries]]
- Decision: [[Decisions/ADR-002 - Pruned trust-boundary traversal]]
- Evidence: [[Evidence/EVD-002 - Phase 1 foundation verification]]
- Review: [[Reviews/Phase 1 Foundation Review]]
- Outcome: scanning and graph exploration honor the documented trust boundary and work reliably.

## Phase 2 — Typed intent chain

Status: complete (2026-07-30)

- Express Requirement → Decision → Issue → Code → Test → Evidence → Commit with typed relations.
- Add schema evolution and clearer impact explanations.
- Requirement: [[Requirements/REQ-003 - Trace a typed intent chain]]
- Decision: [[Decisions/ADR-003 - Typed relation vocabulary]]
- Delivery issue: [[Issues/ISSUE-001 - Implement typed intent chain]]
- Evidence: [[Evidence/EVD-003 - Phase 2 typed chain verification]]
- Review: [[Reviews/Phase 2 Typed Intent Chain Review]]
- Outcome: intent, delivery, implementation, verification, evidence, history, and structure
  relationships have stable forward/inverse semantics across the cache, CLI, vault, and viewer.

## Phase 3 — Adapter platform and TypeScript/JavaScript

Status: complete (2026-07-31)

- Establish a deterministic, typed language-adapter contract.
- Move Python structural analysis behind the same contract without regressions.
- Add TypeScript, JavaScript, TSX, and JSX file, symbol, import, and test relationships.
- Requirement: [[Requirements/REQ-004 - Trace TypeScript and JavaScript structure]]
- Decision: [[Decisions/ADR-004 - Built-in language adapter contract]]
- Delivery issue: [[Issues/ISSUE-002 - Implement TypeScript and JavaScript adapter]]
- Strategy: [[Brain/Language Adapter Strategy]]
- Evidence: [[Evidence/EVD-004 - Phase 3 TypeScript and JavaScript verification]]
- Review: [[Reviews/Phase 3 TypeScript and JavaScript Review]]
- Outcome: Python and TypeScript/JavaScript now share one bounded, deterministic adapter contract;
  TS, TSX, JS, and JSX structure is navigable across the cache, CLI, vault, and viewer.

## Phase 4 — Evidence import and CI graph diff

Status: complete (2026-07-31)

- Import coverage and test-result evidence without executing project code.
- Produce a stable graph diff format for CI.
- Requirement: [[Requirements/REQ-005 - Import verification evidence and compare graph changes]]
- Decision: [[Decisions/ADR-005 - Bounded evidence imports and canonical graph diff]]
- Delivery issue: [[Issues/ISSUE-003 - Implement evidence imports and graph diff]]
- Evidence: [[Evidence/EVD-005 - Phase 4 evidence import and graph diff verification]]
- Review: [[Reviews/Phase 4 Evidence Import and Graph Diff Review]]
- Outcome: existing Cobertura and JUnit reports become bounded per-file evidence, while CI can
  consume a deterministic, timestamp-free graph diff without IntentAtlas running project code.

## Phase 5A — Go language adapter

Status: complete (2026-07-31)

- Add deterministic Go file, symbol, module-local import, and test relationships.
- Requirement: [[Requirements/REQ-006 - Trace Go structure]]
- Decision: [[Decisions/ADR-006 - Conservative Go module projection]]
- Delivery issue: [[Issues/ISSUE-004 - Implement Go language adapter]]
- Strategy: [[Brain/Language Adapter Strategy]]
- Evidence: [[Evidence/EVD-006 - Phase 5A Go adapter verification]]
- Review: [[Reviews/Phase 5A Go Adapter Review]]
- Outcome: Go files, `go.mod` module boundaries, named types, functions, methods, local package
  imports, and tests are navigable through the same offline deterministic graph contract.

## Phase 5B — External delivery inputs

Status: complete (2026-07-31)

- Add optional issue and pull-request inputs through explicit local JSON snapshots.
- Requirement: [[Requirements/REQ-007 - Import local delivery context]]
- Decision: [[Decisions/ADR-007 - Explicit local delivery snapshots]]
- Delivery issue: [[Issues/ISSUE-005 - Implement local delivery imports]]
- Evidence: [[Evidence/EVD-007 - Phase 5B local delivery verification]]
- Review: [[Reviews/Phase 5B Local Delivery Review]]
- Preserve offline operation and require explicit configuration for every external data source.
- Select Rust or Java next according to demand and fixture quality after delivery inputs are
  bounded and verified.
- Outcome: explicit local snapshots connect intent, issues, pull requests, files, and known commits
  through a bounded offline delivery graph.

## Phase 6A — Symbol-level change impact foundation

Status: complete (2026-07-31)

- Map bounded Git diff hunks to exact symbols when the current language adapter exposes a
  trustworthy source span.
- Preserve file-level change relationships as a conservative fallback instead of guessing.
- Requirement: [[Requirements/REQ-008 - Trace symbol-level commit impact]]
- Decision: [[Decisions/ADR-008 - Conservative diff-to-symbol projection]]
- Delivery issue: [[Issues/ISSUE-006 - Implement symbol-level commit impact]]
- Evidence: [[Evidence/EVD-008 - Phase 6A symbol impact verification]]
- Review: [[Reviews/Phase 6A Symbol Impact Review]]
- Outcome: recent commits retain complete file history and gain direct `modifies` evidence for
  the most-specific changed Python symbols when bounded new-side hunks intersect validated AST
  spans; uncertain cases remain safely at file level.

## Phase 6B1 — Explainable test recommendations

Status: complete (2026-08-01)

- Rank direct test candidates from verified symbol and file-change evidence.
- Expose fixed confidence levels, evidence paths, filtering, and deterministic text/JSON output
  without treating inferred test necessity as fact.
- Requirement: [[Requirements/REQ-009 - Recommend tests with explainable confidence]]
- Decision: [[Decisions/ADR-009 - Evidence-ranked test recommendations]]
- Delivery issue: [[Issues/ISSUE-007 - Implement explainable test recommendations]]
- Evidence: [[Evidence/EVD-009 - Phase 6B1 test recommendation verification]]
- Review: [[Reviews/Phase 6B1 Test Recommendation Review]]
- Outcome: commits, files, and symbols now produce bounded, deterministic test candidates with
  inspectable confidence, evidence, and paths while explicitly preserving uncertainty.

## Phase 6B2A — Resilient generated vault synchronization

Status: complete (2026-08-01)

- Preserve the last complete generated vault when a transient or persistent file lock interrupts
  synchronization.
- Avoid rewriting byte-identical generated notes and remove stale notes only after desired output
  is safely in place.
- Requirement: [[Requirements/REQ-010 - Preserve generated vault integrity during synchronization]]
- Decision: [[Decisions/ADR-010 - Failure-preserving atomic vault synchronization]]
- Delivery issue: [[Issues/ISSUE-008 - Implement resilient generated vault synchronization]]
- Evidence: [[Evidence/EVD-010 - Phase 6B2A vault synchronization verification]]
- Review: [[Reviews/Phase 6B2A Vault Synchronization Review]]
- Outcome: generated notes now refresh through failure-preserving atomic replacement; unchanged
  scans avoid rewrites and a locked file cannot trigger a destructive purge.

## Phase 6B2B1 — Labeled recommendation evaluation

Status: complete (2026-08-01)

- Add a deterministic offline evaluator for exhaustive human-labeled test sets.
- Record an honest self-hosted IntentAtlas baseline before widening dependency propagation.
- Requirement: [[Requirements/REQ-011 - Measure test recommendation quality]]
- Decision: [[Decisions/ADR-011 - Closed-world recommendation evaluation]]
- Delivery issue: [[Issues/ISSUE-009 - Implement labeled recommendation evaluation]]
- Evidence: [[Evidence/EVD-011 - Phase 6B2B1 recommendation evaluation verification]]
- Review: [[Reviews/Phase 6B2B1 Recommendation Evaluation Review]]
- Outcome: strict local labels now measure the unchanged production recommendation query with
  deterministic TP, FP, FN, precision, and recall; the first reviewed baseline exposes the real
  precision/recall tradeoff without claiming general accuracy.

## Phase 6B2B2A — Cross-project recommendation benchmarks

Status: complete (2026-08-01)

- Compare low, medium, and high confidence across a bounded local corpus without changing scores.
- Add original, independently labeled Python, TypeScript, and Go graph scenarios as deterministic
  regression fixtures, not as real-world accuracy evidence.
- Requirement: [[Requirements/REQ-012 - Compare recommendation quality across projects]]
- Decision: [[Decisions/ADR-012 - Aggregate independent closed-world benchmarks]]
- Delivery issue: [[Issues/ISSUE-010 - Implement cross-project recommendation benchmarks]]
- Evidence: [[Evidence/EVD-012 - Phase 6B2B2A cross-project benchmark verification]]
- Review: [[Reviews/Phase 6B2B2A Cross-Project Benchmark Review]]
- Outcome: a strict local corpus now compares low, medium, and high thresholds across original
  Python, TypeScript, and Go graph scenarios while keeping real-world validity explicitly open.

## Phase 6B2B2B1 — Indexed graph queries and scale gate

Status: complete (2026-08-01)

- Replace repeated whole-edge scans in impact and recommendation queries with one shared lazy
  adjacency index while preserving exact deterministic results.
- Add a bounded synthetic large-graph benchmark for cold index construction and repeated warm
  queries.
- Requirement: [[Requirements/REQ-013 - Keep graph queries responsive at scale]]
- Decision: [[Decisions/ADR-013 - Lazy deterministic adjacency index]]
- Delivery issue: [[Issues/ISSUE-011 - Implement indexed graph queries and scale benchmark]]
- Evidence: [[Evidence/EVD-013 - Phase 6B2B2B1 indexed query verification]]
- Review: [[Reviews/Phase 6B2B2B1 Indexed Query Review]]
- Outcome: impact and test-recommendation traversal now reuse one deterministic adjacency index;
  a bounded offline benchmark verifies stable results and local-bucket work as unrelated edges grow.

## Phase 6B2B2B2A — Guided local showcase and evidence paths

Status: complete (2026-08-01)

- Ship an original, packaged intent-to-proof demo that opens without scanning or network access.
- Show bounded, deterministic evidence paths for the selected viewer node.
- Requirement: [[Requirements/REQ-014 - Explain the product through a guided local demo]]
- Decision: [[Decisions/ADR-014 - Packaged first-party demo and bounded evidence paths]]
- Delivery issue: [[Issues/ISSUE-012 - Implement guided demo and viewer evidence paths]]
- Evidence: [[Evidence/EVD-014 - Phase 6B2B2B2A guided demo verification]]
- Review: [[Reviews/Phase 6B2B2B2A Guided Demo Review]]
- Outcome: a fresh installation can open an original intent-to-proof showcase with one command,
  and every selected node exposes bounded structural paths to relevant proof-oriented records.

## Phase 6B2B2B2B — License-reviewed real-world validation

Status: complete (2026-08-01)

- Add public real-world benchmark repositories only after explicit network approval and license
  review.
- Add independently reviewed labels and scanner-to-recommendation measurements without copying
  third-party history, branding, or source into the product.
- Define generated-output policies that further reduce Git noise.
- Requirement: [[Requirements/REQ-015 - Validate recommendations on pinned public projects]]
- Decision: [[Decisions/ADR-015 - Separate public acquisition from offline evaluation]]
- Delivery issue: [[Issues/ISSUE-013 - Implement license-reviewed real-world validation]]
- Evidence: [[Evidence/EVD-015 - Phase 6B2B2B2B real-world verification]]
- Review: [[Reviews/Phase 6B2B2B2B Real-World Validation Review]]
- Outcome: three pinned MIT-licensed Python, JavaScript, and Go changes now exercise the unchanged
  scanner-to-recommendation pipeline through nine reviewed commit, file, and symbol cases; all
  checkout and generated data remains approval-gated, ignored, and ephemeral.

## Phase 7A — Evidence-derived Go test links

Status: complete (2026-08-01)

- Replace a verified Go filename-only gap with conservative same-package symbol-reference evidence.
- Reject ambiguous, unexported, comment-only, and literal-only matches rather than widening package
  relationships.
- Requirement: [[Requirements/REQ-016 - Link Go tests through unique symbol references]]
- Decision: [[Decisions/ADR-016 - Prefer unique Go symbol evidence over filename convention]]
- Delivery issue: [[Issues/ISSUE-014 - Implement conservative Go symbol test links]]
- Evidence: [[Evidence/EVD-016 - Phase 7A Go symbol-reference verification]]
- Review: [[Reviews/Phase 7A Go Symbol-Reference Review]]
- Outcome: same-directory Go tests now gain medium-confidence structural evidence only when they
  reference exported declarations uniquely owned by one compatible production file; the pinned
  nine-case benchmark reaches 100% medium precision and recall without changing scores or labels.

## Phase 7B — Broader open-source validation

Status: complete (2026-08-01)

- Expand public benchmarks to larger and more diverse projects with multiple relevant tests,
  source-only commits, indirect dependencies, nested test layouts, and explicit negative cases.
- Preserve license, provenance, offline evaluation, and independently reviewed label boundaries.
- Requirement: [[Requirements/REQ-017 - Validate recommendations on broader project structures]]
- Decision: [[Decisions/ADR-017 - Use broader benchmarks to drive conservative refinements]]
- Delivery issue: [[Issues/ISSUE-015 - Expand and refine real-world validation]]
- Evidence: [[Evidence/EVD-017 - Phase 7B broader validation verification]]
- Review: [[Reviews/Phase 7B Broader Validation Review]]
- Outcome: six pinned projects and 18 reviewed cases expose source-only, multiple-test, package,
  and indirect-dependency behavior. Qualified Go import evidence removes 18 observed false
  positives; medium precision is 85.71% and recall 78.26%, with remaining gaps explicit.

## Phase 7C — Bounded symbol-aware dependency evidence

Status: complete (2026-08-01)

- Replace broad Python test-to-file evidence with exact imported-symbol evidence when resolvable.
- Recover indirect JavaScript tests only through one exact-symbol dependent hop or explicit recent
  co-change evidence; do not enable unrestricted barrel traversal.
- Requirement: [[Requirements/REQ-018 - Refine tests with bounded symbol-aware evidence]]
- Decision: [[Decisions/ADR-018 - Bound dependency propagation with exact symbols and co-change]]
- Delivery issue: [[Issues/ISSUE-016 - Implement bounded symbol-aware test evidence]]
- Evidence: [[Evidence/EVD-018 - Phase 7C symbol-aware dependency verification]]
- Review: [[Reviews/Phase 7C Symbol-Aware Dependency Review]]
- Outcome: exact Python/JavaScript symbol evidence, one-hop exact dependencies, and bounded recent
  co-change remove the observed Click and Axios gaps without unrestricted transitive traversal;
  the pinned 18-case medium result is TP 23, FP 0, FN 0 within its explicit sample boundary.

## Phase 7D — Open-source release readiness

Status: complete

- [x] Add an installed-wheel end-to-end test for init, scan, status, impact, recommendation, and
  loopback viewer retrieval.
- [x] Add Linux, Windows, and macOS CI coverage on the oldest and newest supported Python versions.
- [x] Build wheel and source artifacts twice under a fixed timestamp and verify byte identity,
  integrity, metadata, bundled assets, license bytes, and source-archive boundaries.
- [x] Document the release process and keep publishing as a separate approval-gated action.
- [x] Pass the complete local quality, security, package, CLI/UI, determinism, attribution, and
  Obsidian closure gates.
- [x] Pass the new cross-platform and reproducible-package jobs in remote CI before closing the
  phase.

- Requirement: [[Requirements/REQ-019 - Ship verifiable cross-platform releases]]
- Decision: [[Decisions/ADR-019 - Separate reproducible verification from publication]]
- Delivery issue: [[Issues/ISSUE-017 - Implement open-source release gates]]
- Evidence: [[Evidence/EVD-019 - Phase 7D release readiness verification]]
- Review: [[Reviews/Phase 7D Open-Source Release Readiness Review]]

## Phase 8 — Trustworthy change intelligence

Status: complete (2026-08-01)

- Remove project-specific sample memory from fresh user vaults.
- Represent commit, range, staged, and worktree changes through one bounded change-set model.
- Distinguish exact symbol evidence from conservative file fallback and unknown analysis.
- Rank requirement impact and test candidates with revision, scope, provenance, freshness, and
  explainable confidence.
- Prefer honest abstention or a full-test fallback when evidence is incomplete.
- Requirement: [[Requirements/REQ-020 - Explain revision-scoped change confidence]]
- Decision: [[Decisions/ADR-020 - Separate exact change evidence from fallback]]
- Delivery issue: [[Issues/ISSUE-018 - Implement trustworthy change intelligence]]
- Strategy: [[Brain/Phase 8-10 Strategy]]
- Kickoff: [[Sessions/2026-08-01 - Phase 8 kickoff]]
- Evidence: [[Evidence/EVD-020 - Phase 8 trustworthy change intelligence verification]]
- Review: [[Reviews/Phase 8 Trustworthy Change Intelligence Review]]
- Outcome: one bounded change model now carries exact, fallback, or unknown evidence into
  deterministic requirement/test reports and the local UI; same-file ambiguity stays below the
  default threshold and incomplete analysis abstains or includes the full suite.

## Phase 9 — Pull-request and CI evidence loop

Status: complete (2026-08-01)

- Add a deterministic revision-range review command with Markdown, JSON, and SARIF output.
- Publish nothing by default; begin with a read-only, shadow-mode CI integration.
- Import actual test results with commit identity and freshness, then surface change-centric views.
- Requirement: [[Requirements/REQ-021 - Review revision ranges in CI shadow mode]]
- Decision: [[Decisions/ADR-021 - Compose review formats over trustworthy change reports]]
- Delivery issue: [[Issues/ISSUE-019 - Implement CI shadow review loop]]
- Kickoff: [[Sessions/2026-08-01 - Phase 9 kickoff]]
- Evidence: [[Evidence/EVD-021 - Phase 9 CI shadow review verification]]
- Review: [[Reviews/Phase 9 CI Shadow Review Review]]
- Strategy: [[Brain/Phase 8-10 Strategy]]
- Outcome: deterministic revision reviews now flow through Markdown, JSON, SARIF, a credential-free
  opt-in Action, commit-keyed outcome freshness, and the same local in-memory viewer. Findings stay
  non-blocking and incomplete or stale evidence retains abstention/full-suite safeguards.

## Phase 10 — Scale and open evidence ecosystem

Status: complete (2026-08-01; Phases 10A–10D complete)

- Add incremental scanning and atomic derived indexes without weakening Markdown portability.
- Import open evidence formats such as SCIP, SARIF, and per-test execution maps.
- Define an adapter conformance contract and make the viewer responsive on large repositories.
- Harden release provenance, fuzz/property coverage, browser E2E, and pinned CI dependencies.
- Strategy: [[Brain/Phase 8-10 Strategy]]

### Phase 10A — Content-addressed scan foundation

Status: complete (2026-08-01)

- Reuse bounded adapter fragments only when their complete declared input set has the same content
  fingerprint and cache contract version.
- Rebuild safely when state is missing, stale, malformed, oversized, or changes during scanning.
- Replace graph and derived cache files atomically without storing source contents or weakening the
  portable Markdown vault.
- Requirement: [[Requirements/REQ-022 - Reuse trustworthy scan work safely]]
- Decision: [[Decisions/ADR-022 - Cache adapter fragments by declared input fingerprint]]
- Delivery issue: [[Issues/ISSUE-020 - Implement content-addressed scan foundation]]
- Kickoff: [[Sessions/2026-08-01 - Phase 10A kickoff]]
- Evidence: [[Evidence/EVD-022 - Phase 10A content-addressed scan verification]]
- Review: [[Reviews/Phase 10A Content-Addressed Scan Review]]
- Outcome: repeated CLI scans reuse exact per-adapter structural fragments, selectively rebuild
  changed language inputs, reject unsafe or corrupt derived state, and atomically preserve the last
  complete graph/cache artifact without storing source content.

Phase 10A established the incremental foundation. The sections below record completed Phase 10B,
10C, and 10D delivery.

### Phase 10B — Open evidence imports

Status: complete (2026-08-01)

- Import bounded SCIP protobuf-JSON and SARIF 2.1.0 observations without retaining source or raw
  diagnostic content.
- Import a strict commit-keyed per-test execution map and create runtime test relationships only
  when its commit exactly matches the scanned repository HEAD.
- Keep every input explicit, local, offline, deterministic, project-relative, and disposable.
- Requirement: [[Requirements/REQ-023 - Import open evidence without overstating certainty]]
- Decision: [[Decisions/ADR-023 - Separate observations from aligned execution evidence]]
- Delivery issue: [[Issues/ISSUE-021 - Implement bounded open evidence imports]]
- Kickoff: [[Sessions/2026-08-01 - Phase 10B kickoff]]
- Evidence: [[Evidence/EVD-023 - Phase 10B open evidence verification]]
- Review: [[Reviews/Phase 10B Open Evidence Review]]
- Outcome: explicit SCIP protobuf-JSON and SARIF 2.1.0 reports become bounded source-free file
  observations, while commit-keyed execution maps add runtime test relationships only when both
  commit and every mapped worktree artifact align exactly with HEAD.

### Phase 10C — Adapter conformance and large-graph viewer

Status: complete (2026-08-01)

- Publish one executable conformance contract for safe deterministic language-adapter definitions
  and fragments, shared by fresh and cached scan paths.
- Render deterministic bounded overview and focus windows instead of materializing the complete
  graph as SVG, while retaining global search and linked navigation.
- Precompute browser indexes and bound relationship details so interaction cost follows the visible
  subgraph rather than total repository size.
- Requirement: [[Requirements/REQ-024 - Keep adapters trustworthy and large graphs responsive]]
- Decision: [[Decisions/ADR-024 - Validate adapters and render bounded graph windows]]
- Delivery issue: [[Issues/ISSUE-022 - Implement adapter conformance and bounded viewer windows]]
- Kickoff: [[Sessions/2026-08-01 - Phase 10C kickoff]]
- Evidence: [[Evidence/EVD-024 - Phase 10C adapter and viewer verification]]
- Review: [[Reviews/Phase 10C Adapter and Large Graph Review]]
- Outcome: built-in adapters now pass one executable fresh/cache conformance boundary, while the
  local viewer navigates complete large graphs through indexed deterministic 240-node/900-edge
  overview and focus windows with explicit omission and global hidden-node access.

### Phase 10D — Verification and release provenance

Status: complete (2026-08-01)

- Add deterministic property and mutation-fuzz coverage at untrusted graph and JSON boundaries.
- Exercise the packaged large-graph viewer through a real Chrome-family browser.
- Enforce maintained-source static typing and immutable full-SHA Action references.
- Bind repeated verified artifacts to exact source and build inputs with canonical provenance.
- Keep trusted publishing manual, protected, and outside this phase unless separately approved.
- Requirement: [[Requirements/REQ-025 - Harden verification and release provenance]]
- Decision: [[Decisions/ADR-025 - Layer offline verification before trusted publishing]]
- Delivery issue: [[Issues/ISSUE-023 - Implement verification and provenance hardening]]
- Kickoff: [[Sessions/2026-08-01 - Phase 10D kickoff]]
- Evidence: [[Evidence/EVD-025 - Phase 10D verification and provenance]]
- Review: [[Reviews/Phase 10D Verification and Release Provenance Review]]
- Outcome: deterministic hostile-input tests, a real browser large-graph check, maintained-source
  typing, immutable CI dependencies, and source-bound repeatable artifact provenance now protect
  the verification boundary. All local gates, the network dependency audit, and 13 remote CI jobs
  passed; publishing remains manual, protected, and unexecuted.

## Phase 11 — Release candidate and adoption evidence

Status: complete (Phase 11A and Phase 11B complete; Phase 11C remains owner-controlled)

- Turn the completed Phase 10 capability into an honest, immediately evaluable release candidate.
- Demonstrate conservative same-file behavior rather than presenting only a perfect linear chain.
- Keep sustained pilots, compatibility policy, public launch, and publication as separately gated
  follow-up work.
- Strategy: [[Brain/Phase 11 Strategy]]

### Phase 11A — Honest release candidate and evaluable demo

Status: complete (2026-08-02)

- Establish one canonical `0.3.0rc1` version source without tagging or publishing.
- Add an original same-file two-requirement/two-test counterexample to the built-in demo.
- Provide deterministic text and JSON demo reports while retaining the interactive viewer default.
- Verify documentation, exact-wheel installation, browser behavior, provenance, and complete phase
  gates before closure.
- Requirement: [[Requirements/REQ-026 - Make the release candidate honest and immediately evaluable]]
- Decision: [[Decisions/ADR-026 - Separate scriptable demo evidence from interactive viewing and publication]]
- Delivery issue: [[Issues/ISSUE-024 - Implement the honest 0.3.0 release candidate demo]]
- Kickoff: [[Sessions/2026-08-01 - Phase 11A kickoff]]
- Planned evidence: [[Evidence/EVD-026 - Phase 11A release candidate and demo verification]]
- Planned review: [[Reviews/Phase 11A Release Candidate and Demo Review]]

### Phase 11B - Sustained pilot evidence and compatibility policy

Status: complete (2026-08-02)

- Freeze longitudinal calibration/evaluation histories before changing recommendation behavior.
- Report recommendation quality, coverage, abstention, freshness, execution strategy, cohort size,
  and uncertainty per project, language, threshold, and aggregate.
- Classify graph, report, CLI JSON, evidence, adapter, and cache contracts as stable,
  experimental, or internal with explicit migration/deprecation rules.
- Keep recommendations advisory and the evaluator offline; do not add telemetry or blocking CI.
- Requirement: [[Requirements/REQ-027 - Establish longitudinal recommendation evidence]]
- Decision: [[Decisions/ADR-027 - Freeze pilot evidence before recommendation tuning]]
- Delivery issue: [[Issues/ISSUE-025 - Implement longitudinal pilot and compatibility baseline]]
- Planned evidence: [[Evidence/EVD-027 - Phase 11B longitudinal pilot verification]]
- Planned review: [[Reviews/Phase 11B Longitudinal Pilot and Compatibility Review]]
- Strategy: [[Brain/Phase 11B-13 Delivery Strategy]]
- Handoff: [[Sessions/2026-08-02 - Phase 11B-13 roadmap handoff]]

### Conditional Phase 11C - Public launch checkpoint

Status: not authorized; owner-controlled after Phase 11B, recommended after Phase 12

- Complete at least five independent human first-run observations and demonstrate a below-ten-
  minute median before public launch or any real user-time claim. Phase 12 synthetic/cognitive
  walkthroughs are technical evidence and cannot satisfy this human-validation gate.
- Verify public security reporting, protected publishing environments, exact release provenance,
  contributor intake, benchmark wording, and the no-telemetry contract.
- Repository visibility, tag, release, package publication, deployment, hosted attestation, and
  external announcement each require separate approval.
- Deferral does not block local Phase 12 or Phase 13 delivery.
- Strategy: [[Brain/Phase 11 Strategy]]

## Phase 12 - Trust-first first-run value

Status: complete (2026-08-02)

- Make an aligned, zero-footprint change report the first real-repository outcome.
- Add a deterministic read-only diagnostic for support, ambiguity, freshness, and safe next steps.
- Preserve revision, threshold, candidate counts, selected/omitted meaning, evidence paths,
  fallback strategy, and advisory limits across terminal text, JSON, and the viewer.
- Treat the graph as bounded evidence drill-down rather than the product's primary answer.
- Establish technical onboarding readiness through at least five task-based synthetic/cognitive
  walkthroughs plus clean-install, no-write, cross-surface, browser, keyboard, and accessibility
  gates; do not claim human usability or median user time from those checks.
- Requirement: [[Requirements/REQ-028 - Deliver trust-first first-run value]]
- Decision: [[Decisions/ADR-028 - Make the change report the primary product surface]]
- Delivery issue: [[Issues/ISSUE-026 - Implement zero-footprint onboarding and trust-first reporting]]
- Planned evidence: [[Evidence/EVD-028 - Phase 12 trust-first onboarding verification]]
- Planned review: [[Reviews/Phase 12 Trust-First Onboarding Review]]
- Strategy: [[Brain/Phase 11B-13 Delivery Strategy]]

## Phase 13 - Semantic monorepo foundation

Status: complete on 2026-08-02; EVD-029 complete and Phase 13 Review passed

- Model explicit project/package/source-root and workspace ownership without directory-name guesses.
- Retain resolver candidate sets and abstain when one aligned owner cannot be proven.
- Import strict revision-bound semantic evidence such as SCIP without executing indexers or project
  tooling.
- Partition cache invalidation and bound pre-work repository budgets.
- Serve bounded viewer queries without transferring/indexing the complete graph initially.
- Requirement: [[Requirements/REQ-029 - Scale precise evidence across monorepos]]
- Decision: [[Decisions/ADR-029 - Model workspace boundaries and import semantic evidence]]
- Delivery issue: [[Issues/ISSUE-027 - Implement semantic monorepo foundation]]
- Planned evidence: [[Evidence/EVD-029 - Phase 13 semantic monorepo verification]]
- Planned review: [[Reviews/Phase 13 Semantic Monorepo Foundation Review]]
- Strategy: [[Brain/Phase 11B-13 Delivery Strategy]]

## Phase 14 - One-command guided CLI

Status: complete on 2026-08-02; EVD-030 complete and Phase 14 Review passed

- Make interactive `intentatlas` the shortest trustworthy path to the existing ChangeReport while
  retaining explicit commands and versioned JSON for automation.
- Resolve one safe Git root, deterministically recommend worktree/staged/HEAD scope, and require no
  Git or IntentAtlas terminology on the common path.
- Keep default guidance offline, no-write, Private-safe, execution-free, and browser-off; expose
  uncertainty, omission, fallback, and zero executed tests rather than simplifying them away.
- Use a dependency-free, line-oriented English/Turkish flow with at most one Enter before the
  report, progressive evidence detail, safe cancellation, and non-TTY/CI fail-fast behavior.
- Reuse one immutable production graph/report snapshot for terminal and explicit loopback viewer
  output; do not add a second recommendation engine or automatic persistent setup.
- Close the phase through technical transcript, TTY/non-TTY, no-write, parity, hostile-input,
  browser, package, cross-platform, deterministic-vault, approved-network, and remote-CI evidence.
  This does not replace the Phase 11C five-person human-validation gate.
- Requirement: [[Requirements/REQ-030 - Make trustworthy analysis effortless from the CLI]]
- Decision: [[Decisions/ADR-030 - Layer a TTY-guided flow over deterministic contracts]]
- Delivery issue: [[Issues/ISSUE-028 - Implement one-command guided CLI onboarding]]
- Planned evidence: [[Evidence/EVD-030 - Phase 14 guided CLI verification]]
- Planned review: [[Reviews/Phase 14 One-Command Guided CLI Review]]
- Strategy: [[Brain/Phase 14 Guided CLI Strategy]]
- Handoff: [[Sessions/2026-08-02 - Phase 14 guided CLI handoff]]

## Completion rule

Every phase must end with a linked Evidence note and Review note containing the full change
inventory, test results, acceptance decision, and remaining risks. A failing or incomplete gate
keeps the phase open.
