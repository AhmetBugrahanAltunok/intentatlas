---
id: REQ-031
type: requirement
status: accepted
phase: 15
---
# Open a trustworthy atlas from a local path or public GitHub URL

## User outcome

A maintainer supplies a local folder or a strict public GitHub repository URL to `intentatlas` and
reaches the production ChangeReport plus the existing interactive Atlas without learning clone,
scope, graph, or package-manager details first.

## Acceptance

- The Phase 14 Review passes before implementation and its local guided contracts regress cleanly.
- An exact wheel works as an isolated global CLI tool through temporary pipx install, reinstall,
  clean-shell command use, and uninstall without changing the real user PATH or pipx roots.
- Empty guided source input accepts a local path or supported GitHub URL; `guide URL` works, and a
  one-URL shorthand is TTY-only. Non-TTY URL/empty argv performs no prompt, network, or cache write.
- URL parsing accepts only canonical public GitHub repository HTTPS URLs and rejects credentials,
  ports, query/fragment, page paths, other schemes/hosts, localhost/IP, authentication, and unsafe
  redirects.
- Remote acquisition is explicitly approved before network/cache effects and runs bounded inert
  Git operations without project code, hooks, filters, submodules, LFS smudge, credentials, user
  configuration, shell evaluation, or interactive prompts.
- The managed cache uses an injected/testable OS cache root, deterministic URL identity, atomic
  staging, concurrency exclusion, corruption recovery, honest revision/freshness/history metadata,
  and traversal/link-safe list/info/clear management.
- Local and remote sources converge on the production diagnostic, scanner, graph, ChangeReport,
  terminal sanitizer, and immutable viewer snapshot with no second scan or recommendation path.
- The summary reports Atlas readiness, durable chain, node/edge and layer counts, missing/orphan
  connections, exact revision/scope/freshness/bounds, omissions, zero tests executed, and a
  prominent explicit interactive-Atlas action.
- Missing intent layers remain missing; no requirement, decision, issue, evidence, or delivery fact
  is fabricated from source or Git history.
- EN/TR, hostile/plain/narrow terminal, Ctrl+C, browser, package, security, deterministic-vault,
  approved-network, and full remote-CI gates pass.
- EVD-031 records exact commands, commits, package provenance, cache/network limits, fixed public
  smoke revision/license, remaining distribution limits, and final CI. Review passes only then.
- Phase 11C, tag, release, package publication, deployment, settings, visibility, telemetry, and
  announcements remain unchanged.

## Typed links

- drives:: [[Decisions/ADR-031 - Acquire explicit public repositories into a managed local cache]]
- tracked-by:: [[Issues/ISSUE-029 - Implement frictionless source-to-atlas onboarding]]
- proven-by:: [[Evidence/EVD-031 - Phase 15 source-to-atlas verification]]
