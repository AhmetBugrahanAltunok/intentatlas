from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

CONFIG_NAME = "intentatlas.json"


@dataclass(slots=True)
class ProjectConfig:
    schema_version: int = 1
    vault: str = "atlas"
    graph: str = ".intentatlas/graph.json"
    git_history_limit: int = 25
    exclude: list[str] = field(
        default_factory=lambda: [
            ".git",
            ".intentatlas",
            ".mypy_cache",
            ".pytest_cache",
            ".pytest_tmp",
            ".ruff_cache",
            ".venv",
            "atlas",
            "build",
            "dist",
            "node_modules",
            "var",
            "vendor",
        ]
    )

    @classmethod
    def load(cls, root: Path) -> ProjectConfig:
        path = root / CONFIG_NAME
        if not path.exists():
            return cls()
        try:
            raw: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Cannot read {path}: {exc}") from exc
        if raw.get("schema_version", 1) != 1:
            raise ValueError(f"Unsupported IntentAtlas config schema: {raw.get('schema_version')}")
        return cls(
            schema_version=1,
            vault=str(raw.get("vault", "atlas")),
            graph=str(raw.get("graph", ".intentatlas/graph.json")),
            git_history_limit=max(0, min(int(raw.get("git_history_limit", 25)), 250)),
            exclude=[str(item) for item in raw.get("exclude", cls().exclude)],
        )

    def save_if_missing(self, root: Path) -> Path:
        path = root / CONFIG_NAME
        if not path.exists():
            path.write_text(
                json.dumps(asdict(self), indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
                newline="\n",
            )
        return path

    def graph_path(self, root: Path) -> Path:
        return _inside(root, self.graph)

    def vault_path(self, root: Path) -> Path:
        return _inside(root, self.vault)


def _inside(root: Path, configured: str) -> Path:
    base = root.resolve()
    target = (base / configured).resolve()
    if target != base and base not in target.parents:
        raise ValueError(f"Configured path escapes project root: {configured}")
    return target
