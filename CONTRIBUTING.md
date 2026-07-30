# Contributing to IntentAtlas

Thanks for helping make software intent easier to understand.

## Development setup

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
```

## Before opening a pull request

1. Open an issue for large changes so the intent is clear before implementation.
2. Keep adapters small and keep the core graph language-neutral.
3. Add tests for behavior and a fixture for each new language adapter.
4. Do not commit private vault material, secrets, generated caches, or local workspaces.
5. Update the canonical [`Product Roadmap`](atlas/Brain/Product%20Roadmap.md) or an ADR when a
   change alters a product or architecture decision. The root `ROADMAP.md` is archival only.
6. For phase work, record the complete change inventory, exact verification results, remaining
   risks, and review outcome in the vault before marking the phase complete.

Pull requests should explain the requirement, decision, implementation, and verification.
That trace is the product's own standard and the standard for contributions.
