---
id: ADR-029
type: decision
status: accepted
phase: 13
---
# ADR-029 - Model workspace boundaries and import semantic evidence

## Context

The current graph is repository-rooted. Python recognizes the repository root and one leading
`src/` interpretation, JavaScript/TypeScript resolves conservative relative imports, and Go uses a
bounded module projection. This is useful for small and conventional repositories but insufficient
for multiple source roots, package workspaces, aliases, nested modules, and repeated package names.

Selecting one candidate by traversal order creates false certainty. Recursively teaching built-in
regex/AST/lexer adapters every compiler and build-system rule would also duplicate mature language
tooling, expand the trust boundary, and become unsustainable.

The viewer bounds DOM rendering but still receives and indexes the complete graph. Adapter caches
are content-addressed but whole-adapter fragments, so a local change still hashes the complete
declared language input set and can rebuild unrelated project material.

## Decision

Introduce a versioned workspace layer with explicit repository, project/package, and source-root or
module-boundary identities. Discover boundaries only from supported, bounded, declarative metadata
or explicit IntentAtlas configuration. Do not execute package managers, build tools, compilers,
plugins, or project scripts. Unknown and conflicting declarations become diagnostics.

Resolvers operate on candidate sets scoped by the declared project. Direct module, import, symbol,
test, and re-export relationships that require unique ownership are created only for one aligned
candidate. Ambiguity is preserved in analysis output and may lower the affected artifact to
`fallback` or `unknown`; it never selects a convenient target.

Extend open evidence through a strict revision-bound semantic projection. Accept explicit local
SCIP documents within fixed file, occurrence, symbol, relationship, string, and nesting limits.
Persist only normalized symbol/range/relation observations and producer/schema/revision provenance,
not source text or raw documents. Exact claims require:

1. a safe project-relative path outside every Private boundary;
2. one workspace/project owner;
3. an exact scanned revision and aligned current artifact;
4. a valid occurrence/range and supported semantic role;
5. a producer/schema capability identified in the compatibility matrix.

Anything else remains a bounded observation, fallback, or unknown. IntentAtlas imports semantic
evidence; it does not launch or download the indexer that produced it.

Partition structural cache fragments by adapter and declared project/package. Fingerprint only the
partition's bounded inputs and versioned dependencies. Build a new complete graph in isolation and
retain last-known-good graph/cache artifacts on a failed partition or budget. Record deterministic
diagnostics for rebuilt, reused, rejected, ambiguous, and stale partitions.

Version the graph schema and provide an explicit deterministic migration reader for the previously
supported schema. Do not mutate durable Markdown identities merely to match a derived schema. Any
new node/relation kinds receive documented forward/inverse semantics and compatibility status.

Serve viewer search, neighborhood, paths, and report details through bounded loopback query
responses. The first page/window must not serialize or index the complete graph. The complete
derived graph remains local and queryable, while every response carries total/omitted counts and
snapshot identity.

## Consequences

- Monorepo precision improves by making ownership explicit, while unsupported layouts abstain
  rather than becoming guessed edges.
- Precise language tooling can contribute through a standard local evidence artifact without
  expanding the runtime execution boundary.
- A graph schema migration and new workspace relation vocabulary require stronger compatibility and
  round-trip tests.
- Partitioned cache and bounded viewer APIs add implementation complexity and more derived artifacts
  to invalidate, but reduce whole-repository work.
- Scale claims require both deterministic work counters and recorded real hardware metrics; wall
  time alone is not a portable CI assertion.
- Cross-repository intelligence, arbitrary plugin execution, compiler-indexer development, and
  distributed execution remain separate non-goals.

## Links

- Requirement: REQ-029 (available through the incoming `drives` relationship)
- tracked-by:: [[Issues/ISSUE-027 - Implement semantic monorepo foundation]]
- Adapter strategy: [[Brain/Language Adapter Strategy]]
- Open-evidence decision: [[Decisions/ADR-023 - Separate observations from aligned execution evidence]]
- Scale decision: [[Decisions/ADR-024 - Validate adapters and render bounded graph windows]]
- Strategy: [[Brain/Phase 11B-13 Delivery Strategy]]
