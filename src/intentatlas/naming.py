from __future__ import annotations

import re
from pathlib import Path

from .models import Node

INVALID_FILENAME = re.compile(r'[<>:"/\\|?*\[\]#^\x00-\x1f]+')


def note_title(node: Node) -> str:
    """Return a readable, stable Obsidian note title for a graph node."""

    if node.metadata.get("owner") == "user" and node.path:
        return Path(node.path).stem
    if node.kind == "symbol":
        location = (node.path or "unknown").replace("/", " › ")
        return f"{node.label} — {location}"
    if node.kind == "commit":
        short = str(node.metadata.get("short", node.id.removeprefix("commit:")[:8]))
        return f"Commit {short} — {node.label}"
    if node.path:
        return node.path.replace("/", " › ")
    return node.label


def safe_filename(value: str, limit: int = 180) -> str:
    portable = value.replace(" › ", " - ").replace("—", "-")
    cleaned = INVALID_FILENAME.sub("-", portable).strip(" .-")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return (cleaned[:limit].rstrip(" .-") or "Untitled") + ".md"
