---
id: language-adapter-strategy
type: memory
status: active
---
# Language Adapter Strategy

IntentAtlas will compete through trustworthy intent-to-evidence traceability, not by claiming a
large but shallow language count. The language-neutral graph and typed adapter contract must stay
stable before more parsers are added.

## Sequence

1. Phase 2 establishes typed relations, schema migration, and the adapter contract.
2. Phase 3 adds TypeScript/JavaScript as the first new adapter family.
3. Go follows as a compact, strongly structured validation of the adapter boundary.
4. Rust or Java follows according to user demand, fixture quality, and maintenance cost.

## Selection gates

- A language needs representative public fixtures and deterministic parser behavior.
- Every adapter must connect files, symbols, imports, and tests without executing project code.
- New language support must remain local, offline-capable, and independent of API keys.
- Each adapter requires focused tests, cross-platform verification, documentation, and evidence.
- External projects may inform product expectations, but their code, assets, and identity are not
  copied into IntentAtlas.

This strategy is governed by the [[Brain/Product Roadmap]] and protects the product's distinct
vault-first Requirement → Decision → Issue → Code → Test → Evidence → Commit model.
