from __future__ import annotations

import base64
import csv
import gzip
import hashlib
import io
import tarfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from tools.verify_release import verify_release


def _digest(value: bytes) -> str:
    encoded = base64.urlsafe_b64encode(hashlib.sha256(value).digest()).rstrip(b"=")
    return "sha256=" + encoded.decode("ascii")


def _write_wheel(directory: Path, license_bytes: bytes, package_value: bytes = b"package") -> Path:
    directory.mkdir(parents=True)
    dist_info = "intentatlas-0.1.0.dist-info"
    values = {
        "intentatlas/__init__.py": package_value,
        "intentatlas/__main__.py": b"main",
        "intentatlas/cli.py": b"cli",
        "intentatlas/web/app.js": b"app",
        "intentatlas/web/index.html": b"html",
        "intentatlas/web/styles.css": b"css",
        f"{dist_info}/METADATA": (
            b"Metadata-Version: 2.4\nName: intentatlas\nVersion: 0.1.0\n"
            b"Author: IntentAtlas contributors\nLicense-Expression: MIT\nRequires-Python: >=3.11\n"
        ),
        f"{dist_info}/WHEEL": b"Wheel-Version: 1.0\nTag: py3-none-any\n",
        f"{dist_info}/entry_points.txt": (
            b"[console_scripts]\nintentatlas = intentatlas.cli:main\n"
        ),
        f"{dist_info}/licenses/LICENSE": license_bytes,
    }
    record_name = f"{dist_info}/RECORD"
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    for name, value in values.items():
        writer.writerow((name, _digest(value), len(value)))
    writer.writerow((record_name, "", ""))
    values[record_name] = output.getvalue().encode("utf-8")

    wheel = directory / "intentatlas-0.1.0-py3-none-any.whl"
    with ZipFile(wheel, "w", ZIP_DEFLATED) as archive:
        for name, value in values.items():
            archive.writestr(name, value)
    return wheel


def _write_sdist(directory: Path) -> Path:
    directory.mkdir(exist_ok=True)
    root = "intentatlas-0.1.0"
    values = {
        "LICENSE": b"license",
        "README.md": b"readme",
        "RELEASING.md": b"releasing",
        "pyproject.toml": b"project",
        "src/intentatlas/__init__.py": b"package",
        "src/intentatlas/web/index.html": b"html",
        "tools/verify_release.py": b"verify",
    }
    tar_bytes = io.BytesIO()
    with tarfile.open(fileobj=tar_bytes, mode="w") as archive:
        for name, value in values.items():
            info = tarfile.TarInfo(f"{root}/{name}")
            info.size = len(value)
            info.mtime = 0
            archive.addfile(info, io.BytesIO(value))
    sdist = directory / "intentatlas-0.1.0.tar.gz"
    sdist.write_bytes(gzip.compress(tar_bytes.getvalue(), mtime=0))
    return sdist


def test_release_verifier_accepts_repeated_project_archives(tmp_path) -> None:
    project_root = Path(__file__).parents[1]
    first = tmp_path / "first"
    second = tmp_path / "second"
    license_bytes = (project_root / "LICENSE").read_bytes()
    first_wheel = _write_wheel(first, license_bytes)
    _write_wheel(second, license_bytes)
    _write_sdist(first)
    _write_sdist(second)

    result = verify_release(first, second, project_root)

    assert result.wheel == first_wheel.name
    assert result.wheel_files == 11
    assert result.sdist_files == 7


def test_release_verifier_rejects_non_reproducible_wheel(tmp_path) -> None:
    project_root = Path(__file__).parents[1]
    first = tmp_path / "first"
    second = tmp_path / "second"
    license_bytes = (project_root / "LICENSE").read_bytes()
    _write_wheel(first, license_bytes, b"first")
    _write_wheel(second, license_bytes, b"second")
    _write_sdist(first)
    _write_sdist(second)

    with pytest.raises(ValueError, match="not byte-identical"):
        verify_release(first, second, project_root)
