from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

CONFIG_NAME = "intentatlas.json"
MAX_REPORT_SOURCES = 32


@dataclass(slots=True)
class ProjectConfig:
    schema_version: int = 1
    vault: str = "atlas"
    graph: str = ".intentatlas/graph.json"
    git_history_limit: int = 25
    coverage_reports: list[str] = field(default_factory=list)
    test_reports: list[str] = field(default_factory=list)
    exclude: list[str] = field(
        default_factory=lambda: [
            ".git",
            ".intentatlas",
            ".mypy_cache",
            ".obsidian",
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
            coverage_reports=_report_sources(raw, "coverage_reports"),
            test_reports=_report_sources(raw, "test_reports"),
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
        return _inside(root, self.graph, "graph")

    def vault_path(self, root: Path) -> Path:
        return _inside(root, self.vault, "vault")


def _inside(root: Path, configured: str, label: str) -> Path:
    base = root.resolve()
    target = (base / configured).resolve()
    if target == base:
        raise ValueError(f"Configured {label} path must be below the project root: {configured}")
    if base not in target.parents:
        raise ValueError(f"Configured path escapes project root: {configured}")
    return target


def _report_sources(raw: dict[str, Any], key: str) -> list[str]:
    value = raw.get(key, [])
    if not isinstance(value, list):
        raise ValueError(f"Configured {key} must be a list")
    if len(value) > MAX_REPORT_SOURCES:
        raise ValueError(f"Configured {key} exceeds the {MAX_REPORT_SOURCES}-report limit")
    if any(not isinstance(item, str) for item in value):
        raise ValueError(f"Configured {key} must contain only path strings")
    sources = [item.strip() for item in value]
    if any(not source for source in sources):
        raise ValueError(f"Configured {key} contains an empty path")
    return list(dict.fromkeys(sources))
