---
id: ISSUE-033
type: issue
status: in-progress
phase: 17F
---
# Correct evidence presentation and runnable test integrity

## 17F-A - linked ranking evidence

- [x] Preserve reason, score, path, and evidence as one structural record.
- [x] Make the strongest score-producing reason primary across JSON, text, guided CLI, and viewer.
- [x] Separate omitted-candidate selection reason from its ranking evidence.

## 17F-B - complete omission presentation

- [x] Show selected, candidate, filtered, limit-omitted, and shown/total omission counts everywhere.
- [x] Regress bounded requirement and test omission detail counts.

## 17F-C - runnable test roles

- [x] Distinguish Python runnable files from support, fixture, and package artifacts generally.
- [x] Consume only bounded safe pytest filename/root declarations and abstain on unsupported input.
- [x] Preserve graph edges and existing JavaScript/TypeScript and Go recommendation behavior.

## 17F-D - threshold truth and closure

- [x] Explain low discovery mode and reserve high for stronger evidence without changing scores.
- [ ] Pass focused/full/package/network/browser/vault/final-head CI gates and re-close Phase 17.

## Links

- requirement:: [[Requirements/REQ-033 - Preserve recommendation integrity across supported surfaces]]
- decided-by:: [[Decisions/ADR-035 - Add linked report reasons and explicit runnable test roles]]
- evidence:: [[Evidence/EVD-033 - Phase 17 recommendation integrity verification]]
- review:: [[Reviews/Phase 17 Recommendation Integrity and Python Resolution Review]]
