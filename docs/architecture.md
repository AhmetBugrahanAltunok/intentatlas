# Architecture

IntentAtlas has three layers with explicit ownership.

```text
Repository ──scan──> AtlasGraph ──sync──> Obsidian vault
                         │
                         ├──query──> impact/status CLI
                         └──serve──> local web viewer
```

## 1. Repository adapters

Adapters extract only structural metadata. The Python adapter records files, classes,
functions, imports, and test relationships. The Git adapter reads commit metadata and
changed paths with fixed read-only commands. Repository discovery prunes excluded directories
before descent, does not follow directory links, and excludes the configured vault from the
repository walk. Adapters never execute project code.

## 2. AtlasGraph

`AtlasGraph` is the language-neutral contract. Nodes have a stable ID, kind, label, path,
and small metadata object. Directed edges have a source, target, typed relation, inverse label,
category, and provenance. The graph schema is versioned; schema 2 loads schema-1 caches and
rebuilds them with the current relation catalog. Schema-2 caches are accepted only when their
embedded catalog, edge categories, and inverse labels match the runtime registry.
The graph is serialized to `.intentatlas/graph.json`; it is a rebuildable cache, not the
source of truth.

## 3. Project brain

The `atlas/` folder is an Obsidian vault and the durable human-readable layer.

- Human/agent-owned: Brain, Requirements, Decisions, Issues, Evidence, Reviews, Sessions
- Scanner-owned: Code, Symbols, Tests, Commits
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
