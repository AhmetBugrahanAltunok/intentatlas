from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import tarfile
from dataclasses import dataclass
from email.parser import BytesParser
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

EXPECTED_NAME = "intentatlas"
REQUIRED_PACKAGE_FILES = {
    "intentatlas/__init__.py",
    "intentatlas/__main__.py",
    "intentatlas/cli.py",
    "intentatlas/web/app.js",
    "intentatlas/web/index.html",
    "intentatlas/web/styles.css",
}
FORBIDDEN_SDIST_ROOTS = {
    ".github",
    "AGENTS.md",
    "atlas",
    "benchmarks",
    "intentatlas.json",
}


@dataclass(frozen=True)
class ReleaseVerification:
    wheel: str
    wheel_sha256: str
    sdist: str
    sdist_sha256: str
    wheel_files: int
    sdist_files: int


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _single_artifact(directory: Path, pattern: str, label: str) -> Path:
    if not directory.is_dir():
        raise ValueError(f"Release directory does not exist: {directory}")
    artifacts = sorted(directory.glob(pattern))
    if len(artifacts) != 1:
        raise ValueError(f"Expected exactly one {label} in {directory}, found {len(artifacts)}")
    artifact = artifacts[0]
    if artifact.is_symlink() or not artifact.is_file():
        raise ValueError(f"Release {label} must be a regular file: {artifact}")
    return artifact


def _safe_member(name: str, label: str) -> PurePosixPath:
    path = PurePosixPath(name)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise ValueError(f"Unsafe {label} member path: {name}")
    return path


def _record_digest(value: bytes) -> str:
    digest = hashlib.sha256(value).digest()
    return "sha256=" + base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def _validate_wheel(path: Path, project_root: Path) -> tuple[str, int]:
    with ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError(f"Wheel contains a corrupt member: {path}")
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError("Wheel contains duplicate member names")
        safe_names = [_safe_member(name, "wheel") for name in names]
        dist_info = sorted(
            path.parts[0] for path in safe_names if path.parts[0].endswith(".dist-info")
        )
        if not dist_info:
            raise ValueError("Wheel is missing its dist-info directory")
        dist_info_name = dist_info[0]
        if any(path.parts[0] not in {EXPECTED_NAME, dist_info_name} for path in safe_names):
            raise ValueError("Wheel contains files outside the package and dist-info directories")

        required = REQUIRED_PACKAGE_FILES | {
            f"{dist_info_name}/METADATA",
            f"{dist_info_name}/WHEEL",
            f"{dist_info_name}/entry_points.txt",
            f"{dist_info_name}/RECORD",
            f"{dist_info_name}/licenses/LICENSE",
        }
        missing = sorted(required - set(names))
        if missing:
            raise ValueError(f"Wheel is missing required files: {', '.join(missing)}")

        metadata = BytesParser().parsebytes(archive.read(f"{dist_info_name}/METADATA"))
        version = metadata.get("Version")
        if metadata.get("Name") != EXPECTED_NAME:
            raise ValueError("Wheel metadata has the wrong project name")
        if not version or f"{EXPECTED_NAME}-{version}" not in dist_info_name:
            raise ValueError("Wheel filename and metadata version do not agree")
        if metadata.get("Requires-Python") != ">=3.11":
            raise ValueError("Wheel metadata has the wrong Python requirement")
        if metadata.get("License-Expression") != "MIT":
            raise ValueError("Wheel metadata must retain the MIT license expression")
        if metadata.get("Author") != "IntentAtlas contributors":
            raise ValueError("Wheel metadata has unexpected author attribution")

        entry_points = archive.read(f"{dist_info_name}/entry_points.txt").decode("utf-8")
        if entry_points.strip() != "[console_scripts]\nintentatlas = intentatlas.cli:main":
            raise ValueError("Wheel console entry point is missing or unexpected")
        if archive.read(f"{dist_info_name}/licenses/LICENSE") != (
            project_root / "LICENSE"
        ).read_bytes():
            raise ValueError("Wheel license does not match the repository license")

        record_name = f"{dist_info_name}/RECORD"
        rows = list(csv.reader(io.StringIO(archive.read(record_name).decode("utf-8"))))
        if len(rows) != len(names) or {row[0] for row in rows} != set(names):
            raise ValueError("Wheel RECORD does not describe every archive member exactly once")
        for row in rows:
            if len(row) != 3:
                raise ValueError("Wheel RECORD contains a malformed row")
            member, digest, size = row
            if member == record_name:
                if digest or size:
                    raise ValueError("Wheel RECORD must leave its own hash and size empty")
                continue
            value = archive.read(member)
            if digest != _record_digest(value) or size != str(len(value)):
                raise ValueError(f"Wheel RECORD mismatch for {member}")
    return version, len(names)


def _validate_sdist(path: Path, version: str) -> int:
    expected_root = f"{EXPECTED_NAME}-{version}"
    required = {
        "LICENSE",
        "README.md",
        "RELEASING.md",
        "pyproject.toml",
        "src/intentatlas/__init__.py",
        "src/intentatlas/web/index.html",
        "tools/verify_release.py",
    }
    files: set[str] = set()
    with tarfile.open(path, "r:gz") as archive:
        for member in archive.getmembers():
            member_path = _safe_member(member.name, "source distribution")
            if member_path.parts[0] != expected_root:
                raise ValueError("Source distribution has an unexpected root directory")
            if member.issym() or member.islnk() or not (member.isfile() or member.isdir()):
                raise ValueError(f"Source distribution contains an unsafe member: {member.name}")
            relative = PurePosixPath(*member_path.parts[1:])
            if relative.parts and relative.parts[0] in FORBIDDEN_SDIST_ROOTS:
                raise ValueError(f"Source distribution contains excluded project data: {relative}")
            if member.isfile():
                files.add(str(relative))
    missing = sorted(required - files)
    if missing:
        raise ValueError(f"Source distribution is missing required files: {', '.join(missing)}")
    return len(files)


def verify_release(first: Path, second: Path, project_root: Path) -> ReleaseVerification:
    first_wheel = _single_artifact(first, "*.whl", "wheel")
    second_wheel = _single_artifact(second, "*.whl", "wheel")
    first_sdist = _single_artifact(first, "*.tar.gz", "source distribution")
    second_sdist = _single_artifact(second, "*.tar.gz", "source distribution")
    if first_wheel.name != second_wheel.name or first_sdist.name != second_sdist.name:
        raise ValueError("Repeated builds produced different artifact names")

    first_wheel_hash = _sha256(first_wheel)
    first_sdist_hash = _sha256(first_sdist)
    if first_wheel_hash != _sha256(second_wheel):
        raise ValueError("Repeated wheel builds are not byte-identical")
    if first_sdist_hash != _sha256(second_sdist):
        raise ValueError("Repeated source distributions are not byte-identical")

    version, wheel_files = _validate_wheel(first_wheel, project_root)
    sdist_files = _validate_sdist(first_sdist, version)
    return ReleaseVerification(
        wheel=first_wheel.name,
        wheel_sha256=first_wheel_hash,
        sdist=first_sdist.name,
        sdist_sha256=first_sdist_hash,
        wheel_files=wheel_files,
        sdist_files=sdist_files,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify IntentAtlas release contents and repeated-build reproducibility."
    )
    parser.add_argument("first", type=Path, help="First build output directory")
    parser.add_argument("second", type=Path, help="Second build output directory")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        result = verify_release(args.first, args.second, args.project_root.resolve())
    except (OSError, ValueError, tarfile.TarError) as exc:
        parser.exit(1, f"release verification failed: {exc}\n")
    print(f"Verified reproducible wheel: {result.wheel} sha256={result.wheel_sha256}")
    print(f"Verified reproducible sdist: {result.sdist} sha256={result.sdist_sha256}")
    print(f"Validated archive files: wheel={result.wheel_files}, sdist={result.sdist_files}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
