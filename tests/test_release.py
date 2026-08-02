from __future__ import annotations

import base64
import csv
import gzip
import hashlib
import io
import json
import stat
import tarfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import pytest

from tools.verify_release import (
    _validate_project_metadata,
    release_provenance,
    verify_approved_hashes,
    verify_release,
    write_release_provenance,
)

FIXTURE_VERSION = "9.8.7"
PACKAGE_INIT = f'__version__ = "{FIXTURE_VERSION}"\n'.encode()
PROJECT_METADATA = (
    b"[build-system]\nrequires = [\"hatchling==1.31.0\"]\n"
    b"build-backend = \"hatchling.build\"\n\n[project]\n"
    b"name = \"intentatlas\"\ndynamic = [\"version\"]\n"
    b"description = \"Fixture project\"\nreadme = \"README.md\"\n"
    b"requires-python = \">=3.11\"\nlicense = \"MIT\"\n"
    b"authors = [{ name = \"IntentAtlas contributors\" }]\n"
    b"keywords = [\"fixture\"]\n"
    b"classifiers = [\"Programming Language :: Python :: 3\"]\n"
    b"dependencies = []\n\n"
    b"[project.optional-dependencies]\n"
    b"release = [\"build==1.3.0\", \"hatchling==1.31.0\", \"packaging==26.2\"]\n\n"
    b"[project.scripts]\nintentatlas = \"intentatlas.cli:main\"\n\n"
    b"[project.urls]\nHomepage = \"https://example.invalid/intentatlas\"\n\n"
    b"[tool.hatch.version]\npath = \"src/intentatlas/__init__.py\"\n\n"
    b"[tool.hatch.build.targets.wheel]\npackages = [\"src/intentatlas\"]\n\n"
    b"[tool.hatch.build.targets.sdist]\ninclude = [\n"
    b'  "/src",\n  "/tests",\n  "/benchmarks/recommendation-corpus.json",\n'
    b'  "/benchmarks/corpus/*.json",\n  "/benchmarks/longitudinal/*.json",\n'
    b'  "/tools/verify_release.py",\n  "/docs",\n'
    b'  "/CHANGELOG.md",\n  "/CODE_OF_CONDUCT.md",\n  "/CONTRIBUTING.md",\n'
    b'  "/LICENSE",\n  "/README.md",\n  "/README.tr.md",\n  "/RELEASING.md",\n'
    b'  "/SECURITY.md",\n  "/pyproject.toml",\n]\n'
)


def _package_metadata(extra_metadata: bytes = b"") -> bytes:
    return (
        f"Metadata-Version: 2.4\nName: intentatlas\nVersion: {FIXTURE_VERSION}\n"
        "Summary: Fixture project\nAuthor: IntentAtlas contributors\n"
        "License-Expression: MIT\nLicense-File: LICENSE\nRequires-Python: >=3.11\n"
        "Description-Content-Type: text/markdown\nKeywords: fixture\n"
        "Classifier: Programming Language :: Python :: 3\n"
        "Project-URL: Homepage, https://example.invalid/intentatlas\n"
        "Provides-Extra: release\n"
        "Requires-Dist: build==1.3.0; extra == 'release'\n"
        "Requires-Dist: hatchling==1.31.0; extra == 'release'\n"
        "Requires-Dist: packaging==26.2; extra == 'release'\n"
    ).encode() + extra_metadata + b"\nreadme"


def _zip_info(name: str, mode: int = stat.S_IFREG | 0o644) -> ZipInfo:
    info = ZipInfo(name, date_time=(2024, 1, 1, 0, 0, 0))
    info.compress_type = ZIP_DEFLATED
    info.external_attr = mode << 16
    return info


def _package_values(
    *,
    package_value: bytes = PACKAGE_INIT,
    cli_value: bytes = b"cli",
) -> dict[str, bytes]:
    return {
        "intentatlas/__init__.py": package_value,
        "intentatlas/__main__.py": b"main",
        "intentatlas/cli.py": cli_value,
        "intentatlas/web/app.js": b"app",
        "intentatlas/web/index.html": b"html",
        "intentatlas/web/styles.css": b"css",
    }


def _write_project(
    root: Path,
    *,
    package_value: bytes = PACKAGE_INIT,
    cli_value: bytes = b"cli",
    project_metadata: bytes = PROJECT_METADATA,
) -> Path:
    root.mkdir()
    repository_root = Path(__file__).parents[1]
    values = {
        "LICENSE": (repository_root / "LICENSE").read_bytes(),
        "README.md": b"readme",
        "RELEASING.md": b"releasing",
        "pyproject.toml": project_metadata,
        "tools/verify_release.py": b"verify",
        **{
            f"src/{name}": value
            for name, value in _package_values(
                package_value=package_value,
                cli_value=cli_value,
            ).items()
        },
    }
    for name, value in values.items():
        destination = root.joinpath(*name.split("/"))
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(value)
    return root


def _digest(value: bytes) -> str:
    encoded = base64.urlsafe_b64encode(hashlib.sha256(value).digest()).rstrip(b"=")
    return "sha256=" + encoded.decode("ascii")


def _write_wheel(
    directory: Path,
    license_bytes: bytes,
    package_value: bytes = PACKAGE_INIT,
    cli_value: bytes = b"cli",
    extra_metadata: bytes = b"",
    extra_wheel_metadata: bytes = b"",
    extra_dist_info: dict[str, bytes] | None = None,
    extra_members: list[tuple[str, bytes, int | None]] | None = None,
) -> Path:
    directory.mkdir(parents=True)
    dist_info = f"intentatlas-{FIXTURE_VERSION}.dist-info"
    values = {
        **_package_values(package_value=package_value, cli_value=cli_value),
        f"{dist_info}/METADATA": _package_metadata(extra_metadata),
        f"{dist_info}/WHEEL": (
            b"Wheel-Version: 1.0\nGenerator: hatchling 1.31.0\n"
            b"Root-Is-Purelib: true\nTag: py3-none-any\n"
            + extra_wheel_metadata
        ),
        f"{dist_info}/entry_points.txt": (
            b"[console_scripts]\nintentatlas = intentatlas.cli:main\n"
        ),
        f"{dist_info}/licenses/LICENSE": license_bytes,
    }
    values.update(
        {
            f"{dist_info}/{name}": value
            for name, value in (extra_dist_info or {}).items()
        }
    )
    record_name = f"{dist_info}/RECORD"
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    for name, value in values.items():
        writer.writerow((name, _digest(value), len(value)))
    writer.writerow((record_name, "", ""))
    values[record_name] = output.getvalue().encode("utf-8")

    wheel = directory / f"intentatlas-{FIXTURE_VERSION}-py3-none-any.whl"
    with ZipFile(wheel, "w", ZIP_DEFLATED) as archive:
        for name, value in values.items():
            archive.writestr(_zip_info(name), value)
        for name, value, mode in extra_members or []:
            archive.writestr(_zip_info(name, mode or stat.S_IFREG | 0o644), value)
    return wheel


def _write_sdist(
    directory: Path,
    project_root: Path,
    *,
    package_value: bytes = PACKAGE_INIT,
    cli_value: bytes = b"cli",
    extra_metadata: bytes = b"",
    duplicate_readme: bool = False,
    unsafe_member: str | None = None,
    extra_member: str | None = None,
) -> Path:
    directory.mkdir(exist_ok=True)
    root = f"intentatlas-{FIXTURE_VERSION}"
    package_metadata = _package_metadata(extra_metadata)
    package_values = _package_values(package_value=package_value, cli_value=cli_value)
    values = [
        ("LICENSE", (project_root / "LICENSE").read_bytes()),
        ("PKG-INFO", package_metadata),
        ("README.md", b"readme"),
        ("RELEASING.md", b"releasing"),
        ("pyproject.toml", (project_root / "pyproject.toml").read_bytes()),
        *((f"src/{name}", value) for name, value in package_values.items()),
        ("tools/verify_release.py", b"verify"),
    ]
    if duplicate_readme:
        values.append(("README.md", b"different readme"))
    if unsafe_member is not None:
        values.append((unsafe_member, b"unsafe"))
    if extra_member is not None:
        values.append((extra_member, b"unexpected"))
    tar_bytes = io.BytesIO()
    with tarfile.open(fileobj=tar_bytes, mode="w") as archive:
        for name, value in values:
            info = tarfile.TarInfo(f"{root}/{name}")
            info.size = len(value)
            info.mtime = 0
            archive.addfile(info, io.BytesIO(value))
    sdist = directory / f"intentatlas-{FIXTURE_VERSION}.tar.gz"
    sdist.write_bytes(gzip.compress(tar_bytes.getvalue(), mtime=0))
    return sdist


def test_release_verifier_accepts_repeated_project_archives(tmp_path) -> None:
    project_root = _write_project(tmp_path / "project")
    first = tmp_path / "first"
    second = tmp_path / "second"
    license_bytes = (project_root / "LICENSE").read_bytes()
    first_wheel = _write_wheel(first, license_bytes)
    _write_wheel(second, license_bytes)
    _write_sdist(first, project_root)
    _write_sdist(second, project_root)

    result = verify_release(first, second, project_root)

    assert result.wheel == first_wheel.name
    assert result.version == FIXTURE_VERSION
    assert result.wheel_size == first_wheel.stat().st_size
    assert result.wheel_files == 11
    assert result.sdist_files == 12
    assert result.wheel_generator == "hatchling 1.31.0"


def test_release_verifier_rejects_non_reproducible_wheel(tmp_path) -> None:
    project_root = _write_project(tmp_path / "project")
    first = tmp_path / "first"
    second = tmp_path / "second"
    license_bytes = (project_root / "LICENSE").read_bytes()
    _write_wheel(first, license_bytes, b"first")
    _write_wheel(second, license_bytes, b"second")
    _write_sdist(first, project_root)
    _write_sdist(second, project_root)

    with pytest.raises(ValueError, match="not byte-identical"):
        verify_release(first, second, project_root)


def test_release_verifier_rejects_misleading_artifact_names(tmp_path) -> None:
    project_root = _write_project(tmp_path / "project")
    license_bytes = (project_root / "LICENSE").read_bytes()

    wheel_first = tmp_path / "wheel-first"
    wheel_second = tmp_path / "wheel-second"
    for directory in (wheel_first, wheel_second):
        wheel = _write_wheel(directory, license_bytes)
        wheel.rename(directory / "intentatlas-0.0.0-py3-none-any.whl")
        _write_sdist(directory, project_root)
    with pytest.raises(ValueError, match="filename, dist-info, and metadata"):
        verify_release(wheel_first, wheel_second, project_root)

    sdist_first = tmp_path / "sdist-first"
    sdist_second = tmp_path / "sdist-second"
    for directory in (sdist_first, sdist_second):
        _write_wheel(directory, license_bytes)
        sdist = _write_sdist(directory, project_root)
        sdist.rename(directory / "intentatlas-0.0.0.tar.gz")
    with pytest.raises(ValueError, match="filename and metadata"):
        verify_release(sdist_first, sdist_second, project_root)


def test_release_verifier_rejects_ambiguous_or_unsafe_sdist_members(tmp_path) -> None:
    project_root = _write_project(tmp_path / "project")
    license_bytes = (project_root / "LICENSE").read_bytes()

    duplicate_first = tmp_path / "duplicate-first"
    duplicate_second = tmp_path / "duplicate-second"
    for directory in (duplicate_first, duplicate_second):
        _write_wheel(directory, license_bytes)
        _write_sdist(directory, project_root, duplicate_readme=True)
    with pytest.raises(ValueError, match="duplicate or platform-colliding"):
        verify_release(duplicate_first, duplicate_second, project_root)

    unsafe_first = tmp_path / "unsafe-first"
    unsafe_second = tmp_path / "unsafe-second"
    for directory in (unsafe_first, unsafe_second):
        _write_wheel(directory, license_bytes)
        _write_sdist(directory, project_root, unsafe_member=r"src\..\..\evil.txt")
    with pytest.raises(ValueError, match="Unsafe source distribution member path"):
        verify_release(unsafe_first, unsafe_second, project_root)


def test_release_verifier_requires_wheel_and_sdist_package_byte_parity(tmp_path) -> None:
    project_root = _write_project(tmp_path / "project", cli_value=b"different cli")
    license_bytes = (project_root / "LICENSE").read_bytes()
    first = tmp_path / "first"
    second = tmp_path / "second"
    for directory in (first, second):
        _write_wheel(directory, license_bytes)
        _write_sdist(directory, project_root, cli_value=b"different cli")

    with pytest.raises(ValueError, match="package bytes differ"):
        verify_release(first, second, project_root)


def test_release_verifier_binds_both_artifacts_to_reviewed_checkout_bytes(tmp_path) -> None:
    project_root = _write_project(tmp_path / "project")
    license_bytes = (project_root / "LICENSE").read_bytes()
    first = tmp_path / "first"
    second = tmp_path / "second"
    for directory in (first, second):
        _write_wheel(directory, license_bytes, cli_value=b"identically tampered")
        _write_sdist(directory, project_root, cli_value=b"identically tampered")

    with pytest.raises(ValueError, match="differs from the reviewed source bytes"):
        verify_release(first, second, project_root)


def test_release_verifier_rejects_runtime_version_reassignment(tmp_path) -> None:
    reassigned = (
        f'__version__ = "{FIXTURE_VERSION}"\n'
        '__version__ = "".join(["0.0.0"])\n'
    ).encode()
    project_root = _write_project(tmp_path / "project", package_value=reassigned)
    license_bytes = (project_root / "LICENSE").read_bytes()
    first = tmp_path / "first"
    second = tmp_path / "second"
    for directory in (first, second):
        _write_wheel(directory, license_bytes, package_value=reassigned)
        _write_sdist(directory, project_root, package_value=reassigned)

    with pytest.raises(ValueError, match="exactly one __version__ assignment"):
        verify_release(first, second, project_root)


def test_release_verifier_rejects_indirect_runtime_version_mutation(tmp_path) -> None:
    mutated = (
        f'__version__ = "{FIXTURE_VERSION}"\n'
        'globals()["__version__"] = "0.0.0"\n'
    ).encode()
    project_root = _write_project(tmp_path / "project", package_value=mutated)
    license_bytes = (project_root / "LICENSE").read_bytes()
    first = tmp_path / "first"
    second = tmp_path / "second"
    for directory in (first, second):
        _write_wheel(directory, license_bytes, package_value=mutated)
        _write_sdist(directory, project_root, package_value=mutated)

    with pytest.raises(ValueError, match="version source must remain declarative"):
        verify_release(first, second, project_root)


def test_release_verifier_rejects_injected_install_dependencies(tmp_path) -> None:
    project_root = _write_project(tmp_path / "project")
    license_bytes = (project_root / "LICENSE").read_bytes()
    injected = b"Requires-Dist: unexpected-package>=1\n"
    first = tmp_path / "first"
    second = tmp_path / "second"
    for directory in (first, second):
        _write_wheel(directory, license_bytes, extra_metadata=injected)
        _write_sdist(directory, project_root, extra_metadata=injected)

    with pytest.raises(ValueError, match="dependencies do not match"):
        verify_release(first, second, project_root)


@pytest.mark.parametrize(
    "extra_metadata",
    [
        b"Summary: Conflicting summary\n",
        b"Requires-Python: <3.11\n",
        b"Project-URL: Source, https://example.invalid/unreviewed\n",
    ],
)
def test_release_verifier_rejects_conflicting_or_unreviewed_core_metadata(
    tmp_path, extra_metadata
) -> None:
    project_root = _write_project(tmp_path / "project")
    license_bytes = (project_root / "LICENSE").read_bytes()
    first = tmp_path / "first"
    second = tmp_path / "second"
    for directory in (first, second):
        _write_wheel(directory, license_bytes, extra_metadata=extra_metadata)
        _write_sdist(directory, project_root, extra_metadata=extra_metadata)

    with pytest.raises(ValueError, match="invalid core metadata|unexpected project URLs"):
        verify_release(first, second, project_root)


def test_release_verifier_rejects_duplicate_wheel_metadata(tmp_path) -> None:
    project_root = _write_project(tmp_path / "project")
    license_bytes = (project_root / "LICENSE").read_bytes()
    first = tmp_path / "first"
    second = tmp_path / "second"
    for directory in (first, second):
        _write_wheel(
            directory,
            license_bytes,
            extra_wheel_metadata=b"Generator: unreviewed 1.0\n",
        )
        _write_sdist(directory, project_root)

    with pytest.raises(ValueError, match="expected pure-Python tag"):
        verify_release(first, second, project_root)


def test_release_verifier_rejects_unreviewed_dist_info_files(tmp_path) -> None:
    project_root = _write_project(tmp_path / "project")
    license_bytes = (project_root / "LICENSE").read_bytes()
    first = tmp_path / "first"
    second = tmp_path / "second"
    for directory in (first, second):
        _write_wheel(
            directory,
            license_bytes,
            extra_dist_info={"direct_url.json": b'{"url": "unreviewed"}'},
        )
        _write_sdist(directory, project_root)

    with pytest.raises(ValueError, match="reviewed package manifest"):
        verify_release(first, second, project_root)


@pytest.mark.parametrize(
    "extra_member",
    [".Obsidian/plugins.json", ".intentatlas/graph.json", "secrets/token.txt"],
)
def test_release_verifier_rejects_unreviewed_sdist_roots_case_insensitively(
    tmp_path, extra_member
) -> None:
    project_root = _write_project(tmp_path / "project")
    license_bytes = (project_root / "LICENSE").read_bytes()
    first = tmp_path / "first"
    second = tmp_path / "second"
    for directory in (first, second):
        _write_wheel(directory, license_bytes)
        _write_sdist(directory, project_root, extra_member=extra_member)

    with pytest.raises(ValueError, match="excluded project data|reviewed manifest"):
        verify_release(first, second, project_root)


@pytest.mark.parametrize(
    "members",
    [
        [("intentatlas/linked.py", b"intentatlas/cli.py", stat.S_IFLNK | 0o777)],
        [("intentatlas/cli.py.", b"collision", None)],
        [
            ("intentatlas/caf\N{LATIN SMALL LETTER E WITH ACUTE}.py", b"first", None),
            ("intentatlas/cafe\N{COMBINING ACUTE ACCENT}.py", b"second", None),
        ],
        [("intentatlas/CON.py", b"reserved", None)],
    ],
)
def test_release_verifier_rejects_nonportable_or_nonregular_wheel_members(
    tmp_path, members
) -> None:
    project_root = _write_project(tmp_path / "project")
    license_bytes = (project_root / "LICENSE").read_bytes()
    first = tmp_path / "first"
    second = tmp_path / "second"
    for directory in (first, second):
        _write_wheel(directory, license_bytes, extra_members=members)
        _write_sdist(directory, project_root)

    with pytest.raises(ValueError, match="Wheel contains|Unsafe wheel|platform-colliding"):
        verify_release(first, second, project_root)


@pytest.mark.parametrize(
    "bad_metadata",
    [
        PROJECT_METADATA.replace(
            b'requires = ["hatchling==1.31.0"]',
            b'requires = ["unexpected-backend==1"]',
        ).replace(
            b'build-backend = "hatchling.build"',
            b'build-backend = "unexpected.build"',
        ),
        PROJECT_METADATA.replace(
            b'build-backend = "hatchling.build"',
            b'build-backend = "hatchling.build"\nbackend-path = ["tools"]',
        ),
    ],
)
def test_release_verifier_rejects_unfixed_build_backend(tmp_path, bad_metadata) -> None:
    project_root = _write_project(tmp_path / "project", project_metadata=bad_metadata)
    license_bytes = (project_root / "LICENSE").read_bytes()
    first = tmp_path / "first"
    second = tmp_path / "second"
    for directory in (first, second):
        _write_wheel(directory, license_bytes)
        _write_sdist(directory, project_root)

    with pytest.raises(ValueError, match="fixed Hatchling build backend"):
        verify_release(first, second, project_root)


@pytest.mark.parametrize(
    ("bad_metadata", "message"),
    [
        (
            PROJECT_METADATA.replace(
                b'authors = [{ name = "IntentAtlas contributors" }]',
                b'authors = [{ name = "IntentAtlas contributors" }]\n'
                b'maintainers = [{ name = "Unreviewed maintainer" }]',
            ),
            "unexpected project metadata fields",
        ),
        (
            PROJECT_METADATA
            + b'\n[tool.hatch.build.hooks.custom]\npath = "tools/unreviewed.py"\n',
            "fixed Hatch build configuration",
        ),
        (
            PROJECT_METADATA.replace(b"build==1.3.0", b"build>=1"),
            "fixed release toolchain",
        ),
    ],
)
def test_release_verifier_rejects_unreviewed_project_or_build_configuration(
    bad_metadata, message
) -> None:
    with pytest.raises(ValueError, match=message):
        _validate_project_metadata(bad_metadata)


def test_release_verifier_rejects_malformed_nested_project_tables_cleanly() -> None:
    malformed = (
        b'[build-system]\nrequires = ["hatchling==1.31.0"]\n'
        b'build-backend = "hatchling.build"\n\n'
        b'[project]\nname = "intentatlas"\ndynamic = ["version"]\n'
        b'dependencies = []\n\n[project.optional-dependencies]\n\n'
        b'[tool]\nhatch = "not-a-table"\n'
    )

    with pytest.raises(ValueError, match="invalid Hatch table"):
        _validate_project_metadata(malformed)


def test_release_provenance_is_deterministic_and_bound_to_verified_bytes(tmp_path) -> None:
    project_root = _write_project(tmp_path / "project")
    first = tmp_path / "first"
    second = tmp_path / "second"
    license_bytes = (project_root / "LICENSE").read_bytes()
    wheel = _write_wheel(first, license_bytes)
    _write_wheel(second, license_bytes)
    sdist = _write_sdist(first, project_root)
    _write_sdist(second, project_root)
    result = verify_release(first, second, project_root)
    revision = "a" * 40

    first_record = tmp_path / "provenance-a.json"
    second_record = tmp_path / "provenance-b.json"
    write_release_provenance(
        first_record,
        result,
        source_revision=revision,
        source_date_epoch=1_704_067_200,
    )
    write_release_provenance(
        second_record,
        result,
        source_revision=revision,
        source_date_epoch=1_704_067_200,
    )

    assert first_record.read_bytes() == second_record.read_bytes()
    document = json.loads(first_record.read_text(encoding="utf-8"))
    assert document["source"] == {
        "revision": revision,
        "source_date_epoch": 1_704_067_200,
    }
    assert document["artifacts"] == [
        {
            "name": wheel.name,
            "sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
            "size": wheel.stat().st_size,
            "type": "wheel",
        },
        {
            "name": sdist.name,
            "sha256": hashlib.sha256(sdist.read_bytes()).hexdigest(),
            "size": sdist.stat().st_size,
            "type": "sdist",
        },
    ]
    assert document["verification"]["wheel_generator"] == "hatchling 1.31.0"
    assert "dependency-metadata" in document["verification"]["checks"]
    assert "reviewed-source-manifest" in document["verification"]["checks"]
    assert "reviewed-wheel-manifest" in document["verification"]["checks"]


@pytest.mark.parametrize(
    ("revision", "epoch", "message"),
    [
        ("main", 0, "40-character"),
        ("A" * 40, 0, "40-character"),
        ("a" * 40, -1, "non-negative"),
        ("a" * 40, True, "non-negative"),
    ],
)
def test_release_provenance_rejects_ambiguous_source_inputs(
    tmp_path, revision, epoch, message
) -> None:
    project_root = _write_project(tmp_path / "project")
    first = tmp_path / "first"
    second = tmp_path / "second"
    license_bytes = (project_root / "LICENSE").read_bytes()
    _write_wheel(first, license_bytes)
    _write_wheel(second, license_bytes)
    _write_sdist(first, project_root)
    _write_sdist(second, project_root)
    result = verify_release(first, second, project_root)

    with pytest.raises(ValueError, match=message):
        release_provenance(result, source_revision=revision, source_date_epoch=epoch)


def test_approved_release_hashes_must_match_both_verified_artifacts(tmp_path) -> None:
    project_root = _write_project(tmp_path / "project")
    first = tmp_path / "first"
    second = tmp_path / "second"
    license_bytes = (project_root / "LICENSE").read_bytes()
    _write_wheel(first, license_bytes)
    _write_wheel(second, license_bytes)
    _write_sdist(first, project_root)
    _write_sdist(second, project_root)
    result = verify_release(first, second, project_root)

    verify_approved_hashes(
        result,
        expected_wheel_sha256=result.wheel_sha256,
        expected_sdist_sha256=result.sdist_sha256,
    )
    with pytest.raises(ValueError, match="wheel does not match"):
        verify_approved_hashes(
            result,
            expected_wheel_sha256="0" * 64,
            expected_sdist_sha256=result.sdist_sha256,
        )
    with pytest.raises(ValueError, match="64 lowercase"):
        verify_approved_hashes(
            result,
            expected_wheel_sha256=result.wheel_sha256.upper(),
            expected_sdist_sha256=result.sdist_sha256,
        )
