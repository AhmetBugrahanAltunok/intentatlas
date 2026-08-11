# Recommendation evaluation

IntentAtlas can compare its existing test recommendations with an explicitly complete,
human-reviewed label set. Evaluation is local and deterministic: it reads the saved graph and a
project-local JSON file, but never executes tests, project code, language runtimes, or network
requests.

## Label schema

Schema 1 accepts exactly these fields:

```json
{
  "schema_version": 1,
  "name": "Reviewed changes",
  "label_policy": "complete-test-set",
  "cases": [
    {
      "id": "authentication-change",
      "target": "commit:0123456789abcdef",
      "expected_tests": ["tests/test_auth.py"]
    }
  ]
}
```

`target` must be an exact graph ID for a commit, file, symbol, or test. Every expected test must
be a project-relative POSIX path that resolves exactly to a test node in the graph. An empty
`expected_tests` list is valid and measures unwanted recommendations.

`complete-test-set` is a closed-world promise by the reviewer: every relevant test for the case is
listed. Without that promise, an unlisted recommendation cannot honestly be classified as a false
positive and recall cannot be interpreted reliably.

Labels are interpreted against the current saved graph and current test suite. A historical commit
is the change target, but relevant tests added later still belong in its complete set if they now
exercise that behavior. Labels therefore require renewed human review when test dependencies
change; they are not immutable historical truth.

The parser rejects unknown and duplicate fields, duplicate cases and targets, unsafe paths,
symbolic-link inputs, malformed types, stale graph identities, files over 1 MB, more than 500
cases, or more than 1,000 expected tests per case. The CLI additionally requires the label file to
remain below the project root and outside `atlas/Private/`.

## Metrics

For the selected confidence threshold and per-case result limit:

- true positive (TP): recommended and expected;
- false positive (FP): recommended but not expected;
- false negative (FN): expected but not recommended;
- precision: `TP / (TP + FP)`;
- recall: `TP / (TP + FN)`.

Aggregate precision and recall are micro averages calculated from summed counts. When a metric
has no denominator, JSON represents it as `null` and text represents it as `n/a`.

## CLI

This command reads the project's saved graph. Run `scan` with the same IntentAtlas executable
first. Commit targets in a label file must fall within the configured `git_history_limit`; if a
pinned commit has aged out of that bounded history, increase the limit (maximum 250) or renew the
reviewed labels. Missing targets and tests produce an error that distinguishes these next steps.

```console
intentatlas scan
intentatlas evaluate-recommendations benchmarks/intentatlas-recommendations.json
intentatlas evaluate-recommendations benchmarks/intentatlas-recommendations.json --minimum-confidence high
intentatlas evaluate-recommendations benchmarks/intentatlas-recommendations.json --format json
```

Text and JSON output contain no timestamps and are stable for an unchanged graph, label file, and
options. Metrics describe only the reviewed label cases; they do not prove accuracy on other
commits or repositories.

`evaluate-corpus` has a different input contract: its manifest points to bundled saved graphs, so
it does not read the current project's persistent graph and does not require `scan`.
