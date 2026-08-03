---
id: EVD-033
type: evidence
status: in-progress
phase: 17
---
# EVD-033 - Phase 17 recommendation integrity verification

## Entry and frozen baseline

- Entry: clean `HEAD == main == origin/main == 174369afc56d603373de1443d7826c92fcec395a`;
  Phase 16 remains passed and closed.
- Longitudinal manifest SHA-256:
  `391015effa9b3759cfbf6a8d94eb0c8d58a7c2e27bbd538d6e2377c741543731`.
- Frozen partition hashes remain calibration
  `3a1a903f37ca7e2432007b0210494ea659c64fb3aa2d93f2490de92f09041320` and evaluation
  `edafea2e4225a271664c43b54e90b2987d4c1cf70f67e1ecc5a832d06efb72d5`.
- Two unchanged `evaluate-longitudinal ... --format json` runs were byte-identical, SHA-256
  `dd90bd22ceefba5321e1a0fb2a762adee15f8f943807718b1bcf0117923d3cdd`.
- Before-change overall medium results: calibration TP 38 / FP 52 / FN 0, precision `0.422222`,
  recall `1.0`; evaluation TP 34 / FP 34 / FN 0, precision `0.5`, recall `1.0`.

## Independent reproduction

- Public corpus: `https://github.com/pallets/click.git` exact revision
  `00e592cea702e0b2caa0dee42489fdb1c22cd845`, BSD-3-Clause `LICENSE.txt` SHA-256
  `757302fe7c41e7026fa46d3315ea8604ed5295fc95c2256d9b38adac43f6fbe5`.
- The exact worktree change produced analyzed/aligned ChangeReport state, medium threshold,
  targeted strategy, two selected/two candidates/zero filtered. It showed empty
  `tests/test_utils/__init__.py` at score 65 but confidence low, plus real
  `tests/test_formatting.py` at score 45 low.
- In-memory Click scan produced zero Python exact-symbol test edges. Default recommend-tests
  returned only the empty marker at 65 medium; low also returned test_formatting at 45.
- Self-scan produced only five Python exact-symbol test edges. Four tests from bulk commit
  `2f3d695` ranked 70 above six direct-dependent tests at 65; test_recommendations remained a 45
  filename fallback.
- Root cause: Flit/Hatchling/conventional pyprojects defaulted to `.` source-root, preventing the
  safe src-module normalization. The real qualified caller edge was absent. A re-export file's
  exact import then combined with a filename-only second hop and inherited score 65. Separate
  ChangeReport confidence and missing test filtering compounded the error.
- Pre-fix command `python -m pytest tests/test_phase17_recommendation_integrity.py -q` produced
  `7 failed`, covering confidence/filtering, weakest-hop scoring, empty markers, broad/narrow
  co-change, Flit/Hatch/conventional src layouts, qualified attributes, Click shape, and self-scan.

## Verification pending

- [ ] 17B confidence/filter/counter/strategy parity.
- [ ] 17C source-root/qualified-symbol/re-export precision.
- [ ] 17D candidate eligibility and calibrated ranking.
- [ ] 17E documentation, diagnostics, Windows encoding, complete local/package/network/vault gates.
- [ ] Exact commits, generated notes, push, final-head remote CI, clean synchronized worktree.

## Links

- proves:: [[Requirements/REQ-033 - Preserve recommendation integrity across supported surfaces]]
- references:: [[Decisions/ADR-033 - Canonicalize confidence and conservative Python resolution]]
- references:: [[Decisions/ADR-034 - Retain generated vault outputs under single-writer governance]]
- delivered-by:: [[Issues/ISSUE-032 - Implement recommendation integrity and Python resolution]]
- reviewed-by:: [[Reviews/Phase 17 Recommendation Integrity and Python Resolution Review]]
