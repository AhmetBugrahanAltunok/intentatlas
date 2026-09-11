---
id: release-candidate-inventory
type: memory
status: active
---
# Release Candidate Inventory

Reconciles the candidate at `0.3.0rc1` back to the phases that delivered it. The Phase 21
checklist requires this split so release notes do not present four phases of accumulated work as
one delivery. Derived from Git history, not from recollection.

Baseline: `3854f04` (Phase 17F closure). Everything after it belongs to Phases 18-21A.

## Attribution

| Phase | Delivery | Commits | Files |
| --- | --- | --- | --- |
| 18 — First-run experience hardening | first-run workflow, guidance, demo, diagnostics | `310d9d5`, `a8ef700`, `6936698`, `c83138c`, `f407e49` | 35 |
| 19 — Audited reliability | bounded subprocesses, redaction, adapter spans, graph bounds, viewer paths | `041069a` (remainder) | 42 |
| 20 — Complete change coverage | interval-union coverage, deletion uncertainty, browser evidence path | `041069a` (the nine files EVD-036 names) | 9 |
| 21A — Verification integrity | declared package identity, vault-boundary regressions | `f0e6719` | 11 |
| — | delivery continuity rules | `6f4a561` | 1 (`AGENTS.md`) |

**75 unique files**, not 98. The per-phase counts sum to 98 because 22 files were touched by more
than one phase; they must never be added together in release notes. Of the 75: 26 under `src/`,
29 under `tests/`, 20 documentation and root files.

Phases 19 and 20 share commit `041069a`. The split is authoritative from the EVD-036 change
inventory, which names Phase 20's files exactly; everything else in that commit is Phase 19.

## Files touched by more than one phase

```text
18+19   README.md, docs/guided-cli.md, adapters/python.py, change_report.py, change_set.py,
        cli.py, diagnostic.py, onboarding.py, recommendations.py, viewer.py,
        tests/test_change_report.py, test_cli.py, test_diagnostic.py, test_scanner.py,
        test_viewer.py
18+20   docs/trust-first-preview.md
18+21A  tests/test_change_analysis.py, tests/test_e2e.py
19+21A  docs/architecture.md
20+21A  CHANGELOG.md, tests/test_browser_e2e.py
18+19+21A  tests/test_guided_cli.py
```

## New files, not modifications

Phase 21A added three: `tests/_package_identity.py`, `tests/conftest.py`,
`tests/test_package_identity.py`. Every other file in the inventory existed at `3854f04`.

## Correction to an existing record

EVD-036 lists `AGENTS.md` in the Phase 20 change inventory. Git shows it changed in `6f4a561`,
the documentation commit that followed the Phase 20 source commit, not in `041069a`. The content
attribution is right and the file is small; only the commit placement was imprecise. Recorded here
rather than edited into the closed phase evidence.

## What this inventory is not

It counts files, not behavior. A file appearing under a phase means that phase changed it, not
that the phase owns it. It also says nothing about which changes a user would notice; the
release note still has to be written from the requirement and evidence records, and phases 18-20
were verified under the ambiguous import setup that Phase 21A removed.

## Links

- planned-in:: [[Brain/Alpha Release Execution Plan]]
- references:: [[Evidence/EVD-034 - Phase 18 first-run experience hardening verification]]
- references:: [[Evidence/EVD-035 - Phase 19 audited reliability verification]]
- references:: [[Evidence/EVD-036 - Phase 20 change coverage verification]]
- references:: [[Evidence/EVD-037 - Phase 21A verification integrity verification]]
