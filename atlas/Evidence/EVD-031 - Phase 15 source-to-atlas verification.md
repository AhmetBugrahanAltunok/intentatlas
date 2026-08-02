---
id: EVD-031
type: evidence
status: complete
phase: 15
---
# EVD-031 - Phase 15 source-to-atlas verification

## Entry and implementation identity

- Phase 14 passed at clean synchronized entry
  `a2250936e44fb7dc21634e6e8039ccadba8b1fed`.
- Planning commit: `888b38152daa1aa0983de5f77e571de40c0f3f6f`.
- Primary implementation commit: `492eca4c9312debfc36c2548a15cb01afe259e7c`;
  generated note [[Commits/Commit 492eca4 - Implement Phase 15 source-to-atlas onboarding]].
- Documentation normalization: `884ee80767f6e327725079a5f96652a6746f994f`.
- Compatibility-contract completion and locally verified implementation head:
  `e1f731385d1ae9e3217ca3b2acf9cf69a2b84f25`.
- Phase closure commit: `2a7b767142c7ed37eae41cca33b05bafc8d1cde6`.
- Local evidence commit `8426864f490705704f9dc970d6ae8fd598cef76b` was pushed to `main`.
  GitHub Actions run `30771447445` passed all `13/13` jobs at that exact head. Durable closure
  commit `2a7b767142c7ed37eae41cca33b05bafc8d1cde6` is synchronized here by exact identity and this
  synchronization head receives its own final-head CI verification.

## Change inventory

- `src/intentatlas/acquisition.py` adds strict HTTPS GitHub identity, fixed-argument inert Git,
  bounded shallow acquisition, exact revision/origin checks, atomic managed cache, locking,
  corruption recovery, safe inspection/removal, and non-secret metadata.
- `src/intentatlas/cli.py` adds TTY-only one-URL dispatch and offline `cache list/info/clear`;
  `src/intentatlas/onboarding.py` adds explicit remote consent and converges remote/local sources on
  the existing diagnostic, ChangeSet, in-memory scanner, ChangeReport, terminal sanitizer, and
  immutable browser snapshot.
- `tools/verify_pipx_install.py`, package manifest verification, and CI add exact-wheel isolated
  pipx install/reinstall/uninstall without adding a runtime dependency.
- `tests/test_acquisition.py`, `tests/test_source_to_atlas.py`, release and compatibility tests
  freeze URL rejection, resource bounds, execution/auth isolation, no-write behavior, cache
  lifecycle, TTY/non-TTY dispatch, immutable viewer bytes, and absent-intent truth.
- README/README.tr, installation, managed cache, guided CLI, security, architecture,
  compatibility, documentation index, changelog, roadmap, strategy, Issue, Evidence, Review, and
  handoff records preserve public-install, shallow-history, Phase 11C, and publication limits.
- Generated inventory includes [[Code/src - intentatlas - acquisition.py]],
  [[Code/tools - verify_pipx_install.py]], [[Tests/tests - test_acquisition.py]],
  [[Tests/tests - test_source_to_atlas.py]], and the implementation Commit note above.

## Focused and behavior results

- `python -m pytest tests/test_acquisition.py tests/test_guided_cli.py
  tests/test_source_to_atlas.py -q` passed; two link-capability cases were skipped on this Windows
  host. Ruff and mypy passed for all changed maintained source.
- Strict rejection covers HTTP, SSH/Git/file schemes, non-GitHub/localhost/IP hosts, port,
  credentials, query, fragment, repository page paths, malformed owner/repository, and traversal.
- Fixed Git arguments disable shell evaluation, global/system configuration, credentials,
  interactive prompts, redirects, hooks, external protocols, filters/LFS smudge, submodules, and
  project execution. Tests force output, zero-time, disk, checkout, interruption, corruption,
  refresh-failure, concurrency, metadata, traversal, and link boundaries and verify cleanup.
- A cached remote guide uses one explicit acquisition approval and no second scan. Before/after
  source bytes, mtimes, `HEAD`, and status remain identical. Terminal and viewer receive the same
  one-time graph/report bytes. Empty intent layers remain zero/missing; tests executed remains zero.
- Direct one-URL shorthand runs only with real stdin+stdout TTY. The exact installed wheel's
  non-TTY one-URL invocation returned argparse stderr/exit 2, empty stdout, and entered no guide,
  acquisition, or cache path. Existing local Phase 14 root/scope/EN/TR/hostile-terminal/browser
  behavior regressed cleanly.

## Full local quality and browser results

On Windows with Python `3.13.14`, at implementation head `e1f7313...`:

- `INTENTATLAS_REQUIRE_BROWSER=1 python -m pytest --cov=intentatlas --cov-report=term
  --cov-fail-under=80`: `500 passed, 4 skipped`; branch coverage `85.47%`; the real Chrome gate
  executed successfully.
- `python -m ruff check .`, `python -m mypy`, `python -m bandit -q -r src tools`,
  `node --check src/intentatlas/web/app.js`, `python -m pip check`, `git diff --check`, and clean
  worktree assertion all passed.
- The first complete run exposed only the intentionally added managed-cache compatibility row
  missing from its contract-count regression (`499 passed`). Commit `e1f7313...` names that
  contract and updates experimental count 4 -> 5; the complete suite then passed.
- Approved `python -m pip_audit --skip-editable` reported no known vulnerabilities; the editable
  local IntentAtlas distribution was explicitly skipped.

## Package and installation results

- Two `SOURCE_DATE_EPOCH=1704067200 python -m build --sdist --wheel` runs were byte-identical.
- `tools/verify_release.py` validated wheel `52` files and sdist `189` files, console entry point,
  package/source parity, archive safety, metadata, dependency-free runtime, web assets, and MIT
  boundary. Provenance binds source `e1f731385d1ae9e3217ca3b2acf9cf69a2b84f25` to:
  - wheel `intentatlas-0.3.0rc1-py3-none-any.whl`, SHA-256
    `7b1ffe4e2e6fe0a2563442f6e03e94cdf1909fce65dc029f28f2766674f19339`;
  - sdist `intentatlas-0.3.0rc1.tar.gz`, SHA-256
    `5446b815b11d4cecfa45281adefcb98d7ee82f9d62ad5b60244f74d25cb9d225`.
- The exact wheel passed temporary-root pipx install, command discovery, version/help, reinstall,
  repeated version, uninstall, and removal. A separate clean venv passed install/version/help/demo.
  The real user PATH and pipx roots were not changed.
- Building from the verified sdist reproduced the direct wheel SHA-256 exactly; its extracted full
  test suite passed.
- Remote CI passed Python 3.11/3.12/3.13 full test jobs, Windows/macOS/Linux Python 3.11/3.13
  installed-wheel E2E, real Chrome, static types, security/pip-audit, and reproducible package/pipx
  verification: `13/13` successful jobs in run `30771447445`.

## Approved public network smoke

- Explicit URL: `https://github.com/pypa/sampleproject`.
- Exact acquired revision: `621e4974ca25ce531773def586ba3ed8e736b3fc`; exact origin matched;
  checkout was clean and `git rev-parse --is-shallow-repository` returned `true`.
- Git depth bound was `50`; the merge DAG exposed `151` commits, demonstrating why depth is not a
  total-commit cap. Checkout contained `12` files and `13,390` bytes.
- `LICENSE.txt` is the MIT license; SHA-256
  `71e0bd649395f47e82b500dc6261ce4b8e8d03774727f583e09f5b947e75de97`.
- The initial smoke rejected this valid shallow clone because it assumed total commit count could
  not exceed Git depth. The corrected boundary requires Git's shallow state whenever the total
  exceeds depth, while retaining time/output/file/checkout/cache-disk limits. Focused and full
  regressions passed afterward.
- The cache remained under ignored `var/`; no third-party source, history, graph, or license was
  staged or committed.

## Vault and durable-chain results

- Two scans each reported `1,630 nodes`, `3,596 relationships`, and `1,456` generated notes. The
  second reused all three adapter partitions and rebuilt none.
- Explicit snapshots of `174` files in only Brain, Requirements, Decisions, Issues, Evidence,
  Reviews, and Sessions retained identical bytes, sizes, and mtimes. The second generated-note
  snapshot retained identical bytes, sizes, and mtimes for all `1,456` files.
- `intentatlas status` reported `durable orphans 0`.
- Durable chain: [[Requirements/REQ-031 - Open a trustworthy atlas from a local path or public GitHub URL]]
  -> [[Decisions/ADR-031 - Acquire explicit public repositories into a managed local cache]]
  -> [[Issues/ISSUE-029 - Implement frictionless source-to-atlas onboarding]] -> generated
  Code/Test notes -> this Evidence -> generated implementation Commit note.

## Remaining risks

- History is shallow and may omit older evidence; cache entries consume disk and a hit is an exact
  cached revision, never a latest-remote claim.
- `pipx install intentatlas` is not yet usable from a package index because no package was
  published. pipx, Python, and Git remain prerequisites; there is no zero-prerequisite Windows
  installer.
- Public/private authenticated repositories, redirects, other forges, GitHub page URLs,
  submodules, LFS materialization, and refresh UX are unsupported.
- Automated transcripts, owner checks, and this public smoke are technical evidence, not human
  usability observations. Phase 11C's five independent people and median-time gate remain open.
- Closure identity synchronization and its final-head CI are procedural post-commit checks; any
  failure reopens this Evidence and Review.

## Required evidence

- [x] Exact Phase 14 entry, implementation commits, generated implementation Commit note, pushed
      evidence head, `13/13` remote-CI run, exact closure commit, and complete change inventory.
- [x] Temporary pipx exact-wheel install/reinstall/uninstall and clean-shell command results without
      real user PATH/cache mutation; unpublished-package and Windows-installer boundary.
- [x] Strict URL normalization/rejection matrix and non-TTY zero-prompt/network/cache proof.
- [x] Fixed-argv inert Git configuration, timeout/output/file/byte/disk/history limits, exact SHA,
      no auth/hook/filter/LFS/submodule/project execution, and Private exclusion.
- [x] Atomic cache staging/promotion, lock contention, hit/freshness, refresh/corruption recovery,
      prior-good preservation, injected roots, and traversal/link-safe list/info/clear results.
- [x] Local/remote production diagnostic/scanner/ChangeReport parity, source no-write proof, one
      immutable terminal/browser snapshot, no invented intent, and EN/TR/accessibility results.
- [x] Focused/full coverage, Ruff, mypy, Bandit, Node/browser, pip-check/audit, deterministic
      wheel/sdist/provenance, installed command, extracted sdist, vault determinism, and zero orphans.
- [x] Separate approved real-network smoke with a small fixed public GitHub source, exact revision,
      verified license identity/hash, and no third-party source committed.
- [x] Final limitations: shallow history, cache disk use, public package not yet published,
      zero-prerequisite Windows install absent, and no human-usability/time claim.

## Open gates

No acceptance gate remains open. The closure/synchronization commits must retain a clean tree and
green final-head CI; a failure reopens the phase. Phase 11C remains owner-controlled.

## Typed links

- proves:: [[Requirements/REQ-031 - Open a trustworthy atlas from a local path or public GitHub URL]]
- references:: [[Decisions/ADR-031 - Acquire explicit public repositories into a managed local cache]]
- references:: [[Issues/ISSUE-029 - Implement frictionless source-to-atlas onboarding]]
- reviewed-by:: [[Reviews/Phase 15 Source-to-Atlas Review]]
- strategy:: [[Brain/Phase 15 Source-to-Atlas Strategy]]
- implementation-commit:: [[Commits/Commit 492eca4 - Implement Phase 15 source-to-atlas onboarding]]
