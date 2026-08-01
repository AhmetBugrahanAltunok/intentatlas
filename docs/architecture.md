# Architecture

IntentAtlas has three layers with explicit ownership.

```text
Repository ──scan──> AtlasGraph ──sync──> Obsidian vault
                         │
                         ├──query──> impact/status/test recommendation CLI
                         ├──evaluate──> labeled precision/recall report
                         ├──aggregate──> cross-project threshold corpus
                         ├──validate──> pinned real-world checkout metrics
                         ├──compare──> deterministic CI graph diff
                         └──serve──> local web viewer
first-party demo graph ────────────> local web viewer
```

## 1. Repository adapters

Adapters extract only structural metadata. Built-in language adapters receive a read-only file
and kind mapping, enforce the shared parse-size limit, and return deterministic graph fragments;
they do not mutate the graph directly. The Python adapter uses the standard-library AST. It maps
explicit `from` imports and qualified module attributes to exact local top-level symbols, following
at most eight deterministic package re-export hops and rejecting cycles. A test with exact symbol
evidence does not also inherit the broader file edge for that resolved module.

The CLI may reuse a complete adapter fragment through a disposable content-addressed cache. The
fingerprint covers adapter identity and cache version, the parse limit, and every declared input's
project-relative path, derived kind, and bytes. Python declares `.py`; JavaScript/TypeScript declares
`.js`, `.jsx`, `.ts`, and `.tsx`; Go declares both `.go` and `.mod` because module boundaries affect
resolution. Reuse is whole-adapter rather than per-file so cross-file semantics cannot be assembled
from incompatible partial states. Inputs are fingerprinted again after analysis and a concurrent
change aborts before graph publication.

Cache documents are bounded strict JSON below `.intentatlas/adapter-cache/`. They accept only the
symbol metadata, relation types, and evidence labels emitted by the matching built-in adapter and
contain no source excerpts. Missing, stale, malformed, linked, oversized, or incompatible entries
are cache misses. The public `scan_repository` path remains a cache-independent equivalence
reference. The graph and cache use same-directory temporary files plus atomic replacement, keeping
the previous complete artifact if replacement fails. See [incremental scanning](incremental-scanning.md).

The TypeScript/JavaScript adapter conservatively recognizes explicit declarations and static
relative module references in `.ts`, `.tsx`, `.js`, and `.jsx` files without requiring Node. Named
and default static imports additionally link to a discovered exact symbol when the target export is
unambiguous. Bare package imports, dynamic imports, and unresolved export expressions are not
resolved into exact repository relationships.

The Go adapter uses a small structural lexer to recognize named types, functions, methods, and
import declarations without requiring the Go toolchain. `go.mod` module declarations define local
resolution boundaries, including nested modules. A local package import projects to its discovered
non-test Go files; external and unresolved imports are omitted rather than guessed. Import-like
text inside comments or literals is never treated as a relationship.

For same-directory tests, the adapter also records `go-symbol-reference` evidence when an
identifier names an exported declaration owned by exactly one production file in the compatible
package. Conventional external `<package>_test` files are compatible with `<package>`. Duplicate
declaration names across files, unexported names, comments, literals, missing packages, and
oversized files create no such edge. Filename convention remains separate weak evidence; lexical
reference is advisory structural evidence rather than call-resolution or execution proof.

Tests that import another local Go package are narrower still: named and default imports link only
qualified `package.Symbol` references, while dot imports use unique exported identifiers. Blank
imports and unresolved or ambiguous packages create no direct test edge. Non-test source imports
retain conservative package-level dependencies because they describe implementation structure,
not a test recommendation claim.

The Git adapter reads commit metadata, changed paths, and a bounded recent window of zero-context
diff hunks with fixed read-only commands. Changed new-side lines project to the most-specific
Python symbol only when the current file matches that commit's bounded raw Git blob after
line-ending normalization and validated AST source spans intersect. Blob checks include only
scanned paths with trusted spans, never excluded paths, and stop safely above 1,000 commit/path
candidates. File-level history remains the fallback for stale historical files, deletions, module
edits, adapters without spans, malformed patches, and excessive output. Repository discovery
prunes excluded directories before descent,
does not follow directory links, and excludes the configured vault from the repository walk.
Adapters never execute project code.

Configured evidence adapters read only explicit project-local reports. The Cobertura and JUnit
importers reject DTD/entity declarations, enforce byte and record limits, map report paths only to
one discovered file, and aggregate coverage or result counts without retaining raw failure output.

Open JSON evidence uses the same explicit path, byte, link, and private-vault boundary plus
duplicate-key, depth, value, string, record, and format limits. SCIP protobuf JSON is reduced to
per-file occurrence/definition/reference/diagnostic counts. SARIF 2.1.0 is reduced to per-file
level/rule counts after percent-decoded URIs resolve uniquely inside the project. Both summary kinds
use neutral `references` edges: they do not imply causality, correctness, impact, or test necessity.
Binary SCIP, raw external symbols, diagnostic messages, SARIF snippets/fixes/code flows/properties,
and absolute locations are not persisted.

Test Execution Map schema 1 binds unique test/source path sets to one full Git commit and the fixed
`complete-observed-set` policy. Fixed read-only Git commands resolve current HEAD and require every
mapped test/source artifact to be tracked and unchanged from that HEAD. Every report creates a
bounded per-test summary with `aligned`, `stale`, or `unknown` freshness; only exact `aligned`
reports add `tests` edges with `test-execution-map` provenance. The existing recommendation
query consumes that normal graph evidence, while stale and unknown reports cannot affect ranking.
See [open evidence imports](open-evidence.md).

The delivery adapter reads only explicit project-local schema-1 JSON snapshots after path, byte,
record, link, field, type, duplicate-key, and URL validation. It creates bounded delivery-issue and
pull-request nodes, then links only exact local intent IDs, issue IDs, file paths, and commit SHAs.
Raw provider payloads, bodies, comments, authors, credentials, and unknown fields are rejected.

## 2. AtlasGraph

`AtlasGraph` is the language-neutral contract. Nodes have a stable ID, kind, label, path,
and small metadata object. Directed edges have a source, target, typed relation, inverse label,
category, and provenance. The graph schema is versioned; schema 3 loads schema-1 and schema-2
caches and rebuilds them with the current relation catalog. Current-schema caches are accepted
only when their embedded catalog, edge categories, and inverse labels match the runtime registry.
Relation schema 4 retains direct `modifies`/`modified-by` change evidence and adds invertible
`calls`/`called-by` structure for bounded exact symbol calls. The graph is serialized to
`.intentatlas/graph.json`; it is a rebuildable cache, not the source of truth.

`GraphIndex` is a lazy in-memory view over canonical edges. It stores immutable incoming and
outgoing tuples by node and by exact `(node, relation)` key. Degree, orphan health, breadth-first
impact, and recommendation evidence discovery reuse the same index. A newly accepted edge
invalidates the cached view; the next read rebuilds it in O(E). Local traversal then scales with
the matching adjacency bucket rather than unrelated graph edges. The index is rebuildable and is
not serialized into the graph cache.

The `demo` command builds a compact first-party graph through the same `AtlasGraph`, relation
catalog, serializer, and viewer used by scanned projects. It writes the graph only to an
automatically cleaned temporary directory and never scans the current working directory. The
viewer builds one reusable adjacency view after loading the graph, then derives evidence paths
locally with deterministic breadth-first traversal in both edge directions, limited to depth 6,
800 visited nodes, and 6 proof-oriented results. Path labels use
the stored forward or inverse relation; they are structural explanations, not proof of causality
or completeness.

Graph comparison is a pure operation over two validated caches. Diff schema 1 excludes generation
timestamps and sorts added, removed, and changed nodes plus added and removed edges. The same two
graphs therefore produce byte-for-byte identical JSON suitable for CI artifacts or `--check` gates.

ChangeSet schema 1 is a separate, deterministic Git input boundary. Commit and range scopes resolve
user revisions to full commit IDs before diffing; commit scope compares with its first parent and
uses an explicit root-commit path when no parent exists. Staged scope compares the index, while
worktree scope compares tracked state with `HEAD` and separately enumerates ignored-aware untracked
paths. The model stores status, project-relative current/previous paths, and bounded current-side
hunk ranges only. It does not retain raw patch lines or read untracked file contents. Fixed Git
arguments disable external diffs, text conversion, color, and submodule traversal; revision, byte,
file, hunk, path, and timeout bounds fail closed.

Optional Change Analysis schema 1 always builds a fresh read-only graph of the current worktree.
For worktree scope that scan is aligned by construction. For staged, commit, and range scopes,
bounded blob comparison checks each current artifact against the index or resolved head revision;
line endings are normalized and mismatches become `unknown/stale` before symbol inference. A file
is `analyzed/high` only when every current-side hunk maps to validated source spans (currently the
Python AST adapter). Existing artifacts without complete spans remain `fallback/low`; deleted,
missing, private, unmerged, or stale artifacts remain `unknown/none`. Unsupported but present files
are explicit file fallbacks. Durable vault notes map through frontmatter identity, generated vault
outputs are recognized as derived artifacts, and `Private/` is excluded before Git metadata
collection. The result embeds ChangeSet scope/revisions and per-file freshness, confidence,
artifact IDs, and provenance without treating absence as proof of no impact.

Change Report schema 1 composes that aligned analysis with two bounded graph queries. Requirement
ranking walks only incoming `implemented-by`, `tracked-by`, and `drives` intent links. Exact symbol
paths can reach the default medium threshold; any route that begins at a file or crosses `defines`
is capped at low confidence, so two requirements sharing one file are not treated as sharing one
changed symbol. Test candidates reuse the existing recommendation engine. File fallbacks may
inspect bounded defined symbols to find useful targets, but their scores are capped and the policy
still requires the full suite. `unknown` analysis abstains completely; `fallback` reports either
targeted-plus-full-suite or full-suite-fallback. The report is deterministic, advisory, and never
claims behavioral completeness.

Review Report schema 1 is a presentation envelope over an explicit range Change Report, not a
second inference engine. It preserves the resolved base/head identities, analysis state,
confidence, evidence, and test strategy while adding a fixed `shadow` mode contract. Markdown and
JSON are deterministic renderings of that envelope. SARIF 2.1.0 maps fallback or unknown analysis,
possible requirement impact, and full-suite policy to separate fixed rules. Results are sorted and
bounded, locations accept only encoded project-relative paths and current-side hunk regions, and no
source snippet or absolute path is emitted. A valid review always returns success in shadow mode;
provider APIs, credentials, comments, uploads, and blocking policy remain outside this layer.

Optional Test Outcome schema 1 is a separate strict JSON input, never inferred from unkeyed JUnit
or file timestamps. It binds a complete executed-path set to one full commit ID and stores only
canonical project-relative paths, fixed statuses, and bounded optional durations. A review compares
selected and executed paths only when that commit exactly equals the resolved head; stale input is
reported but all comparison sets are empty. The resulting sets describe one run and are not labeled
as false positives, false negatives, necessity, sufficiency, or behavioral proof.

`changes --report --open` serves the exact fresh in-memory graph used for analysis together with
the report; it does not fall back to a potentially stale graph cache or persist an extra report.
The loopback viewer fetches the optional report endpoint, renders strategy/coverage plus ranked
requirements and tests, and focuses the corresponding graph node when a report item is selected.
The normal viewer receives a 404 for that optional endpoint and continues with graph-only mode.

`review --open` uses the same serving boundary with a separate optional `/review.json` endpoint.
The client prefers that envelope when present, unwraps its nested Change Report for existing ranked
items, and adds revision scope plus commit-keyed outcome freshness and observational comparison.
No second scan, cache fallback, provider request, or persisted review artifact is introduced.

Test recommendation is also a pure graph query. Recommendation schema 1 accepts commit, file,
symbol, or test targets. Fixed scores distinguish exactly changed tests, exact-symbol structural
links, recent co-change, one-hop exact-symbol dependents, file fallback, and filename convention.
For a symbol target, file fallback stays below the default medium threshold. If a candidate test
has exact evidence for a different symbol in the same file, that file fallback is suppressed.
Nested symbols can fall back to a referenced owning symbol; when an owner-named test exists, that
focused match replaces unrelated users of the same large class. A selected file uses exact symbols
from its most recent dated analyzed change when available. A selected file or symbol can also use
tests changed in that same most recent change as explicit historical evidence.

Dependency propagation is deliberately narrow: only production files that directly import the
exact target symbol are inspected, and only tests directly linked to that dependent file qualify.
There is no unrestricted file-level transitive or barrel traversal. Recent co-change commits are
limited to five latest-date records, exact-symbol dependents to 1,000, and the existing artifact,
candidate, reason, observation, and result bounds still apply. The default medium threshold hides
weak file and filename-only symbol fallback. JUnit aggregates remain unscored observations because
freshness is unknown. No test is executed, and missing output is never treated as proof of no
impact.

Recommendation evaluation is a second pure layer around the unchanged production query. Schema-1
label files declare a closed-world `complete-test-set` policy, exact graph target IDs, and complete
project-relative expected test paths. The evaluator resolves every identity strictly, runs the
same bounded recommendation query at a selected threshold and limit, and calculates per-case and
micro-aggregate TP, FP, FN, precision, and recall. It does not infer ground truth from history,
silently skip stale labels, tune scores, execute tests, or add timestamps to output. Undefined
metrics remain explicit, and every report warns that its cases do not establish general accuracy.

Corpus evaluation composes multiple saved graphs and their closed-world labels without merging
graph identities. A strict manifest resolves every input below the invoking project root, then the
same evaluator runs at low, medium, and high confidence with one shared result limit. Per-project
counts remain separate; corpus totals are micro aggregates from summed TP, FP, and FN. Output
contains aggregates rather than every ranked case, keeping the schema bounded while individual
evaluation remains available for diagnosis. One invalid graph or label aborts the corpus.

Real-world evaluation places a provenance gate before the same scanner, recommendation query, and
corpus evaluator. Its strict manifest records only a GitHub URL, full commit, language, SPDX
identifier, bounded license path and SHA-256, and project-local labels. Every checkout must match
the origin and commit, be clean, and contain the reviewed license bytes. The evaluator constructs a
fixed default configuration instead of loading checkout-owned configuration, scans in memory, and
persists nothing. Repository acquisition remains a separate approval-gated action; third-party
source, history, branding, and generated graphs remain outside the product.

The synthetic scale benchmark constructs a relevant commit/file/test chain and bounded unrelated
edges entirely in memory. It reports graph and result counts, a full-scan reference work estimate,
indexed bucket work, and cold/warm timings. Timings are diagnostic and environment-specific; the
stable correctness contract is the graph shape, result identities, and bounded local work.

Release verification is outside the runtime package and executes no repository project code. A
cross-platform subprocess test exercises the installed console module from initialization through
scan, impact, recommendation, and loopback HTTP retrieval. The release builder creates a wheel and
source distribution twice under one fixed `SOURCE_DATE_EPOCH`; the verifier requires matching
artifact names and SHA-256 hashes, checks every wheel `RECORD` entry, validates package metadata,
entry point, web assets, and MIT license bytes, and rejects project-only vault, benchmark,
workflow, and local configuration data from the source archive. Publication remains a separate,
explicitly approved external action.

The loopback viewer uses a narrow `ThreadingHTTPServer` subclass that binds through `TCPServer`
and records the validated numeric server address directly. It avoids the standard HTTP server's
reverse DNS lookup, which is unnecessary for local serving and can delay startup on constrained
macOS runners.

## 3. Project brain

The `atlas/` folder is an Obsidian vault and the durable human-readable layer.

- Human/agent-owned: Brain, Requirements, Decisions, Issues, Evidence, Reviews, Sessions
- Scanner-owned: Code, Symbols, Tests (including imported aggregates), Commits
- Local-only: Private

Generated notes link to one another with standard wikilinks. Human notes can link to any
generated note and remain untouched by subsequent scans. Graph health flags orphans but
does not silently invent meaning.

Vault synchronization is failure-preserving. It renders the complete desired generated set in
memory, skips byte-identical targets, writes each changed note to a dot-prefixed sibling temporary file,
and atomically replaces the target with bounded retries for recognized sharing or permission
locks. Only after all desired replacements succeed are marked stale notes pruned. A persistent
replacement failure leaves the previous target and all not-yet-updated targets present and skips
stale cleanup. This is per-file atomic replacement, not a cross-file transaction.

Human notes may preserve link meaning with `relation:: [[target]]`. Only the documented relation
vocabulary is accepted as typed input; unknown labels fall back to generic references.

## Trust boundaries

Repository contents, Markdown, and commit subjects are untrusted data. IntentAtlas parses
them without executing them, redacts common secret forms, skips private and ignored areas,
rejects graph identity collisions, and serves the viewer only on loopback. See `SECURITY.md`.

## Inspiration boundary

The graph-first, vault-first, and progressive-disclosure principles are inspired by the
MIT-licensed `breferrari/obsidian-mind` project. IntentAtlas has an independent Python
implementation and a different domain: linking software intent to delivery evidence.
