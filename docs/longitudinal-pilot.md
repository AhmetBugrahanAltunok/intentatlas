# Frozen longitudinal recommendation pilot

The longitudinal evaluator measures the unchanged production recommendation path across exact,
license-reviewed public repository histories. It is deterministic and offline: evaluation never
clones, installs dependencies, executes tests, runs project code, or writes into a checkout.
Acquisition is a separate network-approved action, and third-party source remains below the
Git-ignored `.intentatlas/real-world/checkouts/` directory.

## Frozen baseline

Schema 1 contains eight repositories and 64 chronologically ordered commit cases. Each project has
four calibration and four evaluation cases. Python, JavaScript/TypeScript, and Go are separate
non-empty cohorts; `antfu-utils` and `zustand` supply the two explicit pnpm workspace histories.

| Partition | Cases | SHA-256 |
| --- | ---: | --- |
| calibration | 32 | `3a1a903f37ca7e2432007b0210494ea659c64fb3aa2d93f2490de92f09041320` |
| evaluation | 32 | `edafea2e4225a271664c43b54e90b2987d4c1cf70f67e1ecc5a832d06efb72d5` |

The frozen manifest SHA-256 is
`391015effa9b3759cfbf6a8d94eb0c8d58a7c2e27bbd538d6e2377c741543731`.
Two unchanged baseline evaluations produced JSON SHA-256
`dd90bd22ceefba5321e1a0fb2a762adee15f8f943807718b1bcf0117923d3cdd` and text SHA-256
`0a0b9c530dcd57c9e6ca208e665c408da4d7376c0cc05c4463db8ccbf4aa887d`.

### Evaluation benchmark card

| Threshold | Cases | TP | FP | FN | Precision (point) | Recall (point) | Recommendation coverage | Abstention |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| low | 32 | 34 | 34 | 0 | 50.00% | 100.00% | 90.625% | 56.25% |
| medium | 32 | 34 | 34 | 0 | 50.00% | 100.00% | 90.625% | 56.25% |
| high | 32 | 27 | 0 | 7 | 100.00% | 79.4118% | 71.875% | 56.25% |

The CLI reports Wilson 95% intervals and cohort sizes beside every point estimate. It also reports
per-project, per-language, workspace, partition, threshold, and overall tables; analysis and
freshness states; targeted/full-suite strategies; and every FP/FN path with its reviewed category.
Undefined metrics remain JSON `null` and text `n/a`.

These values describe only the frozen reviewed cases. They are not general accuracy, population
estimates, or proof that a targeted subset is sufficient. Low and medium thresholds retain broad
resolver candidates in Cobra and Axios; high confidence removes those false positives but misses
seven evaluation labels. Historical changes frequently retain stale analysis state, so the
existing abstention and full-suite safeguards remain visible. No duration or savings evidence was
supplied, and the result reports it as unknown.

## Input contracts

The strict manifest identifies each project by ID, language cohort, workspace shape, exact GitHub
origin, immutable revision, bounded history limit, explicit exclusions, SPDX identifier, reviewed
license path/hash/date, label path, and classification path. Thresholds are exactly `low`,
`medium`, and `high`.

Each label file uses its own schema version and project ID. Cases have a globally unique ID,
contiguous sequence, immutable revision, offset-aware commit timestamp, explicit partition, and a
closed-world expected test-file set. Canonical partition hashes cover these independent fields and
do not include recommendation output or later error review.

Classification files bind each observed FP or FN set to a reviewed category and the SHA-256 of its
canonical sorted paths. Evaluation rejects stale classifications, while missing classifications
remain visible as a non-zero gap count. The frozen baseline has zero gaps. Categories are label
defect, unsupported construct, stale evidence, resolver ambiguity, and recommendation-policy gap.

Direct symlinks, traversal and absolute paths, duplicate JSON keys, unknown fields, oversized
files, duplicate identities, dirty checkouts, origin/revision mismatches, license mismatches,
timestamp mismatches, cases outside bounded history, and project material under `atlas/Private/`
are rejected.

## Acquire the pinned checkouts

Network approval is required. From the repository root, clone the public projects below into the
Git-ignored checkout directory, then detach each checkout at its manifest revision:

```powershell
$work = ".intentatlas/real-world/checkouts"
New-Item -ItemType Directory -Force -Path $work | Out-Null

git clone --no-tags https://github.com/antfu/utils "$work/antfu-utils"
git -C "$work/antfu-utils" checkout --detach 91f8cf73bebddae8f7ebcac82e47c9bcba9805e2
git clone --no-tags https://github.com/axios/axios "$work/axios"
git -C "$work/axios" checkout --detach c3f553c740ebf3dff5e22dae24e9caaafafddd2d
git clone --no-tags https://github.com/spf13/cobra "$work/cobra"
git -C "$work/cobra" checkout --detach 61968e893eee2f27696c2fbc8e34fa5c4afaf7c4
git clone --no-tags https://github.com/tidwall/match "$work/match"
git -C "$work/match" checkout --detach 9eab4b2d580b9e1c5ef6399492a09f5a2bdd286b
git clone --no-tags https://github.com/sindresorhus/p-limit "$work/p-limit"
git -C "$work/p-limit" checkout --detach ef37eb2f372d385883d113803c98ba0bf3828ad1
git clone --no-tags https://github.com/dbader/schedule "$work/schedule"
git -C "$work/schedule" checkout --detach 2dcb5833cdf2b7d7a1bda90c19e2fb7e373e66df
git clone --no-tags https://github.com/sindresorhus/yocto-queue "$work/yocto-queue"
git -C "$work/yocto-queue" checkout --detach b07eac099753833b29d06c614149904445739776
git clone --no-tags https://github.com/pmndrs/zustand "$work/zustand"
git -C "$work/zustand" checkout --detach beca84e600e4e250f6b244d22878e72948f331c7
```

Review the manifest license hashes before evaluation. IntentAtlas's MIT license does not relicense
these repositories. Commit messages, documentation, and source are untrusted data and never
control execution.

## Run the offline evaluator

```console
intentatlas evaluate-longitudinal benchmarks/longitudinal/manifest.json .intentatlas/real-world/checkouts
intentatlas evaluate-longitudinal benchmarks/longitudinal/manifest.json .intentatlas/real-world/checkouts --format json
```

Type-declaration checks named `*.test-d.ts` are not production scanner test nodes and are excluded
from expected runtime test-file labels. Click and itsdangerous were considered but rejected before
baseline output because their overload/platform definitions produce duplicate Python adapter
symbol identities. No adapter change, language expansion, raw patch, or third-party source was
introduced to admit them.

The compatibility class and migration rules for this stable versioned interchange are documented
in the [pre-1.0 compatibility policy](compatibility-policy.md).
