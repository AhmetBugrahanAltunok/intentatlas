---
id: REQ-040
type: requirement
status: accepted
phase: 21D
---
# Prove the fail-closed branches rather than assert them

## User outcome

IntentAtlas repeatedly promises to abstain rather than guess when a bound is exceeded, a pipe
breaks, a child cannot be collected, or a revision cannot be resolved. Those promises are the
reason a maintainer can trust a quiet result. Each one has executable evidence instead of only a
documented claim.

## Acceptance

- The loopback viewer's every served route is exercised in process: each `/api/graph/*` query,
  the raw graph document, the optional report endpoints when supplied and their absence when not,
  the packaged assets, and unknown routes.
- A malformed graph query returns a bounded schema-1 error with a non-200 status and no traceback
  text, for a non-numeric bound, a negative bound, a repeated parameter, a missing required
  parameter, and a non-ASCII digit.
- An unparsable or non-UTF-8 graph document is refused before a server starts.
- Bounded process collection fails closed for a negative allowance, an unstartable command, a
  containment failure, a missing stdout pipe, an unreadable pipe, an uncollectable child, and a
  zero allowance that receives output. A containment failure leaves no surviving child.
- A descendant that keeps the stdout pipe open after the parent exits cleanly fails closed
  promptly instead of blocking on a reader that can never reach end of file.
- ChangeSet text rendering is covered directly, including absent revisions, rename provenance,
  and hunk ranges, and an unknown output format is refused.
- Change freshness abstains for unmerged, missing, symlinked, and unresolvable artifacts and when
  Git is unavailable; deletion freshness depends on the artifact actually being gone.
- Source acquisition refuses local and `file://` origins, so a reachable on-disk repository
  stays unacquirable, and the fixed Git argument list carries the protocol and redirect
  settings that enforce it.
- The longitudinal pilot's strict loaders refuse every malformed manifest and label shape they
  document, exercised against the real frozen manifest, while still accepting it unmutated.
- The full suite, Ruff, mypy, and Bandit pass with no runtime module modified.

## Links

- proven-by:: [[Evidence/EVD-040 - Phase 21D fail-closed branch verification]]
- reviewed-by:: [[Reviews/Phase 21D Fail-Closed Branch Review]]
- extends:: [[Requirements/REQ-037 - Prove which package and boundaries verification covers]]
