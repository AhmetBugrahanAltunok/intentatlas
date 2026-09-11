"""Fail the session before any test runs when the imported package is not the declared one."""

from __future__ import annotations

import _package_identity
import pytest


def pytest_sessionstart(session: pytest.Session) -> None:
    error = _package_identity.identity_error()
    if error is not None:
        raise pytest.UsageError(error)
