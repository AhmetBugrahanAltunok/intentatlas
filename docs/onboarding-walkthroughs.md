# Technical onboarding walkthroughs

Phase 12 uses deterministic, task-based synthetic/cognitive walkthroughs to verify that a
maintainer-facing answer is technically available and semantically honest. These scenarios are
automated regressions, not participant observations. They collect no human timing, and no median
user duration is calculated from them.

| Scenario | Maintainer task | Required observable result | Regression |
| --- | --- | --- | --- |
| 01 | Choose a safe first command in an unconfigured checkout | Deterministic read-only diagnostic, no network requirement, no created state | `test_walkthrough_01_decide_the_safe_first_command_without_configuration` |
| 02 | Explain an aligned symbol change | Selected requirement and test use the recorded evidence paths; strategy is targeted | `test_walkthrough_02_explain_an_aligned_change_with_recorded_paths` |
| 03 | Interpret an omitted candidate | Counts and threshold expose the omission; wording does not claim no impact | `test_walkthrough_03_interpret_an_omission_without_claiming_no_impact` |
| 04 | Decide what to run when analysis is stale | Recommendations abstain and the full-suite strategy remains explicit | `test_walkthrough_04_choose_the_safe_strategy_for_stale_analysis` |
| 05 | Recognize an unsafe or ambiguous scope | Multiple roots, unsupported language, and oversized files remain visible without writes or network use | `test_walkthrough_05_recognize_ambiguity_and_unsupported_scope` |

Run all five scenarios with:

```console
python -m pytest tests/test_onboarding_walkthroughs.py -q
```

The separate clean-installed-wheel, text/JSON/UI equivalence, no-write, and real-browser keyboard
and accessibility checks remain Phase 12 gates. Human observation follows the
[first-run observation guide](first-run-observation-guide.md) at Phase 11C.
