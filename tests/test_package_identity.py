from __future__ import annotations

import os
from pathlib import Path

import _package_identity
import conftest
import pytest


def _declare(monkeypatch: pytest.MonkeyPatch, mode: str | None) -> None:
    if mode is None:
        monkeypatch.delenv(_package_identity.MODE_VARIABLE, raising=False)
        return
    monkeypatch.setenv(_package_identity.MODE_VARIABLE, mode)


def _import_root(monkeypatch: pytest.MonkeyPatch, root: Path) -> None:
    monkeypatch.setattr(_package_identity, "IMPORT_ROOT", root)


def test_working_tree_import_satisfies_the_default_source_claim(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _declare(monkeypatch, None)
    _import_root(monkeypatch, _package_identity.SOURCE_IMPORT_ROOT)
    assert _package_identity.declared_mode() == _package_identity.SOURCE_MODE
    assert _package_identity.identity_error() is None


def test_installed_package_cannot_masquerade_as_the_working_tree(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    site_packages = tmp_path / "site-packages"
    _declare(monkeypatch, None)
    _import_root(monkeypatch, site_packages)
    error = _package_identity.identity_error()
    assert error is not None
    assert str(site_packages) in error
    assert str(_package_identity.SOURCE_IMPORT_ROOT) in error
    assert 'pip install -e ".[dev]"' in error
    assert f"{_package_identity.MODE_VARIABLE}={_package_identity.INSTALLED_MODE}" in error


def test_working_tree_cannot_masquerade_as_a_verified_distribution(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _declare(monkeypatch, _package_identity.INSTALLED_MODE)
    _import_root(monkeypatch, _package_identity.SOURCE_IMPORT_ROOT)
    error = _package_identity.identity_error()
    assert error is not None
    assert str(_package_identity.SOURCE_IMPORT_ROOT) in error


def test_declared_installed_distribution_is_accepted(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _declare(monkeypatch, _package_identity.INSTALLED_MODE)
    _import_root(monkeypatch, tmp_path / "site-packages")
    assert _package_identity.identity_error() is None


def test_unknown_declared_mode_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    _declare(monkeypatch, "whichever")
    _import_root(monkeypatch, _package_identity.SOURCE_IMPORT_ROOT)
    error = _package_identity.identity_error()
    assert error is not None
    assert "'source'" in error
    assert "'installed'" in error


def test_session_start_refuses_a_contradicted_claim(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _declare(monkeypatch, None)
    _import_root(monkeypatch, tmp_path / "site-packages")
    with pytest.raises(pytest.UsageError):
        conftest.pytest_sessionstart(None)  # type: ignore[arg-type]


def test_session_start_accepts_a_matching_claim(monkeypatch: pytest.MonkeyPatch) -> None:
    _declare(monkeypatch, None)
    _import_root(monkeypatch, _package_identity.SOURCE_IMPORT_ROOT)
    assert conftest.pytest_sessionstart(None) is None  # type: ignore[arg-type]


def test_child_environment_exports_an_absolute_working_tree_root(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    root = tmp_path / "src"
    _import_root(monkeypatch, root)
    environment = _package_identity.child_environment({})
    assert environment["PYTHONPATH"] == str(root)
    assert Path(environment["PYTHONPATH"]).is_absolute()


def test_child_environment_preserves_existing_entries_without_duplicating(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    root = tmp_path / "src"
    _import_root(monkeypatch, root)
    existing = os.pathsep.join([str(root), str(tmp_path / "other")])
    environment = _package_identity.child_environment({"PYTHONPATH": existing})
    assert environment["PYTHONPATH"].split(os.pathsep) == [str(root), str(tmp_path / "other")]


def test_child_environment_leaves_an_interpreter_default_root_alone(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    roots = _package_identity._interpreter_import_roots()
    if not roots:
        pytest.skip("The interpreter reports no site-packages root")
    _import_root(monkeypatch, next(iter(roots)))
    assert "PYTHONPATH" not in _package_identity.child_environment({})


def test_the_running_session_agrees_with_its_own_declaration() -> None:
    assert _package_identity.identity_error() is None
    assert _package_identity.PACKAGE_ROOT.name == "intentatlas"
