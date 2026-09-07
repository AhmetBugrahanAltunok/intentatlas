---
id: ISSUE-035
type: issue
status: closed
phase: 19
---
# Apply audited reliability fixes

## Change Report and query correctness

- [x] Count high-fan-out recommendations before result limiting.
- [x] Add explicit artifact/test-signal analysis coverage and lower-bound semantics.
- [x] Truncate the 200-artifact analysis deterministically and require a full-suite strategy.
- [x] Replace path omission boolean semantics with explicit truncation and unknown counts.

## Trust boundaries

- [x] Redact delivery strings and exact `token`/`auth` keys before persistence.
- [x] Redact header-style `Authorization`/Bearer values and exact authorization keys.
- [x] Stream and bound Git stdout; contain timeouts, process errors, and descendant processes.
- [x] Bound saved graph byte, node, and edge inputs.
- [x] Add safe stale cache-lock recovery.
- [x] Refuse to reap a stale-looking lock whose local owner PID remains live.

## Product correctness

- [x] Resolve staged delete plus same-path recreation deterministically.
- [x] Query viewer evidence paths from the complete server graph snapshot.
- [x] Add conservative JavaScript/TypeScript and Go symbol spans and invalidate old adapter caches.
- [x] Preserve proven Python overload implementations while ambiguous duplicate groups abstain.
- [x] Preserve file fallback for uncertain declaration boundaries.

## Verification

- [x] Add focused regressions for every changed behavior.
- [x] Pass the final complete suite with branch coverage above 80% after all follow-up fixes.
- [x] Pass final Ruff, strict mypy, Bandit, browser E2E, and `git diff --check` gates.

## Links

- implements:: [[Requirements/REQ-035 - Close audited trust and cross-language analysis gaps]]
- decided-by:: [[Decisions/ADR-037 - Bound trust claims and abstain on uncertain structure]]
- evidence:: [[Evidence/EVD-035 - Phase 19 audited reliability verification]]
- reviewed-by:: [[Reviews/Phase 19 Audited Reliability Review]]
- implemented-by:: [[Code/src - intentatlas - change_report.py]]
- implemented-by:: [[Code/src - intentatlas - security.py]]
- implemented-by:: [[Code/src - intentatlas - diagnostic.py]]
- implemented-by:: [[Code/src - intentatlas - change_set.py]]
- implemented-by:: [[Code/src - intentatlas - adapters - javascript.py]]
- implemented-by:: [[Code/src - intentatlas - adapters - go.py]]
- implemented-by:: [[Code/src - intentatlas - viewer.py]]
