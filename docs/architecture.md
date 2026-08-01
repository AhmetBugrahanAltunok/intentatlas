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
they do not mutate the graph directly. The Python adapter uses the standard-library AST. The
TypeScript/JavaScript adapter conservatively recognizes explicit declarations and static relative
module references in `.ts`, `.tsx`, `.js`, and `.jsx` files without requiring Node. Bare package
imports are not resolved into repository relationships.

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

The delivery adapter reads only explicit project-local schema-1 JSON snapshots after path, byte,
record, link, field, type, duplicate-key, and URL validation. It creates bounded delivery-issue and
pull-request nodes, then links only exact local intent IDs, issue IDs, file paths, and commit SHAs.
Raw provider payloads, bodies, comments, authors, credentials, and unknown fields are rejected.

## 2. AtlasGraph

`AtlasGraph` is the language-neutral contract. Nodes have a stable ID, kind, label, path,
and small metadata object. Directed edges have a source, target, typed relation, inverse label,
category, and provenance. The graph schema is versioned; schema 2 loads schema-1 caches and
rebuilds them with the current relation catalog. Schema-2 caches are accepted only when their
embedded catalog, edge categories, and inverse labels match the runtime registry.
Relation schema 3 adds invertible `modifies`/`modified-by` semantics for direct symbol-change
evidence. The graph is serialized to `.intentatlas/graph.json`; it is a rebuildable cache, not the
source of truth.

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

Test recommendation is also a pure graph query. Recommendation schema 1 accepts commit, file,
symbol, or test targets and ranks only direct `changes`, `modifies`, `defines`, and `tests`
evidence. Fixed scores distinguish exact-symbol structural links, file fallback, filename
conventions, and directly changed tests. The default medium threshold hides weak filename-only
file matches. JUnit aggregates remain unscored observations because freshness is unknown.
Artifact signals, candidate tests, reasons, observations, and returned results have explicit
bounds. No test is executed, and missing output is never treated as proof of no impact.

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
