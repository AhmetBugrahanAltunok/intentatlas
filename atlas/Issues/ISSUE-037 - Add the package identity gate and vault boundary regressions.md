---
id: ISSUE-037
type: issue
status: closed
phase: 21A
---
# Add the package identity gate and vault boundary regressions

- [x] Resolve the imported package root and expose a declared-mode comparison.
- [x] Fail the session before collection when the declaration and the import disagree.
- [x] Derive subprocess import roots from the imported module in every CLI-spawning test.
- [x] Remove the hardcoded relative source path from the guided CLI regression.
- [x] Declare installed-artifact intent in the cross-platform packaging job.
- [x] Regress the gate in both directions, including an actual offline wheel round trip.
- [x] Cover the previously untested vault classification, including the `Private/` boundary.
- [x] Complete all local quality and vault continuity gates; record the review decision.

Closed 2026-09-11: 612 passed, 4 platform skips; branch-enabled total coverage 86.71%.

## Links

- implements:: [[Requirements/REQ-037 - Prove which package and boundaries verification covers]]
- follows:: [[Decisions/ADR-039 - Declare and derive the verified package identity]]
- verified-by:: [[Evidence/EVD-037 - Phase 21A verification integrity verification]]
- reviewed-by:: [[Reviews/Phase 21A Verification Integrity Review]]
- implemented-by:: [[Code/src - intentatlas - change_analysis.py]]
- verified-by:: [[Tests/tests - test_change_analysis.py]]
- verified-by:: [[Tests/tests - test_e2e.py]]
- verified-by:: [[Tests/tests - test_browser_e2e.py]]
- verified-by:: [[Tests/tests - test_guided_cli.py]]
