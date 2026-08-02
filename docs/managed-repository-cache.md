# Managed public-repository cache

`intentatlas guide https://github.com/OWNER/REPOSITORY` and the TTY-only one-URL shorthand accept
one strict public GitHub repository identity. Before the first network/cache effect, the guide
shows the normalized URL, shallow-history and resource bounds, cache write, unsupported private
authentication, and disabled execution behavior. Only an empty Enter approves it.

The acquisition uses fixed Git arguments without a shell, credentials, interactive prompts, user
configuration, redirects, hooks, filters, submodules, LFS smudging, or project code. It checks out
no `atlas/Private/` content. History is shallow (at most 50 commits); the exact acquired commit and
available history count are shown. A cache hit is an exact cached revision, never a claim that the
repository is current on GitHub.

Entries live under the operating system's user cache convention. They are created in unique
staging directories, validated, then atomically promoted under a deterministic URL-derived ID.
Concurrent mutation uses a bounded lock. A failed refresh preserves the prior complete entry;
invalid metadata triggers reacquisition. Metadata contains only URL, revision, time, bounds, and
file/byte counts—not source text, environment values, logs, credentials, or tokens.

Cache management is offline and exact-target only:

```text
intentatlas cache list
intentatlas cache list --format json
intentatlas cache info CACHE_ID
intentatlas cache clear CACHE_ID
```

Traversal identities and link, junction, or reparse-point roots/targets are rejected. `clear`
removes only the validated ID beneath the canonical managed cache root.
