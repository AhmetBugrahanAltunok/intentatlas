# One-command guided CLI

Run `intentatlas` inside a trusted Git repository in a real interactive terminal. IntentAtlas
finds only the nearest enclosing safe Git root, displays that root and a conservative default
scope, and waits for confirmation. Press Enter once to analyze; use `S` to choose another bounded
scope or `Q` to leave without persistent output. An explicit path or strict public GitHub URL is
also supported:

```text
intentatlas guide [PATH_OR_PUBLIC_GITHUB_URL]
intentatlas https://github.com/OWNER/REPOSITORY
```

Empty arguments open the guide only when both stdin and stdout are TTYs. A pipe, redirected stream,
CI process, or other non-TTY context retains the existing argparse diagnostic on stderr and exit
code 2. It never prompts, scans, or waits. The explicit `guide` command also refuses non-TTY use
and points to `intentatlas diagnose PATH` plus `intentatlas changes PATH --commit HEAD --report`
(or `--worktree --report`) as non-interactive alternatives.
If the command was installed into a virtual environment, activate that environment first or invoke
its `intentatlas` executable by full path.

## Scope and trust contract

The default is selected from bounded Git metadata in this order:

1. conflicts or unstaged/untracked files: `worktree`;
2. staged changes only: `staged`;
3. clean repository: the full resolved `HEAD` commit;
4. unborn repository: `worktree`.

The root and scope appear before analysis. The guide rejects files, symbolic-link/junction roots,
unsafe Git markers, missing repositories, and literal or configured `atlas/Private` targets. It
ascends only through parents; it does not scan siblings or the wider filesystem. A UNC path does
not receive a claim that operating-system filesystem access is network-free.

Local paths are offline at the application boundary and create no project, vault, cache, graph,
report, test, or Git output. A public GitHub URL requires an explicit Enter after a summary naming
the HTTPS request and managed-cache write. Acquisition is shallow and bounded, rejects private or
authenticated repositories, and disables prompts, redirects, hooks, filters, submodules, LFS,
user Git configuration, and project execution. After acquisition, the exact cached revision and
scope are shown and the same no-write analysis runs. See the
[managed-cache contract](managed-repository-cache.md).

The guide does not run `init`, `scan`, persistent `open`, tests, hooks,
project code, shell commands, package managers, compilers, plugins, or indexers. Commands shown in
the help action are text only. Ctrl+C, EOF, and `Q` leave safely.

## Result semantics

The guide calls the production diagnostic, ChangeSet, structural scan, and Change Report paths.
It does not contain a separate analysis or scoring engine. The summary preserves exact scope and
resolved revisions, analysis state and freshness, confidence threshold, selected/candidate/
filtered/limit-omitted counts, reasons and evidence, omission causes, test strategy, advisory, and
`Tests executed: 0`.

`fallback` and `unknown` retain their production full-suite meanings. A candidate that is not
selected is only below the displayed threshold or beyond the displayed result limit; it is never
claimed to be unaffected or unnecessary. Complete details are the unchanged schema-1 Change
Report JSON. Human copy can be switched between English and Turkish without rescanning; enum
values, IDs, commands, flags, and JSON remain canonical.

The two Enter actions are deliberately contextual and are labeled on their respective screens:
Enter on the confirmation screen starts the displayed analysis, while Enter on the result action
screen exits exactly like `Q`. Result actions `1` through `6` and `L` always require their explicit
key; Enter never repeats the analysis or opens the viewer.

The browser is optional and starts only after the explicit viewer menu choice. It binds to numeric
IPv4 loopback on an ephemeral port and receives the exact immutable graph/report bytes already
used by the terminal result. There is no second scan. If the browser or listener is unavailable,
the terminal result remains valid and the guide reports the failure.

Output is line-oriented, color-independent, keyboard-only, and screen-reader compatible. Control
characters, ANSI escape sequences, bidirectional controls, and embedded newlines from untrusted
repository labels or paths are escaped before terminal rendering. No full-screen TUI, cursor
animation, or runtime dependency is introduced.

The PowerShell-friendly presentation begins with a prominent ASCII-safe IntentAtlas banner and
groups output under Source and Scope, Safety Boundary, Analysis Result, Recommendations, Atlas
Snapshot, and Next Action. Long sanitized evidence is wrapped, and every choice is printed on its
own line. These sections are presentation only: they do not alter the report, consent, no-write,
scope, revision, omission, or fallback contracts described above.

In the interactive viewer, opening or closing Change Report preserves document scroll while moving
keyboard focus. Repeating Change Report and Fit Graph therefore keeps the same settled graph
transform and viewport geometry; initial bounded force-layout motion remains intentional.

This technical onboarding path is not human usability evidence. Phase 11C still requires five independent
consented observations and a median time below ten minutes before public launch or any
real user-time claim.
