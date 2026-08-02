from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any

from .safe_io import read_bounded_regular_file

CONFIG_NAME = "intentatlas.json"
MAX_CONFIG_BYTES = 64_000
MAX_EXCLUDES = 128
MAX_REPORT_SOURCES = 32
CONFIG_FIELDS = frozenset(
    {
        "schema_version",
        "vault",
        "graph",
        "git_history_limit",
        "coverage_reports",
        "test_reports",
        "delivery_reports",
        "scip_reports",
        "sarif_reports",
        "test_execution_reports",
        "exclude",
    }
)


@dataclass(slots=True)
class ProjectConfig:
    schema_version: int = 1
    vault: str = "atlas"
    graph: str = ".intentatlas/graph.json"
    git_history_limit: int = 25
    coverage_reports: list[str] = field(default_factory=list)
    test_reports: list[str] = field(default_factory=list)
    delivery_reports: list[str] = field(default_factory=list)
    scip_reports: list[str] = field(default_factory=list)
    sarif_reports: list[str] = field(default_factory=list)
    test_execution_reports: list[str] = field(default_factory=list)
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
        if path.is_symlink():
            raise ValueError(f"Cannot read {path}: configuration file may not be a symbolic link")
        if not path.exists():
            return cls()
        try:
            encoded = read_bounded_regular_file(path, MAX_CONFIG_BYTES)
            if encoded is None:
                raise ValueError(
                    "configuration must be a stable regular file within the byte limit"
                )
            document = json.loads(
                encoded.decode("utf-8"),
                object_pairs_hook=_reject_duplicate_keys,
            )
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"Cannot read {path}: {exc}") from exc
        if not isinstance(document, dict):
            raise ValueError("IntentAtlas configuration must be a JSON object")
        raw: dict[str, Any] = document
        unknown = sorted(set(raw) - CONFIG_FIELDS)
        if unknown:
            raise ValueError(f"Unknown IntentAtlas config fields: {', '.join(unknown)}")
        schema_version = raw.get("schema_version", 1)
        if not isinstance(schema_version, int) or isinstance(schema_version, bool):
            raise ValueError("Configured schema_version must be an integer")
        if schema_version != 1:
            raise ValueError(f"Unsupported IntentAtlas config schema: {schema_version}")
        history_limit = raw.get("git_history_limit", 25)
        if not isinstance(history_limit, int) or isinstance(history_limit, bool):
            raise ValueError("Configured git_history_limit must be an integer")
        return cls(
            schema_version=1,
            vault=_string_field(raw, "vault", "atlas"),
            graph=_string_field(raw, "graph", ".intentatlas/graph.json"),
            git_history_limit=max(0, min(history_limit, 250)),
            coverage_reports=_report_sources(raw, "coverage_reports"),
            test_reports=_report_sources(raw, "test_reports"),
            delivery_reports=_report_sources(raw, "delivery_reports"),
            scip_reports=_report_sources(raw, "scip_reports"),
            sarif_reports=_report_sources(raw, "sarif_reports"),
            test_execution_reports=_report_sources(raw, "test_execution_reports"),
            exclude=_exclude_sources(raw, cls().exclude),
        )

    def save_if_missing(self, root: Path) -> Path:
        path = root / CONFIG_NAME
        if path.is_symlink():
            raise ValueError(f"Configuration path may not be a symbolic link: {path}")
        try:
            with path.open("x", encoding="utf-8", newline="\n") as handle:
                handle.write(json.dumps(asdict(self), indent=2, ensure_ascii=False) + "\n")
        except FileExistsError:
            if path.is_symlink() or not path.is_file():
                raise ValueError(
                    f"Configuration path must be a regular file: {path}"
                ) from None
        return path

    def graph_path(self, root: Path) -> Path:
        return _inside(root, self.graph, "graph", protect_private=True)

    def vault_path(self, root: Path) -> Path:
        return _inside(root, self.vault, "vault", protect_private=True)


def _inside(root: Path, configured: str, label: str, *, protect_private: bool) -> Path:
    base = root.resolve()
    unresolved = base / configured
    private = base / "atlas" / "Private"
    lexical_target = Path(os.path.abspath(unresolved))
    if protect_private and (
        lexical_target == private or private in lexical_target.parents
    ):
        raise ValueError(f"Configured {label} path may not be inside atlas/Private: {configured}")
    target = unresolved.resolve()
    if target == base:
        raise ValueError(f"Configured {label} path must be below the project root: {configured}")
    if base not in target.parents:
        raise ValueError(f"Configured path escapes project root: {configured}")
    if protect_private and (target == private or private in target.parents):
        raise ValueError(f"Configured {label} path may not be inside atlas/Private: {configured}")
    return target


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key in IntentAtlas configuration: {key}")
        result[key] = value
    return result


def _string_field(raw: dict[str, Any], key: str, default: str) -> str:
    value = raw.get(key, default)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Configured {key} must be a non-empty string")
    return value


def _exclude_sources(raw: dict[str, Any], default: list[str]) -> list[str]:
    value = raw.get("exclude", default)
    if not isinstance(value, list):
        raise ValueError("Configured exclude must be a list")
    if len(value) > MAX_EXCLUDES:
        raise ValueError(f"Configured exclude exceeds the {MAX_EXCLUDES}-path limit")
    if any(not isinstance(item, str) for item in value):
        raise ValueError("Configured exclude must contain only path strings")
    sources: list[str] = []
    for item in value:
        normalized = item.strip().replace("\\", "/").strip("/")
        pure = PurePosixPath(normalized)
        if (
            not normalized
            or pure.is_absolute()
            or ".." in pure.parts
            or any(ord(character) < 32 for character in normalized)
        ):
            raise ValueError(f"Configured exclude contains an unsafe path: {item!r}")
        sources.append(normalized)
    return list(dict.fromkeys(sources))


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
