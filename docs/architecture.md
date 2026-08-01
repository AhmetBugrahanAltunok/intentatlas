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

Adapter conformance contract version 1 validates stable names, complete suffix inputs, cache
versions, declared evidence, canonical symbol nodes, structural endpoint shapes, bounded counts,
and deterministic repeated output. Fresh fragments are validated before merge or cache storage;
strictly decoded cache fragments pass the same validator before reuse. The public fixture helper is
an executable compatibility target, not an external adapter loader. See
[language adapter conformance](adapter-conformance.md).

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

The `demo` command builds a compact, pre-authored first-party same-file counterexample through the
same `AtlasGraph`, relation catalog, recommendation engine, Change Report, serializer, and viewer
used after real scans. It demonstrates downstream inference and presentation, not repository
discovery, AST parsing, or Git diff extraction. The interactive default writes the graph only to an
automatically cleaned temporary directory, serves a production-shaped report from the same graph
snapshot, and never scans the current working directory. Explicit text/JSON report modes derive
the changed symbol, exact-symbol requirement, and test evidence from graph indexes and production
recommendations, then exit without a listener. Both modes state that an omitted same-file path is
not proof of no impact or no test need. The viewer normalizes accepted names to numeric IPv4
loopback, rejects foreign `Host` headers, and applies defensive response policies before returning
local graph data. It builds one reusable adjacency view after loading the graph, then derives
evidence paths locally with deterministic breadth-first traversal in both edge directions, limited
to depth 6, 800 visited nodes, and 6 proof-oriented results. Path labels use the stored forward or
inverse relation; they are structural explanations, not proof of causality or completeness.

The client also builds stable node, edge, degree, search, and adjacency indexes once. SVG rendering
is limited to a deterministic 240-node/900-edge window: a layer-balanced overview or a two-hop
focus neighborhood. Global search and linked navigation can focus a node outside the current
window; relationship details are capped at 80 items with an explicit omitted count. The complete
graph remains available in memory, so a window is a rendering projection rather than data loss.
Initial JSON transfer still scales with total graph size; server-side shards remain a later option.

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
entry point, pure-Python tag, web assets, canonical version source, dependency contract, and MIT
license bytes. It also requires exact metadata-derived outer names, rejects
duplicate/platform-colliding or unsafe archive paths, compares every source-archive file against a
positive reviewed-checkout manifest, requires the wheel's complete member set, and requires both
artifact runtime payloads to match those reviewed bytes. Generated `PKG-INFO` is validated
semantically against the checkout's fixed backend, hook-free build configuration, complete project
metadata field set, and dependency metadata. Rebuilding the verified source archive under the same
epoch must reproduce the direct wheel byte-for-byte. The source archive includes only the small
original closed-world corpus needed by its test suite plus declared source, tests, docs, tools, and
release files; vault data,
local state, real-world benchmark records, workflows, and undeclared roots remain excluded.
Release backend/frontend versions are fixed for candidate reproduction. Publication remains a
separate, explicitly approved external action.

Release hardening adds three independent gates around that verifier. Fixed-seed generated graphs
and hostile JSON mutations must either preserve graph invariants or fail with a bounded validation
error. A Chrome-family headless browser must execute the packaged viewer and render the expected
240-node large-graph window. Maintained Python source is checked statically, while a repository
policy test rejects every external Action reference that is not a full immutable commit SHA.

After repeated archive verification, the verifier can write canonical provenance JSON containing
the exact source revision, fixed build epoch, artifact names, sizes, SHA-256 digests, and completed
checks. This record is deterministic descriptive evidence, not a signature. Default CI remains
verification-only; trusted publishing is a separate protected manual boundary over explicitly
approved source and artifact identities. External environment configuration must restrict that
identity to protected `main` or an explicitly approved release ref.

The loopback viewer uses a narrow IPv4 `ThreadingHTTPServer` subclass that binds through
`TCPServer`. The accepted `localhost` alias is normalized to numeric `127.0.0.1` before binding and
the emitted URL uses that validated address. This avoids the standard HTTP server's reverse DNS
lookup, which is unnecessary for local serving and can delay startup on constrained macOS runners.

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
