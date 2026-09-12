# Workflows

The guided flow, public-repository analysis, the packaged demo, the zero-footprint expert
preview, and deliberate adoption of the persistent vault. For installing and your first
command, see the [README](../README.md).

From a real repository in an interactive terminal, run one command:

```powershell
intentatlas
```

IntentAtlas shows the nearest safe Git root and a conservative scope before doing the analysis.
Press Enter once to accept it. Conflict, unstaged, or untracked state selects `worktree`; a
staged-only repository selects `staged`; a clean repository selects the exact `HEAD`; an unborn
repository selects `worktree`. The result uses the production Change Report and writes nothing.
Pipes, redirects, CI, or any other non-TTY invocation keep argparse's existing stderr/exit-2
behavior and never prompt or scan. Use `intentatlas guide [PATH]` for the same flow at an explicit
path. See the [guided CLI contract](guided-cli.md).

The interactive transcript uses a prominent IntentAtlas heading, clearly named source/safety/
analysis/recommendation/Atlas sections, wrapped evidence, and one option per line. The browser
viewer keeps page and graph geometry stable when **Change report** and **Fit graph** are used
repeatedly.

To analyze a public GitHub repository without cloning it manually, use a real interactive
terminal:

```text
intentatlas https://github.com/OWNER/REPOSITORY
# or: intentatlas guide https://github.com/OWNER/REPOSITORY
```

Before any network or cache effect, IntentAtlas shows the normalized URL, managed-cache write,
shallow/resource bounds, and disabled execution behavior. Enter is the only approval. The result
shows the exact cached revision and uses the same production, no-write Change Report and immutable
viewer snapshot. Private/authenticated repositories, redirects, repository page URLs, hooks,
filters, LFS, submodules, and project execution are unsupported. See the
[managed repository cache](managed-repository-cache.md).

To evaluate the packaged synthetic contract without touching a repository:

```powershell
intentatlas demo --report text
intentatlas demo --report json
intentatlas demo
```

The built-in showcase is original, offline, and temporary. Its synthetic graph and relationships
are prebuilt, so it exercises the production graph, recommendation, report, and viewer layers but
does not exercise repository discovery, AST parsing, or Git diff extraction. It does not scan the
current directory. See the [guided demo](guided-demo.md).

The explicit expert commands remain available for a zero-footprint preview:

```powershell
intentatlas diagnose C:\path\to\your-project
# Then run the exact Next safe command it prints. Examples:
intentatlas changes C:\path\to\your-project --worktree --report
intentatlas changes C:\path\to\your-project --commit HEAD --report --format json
```

These commands are offline and no-write. The diagnostic reports bounded capability, ambiguity,
evidence readiness, and the safe next command. The report states its exact revision and scope,
freshness, confidence threshold, selected and omitted candidates, recorded ranking paths, and
fallback test strategy. An omission is not proof that intent is unaffected or a test unnecessary.
If a saved graph exists, `diagnose` also reports the number of detected Python test files and exact
`python-symbol-reference` test links. `missing-exact-links` means tests were found but no exact
symbol-to-test edge was formed; it is not a ready result. Graph freshness is still not assessed.
For the next command, `diagnose` selects `worktree` for unstaged, untracked, or conflicted changes;
`staged` when only the index changed; exact `HEAD` when the working copy is clean; and `worktree`
for a repository with no commit yet. This prevents a dirty working copy from being mistaken for
the committed `HEAD` snapshot.
Only `--open` explicitly starts the loopback-only viewer for that same in-memory report snapshot.
See the [trust-first preview](trust-first-preview.md) and [documentation index](index.md).

After interpreting the preview, deliberately adopt the persistent vault workflow:

```powershell
intentatlas init C:\path\to\your-project
intentatlas scan C:\path\to\your-project
intentatlas open C:\path\to\your-project
```

If you do not want to write into an active repository yet, try these three commands in a disposable
copy or small test repository first. `init` creates `intentatlas.json`, starter Markdown folders,
portable Obsidian settings, and missing local-state `.gitignore` rules. `scan` writes the disposable
`.intentatlas/` cache and generated areas under `atlas/`; it never executes project code and never
overwrites user-owned notes. Review `git status` before committing anything.

`init` creates generic guidance and empty intent folders; it never seeds IntentAtlas's own
requirements, decisions, evidence, reviews, or dated sessions into the target repository.
It also preserves the existing `.gitignore` and adds only missing local-state rules for
`.intentatlas/`, `.venv-intentatlas/`, and Obsidian workspace/cache files. The durable `atlas/`
notes and portable Obsidian settings remain trackable.
Obsidian is optional: `atlas/` is the Markdown layer used by the persistent workflow, but you can
inspect the same generated graph with `intentatlas open` without installing Obsidian.

`status`, `impact`, `recommend-tests`, `diff`, and recommendation evaluation read the persistent
graph and therefore require `scan` first. `diagnose`, `guide`, and `changes --report` perform their
own read-only inspection and do not require a saved graph.

For `impact`, `TARGET` may be an exact graph ID (`commit:FULL_SHA` or
`symbol:src/auth.py::rotate_session`), a project-relative path such as `src/auth.py`, an exact
label, or a unique partial match:

```text
intentatlas impact src/auth.py C:\path\to\your-project --depth 2
intentatlas impact symbol:src/auth.py::rotate_session C:\path\to\your-project --direction upstream
```

Every two spaces in the result means one relationship hop from the original target. Rows are a
flat traversal result; an indented row is not a child of the line immediately above it.
Commands with optional `[PATH]` use the current directory when it is omitted. `impact` and
`recommend-tests` print the resolved project root so a graph from the wrong directory is visible.

Repeated CLI scans reuse a bounded content-addressed fragment for each unchanged built-in language
adapter. The command reports reused and rebuilt adapter counts. This cache contains graph metadata,
not source text, and is always safe to remove; a malformed or stale entry is rebuilt. Graph and
cache files are replaced atomically. See [incremental scanning](incremental-scanning.md).

If you use Obsidian, open the `atlas/` directory as a vault. Its standard Graph View will show
requirements, decisions, code, tests, evidence, and commits as color-coded nodes.

On macOS or Linux, use an explicit path such as `/path/to/your-project`. If the environment is not
activated, invoke `intentatlas` from the environment folder selected during installation.

Python 3.11, 3.12, and 3.13 are supported. The complete suite runs on Linux, while an installed
wheel smoke test covers the CLI, scan, recommendation, and loopback viewer workflow on Linux,
Windows, and macOS for the oldest and newest supported Python versions. CI also runs maintained
source typing, immutable Action-reference policy, and real-browser rendering gates. See
[the release process](../RELEASING.md) for the local reproducibility and artifact checks.
The candidate's exact wheel also passes an isolated pipx install/reinstall/uninstall lifecycle,
but no package has been published and no zero-prerequisite Windows installer exists. See
[installation status](installation.md).


## The project brain

The `atlas/` vault deliberately separates ownership:

- `Brain/`, `Requirements/`, `Decisions/`, `Issues/`, `Evidence/`, `Reviews/`, and `Sessions/`
  are written by people and agents.
- `Code/`, `Symbols/`, `Tests/`, and `Commits/` are generated by the scanner.
- `Private/` is local-only, user-provisioned, ignored by Git, and never created or scanned by
  IntentAtlas.

Generated-note synchronization prepares the complete desired view before changing files. It
leaves byte-identical notes untouched, atomically replaces changed notes with bounded retries for
transient file locks, and removes stale generated notes only after every desired note is present.
A persistent error therefore fails clearly without first deleting the previous generated view.

Folders group by purpose; links group by meaning. An orphaned durable note is treated
as a health issue, because project knowledge only becomes useful when it is connected.

Typed Markdown links use the portable `relation:: [[target]]` form. For example,
`drives:: [[Decisions/ADR-001 - Vault-first intent graph]]` preserves the meaning of a link;
ordinary wikilinks remain safe generic references.

