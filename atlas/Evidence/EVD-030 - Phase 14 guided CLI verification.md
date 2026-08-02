---
id: EVD-030
type: evidence
status: pending
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
- [ ] Complete inventory of CLI/parser, onboarding, localization, terminal-safety, documentation,
      package, workflow, vault, and test changes.
- [ ] Transcript proving one command and at most one Enter reach the report from a repository root;
      nested-directory and outside-repository paths remain within the declared interaction budget.
- [ ] Deterministic scope cases for conflict, unstaged, untracked, staged-only, clean HEAD, detached
      HEAD, unborn, empty, one-commit, explicit commit, and explicit range behavior.
- [ ] Before/after filesystem metadata and Git snapshots proving diagnostic, default report,
      cancellation, errors, details, language switching, command recipes, and rejected browser
      selection are no-write.
- [ ] Explicit proof of no project code/test/hook/build/package/compiler/plugin/indexer execution,
      no external request/telemetry/update check, no recent-project/preference persistence, and no
      `atlas/Private/` read or enumeration.
- [ ] Guided summary/details parity with the same immutable ChangeReport across exact scope/revision,
      state, freshness, threshold, counts, ordering, scores, confidence, reasons, evidence paths,
      omission classes, strategy, advisory, and zero executed tests.
- [ ] Targeted, targeted-plus-full-suite, full-suite-fallback, abstain-and-full-suite,
      no-targets-found, no-changes, stale, ambiguous-owner, unsupported-language, oversized,
      truncated, and budget-failure transcripts.
- [ ] TTY dispatch and explicit `guide` pass while empty-argv non-TTY, redirected, pipe, and CI cases
      preserve stderr/exit 2 and prove no input consumption, wait, repository scan, or write.
- [ ] Ctrl+C/exit-130, Q/EOF, invalid/missing/file/quoted/spaced/Unicode/UNC paths, Git missing,
      non-Git repo, invalid config, unsafe vault, symlink/junction, permissions, concurrent mutation,
      and terminal control/ANSI/bidi/newline injection results.
- [ ] English/Turkish semantic parity, locale/explicit override/fallback, canonical unlocalized
      enums/commands/JSON, narrow terminals, screen-reader linear ordering, `NO_COLOR`, `TERM=dumb`,
      and encoding fallback results.
- [ ] Explicit browser selection serves the exact prior snapshot on IPv4 loopback and an ephemeral
      port; refusal creates no listener; browser failure retains a usable URL/result; Host, headers,
      escaping, keyboard/accessibility, and bounded queries pass in real Chrome.
- [ ] Existing `--help`, `--version`, commands, flags, supported text/JSON meanings, schema output,
      stable ordering, stdout/stderr separation, and exit codes pass compatibility regressions.
- [ ] Clean installed-wheel guided/explicit CLI flows on supported platforms and Python versions,
      extracted-sdist full suite, and deterministic fixed-epoch package/provenance verification.
- [ ] Focused guided/CLI/diagnostic/report/security/browser tests and complete browser-required
      coverage, Ruff, Mypy, Bandit, Node syntax, pip-check, and diff-check results.
- [ ] Two-pass vault bytes/mtime determinism, explicit user-owned snapshot, zero-orphan result, and
      complete REQ-030 -> ADR-030 -> ISSUE-028 -> Code/Test -> EVD-030 -> Commit assertions.
- [ ] Approved dependency network audit and complete remote CI, or an explicit open gate.
- [ ] Final limitations and risks, including that technical transcripts and any owner walkthrough
      are not independent human usability evidence and cannot supply a time median.

## Planned focused verification

```text
python -m pytest tests/test_guided_cli.py tests/test_cli.py tests/test_diagnostic.py \
  tests/test_trust_first.py tests/test_change_report.py tests/test_onboarding_walkthroughs.py \
  tests/test_security.py -q
```

The implementation may refine exact test filenames, but EVD-030 must record the commands actually
run and may not replace full closure gates with this focused set.

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
