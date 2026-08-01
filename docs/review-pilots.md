# Review shadow-mode pilots

The deterministic pilot in `tests/test_review_pilots.py` exercises three representative local Git
ranges through the public `review` CLI. It creates only original temporary fixtures, requires no
network or provider credential, and never executes fixture project code or tests.

## Cases

1. **Exact and aligned** — a Python function hunk maps to its AST symbol, its directly linked test
   is selected with the targeted strategy, and an outcome sidecar keyed to the resolved head shows
   that selected path as executed.
2. **Stale outcome** — the same structural prediction receives a sidecar keyed to the baseline.
   Freshness becomes stale and every comparison set is empty.
3. **Unsupported fallback** — a TOML-only range has file fallback rather than symbol evidence.
   SARIF reports `IA101` and `IA300`, and the policy remains `full-suite-fallback` even though the
   sidecar itself is aligned.

These pilots are regression evidence for the declared fixtures, not a general precision/recall or
behavioral-completeness claim. Broader recommendation accuracy remains bounded by the separately
reviewed real-world corpus.
