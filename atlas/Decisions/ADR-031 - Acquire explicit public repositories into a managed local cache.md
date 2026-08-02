---
id: ADR-031
type: decision
status: accepted
phase: 15
---
# ADR-031 - Acquire explicit public repositories into a managed local cache

## Context

ADR-028 made ChangeReport the trustworthy first real-repository answer. ADR-030 made that answer
reachable through a TTY-only guided layer and held one immutable graph/report snapshot for terminal
and browser. A public GitHub source currently still requires manual cloning and path selection.

## Decision

Keep ADR-028 and ADR-030 intact: ChangeReport remains the trust answer and the existing graph viewer
becomes a more visible exploration action over the same snapshot. Add no analysis, resolver,
scoring, recommendation, freshness, or viewer semantics.

Accept only strict `https://github.com/<owner>/<repo>[.git]` identities. Acquire an explicitly
approved public repository with fixed-argv `git`, `shell=False`, isolated Git configuration,
disabled credentials/prompts/hooks/filters/LFS/submodules, no redirects, shallow bounded history,
and enforced time/output/file/checkout/disk limits. Resolve and record a full commit SHA.

Use a standard-library managed cache under the operating system's user cache convention, with an
injectable root for tests. Derive a non-secret identity from the normalized URL, clone into unique
staging, validate before atomic promotion, serialize same-repository mutation with an atomic lock,
and preserve the prior completed entry on failure. Metadata stores only source identity, exact
revision, bounded-history/cache state, and non-secret counts—never environment values,
credentials, tokens, logs, or source contents.

Provide `cache list`, `cache info ID`, and `cache clear ID`. Clear accepts only one validated cache
ID beneath a canonical managed root and rejects symlink, junction, reparse, and traversal escape.

Exclude `atlas/Private/` before remote checkout and again at existing scanner/change boundaries.
Do not call GitHub APIs, fetch issues/PRs, authenticate, initialize or write the analyzed source,
execute repository tooling, or persist a second graph/report truth.

## Consequences

- First public acquisition has explicit network/cache effects; cache hits can use one exact cached
  revision without claiming it is latest. Refresh failure never relabels cached state as fresh.
- Bounded/shallow Git history can omit older commits and must be visible in terminal and metadata.
- `pipx install intentatlas` remains documentation for a future published package, not proof that a
  public artifact or zero-prerequisite installer exists today.
- Guided prompt presentation stays experimental; protected no-write/network-consent/cache/privacy/
  revision/omission/fallback/exit meanings extend the compatibility matrix.

## Links

- Requirement: REQ-031 (incoming `drives` link)
- tracked-by:: [[Issues/ISSUE-029 - Implement frictionless source-to-atlas onboarding]]
- preserves:: [[Decisions/ADR-028 - Make the change report the primary product surface]]
- extends:: [[Decisions/ADR-030 - Layer a TTY-guided flow over deterministic contracts]]
- strategy:: [[Brain/Phase 15 Source-to-Atlas Strategy]]
