---
id: ISSUE-036
type: issue
status: closed
phase: 20
---
# Close partial hunk deletion and browser regressions

- [x] Cover partial intervals, gaps, parent/child ownership, and equivalent hunk segmentation.
- [x] Preserve zero-count deletion ranges and conservative report behavior.
- [x] Regress actual Git-to-CLI text/JSON workflows.
- [x] Diagnose browser path failure; verify one selection and delayed response.
- [x] Complete all local quality and vault continuity gates; record review decision.

Closed 2026-09-07: 595 passed, 4 platform skips; branch-enabled total coverage 86.47%.

## Links

- implements:: [[Requirements/REQ-036 - Require complete change coverage before targeted advice]]
- follows:: [[Decisions/ADR-038 - Preserve uncovered change ranges and deletion uncertainty]]
- verified-by:: [[Evidence/EVD-036 - Phase 20 change coverage verification]]
- reviewed-by:: [[Reviews/Phase 20 Change Coverage Review]]
- implemented-by:: [[Code/src - intentatlas - symbol_spans.py]]
- implemented-by:: [[Code/src - intentatlas - git_history.py]]
- verified-by:: [[Tests/tests - test_change_coverage.py]]
- verified-by:: [[Tests/tests - test_symbol_spans.py]]
- verified-by:: [[Tests/tests - test_git_history.py]]
- verified-by:: [[Tests/tests - test_browser_e2e.py]]
