from __future__ import annotations

import configparser
import re
import tomllib
from dataclasses import dataclass
from fnmatch import fnmatchcase
from pathlib import Path
from typing import Any

from .safe_io import read_bounded_regular_file

MAX_TEST_CONFIG_BYTES = 1_000_000
MAX_PYTHON_TEST_PATTERNS = 32
MAX_PYTHON_TEST_PATTERN_LENGTH = 100
DEFAULT_PYTHON_TEST_PATTERNS = ("test_*.py", "*_test.py")
_SAFE_PATTERN = re.compile(r"^[A-Za-z0-9_.*?\[\]-]+\.py$")


@dataclass(frozen=True, slots=True)
class PythonTestPolicy:
    patterns: tuple[str, ...]
    evidence: str


@dataclass(frozen=True, slots=True)
class TestRole:
    role: str
    runner: str
    evidence: str
    pattern: str | None = None

    def metadata(self) -> dict[str, str]:
        value = {
            "test_role": self.role,
            "test_runner": self.runner,
            "test_role_evidence": self.evidence,
        }
        if self.pattern is not None:
            value["test_pattern"] = self.pattern
        return value


def load_python_test_policy(root: Path) -> PythonTestPolicy:
    """Load one bounded pytest filename declaration without importing project code."""

    pyproject = _toml_patterns(root / "pyproject.toml")
    if pyproject is not None:
        return pyproject
    for name, section in (
        ("pytest.ini", "pytest"),
        ("setup.cfg", "tool:pytest"),
        ("tox.ini", "pytest"),
    ):
        declared = _ini_patterns(root / name, section)
        if declared is not None:
            return declared
    return PythonTestPolicy(DEFAULT_PYTHON_TEST_PATTERNS, "pytest-default-python-files")


def classify_python_test(path: Path, policy: PythonTestPolicy) -> TestRole:
    name = path.name.casefold()
    if name == "__init__.py":
        return TestRole("package", "pytest", "python-package-marker")
    if name == "conftest.py":
        return TestRole("fixture", "pytest", "pytest-conftest")
    for pattern in policy.patterns:
        if fnmatchcase(name, pattern.casefold()):
            return TestRole("runnable", "pytest", policy.evidence, pattern)
    return TestRole("support", "pytest", policy.evidence)


def _toml_patterns(path: Path) -> PythonTestPolicy | None:
    raw = read_bounded_regular_file(path, MAX_TEST_CONFIG_BYTES)
    if raw is None:
        return None
    try:
        parsed = tomllib.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError):
        return None
    value = _nested(parsed, "tool", "pytest", "ini_options", "python_files")
    if value is None:
        return None
    patterns = _patterns(value)
    return PythonTestPolicy(patterns, "pyproject-pytest-python-files")


def _ini_patterns(path: Path, section: str) -> PythonTestPolicy | None:
    raw = read_bounded_regular_file(path, MAX_TEST_CONFIG_BYTES)
    if raw is None:
        return None
    parser = configparser.ConfigParser(interpolation=None, strict=True)
    try:
        parser.read_string(raw.decode("utf-8"))
    except (UnicodeDecodeError, configparser.Error):
        return None
    if not parser.has_option(section, "python_files"):
        return None
    patterns = _patterns(parser.get(section, "python_files"))
    return PythonTestPolicy(patterns, f"{path.name}-pytest-python-files")


def _patterns(value: object) -> tuple[str, ...]:
    candidates: list[object] = []
    if isinstance(value, str):
        candidates.extend(value.split())
    elif isinstance(value, list):
        candidates.extend(value)
    else:
        return ()
    patterns: list[str] = []
    for candidate in candidates[: MAX_PYTHON_TEST_PATTERNS + 1]:
        if not isinstance(candidate, str):
            return ()
        pattern = candidate.strip()
        if (
            not pattern
            or len(pattern) > MAX_PYTHON_TEST_PATTERN_LENGTH
            or "/" in pattern
            or "\\" in pattern
            or ".." in pattern
            or _SAFE_PATTERN.fullmatch(pattern) is None
        ):
            return ()
        if pattern not in patterns:
            patterns.append(pattern)
    if len(patterns) > MAX_PYTHON_TEST_PATTERNS:
        return ()
    return tuple(patterns)


def _nested(value: dict[str, Any], *keys: str) -> object | None:
    current: object = value
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current
