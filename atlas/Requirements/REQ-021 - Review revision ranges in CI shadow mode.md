---
id: REQ-021
type: requirement
status: accepted
phase: 9
---
# Review revision ranges in CI shadow mode

Given an explicit base and head revision, a developer or CI job can produce a deterministic,
read-only review of possible requirement impact, candidate tests, and analysis gaps without
publishing, blocking, executing project code, or requiring network credentials.

## Acceptance

- `review --base <revision> --head <revision>` reuses the bounded ChangeSet, freshness, analysis,
  requirement-impact, and test-policy contracts rather than inventing a second inference path.
- Markdown, JSON, and SARIF outputs are deterministic and contain scope, resolved revisions,
  confidence, evidence, and fallback strategy.
- SARIF output is bounded, schema-compatible, path-safe, contains no source snippets or absolute
  paths, and distinguishes impacted intent from incomplete analysis.
- The initial CI workflow is opt-in, read-only, credential-free, and shadow-only: findings never
  change the process exit code or mutate a pull request.
- Imported test outcomes later carry an exact commit identity and freshness before comparison with
  predicted tests.
- The local viewer later presents the same change-centric report without weakening uncertainty.
- The complete phase protocol, representative pilots, and final Evidence/Review records pass
  before Phase 9 closes.

## Typed links

- drives:: [[Decisions/ADR-021 - Compose review formats over trustworthy change reports]]

## Trace

- Roadmap: [[Brain/Product Roadmap]]
- Strategy: [[Brain/Phase 8-10 Strategy]]
- Delivery: [[Issues/ISSUE-019 - Implement CI shadow review loop]]
