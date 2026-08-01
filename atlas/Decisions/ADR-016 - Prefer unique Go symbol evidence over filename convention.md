---
id: ADR-016
type: decision
status: accepted
phase: 7A
---
# ADR-016 — Prefer unique Go symbol evidence over filename convention

## Context

Go tests in the same package do not import their production package. IntentAtlas therefore linked
`match_test.go` to `match.go` only by filename, even though the test directly calls exported
functions declared in that file. The weak evidence was intentionally hidden by the default medium
threshold. Linking every test to every file in a package would recover the test but create broad
false positives.

## Decision

While scanning already bounded Go files, collect exported declaration names by directory and
package plus identifier tokens from test files. Add `go-symbol-reference` only when a test token
matches a declaration name owned by exactly one non-test source file. Accept the production
package name and the conventional external `<package>_test` form. Keep existing import-based and
filename-convention relationships unchanged.

Masking and tokenization continue to exclude comments and literals. Ambiguous declaration names,
unexported declarations, missing package declarations, oversized files, and unmatched packages
remain unlinked. Treat the result as medium-confidence structural evidence, not semantic proof.

## Consequences

- Common same-package tests can reach medium confidence from direct source references without a Go
  installation, coverage report, or package-wide fan-out.
- The pinned Go benchmark's file case is recovered at the default threshold.
- Conservative omissions remain for unexported and indirect behavior.
- Lexical shadowing can still create a false association, so explanations and advisory boundaries
  remain necessary.

## Links

- Requirement: REQ-016 (available through the incoming `drives` relationship)
- tracked-by:: [[Issues/ISSUE-014 - Implement conservative Go symbol test links]]
