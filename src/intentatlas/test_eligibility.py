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
MAX_PYTHON_TEST_PATHS = 32
MAX_PYTHON_TEST_PATH_LENGTH = 200
DEFAULT_PYTHON_TEST_PATTERNS = ("test_*.py", "*_test.py")
_SAFE_PATTERN = re.compile(r"^[A-Za-z0-9_.*?\[\]-]+\.py$")
_SAFE_PATH_PART = re.compile(r"^[A-Za-z0-9_.-]+$")


@dataclass(frozen=True, slots=True)
class PythonTestPolicy:
    patterns: tuple[str, ...]
    evidence: str
    testpaths: tuple[str, ...] | None = None


@dataclass(frozen=True, slots=True)
class TestRole:
    role: str
    runner: str
    evidence: str
    pattern: str | None = None
    discovery_root: str | None = None

    def metadata(self) -> dict[str, str]:
        value = {
            "test_role": self.role,
            "test_runner": self.runner,
            "test_role_evidence": self.evidence,
        }
        if self.pattern is not None:
            value["test_pattern"] = self.pattern
        if self.discovery_root is not None:
            value["test_discovery_root"] = self.discovery_root
        return value


def load_python_test_policy(root: Path) -> PythonTestPolicy:
    """Load one bounded pytest filename policy without importing project code."""

    pyproject = _toml_policy(root / "pyproject.toml")
    if pyproject is not None:
        return pyproject
    for name, section in (
        ("pytest.ini", "pytest"),
        ("setup.cfg", "tool:pytest"),
        ("tox.ini", "pytest"),
    ):
        declared = _ini_policy(root / name, section)
        if declared is not None:
            return declared
    return PythonTestPolicy(DEFAULT_PYTHON_TEST_PATTERNS, "pytest-default-python-files")


def classify_python_test(path: Path, policy: PythonTestPolicy) -> TestRole:
    name = path.name.casefold()
    if name == "__init__.py":
        return TestRole("package", "pytest", "python-package-marker")
    if name == "conftest.py":
        return TestRole("fixture", "pytest", "pytest-conftest")
    discovery_root = _matching_testpath(path, policy.testpaths)
    if policy.testpaths is not None and discovery_root is None:
        return TestRole("support", "pytest", policy.evidence)
    for pattern in policy.patterns:
        if fnmatchcase(name, pattern.casefold()):
            return TestRole(
                "runnable", "pytest", policy.evidence, pattern, discovery_root
            )
    return TestRole("support", "pytest", policy.evidence)


def _toml_policy(path: Path) -> PythonTestPolicy | None:
    raw = read_bounded_regular_file(path, MAX_TEST_CONFIG_BYTES)
    if raw is None:
        return None
    try:
        parsed = tomllib.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError):
        return None
    options = _nested(parsed, "tool", "pytest", "ini_options")
    if not isinstance(options, dict):
        return None
    python_files = options.get("python_files")
    testpaths = options.get("testpaths")
    if python_files is None and testpaths is None:
        return None
    patterns = (
        DEFAULT_PYTHON_TEST_PATTERNS if python_files is None else _patterns(python_files)
    )
    roots = None if testpaths is None else _testpaths(testpaths)
    evidence = (
        "pyproject-pytest-python-files"
        if testpaths is None
        else "pyproject-pytest-discovery"
    )
    return PythonTestPolicy(patterns, evidence, roots)


def _ini_policy(path: Path, section: str) -> PythonTestPolicy | None:
    raw = read_bounded_regular_file(path, MAX_TEST_CONFIG_BYTES)
    if raw is None:
        return None
    parser = configparser.ConfigParser(interpolation=None, strict=True)
    try:
        parser.read_string(raw.decode("utf-8"))
    except (UnicodeDecodeError, configparser.Error):
        return None
    has_patterns = parser.has_option(section, "python_files")
    has_testpaths = parser.has_option(section, "testpaths")
    if not has_patterns and not has_testpaths:
        return None
    patterns = (
        _patterns(parser.get(section, "python_files"))
        if has_patterns
        else DEFAULT_PYTHON_TEST_PATTERNS
    )
    roots = _testpaths(parser.get(section, "testpaths")) if has_testpaths else None
    evidence = (
        f"{path.name}-pytest-discovery"
        if has_testpaths
        else f"{path.name}-pytest-python-files"
    )
    return PythonTestPolicy(patterns, evidence, roots)


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


def _testpaths(value: object) -> tuple[str, ...]:
    candidates: list[object] = []
    if isinstance(value, str):
        candidates.extend(value.split())
    elif isinstance(value, list):
        candidates.extend(value)
    else:
        return ()
    roots: list[str] = []
    for candidate in candidates[: MAX_PYTHON_TEST_PATHS + 1]:
        if not isinstance(candidate, str):
            return ()
        normalized = candidate.strip().replace("\\", "/").strip("/")
        parts = normalized.split("/")
        if (
            not normalized
            or len(normalized) > MAX_PYTHON_TEST_PATH_LENGTH
            or candidate.startswith(("/", "\\"))
            or ":" in candidate
            or any(part in {"", ".", ".."} for part in parts)
            or any(_SAFE_PATH_PART.fullmatch(part) is None for part in parts)
        ):
            return ()
        if normalized not in roots:
            roots.append(normalized)
    if len(roots) > MAX_PYTHON_TEST_PATHS:
        return ()
    return tuple(roots)


def _matching_testpath(path: Path, roots: tuple[str, ...] | None) -> str | None:
    if roots is None:
        return None
    normalized = path.as_posix().casefold()
    for root in roots:
        folded = root.casefold()
        if normalized == folded or normalized.startswith(f"{folded}/"):
            return root
    return None


def _nested(value: dict[str, Any], *keys: str) -> object | None:
    current: object = value
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current
