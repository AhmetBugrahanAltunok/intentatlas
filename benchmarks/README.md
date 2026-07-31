# Recommendation evaluation benchmarks

`intentatlas-recommendations.json` is the first reviewed, self-hosted IntentAtlas baseline. Each
case uses the `complete-test-set` policy: the listed paths are the full set of tests judged
relevant to that target, not merely examples of known-positive tests.

The Phase 6A case covers the four focused test modules that verify Git history, graph behavior,
typed relations, and scanner symbol-impact behavior changed by that commit. Three additional
medium-confidence recommendations (`test_adapters.py`, `test_delivery.py`, and
`test_evidence.py`) arise from broad file-level relationships but do not exercise the changed
behavior, so the reviewed label treats them as false positives.

The Phase 6B1 case covers the recommendation engine, its CLI integration, and the evaluator tests
that exercise the same production query. All three are relevant in the current test suite.

These labels were established by reviewing the changes and behavioral tests. The two cases are
useful as a reproducible regression baseline and threshold comparison, but they are too small and
too closely related to this repository to support claims about general accuracy or score tuning.
The labels describe relevant tests in the current graph, not only files that existed when a
historical commit was created. Reviewers must therefore revisit the complete set when test
dependencies are added, removed, or restructured.

Run the default baseline from the repository root:

```console
intentatlas evaluate-recommendations benchmarks/intentatlas-recommendations.json
```

See `docs/recommendation-evaluation.md` for the label schema and metric contract.

For cross-project threshold comparison, `recommendation-corpus.json` references the original
Python, TypeScript, and Go graph scenarios under `corpus/`. See
`docs/recommendation-corpus.md` for the manifest contract.
