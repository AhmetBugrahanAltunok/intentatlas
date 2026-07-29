from __future__ import annotations

import re
from typing import Any

SECRET_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key|access[_-]?token|token|secret|password)\s*[:=]\s*([^\s,;]+)"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{12,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bnvapi-[A-Za-z0-9_-]{12,}\b"),
    re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----"),
)


def redact(value: Any) -> Any:
    """Redact common secret shapes before untrusted metadata is persisted."""

    if isinstance(value, dict):
        return {
            key: ("[REDACTED]" if _secret_key(str(key)) else redact(item))
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    if not isinstance(value, str):
        return value

    text = value
    for pattern in SECRET_PATTERNS:
        if pattern.groups >= 2:
            text = pattern.sub(lambda match: f"{match.group(1)}=[REDACTED]", text)
        else:
            text = pattern.sub("[REDACTED]", text)
    return text


def _secret_key(key: str) -> bool:
    normalized = key.casefold().replace("-", "_")
    return any(
        marker in normalized
        for marker in ("api_key", "access_token", "password", "private_key", "secret")
    )
