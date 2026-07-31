# Cross-project recommendation corpus

IntentAtlas can compare low, medium, and high recommendation confidence across multiple saved
graphs and exhaustive label files. Corpus evaluation is deterministic and offline: it never scans,
executes, installs, or downloads the referenced projects.

## Manifest schema

Schema 1 accepts exactly these fields:

```json
{
  "schema_version": 1,
  "name": "Reviewed projects",
  "projects": [
    {
      "id": "python-service",
      "name": "Python service",
      "graph": "benchmarks/python-service.graph.json",
      "labels": "benchmarks/python-service.labels.json"
    }
  ]
}
```

Project IDs are stable ASCII identifiers. Graph and label paths are canonical project-relative
POSIX paths. IDs, graph paths, and label paths must be unique, and one file cannot serve as both
the graph and labels for an entry.

The manifest remains below the invoking project root and outside `atlas/Private/`. The same rule
applies to every referenced file. Direct symbolic links, duplicate JSON keys, unknown fields,
malformed values, traversal or absolute paths, and missing inputs are rejected.

Limits are 256 KB per manifest, 50 projects, 2,000 total evaluation cases, 50 MB per saved graph,
and 250 MB for all corpus graphs. Each label file retains the evaluation schema's 1 MB, 500-case,
and 1,000-expected-test-per-case limits.

## Evaluation behavior

Every graph is loaded through the production graph validator and every label document through the
schema-1 `complete-test-set` validator. The production recommendation query runs at low, medium,
and high confidence with the same visible per-case result limit. Recommendation scores are not
changed.

For each threshold, output contains per-project and micro-aggregate case, expected,
recommendation, TP, FP, FN, precision, and recall values. Micro metrics use summed counts rather
than averaging project percentages. Undefined precision or recall remains JSON `null` and text
`n/a`. Detailed ranked recommendations remain available through `evaluate-recommendations`.

## CLI

```console
intentatlas evaluate-corpus benchmarks/recommendation-corpus.json
intentatlas evaluate-corpus benchmarks/recommendation-corpus.json --limit 20 --format json
```

The bundled corpus contains small, original, MIT-licensed graph scenarios representing Python,
TypeScript, and Go relationships. They verify aggregation and confidence semantics but are not full
repositories and cannot establish real-world accuracy. Public repository benchmarks require
separate license review and remain future work.
