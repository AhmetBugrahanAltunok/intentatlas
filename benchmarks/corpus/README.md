# Original recommendation corpus fixtures

These schema-1 graph and label pairs are small, original IntentAtlas regression scenarios. They
contain no copied source code, repository history, logo, or data from another project and remain
inside IntentAtlas's MIT license boundary.

- `python-auth` models an exact Python symbol change, one directly changed test, one relevant
  structural test, and one broad structural false positive.
- `typescript-checkout` models a TypeScript file fallback with one relevant structural test and
  one weak filename-convention false positive.
- `go-package` models a directly changed Go test plus a broad package-level integration test that
  does not exercise the changed behavior.

Every label uses `complete-test-set` and was selected from the scenario's stated behavior, not
copied from evaluator output. These deliberately small graphs test confidence and aggregation
semantics. They are not full repositories and do not establish accuracy on real-world projects.

Run all three thresholds from the repository root:

```console
intentatlas evaluate-corpus benchmarks/recommendation-corpus.json
intentatlas evaluate-corpus benchmarks/recommendation-corpus.json --format json
```
