
---
id: EVD-001
type: evidence
status: verified
---
# Initial scanner acceptance

Evidence for [[Requirements/REQ-001 - Explain change impact]]:

- Scanner and graph tests: [[tests › test_scanner.py]] and [[tests › test_graph.py]]
- Vault ownership tests: [[tests › test_vault.py]]
- CLI acceptance tests: [[tests › test_cli.py]]

## Verified on 2026-07-30

- `pytest`: 20 passed, 86% branch-aware coverage.
- `ruff`: all checks passed.
- `bandit`: no findings after reviewing the fixed, read-only Git subprocess boundary.
- `pip-audit`: no known vulnerabilities; the local editable IntentAtlas distribution was skipped.
- Wheel build: `intentatlas-0.1.0-py3-none-any.whl` created successfully.
- Real repository scan: 152 nodes, 165 relationships, 0 orphaned durable notes.
- Browser acceptance: all 152 nodes and 163 links rendered; search and keyboard node details verified.
