from __future__ import annotations

import argparse
import ast
import base64
import csv
import hashlib
import io
import json
import re
import stat
import tarfile
import tomllib
import unicodedata
from collections import Counter
from dataclasses import dataclass
from email.parser import BytesParser
from pathlib import Path, PurePosixPath
from zipfile import BadZipFile, ZipFile, ZipInfo

from packaging.metadata import Metadata
from packaging.requirements import InvalidRequirement, Requirement

EXPECTED_NAME = "intentatlas"
PROVENANCE_SCHEMA_VERSION = 1
FULL_GIT_SHA = re.compile(r"[0-9a-f]{40}")
MAX_ARCHIVE_FILES = 10_000
MAX_ARCHIVE_MEMBER_BYTES = 10 * 1024 * 1024
MAX_ARCHIVE_UNCOMPRESSED_BYTES = 100 * 1024 * 1024
REQUIRED_PACKAGE_FILES = {
    "intentatlas/__init__.py",
    "intentatlas/__main__.py",
    "intentatlas/cli.py",
    "intentatlas/onboarding.py",
    "intentatlas/web/app.js",
    "intentatlas/web/index.html",
    "intentatlas/web/styles.css",
}
FORBIDDEN_SDIST_ROOTS = {
    ".git",
    ".github",
    ".intentatlas",
    ".obsidian",
    ".venv",
    "AGENTS.md",
    "atlas",
    "benchmarks",
    "build",
    "dist",
    "intentatlas.json",
    "var",
}
FORBIDDEN_SDIST_ROOTS_CASEFOLDED = {root.casefold() for root in FORBIDDEN_SDIST_ROOTS}
LONGITUDINAL_PILOT_PROJECTS = (
    "antfu-utils",
    "axios",
    "cobra",
    "match",
    "p-limit",
    "schedule",
    "yocto-queue",
    "zustand",
)
ALLOWED_SDIST_BENCHMARKS = {
    "benchmarks/recommendation-corpus.json",
    "benchmarks/corpus/go-package.graph.json",
    "benchmarks/corpus/go-package.labels.json",
    "benchmarks/corpus/python-auth.graph.json",
    "benchmarks/corpus/python-auth.labels.json",
    "benchmarks/corpus/typescript-checkout.graph.json",
    "benchmarks/corpus/typescript-checkout.labels.json",
    "benchmarks/longitudinal/manifest.json",
} | {
    f"benchmarks/longitudinal/{project}.{kind}.json"
    for project in LONGITUDINAL_PILOT_PROJECTS
    for kind in ("labels", "classifications")
}
SDIST_TREE_ROOTS = ("src", "tests", "docs")
SDIST_ROOT_FILES = {
    ".gitignore",
    "CHANGELOG.md",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "README.md",
    "README.tr.md",
    "RELEASING.md",
    "SECURITY.md",
    "pyproject.toml",
    "tools/verify_release.py",
}
WINDOWS_RESERVED_STEMS = {
    "con",
    "prn",
    "aux",
    "nul",
    *(f"com{index}" for index in range(1, 10)),
    *(f"lpt{index}" for index in range(1, 10)),
}
WINDOWS_INVALID_CHARACTERS = frozenset('<>"|?*')
EXPECTED_PROJECT_KEYS = {
    "name",
    "dynamic",
    "description",
    "readme",
    "requires-python",
    "license",
    "authors",
    "keywords",
    "classifiers",
    "dependencies",
    "optional-dependencies",
    "scripts",
    "urls",
}
EXPECTED_SDIST_INCLUDES = (
    "/src",
    "/tests",
    "/benchmarks/recommendation-corpus.json",
    "/benchmarks/corpus/*.json",
    "/benchmarks/longitudinal/*.json",
    "/tools/verify_release.py",
    "/docs",
    "/CHANGELOG.md",
    "/CODE_OF_CONDUCT.md",
    "/CONTRIBUTING.md",
    "/LICENSE",
    "/README.md",
    "/README.tr.md",
    "/RELEASING.md",
    "/SECURITY.md",
    "/pyproject.toml",
)
EXPECTED_RELEASE_DEPENDENCIES = (
    "build==1.3.0",
    "hatchling==1.31.0",
    "packaging==26.2",
)


@dataclass(frozen=True)
class ReleaseVerification:
    version: str
    wheel: str
    wheel_sha256: str
    wheel_size: int
    sdist: str
    sdist_sha256: str
    sdist_size: int
    wheel_files: int
    sdist_files: int
    wheel_generator: str


@dataclass(frozen=True)
class ProjectMetadataContract:
    description: str
    requires_python: str
    license_expression: str
    author: str
    keywords: tuple[str, ...]
    classifiers: tuple[str, ...]
    project_urls: dict[str, str]
    optional_dependencies: dict[str, tuple[str, ...]]


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
    if (
        not name
        or "\\" in name
        or any(ord(character) < 32 or ord(character) == 127 for character in name)
    ):
        raise ValueError(f"Unsafe {label} member path: {name}")
    canonical = name[:-1] if name.endswith("/") else name
    parts = canonical.split("/")
    if not canonical or any(
        not part
        or part in {".", ".."}
        or ":" in part
        or part.rstrip(" .") != part
        or WINDOWS_INVALID_CHARACTERS.intersection(part)
        or unicodedata.normalize("NFC", part).split(".", maxsplit=1)[0].casefold()
        in WINDOWS_RESERVED_STEMS
        for part in parts
    ):
        raise ValueError(f"Unsafe {label} member path: {name}")
    path = PurePosixPath(*parts)
    if path.is_absolute() or not path.parts:
        raise ValueError(f"Unsafe {label} member path: {name}")
    return path


def _bounded_archive(sizes: list[int], label: str) -> None:
    if len(sizes) > MAX_ARCHIVE_FILES:
        raise ValueError(f"{label} exceeds the {MAX_ARCHIVE_FILES}-member limit")
    if any(size < 0 or size > MAX_ARCHIVE_MEMBER_BYTES for size in sizes):
        raise ValueError(
            f"{label} contains a member above the {MAX_ARCHIVE_MEMBER_BYTES}-byte limit"
        )
    if sum(sizes) > MAX_ARCHIVE_UNCOMPRESSED_BYTES:
        raise ValueError(
            f"{label} exceeds the {MAX_ARCHIVE_UNCOMPRESSED_BYTES}-byte expanded limit"
        )


def _unique_members(paths: list[PurePosixPath], label: str) -> None:
    seen: dict[str, str] = {}
    for path in paths:
        rendered = path.as_posix()
        key = unicodedata.normalize("NFC", rendered).casefold()
        previous = seen.get(key)
        if previous is not None:
            raise ValueError(
                f"{label} contains duplicate or platform-colliding members: "
                f"{previous}, {rendered}"
            )
        seen[key] = rendered


def _wheel_component(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9.]+", "_", value)


def _canonical_source_version(value: bytes, label: str) -> str:
    try:
        tree = ast.parse(value.decode("utf-8"))
    except (SyntaxError, UnicodeDecodeError) as exc:
        raise ValueError(f"{label} has an unreadable canonical version source") from exc
    mutations = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
        and node.id == "__version__"
        and isinstance(node.ctx, (ast.Store, ast.Del))
    ]
    if len(mutations) != 1:
        raise ValueError(f"{label} must contain exactly one __version__ assignment")
    if any(
        isinstance(node, ast.Call)
        or (
            isinstance(node, (ast.Attribute, ast.Subscript))
            and isinstance(node.ctx, (ast.Store, ast.Del))
        )
        for node in ast.walk(tree)
    ):
        raise ValueError(f"{label} version source must remain declarative")

    versions: list[str] = []
    for statement in tree.body:
        candidate: ast.expr | None = None
        names: list[str] = []
        if isinstance(statement, ast.Assign):
            names = [target.id for target in statement.targets if isinstance(target, ast.Name)]
            candidate = statement.value
        elif isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
            names = [statement.target.id]
            candidate = statement.value
        else:
            continue
        if (
            "__version__" in names
            and isinstance(candidate, ast.Constant)
            and isinstance(candidate.value, str)
        ):
            versions.append(candidate.value)
    if len(versions) != 1:
        raise ValueError(f"{label} must contain exactly one static __version__ string")
    return versions[0]


def _string_tuple(value: object, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(f"Source pyproject has invalid {label}")
    return tuple(value)


def _validate_project_metadata(value: bytes) -> ProjectMetadataContract:
    try:
        document = tomllib.loads(value.decode("utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as exc:
        raise ValueError("Source distribution contains an invalid pyproject.toml") from exc

    build_system = document.get("build-system")
    metadata = document.get("project")
    tool = document.get("tool")
    if not isinstance(build_system, dict):
        raise ValueError("Source pyproject has an invalid build-system table")
    if (
        set(build_system) != {"requires", "build-backend"}
        or build_system.get("requires") != ["hatchling==1.31.0"]
        or build_system.get("build-backend") != "hatchling.build"
    ):
        raise ValueError("Source pyproject must retain the fixed Hatchling build backend")
    if not isinstance(tool, dict):
        raise ValueError("Source pyproject has an invalid tool table")
    hatch = tool.get("hatch")
    if not isinstance(hatch, dict):
        raise ValueError("Source pyproject has an invalid Hatch table")
    version = hatch.get("version")
    if not isinstance(version, dict):
        raise ValueError("Source pyproject has an invalid Hatch version table")
    if not isinstance(metadata, dict) or metadata.get("name") != EXPECTED_NAME:
        raise ValueError("Source pyproject has the wrong project name")
    if set(metadata) != EXPECTED_PROJECT_KEYS:
        raise ValueError("Source pyproject has unexpected project metadata fields")
    if set(hatch) != {"version", "build"} or version != {
        "path": "src/intentatlas/__init__.py"
    }:
        raise ValueError("Source pyproject must retain the fixed Hatch build configuration")
    expected_build = {
        "targets": {
            "wheel": {"packages": ["src/intentatlas"]},
            "sdist": {"include": list(EXPECTED_SDIST_INCLUDES)},
        }
    }
    if hatch.get("build") != expected_build:
        raise ValueError("Source pyproject must retain the fixed Hatch build configuration")
    if metadata.get("dynamic") != ["version"] or "version" in metadata:
        raise ValueError("Source pyproject must retain one dynamic version source")
    if metadata.get("dependencies") != []:
        raise ValueError("Source pyproject must not add unconditional runtime dependencies")
    description = metadata.get("description")
    requires_python = metadata.get("requires-python")
    license_expression = metadata.get("license")
    authors = metadata.get("authors")
    keywords = _string_tuple(metadata.get("keywords"), "keywords")
    classifiers = _string_tuple(metadata.get("classifiers"), "classifiers")
    scripts = metadata.get("scripts")
    urls = metadata.get("urls")
    if not isinstance(description, str) or not description:
        raise ValueError("Source pyproject has an invalid description")
    if not isinstance(requires_python, str) or not requires_python:
        raise ValueError("Source pyproject has an invalid Python requirement")
    if license_expression != "MIT":
        raise ValueError("Source pyproject must retain the MIT license expression")
    if authors != [{"name": "IntentAtlas contributors"}]:
        raise ValueError("Source pyproject has unexpected author attribution")
    if metadata.get("readme") != "README.md":
        raise ValueError("Source pyproject must retain README.md as project description")
    if scripts != {"intentatlas": "intentatlas.cli:main"}:
        raise ValueError("Source pyproject has an unexpected console entry point")
    if not isinstance(urls, dict) or any(
        not isinstance(key, str) or not isinstance(url, str) or not url
        for key, url in urls.items()
    ):
        raise ValueError("Source pyproject has invalid project URLs")
    optional = metadata.get("optional-dependencies")
    if not isinstance(optional, dict) or any(not isinstance(key, str) for key in optional):
        raise ValueError("Source pyproject has invalid optional dependencies")
    if _string_tuple(optional.get("release"), "release optional dependencies") != (
        EXPECTED_RELEASE_DEPENDENCIES
    ):
        raise ValueError("Source pyproject must retain the fixed release toolchain")
    return ProjectMetadataContract(
        description,
        requires_python,
        license_expression,
        "IntentAtlas contributors",
        keywords,
        classifiers,
        dict(urls),
        {
            key: _string_tuple(dependencies, f"{key} optional dependencies")
            for key, dependencies in optional.items()
        },
    )


def _record_digest(value: bytes) -> str:
    digest = hashlib.sha256(value).digest()
    return "sha256=" + base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def _validate_wheel_member_type(info: ZipInfo) -> None:
    if info.flag_bits & 0x1:
        raise ValueError(f"Wheel contains an encrypted member: {info.filename}")
    file_type = stat.S_IFMT(info.external_attr >> 16)
    if file_type not in {0, stat.S_IFREG, stat.S_IFDIR}:
        raise ValueError(f"Wheel contains a non-regular member: {info.filename}")
    if file_type == stat.S_IFDIR and not info.is_dir():
        raise ValueError(f"Wheel contains inconsistent member metadata: {info.filename}")


def _project_source_manifest(project_root: Path) -> dict[str, bytes]:
    sources: dict[str, bytes] = {}

    def include(candidate: Path) -> None:
        relative = candidate.relative_to(project_root)
        if "__pycache__" in relative.parts or candidate.suffix in {".pyc", ".pyo"}:
            return
        if candidate.is_symlink():
            raise ValueError(f"Reviewed source manifest contains a symlink: {relative}")
        if candidate.is_dir():
            return
        if not candidate.is_file():
            raise ValueError(f"Reviewed source manifest contains a non-file: {relative}")
        sources[relative.as_posix()] = candidate.read_bytes()

    for root_name in SDIST_TREE_ROOTS:
        root = project_root / root_name
        if root.is_symlink():
            raise ValueError(f"Reviewed source manifest contains a symlink: {root_name}")
        if root.is_dir():
            for candidate in sorted(root.rglob("*")):
                include(candidate)
    for relative_name in sorted(SDIST_ROOT_FILES | ALLOWED_SDIST_BENCHMARKS):
        candidate = project_root.joinpath(*PurePosixPath(relative_name).parts)
        if candidate.exists() or candidate.is_symlink():
            include(candidate)

    required = {
        "LICENSE",
        "README.md",
        "RELEASING.md",
        "pyproject.toml",
        "src/intentatlas/__init__.py",
        "src/intentatlas/web/index.html",
        "tools/verify_release.py",
    }
    missing = sorted(required - sources.keys())
    if missing:
        raise ValueError("Reviewed source manifest is incomplete: " + ", ".join(missing))
    return sources


def _compare_payloads(
    first: dict[str, bytes],
    second: dict[str, bytes],
    *,
    label: str,
) -> None:
    if first.keys() != second.keys():
        missing_from_second = sorted(first.keys() - second.keys())
        missing_from_first = sorted(second.keys() - first.keys())
        details = []
        if missing_from_second:
            details.append("missing from second: " + ", ".join(missing_from_second))
        if missing_from_first:
            details.append("missing from first: " + ", ".join(missing_from_first))
        raise ValueError(f"{label} file manifests differ (" + "; ".join(details) + ")")
    changed = sorted(name for name in first if first[name] != second[name])
    if changed:
        raise ValueError(f"{label} bytes differ: " + ", ".join(changed))


def _validated_package_metadata(
    value: bytes,
    label: str,
    contract: ProjectMetadataContract,
    readme_bytes: bytes,
    expected_version: str | None = None,
) -> str:
    try:
        metadata = Metadata.from_email(value, validate=True)
        readme = readme_bytes.decode("utf-8")
    except (ExceptionGroup, UnicodeDecodeError, ValueError) as exc:
        raise ValueError(f"{label} contains invalid core metadata") from exc
    version = str(metadata.version) if metadata.version is not None else None
    expected_singletons = {
        "metadata version": (metadata.metadata_version, "2.4"),
        "project name": (metadata.name, EXPECTED_NAME),
        "summary": (metadata.summary, contract.description),
        "Python requirement": (str(metadata.requires_python), contract.requires_python),
        "license expression": (metadata.license_expression, contract.license_expression),
        "author attribution": (metadata.author, contract.author),
        "description type": (metadata.description_content_type, "text/markdown"),
    }
    for field, (observed, expected) in expected_singletons.items():
        if observed != expected:
            raise ValueError(f"{label} has unexpected {field}")
    if expected_version is not None and version != expected_version:
        raise ValueError(f"{label} has an unexpected version")
    if metadata.keywords != list(contract.keywords):
        raise ValueError(f"{label} has unexpected project keywords")
    if metadata.classifiers != list(contract.classifiers):
        raise ValueError(f"{label} has unexpected project classifiers")
    if metadata.project_urls != contract.project_urls:
        raise ValueError(f"{label} has unexpected project URLs")
    if metadata.license_files != ["LICENSE"]:
        raise ValueError(f"{label} has unexpected license files")
    if metadata.description != readme:
        raise ValueError(f"{label} description does not match the reviewed README")
    if metadata.dynamic:
        raise ValueError(f"{label} must not retain unresolved dynamic metadata")
    extras = metadata.provides_extra or []
    if extras != sorted(contract.optional_dependencies):
        raise ValueError(f"{label} has unexpected optional dependency groups")
    try:
        observed_requirements = Counter(metadata.requires_dist or [])
        expected_requirements = Counter(
            Requirement(f"{requirement}; extra == '{extra}'")
            for extra, requirements in contract.optional_dependencies.items()
            for requirement in requirements
        )
    except InvalidRequirement as exc:
        raise ValueError(f"{label} contains an invalid dependency requirement") from exc
    if observed_requirements != expected_requirements:
        raise ValueError(f"{label} dependencies do not match the reviewed source pyproject")
    if version is None:
        raise ValueError(f"{label} has an unexpected version")
    return version


def _validate_wheel(
    path: Path,
    project_root: Path,
    contract: ProjectMetadataContract,
    readme_bytes: bytes,
    reviewed_package: dict[str, bytes],
) -> tuple[str, int, str, dict[str, bytes]]:
    with ZipFile(path) as archive:
        infos = archive.infolist()
        _bounded_archive([info.file_size for info in infos], "Wheel")
        for info in infos:
            _validate_wheel_member_type(info)
        if archive.testzip() is not None:
            raise ValueError(f"Wheel contains a corrupt member: {path}")
        names = archive.namelist()
        safe_names = [_safe_member(name, "wheel") for name in names]
        _unique_members(safe_names, "Wheel")
        dist_info = {
            member.parts[0]
            for member in safe_names
            if member.parts[0].endswith(".dist-info")
        }
        if len(dist_info) != 1:
            raise ValueError("Wheel must contain exactly one dist-info directory")
        dist_info_name = next(iter(dist_info))
        if any(member.parts[0] not in {EXPECTED_NAME, dist_info_name} for member in safe_names):
            raise ValueError("Wheel contains files outside the package and dist-info directories")

        required_dist_info = {
            f"{dist_info_name}/METADATA",
            f"{dist_info_name}/WHEEL",
            f"{dist_info_name}/entry_points.txt",
            f"{dist_info_name}/RECORD",
            f"{dist_info_name}/licenses/LICENSE",
        }
        expected_names = set(reviewed_package) | required_dist_info
        if set(names) != expected_names:
            missing = sorted(expected_names - set(names))
            unexpected = sorted(set(names) - expected_names)
            details = []
            if missing:
                details.append("missing: " + ", ".join(missing))
            if unexpected:
                details.append("unexpected: " + ", ".join(unexpected))
            raise ValueError(
                "Wheel does not match the reviewed package manifest ("
                + "; ".join(details)
                + ")"
            )

        version = _validated_package_metadata(
            archive.read(f"{dist_info_name}/METADATA"),
            "Wheel metadata",
            contract,
            readme_bytes,
        )
        expected_dist_info = f"{EXPECTED_NAME}-{_wheel_component(version)}.dist-info"
        expected_wheel = f"{EXPECTED_NAME}-{_wheel_component(version)}-py3-none-any.whl"
        if dist_info_name != expected_dist_info or path.name != expected_wheel:
            raise ValueError("Wheel filename, dist-info, and metadata version do not agree")

        wheel_metadata = BytesParser().parsebytes(archive.read(f"{dist_info_name}/WHEEL"))
        generators = wheel_metadata.get_all("Generator", [])
        if (
            set(wheel_metadata.keys())
            != {"Wheel-Version", "Generator", "Root-Is-Purelib", "Tag"}
            or wheel_metadata.get_all("Wheel-Version", []) != ["1.0"]
            or wheel_metadata.get_all("Root-Is-Purelib", []) != ["true"]
            or wheel_metadata.get_all("Tag", []) != ["py3-none-any"]
            or generators != ["hatchling 1.31.0"]
        ):
            raise ValueError("Wheel build metadata is missing the expected pure-Python tag")
        generator = generators[0]

        packaged_version = _canonical_source_version(
            archive.read("intentatlas/__init__.py"), "Wheel package"
        )
        if packaged_version != version:
            raise ValueError("Wheel package version does not match wheel metadata")

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
        package_files = {name: archive.read(name) for name in reviewed_package}
    return version, len(names), generator, package_files


def _validate_sdist(
    path: Path,
    version: str,
    project_root: Path,
    contract: ProjectMetadataContract,
    reviewed_sources: dict[str, bytes],
) -> tuple[int, dict[str, bytes]]:
    expected_root = f"{EXPECTED_NAME}-{version}"
    if path.name != f"{expected_root}.tar.gz":
        raise ValueError("Source-distribution filename and metadata version do not agree")
    archived_files: dict[str, bytes] = {}
    with tarfile.open(path, "r:gz") as archive:
        members = archive.getmembers()
        _bounded_archive([member.size for member in members], "Source distribution")
        safe_members = [_safe_member(member.name, "source distribution") for member in members]
        _unique_members(safe_members, "Source distribution")
        for member, member_path in zip(members, safe_members, strict=True):
            if member_path.parts[0] != expected_root:
                raise ValueError("Source distribution has an unexpected root directory")
            if member.issym() or member.islnk() or not (member.isfile() or member.isdir()):
                raise ValueError(f"Source distribution contains an unsafe member: {member.name}")
            relative = PurePosixPath(*member_path.parts[1:])
            relative_name = relative.as_posix()
            if (
                relative.parts
                and relative.parts[0].casefold() in FORBIDDEN_SDIST_ROOTS_CASEFOLDED
                and relative_name not in ALLOWED_SDIST_BENCHMARKS
            ):
                raise ValueError(f"Source distribution contains excluded project data: {relative}")
            if member.isfile():
                if not relative.parts:
                    raise ValueError("Source distribution root must be a directory")
                handle = archive.extractfile(member)
                if handle is None:
                    raise ValueError(
                        f"Source distribution member could not be read: {relative_name}"
                    )
                archived_files[relative_name] = handle.read()

    expected_names = set(reviewed_sources) | {"PKG-INFO"}
    if archived_files.keys() != expected_names:
        missing = sorted(expected_names - archived_files.keys())
        unexpected = sorted(archived_files.keys() - expected_names)
        details = []
        if missing:
            details.append("missing: " + ", ".join(missing))
        if unexpected:
            details.append("unexpected: " + ", ".join(unexpected))
        raise ValueError(
            "Source distribution does not match the reviewed manifest ("
            + "; ".join(details)
            + ")"
        )
    changed_sources = sorted(
        name for name, value in reviewed_sources.items() if archived_files[name] != value
    )
    if changed_sources:
        raise ValueError(
            "Source distribution differs from the reviewed source bytes: "
            + ", ".join(changed_sources)
        )
    if archived_files["LICENSE"] != (project_root / "LICENSE").read_bytes():
        raise ValueError("Source-distribution license does not match the repository license")
    _validated_package_metadata(
        archived_files["PKG-INFO"],
        "Source metadata",
        contract,
        reviewed_sources["README.md"],
        version,
    )
    if archived_files["pyproject.toml"] != (project_root / "pyproject.toml").read_bytes():
        raise ValueError("Source pyproject does not match the reviewed checkout")
    _validate_project_metadata(archived_files["pyproject.toml"])
    source_version = _canonical_source_version(
        archived_files["src/intentatlas/__init__.py"], "Source package"
    )
    if source_version != version:
        raise ValueError("Source package version does not match wheel metadata")
    package_files = {
        name.removeprefix("src/"): value
        for name, value in archived_files.items()
        if name.startswith("src/intentatlas/")
    }
    missing_package = sorted(REQUIRED_PACKAGE_FILES - set(package_files))
    if missing_package:
        raise ValueError(
            "Source distribution is missing runtime package files: "
            + ", ".join(missing_package)
        )
    return len(archived_files), package_files


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

    reviewed_sources = _project_source_manifest(project_root)
    contract = _validate_project_metadata(reviewed_sources["pyproject.toml"])
    reviewed_package = {
        name.removeprefix("src/"): value
        for name, value in reviewed_sources.items()
        if name.startswith("src/intentatlas/")
    }
    version, wheel_files, wheel_generator, wheel_package = _validate_wheel(
        first_wheel,
        project_root,
        contract,
        reviewed_sources["README.md"],
        reviewed_package,
    )
    sdist_files, sdist_package = _validate_sdist(
        first_sdist,
        version,
        project_root,
        contract,
        reviewed_sources,
    )
    _compare_payloads(
        wheel_package,
        sdist_package,
        label="Wheel and source package",
    )
    _compare_payloads(
        reviewed_package,
        wheel_package,
        label="Reviewed checkout and artifact package",
    )
    return ReleaseVerification(
        version=version,
        wheel=first_wheel.name,
        wheel_sha256=first_wheel_hash,
        wheel_size=first_wheel.stat().st_size,
        sdist=first_sdist.name,
        sdist_sha256=first_sdist_hash,
        sdist_size=first_sdist.stat().st_size,
        wheel_files=wheel_files,
        sdist_files=sdist_files,
        wheel_generator=wheel_generator,
    )


def release_provenance(
    result: ReleaseVerification,
    *,
    source_revision: str,
    source_date_epoch: int,
) -> dict[str, object]:
    if FULL_GIT_SHA.fullmatch(source_revision) is None:
        raise ValueError("Release provenance requires a lowercase 40-character Git revision")
    if (
        isinstance(source_date_epoch, bool)
        or not isinstance(source_date_epoch, int)
        or source_date_epoch < 0
    ):
        raise ValueError("Release provenance requires a non-negative SOURCE_DATE_EPOCH")
    artifacts = [
        {
            "name": result.wheel,
            "type": "wheel",
            "size": result.wheel_size,
            "sha256": result.wheel_sha256,
        },
        {
            "name": result.sdist,
            "type": "sdist",
            "size": result.sdist_size,
            "sha256": result.sdist_sha256,
        },
    ]
    artifacts.sort(key=lambda item: str(item["name"]))
    return {
        "schema_version": PROVENANCE_SCHEMA_VERSION,
        "format": "intentatlas-release-provenance",
        "project": EXPECTED_NAME,
        "version": result.version,
        "source": {
            "revision": source_revision,
            "source_date_epoch": source_date_epoch,
        },
        "artifacts": artifacts,
        "verification": {
            "repeated_builds_byte_identical": True,
            "checks": [
                "archive-member-safety",
                "artifact-sha256",
                "bundled-web-assets",
                "console-entry-point",
                "dependency-metadata",
                "mit-license-bytes",
                "package-boundaries",
                "package-payload-parity",
                "python-metadata",
                "reviewed-source-manifest",
                "reviewed-wheel-manifest",
                "source-metadata",
                "wheel-record",
            ],
            "wheel_files": result.wheel_files,
            "sdist_files": result.sdist_files,
            "wheel_generator": result.wheel_generator,
        },
    }


def write_release_provenance(
    path: Path,
    result: ReleaseVerification,
    *,
    source_revision: str,
    source_date_epoch: int,
) -> None:
    document = release_provenance(
        result,
        source_revision=source_revision,
        source_date_epoch=source_date_epoch,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(document, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def verify_approved_hashes(
    result: ReleaseVerification,
    *,
    expected_wheel_sha256: str,
    expected_sdist_sha256: str,
) -> None:
    for label, value in (
        ("wheel", expected_wheel_sha256),
        ("source distribution", expected_sdist_sha256),
    ):
        if re.fullmatch(r"[0-9a-f]{64}", value) is None:
            raise ValueError(f"Approved {label} SHA-256 must be 64 lowercase hex characters")
    if result.wheel_sha256 != expected_wheel_sha256:
        raise ValueError("Verified wheel does not match the approved SHA-256")
    if result.sdist_sha256 != expected_sdist_sha256:
        raise ValueError("Verified source distribution does not match the approved SHA-256")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify IntentAtlas release contents and repeated-build reproducibility."
    )
    parser.add_argument("first", type=Path, help="First build output directory")
    parser.add_argument("second", type=Path, help="Second build output directory")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--write-provenance", type=Path)
    parser.add_argument("--source-revision")
    parser.add_argument("--source-date-epoch", type=int)
    parser.add_argument("--expected-wheel-sha256")
    parser.add_argument("--expected-sdist-sha256")
    args = parser.parse_args()
    try:
        result = verify_release(args.first, args.second, args.project_root.resolve())
        expected_hashes = (args.expected_wheel_sha256, args.expected_sdist_sha256)
        if any(value is not None for value in expected_hashes):
            if any(value is None for value in expected_hashes):
                raise ValueError("Both approved artifact SHA-256 values are required")
            verify_approved_hashes(
                result,
                expected_wheel_sha256=args.expected_wheel_sha256,
                expected_sdist_sha256=args.expected_sdist_sha256,
            )
        if args.write_provenance is not None:
            if args.source_revision is None or args.source_date_epoch is None:
                raise ValueError(
                    "Writing provenance requires --source-revision and --source-date-epoch"
                )
            write_release_provenance(
                args.write_provenance,
                result,
                source_revision=args.source_revision,
                source_date_epoch=args.source_date_epoch,
            )
    except (BadZipFile, OSError, ValueError, tarfile.TarError) as exc:
        parser.exit(1, f"release verification failed: {exc}\n")
    print(f"Verified reproducible wheel: {result.wheel} sha256={result.wheel_sha256}")
    print(f"Verified reproducible sdist: {result.sdist} sha256={result.sdist_sha256}")
    print(f"Validated archive files: wheel={result.wheel_files}, sdist={result.sdist_files}")
    if args.write_provenance is not None:
        print(f"Wrote deterministic release provenance: {args.write_provenance}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
