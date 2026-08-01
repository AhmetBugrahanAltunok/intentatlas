# CI shadow review

`intentatlas review` evaluates one explicit Git revision range through the same bounded ChangeSet,
freshness, requirement-impact, and test-policy pipeline used by `changes --report`.

```text
intentatlas review [PATH] --base <revision> --head <revision> [--format markdown|json|sarif]
                   [--test-outcomes <project-relative-json>]
```

The default Markdown format is suitable for a local artifact. JSON embeds Change Report schema 1
inside Review Report schema 1. SARIF 2.1.0 provides fixed rules for incomplete analysis, possible
requirement impact, and full-suite fallback. All three formats are deterministic for the same
repository state, revisions, confidence threshold, and result limit.

## Shadow-mode contract

- A valid analysis returns exit status 0 even when findings exist.
- The command does not execute project code or tests.
- It does not call a hosting-provider API, upload an artifact, comment on a pull request, or require
  credentials or network access.
- Findings are advisory structural evidence. They do not prove that a requirement changed, a test
  is required, or omitted behavior is unaffected.
- `fallback` and `unknown` analysis retain the conservative full-suite policy.

Invalid revisions, unsafe repository state, malformed configuration, and exceeded safety bounds
remain ordinary command errors and return a nonzero status.

## Commit-keyed test outcomes

An optional sidecar can describe the complete set of test paths executed for one exact commit:

```json
{
  "schema_version": 1,
  "commit": "0123456789abcdef0123456789abcdef01234567",
  "test_set_policy": "complete-executed-set",
  "tests": [
    {"path": "tests/test_auth.py", "status": "passed", "duration_ms": 18},
    {"path": "tests/test_profile.py", "status": "failed"}
  ]
}
```

The loader requires a full commit ID, canonical project-relative unique paths, fixed statuses, and
bounded optional durations. It rejects unknown fields, duplicate JSON keys, symbolic links,
absolute or traversal paths, oversized files, and locations outside the project or under
`atlas/Private/`. Failure output, source snippets, environment values, and timestamps are outside
the schema.

When `commit` exactly equals the resolved review head, the report lists selected candidates that
were executed, selected candidates not executed, and executed paths outside the selected list. If
the identities differ, freshness is `stale` and all comparison sets are withheld. These are facts
about one execution, not false-positive/false-negative or correctness labels.

## SARIF safety boundary

SARIF results are capped at 1,000 and sorted deterministically. Artifact locations are emitted only
when a changed path is safe and project-relative. When available, a location contains the first
bounded current-side hunk region. Results contain no raw diff lines, source snippets, absolute
paths, environment values, or credentials.

The initial command writes only to standard output. A future opt-in workflow may save that output
as a CI artifact, but publication and blocking policy are intentionally separate, explicit steps.

`--open` serves the exact fresh in-memory graph and Review Report on a loopback-only viewer. It does
not persist a second report or fall back to the graph cache. The panel shows revision scope,
strategy, possible intent, candidate tests, and aligned/stale outcome evidence with the same
advisory language as the serialized formats.

## Opt-in composite Action

The repository includes `.github/actions/intentatlas-review/action.yml`. It must be invoked
explicitly after a full Git checkout; merely installing IntentAtlas does not enable a workflow.

```yaml
- id: intentatlas
  uses: ./.github/actions/intentatlas-review
  with:
    base: ${{ github.event.pull_request.base.sha }}
    head: ${{ github.event.pull_request.head.sha }}
    format: sarif
    test_outcomes: .intentatlas/test-outcomes.json
```

The Action loads IntentAtlas from its own checked-out `src/` tree, runs the public `review` command,
and writes one report below the runner's temporary directory. The `report` output contains that
local path. It does not accept a token, request permissions, publish a job summary, upload the
report, or modify a pull request. A calling workflow must make any later publication decision
explicitly.
