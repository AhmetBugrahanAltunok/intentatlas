---
id: EVD-030
type: evidence
status: in-progress
phase: 14
---
# EVD-030 - Phase 14 guided CLI verification

This is the required verification plan. It is not evidence that Phase 14 has passed.

## Claim to verify

An installed IntentAtlas CLI can turn an interactive zero-argument invocation into a minimal,
truthful, no-write path to the existing ChangeReport while preserving every explicit CLI/JSON,
privacy, fallback, omission, packaging, and automation contract.

## Required evidence

- [ ] Exact clean starting revision, Phase 13 entry Review, implementation revisions, closure head,
      generated Commit notes, and pushed remote-CI head.
- [x] Complete inventory of CLI/parser, onboarding, localization, terminal-safety, documentation,
      package, workflow, vault, and test changes.
- [x] Transcript proving one command and at most one Enter reach the report from a repository root;
      nested-directory and outside-repository paths remain within the declared interaction budget.
- [x] Deterministic scope cases for conflict, unstaged, untracked, staged-only, clean HEAD, detached
      HEAD, unborn, empty, one-commit, explicit commit, and explicit range behavior.
- [x] Before/after filesystem metadata and Git snapshots proving diagnostic, default report,
      cancellation, errors, details, language switching, command recipes, and rejected browser
      selection are no-write.
- [x] Explicit proof of no project code/test/hook/build/package/compiler/plugin/indexer execution,
      no external request/telemetry/update check, no recent-project/preference persistence, and no
      `atlas/Private/` read or enumeration.
- [x] Guided summary/details parity with the same immutable ChangeReport across exact scope/revision,
      state, freshness, threshold, counts, ordering, scores, confidence, reasons, evidence paths,
      omission classes, strategy, advisory, and zero executed tests.
- [x] Targeted, targeted-plus-full-suite, full-suite-fallback, abstain-and-full-suite,
      no-targets-found, no-changes, stale, ambiguous-owner, unsupported-language, oversized,
      truncated, and budget-failure transcripts.
- [x] TTY dispatch and explicit `guide` pass while empty-argv non-TTY, redirected, pipe, and CI cases
      preserve stderr/exit 2 and prove no input consumption, wait, repository scan, or write.
- [x] Ctrl+C/exit-130, Q/EOF, invalid/missing/file/quoted/spaced/Unicode/UNC paths, Git missing,
      non-Git repo, invalid config, unsafe vault, symlink/junction, permissions, concurrent mutation,
      and terminal control/ANSI/bidi/newline injection results.
- [x] English/Turkish semantic parity, locale/explicit override/fallback, canonical unlocalized
      enums/commands/JSON, narrow terminals, screen-reader linear ordering, `NO_COLOR`, `TERM=dumb`,
      and encoding fallback results.
- [x] Explicit browser selection serves the exact prior snapshot on IPv4 loopback and an ephemeral
      port; refusal creates no listener; browser failure retains a usable URL/result; Host, headers,
      escaping, keyboard/accessibility, and bounded queries pass in real Chrome.
- [x] Existing `--help`, `--version`, commands, flags, supported text/JSON meanings, schema output,
      stable ordering, stdout/stderr separation, and exit codes pass compatibility regressions.
- [x] Clean installed-wheel guided/explicit CLI flows on supported platforms and Python versions,
      extracted-sdist full suite, and deterministic fixed-epoch package/provenance verification.
- [x] Focused guided/CLI/diagnostic/report/security/browser tests and complete browser-required
      coverage, Ruff, Mypy, Bandit, Node syntax, pip-check, and diff-check results.
- [ ] Two-pass vault bytes/mtime determinism, explicit user-owned snapshot, zero-orphan result, and
      complete REQ-030 -> ADR-030 -> ISSUE-028 -> Code/Test -> EVD-030 -> Commit assertions.
- [ ] Approved dependency network audit and complete remote CI, or an explicit open gate.
- [x] Final limitations and risks, including that technical transcripts and any owner walkthrough
      are not independent human usability evidence and cannot supply a time median.

## Planned focused verification

```text
python -m pytest tests/test_guided_cli.py tests/test_cli.py tests/test_diagnostic.py \
  tests/test_trust_first.py tests/test_change_report.py tests/test_onboarding_walkthroughs.py \
  tests/test_security.py -q
```

The implementation may refine exact test filenames, but EVD-030 must record the commands actually
run and may not replace full closure gates with this focused set.

## Entry and implementation identity

- Phase 13 entry Review: [[Reviews/Phase 13 Semantic Monorepo Foundation Review]] — `pass` before
  Phase 14 implementation.
- Clean accepted planning HEAD: `99aafce7748db44ded2a99791ba0cb245c04f49f`.
- Pre-plan synchronized `origin/main`: `6679150554a513b7ab11f59e2fd1074bd9282f24`.
- Implementation commit: `644d8b9003857a3cb95abfd16dd182b093471376`.
- Closure commit, generated Commit-note link, pushed head, and remote CI remain pending at this
  checkpoint; Phase 14 is not yet closed.

## Change inventory

- `src/intentatlas/onboarding.py`: injected line terminal, EN/TR catalog, control/ANSI/bidi/newline
  sanitization, safe root resolution, deterministic Git scope selection, immutable report snapshot,
  progressive detail/actions, and explicit ephemeral-loopback viewer handoff.
- `src/intentatlas/cli.py`: TTY-only empty-argv pre-dispatch and additive `guide [PATH]` parser route;
  existing argparse route remains authoritative for non-TTY and explicit commands.
- Tests: `tests/test_guided_cli.py` freezes root/scope/no-write/no-execution/localization/error/
  omission/strategy/browser semantics; E2E, release, trust-first, and compatibility tests cover the
  installed package and public contracts.
- Package verification requires `intentatlas/onboarding.py` in both wheel and sdist payloads.
- README/README.tr and guided CLI, trust-first, architecture, compatibility, observation, index,
  and changelog docs describe the one-command path without changing Phase 11C.
- No runtime dependency, workflow permission, language adapter, resolver, scoring, recommendation,
  telemetry, hosted behavior, plugin/indexer execution, or publication surface was added.

## Local verification results

All commands below ran on Windows with Python `3.13.14`; supported cross-platform/Python matrix
execution remains a remote-CI closure gate.

- Planned focused suite (51 collected):
  `python -m pytest tests/test_guided_cli.py tests/test_cli.py tests/test_diagnostic.py
  tests/test_trust_first.py tests/test_change_report.py tests/test_onboarding_walkthroughs.py
  tests/test_security.py -q` — passed with one environment-dependent directory-link skip.
- Browser-required full coverage:
  `INTENTATLAS_BROWSER_REQUIRED=1 python -m pytest --cov=intentatlas
  --cov-report=term-missing --cov-fail-under=80` — `465 passed, 3 skipped`, total coverage
  `85.94%`.
- `python -m ruff check .` — passed.
- `python -m mypy` — passed for 44 source files.
- `python -m bandit -q -r src tools` — passed.
- `python -m pip check` — `No broken requirements found`.
- `node --check src/intentatlas/web/app.js` and `git diff --check` — passed.
- `INTENTATLAS_BROWSER_REQUIRED=1 python -m pytest tests/test_browser_e2e.py -q` — `2 passed`
  in real Chrome-family execution.
- Approved `python -m pip_audit --skip-editable` — `No known vulnerabilities found`; only the
  unpublished editable IntentAtlas distribution was intentionally skipped.

## Package and provenance results

Fixed `SOURCE_DATE_EPOCH=1785703508` builds at implementation revision
`644d8b9003857a3cb95abfd16dd182b093471376` passed `tools/verify_release.py`:

- wheel: `intentatlas-0.3.0rc1-py3-none-any.whl`, SHA-256
  `5909f789d902282b2933bf90ff53b84fd9f27e28a86ff59855c3c9eeac619bc0`, 170706 bytes,
  51 validated members;
- sdist: `intentatlas-0.3.0rc1.tar.gz`, SHA-256
  `098ce7716a92c7b32abe46b85e6303cf7d370606358e27d0e36f1bacaee58be6`, 296104 bytes,
  183 validated members;
- repeated artifacts were byte-identical; the wheel rebuilt from the sdist reproduced the direct
  wheel hash exactly;
- clean installed-wheel `--version`, deterministic demo JSON, empty-argv non-TTY exit 2, explicit
  guide non-TTY exit 2, and `tests/test_e2e.py` passed;
- the extracted sdist full suite passed with browser-required coverage enabled.

The first extracted-sdist wrapper stopped because it referenced a nonexistent archive-local
`.venv`; it performed no source mutation. The corrected command used the exact absolute verified
environment interpreter and passed the full suite. This corrected final result, rather than the
wrapper error, is the closure evidence.

## Technical transcript findings

- One empty-argv TTY dispatch, one visible root/scope confirmation, and one Enter reach the same
  production ChangeReport; non-TTY empty argv neither consumes supplied stdin nor calls the guide.
- Before/after byte, size, mtime, Git status, staged diff, and worktree diff snapshots are identical
  across the common result and progressive reasons/omissions/details/commands/language actions.
- A subprocess guard observed only bounded `git` invocations during the common guide path; no test,
  hook, project code, shell, build/package tool, compiler, plugin, indexer, update check, telemetry,
  preference, or recent-project action occurred.
- Targeted, targeted-plus-full-suite, full-suite-fallback, abstain-and-full-suite, no-targets-found,
  no-changes, stale, threshold omission, limit omission, diagnostic ambiguity/unsupported/
  oversized/truncated limits, and analysis-budget errors retain production meanings.
- EN/TR renderings preserve canonical enums/IDs/commands/flags/JSON and the same no-write,
  execution-free, Private-safe, omission, strategy, advisory, and zero-test meanings.
- Viewer selection passes the exact serialized graph/report bytes from one collection call to
  `127.0.0.1` port `0`; refusal calls no listener; browser/listener failure preserves the terminal
  result. Existing Host/header/escaping/keyboard/accessibility/bounded-query behavior passed Chrome.
- No native PTY helper is installed in the local Windows environment, so injected TTY streams
  exercise the state machine locally; real console/OS/Python combinations remain covered by remote
  installed-wheel CI. Non-TTY behavior was verified in real subprocesses and a clean wheel.

## Limitations and remaining gates

- Generated vault/Commit-note determinism and final durable-chain assertions are not yet recorded.
- Final push and remote CI are not yet recorded; Phase 14 remains open until both pass at one exact
  pushed head.
- No public tag, release, package publication, deployment, settings/visibility change, announcement,
  telemetry, or Phase 11C action occurred.

## Open risk carried to Phase 11C

External human usability remains unverified. No synthetic transcript, pseudo-TTY, automated
walkthrough, owner dry run, model, or agent counts as an independent participant. Phase 11C still
requires five consented first-run observations and the separately defined below-ten-minute median
before public launch or any real user-time claim.

## Typed links

- proves:: [[Requirements/REQ-030 - Make trustworthy analysis effortless from the CLI]]
- references:: [[Decisions/ADR-030 - Layer a TTY-guided flow over deterministic contracts]]
- references:: [[Issues/ISSUE-028 - Implement one-command guided CLI onboarding]]
- reviewed-by:: [[Reviews/Phase 14 One-Command Guided CLI Review]]
- strategy:: [[Brain/Phase 14 Guided CLI Strategy]]
