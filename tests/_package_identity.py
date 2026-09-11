"""Resolve the ``intentatlas`` package under test and build matching child environments.

A test session imports ``intentatlas`` either from this working tree or from a deliberately
installed distribution. Both are legitimate, but they must never be confused: an installed copy
can hide current source changes, and a working-tree copy cannot prove a packaged artifact. The
session therefore declares which one it verifies, and every subprocess derives its import root
from the imported module instead of assuming a repository layout.
"""

from __future__ import annotations

import os
import sysconfig
from collections.abc import Mapping
from pathlib import Path

import intentatlas

MODE_VARIABLE = "INTENTATLAS_TEST_PACKAGE"
SOURCE_MODE = "source"
INSTALLED_MODE = "installed"

PACKAGE_ROOT = Path(intentatlas.__file__).resolve().parent
IMPORT_ROOT = PACKAGE_ROOT.parent
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_IMPORT_ROOT = REPOSITORY_ROOT / "src"


def _interpreter_import_roots() -> frozenset[Path]:
    paths = sysconfig.get_paths()
    return frozenset(
        Path(paths[name]).resolve() for name in ("purelib", "platlib") if paths.get(name)
    )


def declared_mode() -> str:
    """Return the package identity this session claims to verify."""

    return os.environ.get(MODE_VARIABLE, SOURCE_MODE)


def identity_error() -> str | None:
    """Return an actionable message when the imported package contradicts the declared mode."""

    mode = declared_mode()
    if mode not in {SOURCE_MODE, INSTALLED_MODE}:
        return (
            f"{MODE_VARIABLE} must be {SOURCE_MODE!r} or {INSTALLED_MODE!r}, not {mode!r}. "
            f"Unset it to verify the working tree at {SOURCE_IMPORT_ROOT}."
        )
    imported_from_source = IMPORT_ROOT == SOURCE_IMPORT_ROOT
    if mode == SOURCE_MODE and not imported_from_source:
        return (
            f"Tests import intentatlas from {IMPORT_ROOT}, not the working tree at "
            f"{SOURCE_IMPORT_ROOT}. An installed copy can hide or contradict current source "
            'changes. Install the working tree with: python -m pip install -e ".[dev]". '
            f"To verify a deliberately installed distribution instead, set "
            f"{MODE_VARIABLE}={INSTALLED_MODE}."
        )
    if mode == INSTALLED_MODE and imported_from_source:
        return (
            f"{MODE_VARIABLE}={INSTALLED_MODE} claims an installed distribution, but tests "
            f"import intentatlas from the working tree at {SOURCE_IMPORT_ROOT}. Install the "
            "artifact under verification, or unset the variable to verify the working tree."
        )
    return None


def child_environment(base: Mapping[str, str] | None = None) -> dict[str, str]:
    """Return an environment whose subprocesses import the same package as this session.

    A package already on the interpreter's default import path needs no help. A working-tree
    package does, and its absolute root is prepended so a child started in any directory
    resolves it.
    """

    environment = dict(os.environ if base is None else base)
    if IMPORT_ROOT in _interpreter_import_roots():
        return environment
    existing = environment.get("PYTHONPATH", "")
    roots = [str(IMPORT_ROOT), *(entry for entry in existing.split(os.pathsep) if entry)]
    environment["PYTHONPATH"] = os.pathsep.join(dict.fromkeys(roots))
    return environment
