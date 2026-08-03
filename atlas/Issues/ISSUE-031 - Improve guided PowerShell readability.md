---
id: ISSUE-031
type: issue
status: in-progress
phase: 16
---
# Improve guided PowerShell readability

## Problem

The production guided flow reports the required trust semantics, but the PowerShell transcript
looks like one dense text wall. The product name, safety boundary, analysis result, recommendation
details, Atlas summary, and choices do not have enough visual hierarchy.

## Work packages

### 16B1 - presentation contract

- [x] Freeze protected Phase 14/15 meanings and canonical machine values before presentation work.
- [x] Add an ASCII-safe prominent IntentAtlas banner and named EN/TR sections without ANSI color.

### 16B2 - readable evidence and choices

- [x] Split selected candidate identity, reason, and evidence onto readable indented lines.
- [x] Wrap long sanitized trust/evidence/advisory copy at a bounded width.
- [x] Render confirmation, scope, consent, and post-result choices one per line.

### 16B3 - regression and closure

- [x] Prove one-Enter result access, EN/TR hierarchy, plain/ASCII/hostile text, no-write,
      non-TTY, immutable snapshot, and existing explicit command behavior.
- [x] Pass complete local/package/browser/vault/network gates; final remote CI remains.

## Links

- implements:: [[Requirements/REQ-032 - Keep guided analysis visually stable and readable]]
- decided-by:: [[Decisions/ADR-032 - Prevent focus-driven viewport drift and structure terminal presentation]]
- planned-evidence:: [[Evidence/EVD-032 - Phase 16 guided experience stability verification]]
- reviewed-by:: [[Reviews/Phase 16 Guided Experience Stability Review]]
