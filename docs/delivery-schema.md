# Local delivery snapshot schema

IntentAtlas imports bounded issue and pull-request metadata from an explicit project-local JSON
file. It does not call a provider, use credentials, or retain discussion bodies.

```json
{
  "schema_version": 1,
  "source": "github-export",
  "repository": "owner/repository",
  "issues": [{
    "id": 123,
    "title": "Explain a delivery gap",
    "state": "open",
    "url": "https://github.com/owner/repository/issues/123",
    "labels": ["enhancement"],
    "intent_ids": ["REQ-007", "ADR-007"]
  }],
  "pull_requests": [{
    "id": 456,
    "title": "Connect delivery context",
    "state": "merged",
    "url": "https://github.com/owner/repository/pull/456",
    "draft": false,
    "issue_ids": ["123"],
    "changed_files": ["src/package/module.py"],
    "commit_shas": ["0123456789abcdef0123456789abcdef01234567"]
  }]
}
```

Configure `"delivery_reports": ["reports/delivery.json"]` in `intentatlas.json`, then run
`intentatlas scan`.

Fields are allowlisted and bounded. URLs must be HTTP(S) without credentials, queries, or
fragments. File paths and commit SHAs link only on exact local matches. Unknown references create
no relationship. Source, repository, IDs, titles, states, URLs, labels, and the recorded report path
are secret-redacted before graph or generated-vault persistence. Bodies, comments, authors, raw API
payloads, and unknown fields are rejected.
