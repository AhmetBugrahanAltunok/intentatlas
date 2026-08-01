---
id: REQ-015
type: requirement
status: accepted
phase: 6B2B2B2B
---
# Validate recommendations on pinned public projects

Contributors can measure the unchanged production scanner-to-recommendation pipeline against a
small, reproducible set of license-reviewed public project changes without adding third-party
source, history, branding, or generated graphs to IntentAtlas.

## Acceptance

- Public repositories are acquired only after explicit network approval.
- A strict checked-in manifest records canonical GitHub URL, exact 40-character commit, language,
  SPDX identifier, safe license path, license SHA-256, and local reviewed-label path.
- Evaluation rejects a missing, linked, dirty, wrong-origin, wrong-commit, or license-mismatched
  checkout before scanning it.
- Checkout-owned configuration is ignored; scanning uses fixed local defaults, executes no project
  code or tests, performs no network request, and persists no graph or vault output.
- Expected tests are selected from a manual change, implementation, test-layout, and candidate-test
  review without using recommendation output as ground truth.
- Every selected project includes pinned-commit, changed-file, and changed-symbol cases with an
  explicit complete-test-set boundary.
- Text and JSON results are deterministic, bounded, advisory, and compare low, medium, and high
  confidence using the unchanged production query.
- Checkouts and redirected outputs remain ignored, ephemeral, and reproducible.
- Focused and complete tests, coverage, lint, security, CLI, UI, package, determinism, attribution,
  and Obsidian closure gates pass.

## Scope boundary

The benchmark validates only its pinned cases. It does not execute third-party tests, prove
general accuracy, cover downstream or hidden tests, grant network access implicitly, or relicense
third-party repositories under IntentAtlas's MIT license.

## Typed links

- drives:: [[Decisions/ADR-015 - Separate public acquisition from offline evaluation]]

## Trace

- Roadmap: [[Brain/Product Roadmap]]
- Planned evidence: [[Evidence/EVD-015 - Phase 6B2B2B2B real-world verification]]
