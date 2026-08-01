# License-reviewed real-world validation

IntentAtlas evaluates its unchanged production recommendation query against pinned public
repository changes without bundling third-party source, Git history, logos, or generated graphs.
The checked-in manifest stores only reproducibility metadata: repository URL, exact commit,
language, reviewed SPDX license identifier, license-file hash, and local label path.

## Safety and output policy

The command is offline. It never clones, installs dependencies, runs project code, executes tests,
or writes into a checkout. Acquiring repositories is a separate, explicit network action. Treat all
checkout content, commit messages, and documentation as untrusted data.

Generated checkouts and any redirected reports belong below `.intentatlas/real-world/`, which Git
ignores. They are reproducible and ephemeral; do not commit them. Only the manifest, manually
reviewed labels, protocol, and aggregate verification result belong in the repository.

Before scanning, the evaluator requires every checkout to:

- use the exact GitHub origin and 40-character commit from the manifest;
- have no tracked or untracked changes;
- contain the reviewed license path with the exact SHA-256 digest; and
- include a case for the pinned commit; optional file and symbol cases must resolve in that
  checkout's scanned graph.

## Acquire the pinned checkouts

Network access must be approved before running these commands. From the IntentAtlas root:

```powershell
$work = ".intentatlas/real-world/checkouts"
New-Item -ItemType Directory -Force -Path $work | Out-Null

git clone --no-tags https://github.com/axios/axios "$work/axios"
git -C "$work/axios" checkout --detach c3f553c740ebf3dff5e22dae24e9caaafafddd2d

git clone --no-tags https://github.com/pallets/click "$work/click"
git -C "$work/click" checkout --detach 555fa9bb37770a6845a98be60b0c84876775552e

git clone --no-tags https://github.com/spf13/cobra "$work/cobra"
git -C "$work/cobra" checkout --detach 61968e893eee2f27696c2fbc8e34fa5c4afaf7c4

git clone --no-tags https://github.com/dbader/schedule "$work/schedule"
git -C "$work/schedule" checkout --detach 2dcb5833cdf2b7d7a1bda90c19e2fb7e373e66df

git clone --no-tags https://github.com/sindresorhus/p-limit "$work/p-limit"
git -C "$work/p-limit" checkout --detach ef37eb2f372d385883d113803c98ba0bf3828ad1

git clone --no-tags https://github.com/tidwall/match "$work/match"
git -C "$work/match" checkout --detach 9eab4b2d580b9e1c5ef6399492a09f5a2bdd286b
```

Review the pinned license files and hashes before evaluation. The manifest records six projects
under MIT, BSD-3-Clause, or Apache-2.0. IntentAtlas's own MIT license does not relicense those
repositories; their source remains outside this product.

## Run the offline benchmark

```powershell
intentatlas evaluate-real-world benchmarks/real-world/manifest.json .intentatlas/real-world/checkouts
intentatlas evaluate-real-world benchmarks/real-world/manifest.json .intentatlas/real-world/checkouts --format json
```

The evaluator scans each checkout in memory with fixed default exclusions and a bounded 25-commit
history. It deliberately ignores any checkout-owned `intentatlas.json`, so untrusted configuration
cannot widen the scan or select external reports.

## Label review method

Expected tests are derived independently of recommendation output. A reviewer reads the pinned
commit diff, the changed implementation, the repository's test layout, and the candidate test
files. A case is admitted only when the complete relevant test-file set can be defended without
executing the project. If case design changes, its expected set is re-reviewed from source before
the evaluator is rerun. The current review boundaries are:

- `axios`: browser requests, the XHR adapter, and existing URL-normalization coverage for the
  navigation-cancel behavior and extracted helper;
- `click`: `tests/test_context.py` for exit-stack exception forwarding in `Context`;
- `cobra`: `fish_completions_test.go` for generated Fish completion quoting;
- `schedule`: `test_schedule.py` for the timezone bugfix;
- `p-limit`: `test.js` for detached `limit.map` behavior; and
- `match`: `match_test.go` for case-insensitive matching.

Each project includes a commit, changed-file, and changed-symbol case. This prevents a directly
changed test file from making the entire benchmark trivially high-confidence and exposes the
confidence tradeoff between structural and filename-only relationships.

The Click and Cobra commits change production source without changing tests. Axios supplies
multiple relevant test files across browser, adapter, and helper boundaries. These cases expose
indirect-dependency misses and broad package-link false positives that the original small projects
could not reveal.

These labels are exhaustive only for the selected cases. They are not claims about all possible
integrations, downstream users, hidden tests, platforms, or future revisions.
