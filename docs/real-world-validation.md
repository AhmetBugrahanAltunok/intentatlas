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
$work = ".intentatlas/real-world/sources"
New-Item -ItemType Directory -Force -Path $work | Out-Null

git clone --no-tags https://github.com/dbader/schedule "$work/schedule"
git -C "$work/schedule" checkout --detach 2dcb5833cdf2b7d7a1bda90c19e2fb7e373e66df

git clone --no-tags https://github.com/sindresorhus/p-limit "$work/p-limit"
git -C "$work/p-limit" checkout --detach ef37eb2f372d385883d113803c98ba0bf3828ad1

git clone --no-tags https://github.com/tidwall/match "$work/match"
git -C "$work/match" checkout --detach 9eab4b2d580b9e1c5ef6399492a09f5a2bdd286b
```

Review the pinned license files and hashes before evaluation. The manifest currently records three
MIT-licensed projects. IntentAtlas's own MIT license does not relicense those repositories; their
source remains outside this product.

## Run the offline benchmark

```powershell
intentatlas evaluate-real-world benchmarks/real-world/manifest.json .intentatlas/real-world/sources
intentatlas evaluate-real-world benchmarks/real-world/manifest.json .intentatlas/real-world/sources --format json
```

The evaluator scans each checkout in memory with fixed default exclusions and a bounded 25-commit
history. It deliberately ignores any checkout-owned `intentatlas.json`, so untrusted configuration
cannot widen the scan or select external reports.

## Label review method

Expected tests are derived independently of recommendation output. A reviewer reads the pinned
commit diff, the changed implementation, the repository's test layout, and the candidate test
files. A case is admitted only when the complete relevant test-file set can be defended without
executing the project. If case design changes, its expected set is re-reviewed from source before
the evaluator is rerun. The current projects each have one behavior-test file for the selected
change:

- `schedule`: `test_schedule.py` for the timezone bugfix;
- `p-limit`: `test.js` for detached `limit.map` behavior; and
- `match`: `match_test.go` for case-insensitive matching.

Each project includes a commit, changed-file, and changed-symbol case. This prevents a directly
changed test file from making the entire benchmark trivially high-confidence and exposes the
confidence tradeoff between structural and filename-only relationships.

These labels are exhaustive only for the selected cases. They are not claims about all possible
integrations, downstream users, hidden tests, platforms, or future revisions.
