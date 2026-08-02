---
id: ISSUE-029
type: issue
status: open
phase: 15
---
# Implement frictionless source-to-atlas onboarding

## Entry

- [x] Phase 14 Review is `passed` and EVD-030 is `complete`.
- [x] Clean `main == origin/main == a2250936e44fb7dc21634e6e8039ccadba8b1fed`.
- [x] REQ-031 and ADR-031 define acquisition, cache, integration, and publication boundaries.

## 15A - isolated global installation readiness

- [x] Verify exact-wheel install, clean-shell command discovery, version/help/guide, reinstall, and
      uninstall with temporary pipx home/bin roots and no real PATH mutation.
- [x] Freeze honest public-install wording and the open zero-prerequisite Windows boundary.
- [x] Add only the missing global-command gates; retain existing package/provenance tests.

## 15B - safe public GitHub acquisition

- [x] Add strict GitHub URL normalization and TTY-only guided URL dispatch.
- [x] Implement inert bounded Git acquisition, exact revision, Private exclusion, atomic managed
      cache, cache hit/corruption/concurrency handling, and injected cache roots.
- [x] Add safe `cache list`, `cache info`, and exact-target `cache clear` commands.
- [x] Prove scheme/host/credential/path/redirect rejection, no auth/tool execution, bounded failure,
      source no-write, cleanup safety, and deterministic offline tests.

## 15C - production source-to-atlas integration

- [x] Connect acquired and local sources to one diagnostic/scan/ChangeReport snapshot.
- [x] Add truthful Atlas/layer/link/revision/scope/freshness/bound summaries and prominent explicit
      existing-viewer action without inventing intent.
- [x] Preserve EN/TR, terminal safety/accessibility, browser controls, explicit CLI/JSON behavior,
      packaging, and no-runtime-dependency boundaries.
- [x] Update installation, guided, cache, security, architecture, compatibility, README/README.tr,
      changelog, roadmap, Evidence, and Review records.

## Closure

- [x] Focused/full/coverage/lint/type/security/browser/package/provenance/network/vault gates pass.
- [x] Fixed public-repository smoke records exact revision and license without committing source.
- [x] Generated Code/Test/Commit notes and zero-orphan durable chain pass deterministically.
- [ ] EVD-031 is complete, Review passes, commits are pushed, and final-head CI is fully green.
- [ ] Phase 11C and every publication/deployment/settings/announcement boundary remain unchanged.

## Typed links

- implements:: [[Requirements/REQ-031 - Open a trustworthy atlas from a local path or public GitHub URL]]
- decided-by:: [[Decisions/ADR-031 - Acquire explicit public repositories into a managed local cache]]
- planned-evidence:: [[Evidence/EVD-031 - Phase 15 source-to-atlas verification]]
- reviewed-by:: [[Reviews/Phase 15 Source-to-Atlas Review]]
