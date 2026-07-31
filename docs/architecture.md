# Architecture

IntentAtlas has three layers with explicit ownership.

```text
Repository ──scan──> AtlasGraph ──sync──> Obsidian vault
                         │
                         ├──query──> impact/status CLI
                         ├──compare──> deterministic CI graph diff
                         └──serve──> local web viewer
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

The Git adapter reads commit metadata and changed paths with fixed read-only commands. Repository
discovery prunes excluded directories before descent, does not follow directory links, and
excludes the configured vault from the repository walk. Adapters never execute project code.

Configured evidence adapters read only explicit project-local reports. The Cobertura and JUnit
importers reject DTD/entity declarations, enforce byte and record limits, map report paths only to
one discovered file, and aggregate coverage or result counts without retaining raw failure output.

## 2. AtlasGraph

`AtlasGraph` is the language-neutral contract. Nodes have a stable ID, kind, label, path,
and small metadata object. Directed edges have a source, target, typed relation, inverse label,
category, and provenance. The graph schema is versioned; schema 2 loads schema-1 caches and
rebuilds them with the current relation catalog. Schema-2 caches are accepted only when their
embedded catalog, edge categories, and inverse labels match the runtime registry.
The graph is serialized to `.intentatlas/graph.json`; it is a rebuildable cache, not the
source of truth.

Graph comparison is a pure operation over two validated caches. Diff schema 1 excludes generation
timestamps and sorts added, removed, and changed nodes plus added and removed edges. The same two
graphs therefore produce byte-for-byte identical JSON suitable for CI artifacts or `--check` gates.

## 3. Project brain

The `atlas/` folder is an Obsidian vault and the durable human-readable layer.

- Human/agent-owned: Brain, Requirements, Decisions, Issues, Evidence, Reviews, Sessions
- Scanner-owned: Code, Symbols, Tests (including imported aggregates), Commits
- Local-only: Private

Generated notes link to one another with standard wikilinks. Human notes can link to any
generated note and remain untouched by subsequent scans. Graph health flags orphans but
does not silently invent meaning.

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
