
---
id: REQ-001
type: requirement
status: accepted
---
# Explain change impact

Before changing a project artifact, a developer can see its upstream intent and downstream
implementation or verification relationships.

## Acceptance

- A local scan creates a deterministic relationship graph.
- The graph is explorable in Obsidian and a standalone local viewer.
- Impact can be queried without sending source code to an external service.

Implemented through [[Decisions/ADR-001 - Vault-first intent graph]] and verified by
[[Evidence/EVD-001 - Initial scanner acceptance]].
