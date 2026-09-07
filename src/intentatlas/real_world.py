from __future__ import annotations

import hashlib
import json
import re
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from .bounded_process import ProcessCollectionError, run_bounded_process
from .config import ProjectConfig
from .corpus import CorpusEvaluationResult, CorpusProject, evaluate_corpus, render_corpus
from .evaluation import load_evaluation_labels
from .scanner import scan_repository

REAL_WORLD_SCHEMA_VERSION = 1
GENERATED_OUTPUT_POLICY = "ephemeral-only"
MAX_MANIFEST_BYTES = 256_000
MAX_PROJECTS = 10
MAX_LICENSE_BYTES = 128_000
MAX_GIT_OUTPUT_BYTES = 1_000_000
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")
SAFE_COMMIT = re.compile(r"^[0-9a-f]{40}$")
SAFE_SHA256 = re.compile(r"^[0-9a-f]{64}$")
SAFE_SPDX = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.+-]{0,99}$")
GITHUB_REPOSITORY = re.compile(
    r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$"
)
WINDOWS_ABSOLUTE = re.compile(r"^[A-Za-z]:[/\\]")
ADVISORY = (
    "Real-world metrics apply only to the pinned commits and reviewed complete-test-set labels; "
    "they do not prove accuracy on other changes or repositories."
)


@dataclass(frozen=True, slots=True)
class ReviewedLicense:
    spdx: str
    path: str
    sha256: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RealWorldManifestProject:
    id: str
    name: str
    language: str
    repository: str
    commit: str
    license: ReviewedLicense
    labels: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "language": self.language,
            "repository": self.repository,
            "commit": self.commit,
            "license": self.license.to_dict(),
            "labels": self.labels,
        }


@dataclass(frozen=True, slots=True)
class RealWorldManifest:
    name: str
    projects: tuple[RealWorldManifestProject, ...]
    generated_output_policy: str = GENERATED_OUTPUT_POLICY


@dataclass(frozen=True, slots=True)
class RealWorldEvaluationResult:
    name: str
    projects: tuple[RealWorldManifestProject, ...]
    evaluation: CorpusEvaluationResult

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": REAL_WORLD_SCHEMA_VERSION,
            "advisory": ADVISORY,
            "generated_output_policy": GENERATED_OUTPUT_POLICY,
            "name": self.name,
            "projects": [project.to_dict() for project in self.projects],
            "evaluation": self.evaluation.to_dict(),
        }


def load_real_world_manifest(path: Path) -> RealWorldManifest:
    if path.is_symlink():
        raise ValueError(f"Real-world manifest may not be a symbolic link: {path.name}")
    if not path.is_file():
        raise ValueError(f"Real-world manifest does not exist: {path.name}")
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise ValueError(f"Cannot inspect real-world manifest {path.name}: {exc}") from exc
    if size > MAX_MANIFEST_BYTES:
        raise ValueError(
            f"Real-world manifest exceeds the {MAX_MANIFEST_BYTES}-byte limit: {path.name}"
        )
    try:
        document = json.loads(
            path.read_bytes().decode("utf-8"),
            object_pairs_hook=_unique_object,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError(f"Cannot parse real-world manifest {path.name}: {exc}") from exc
    if not isinstance(document, dict):
        raise ValueError("Real-world manifest must be a JSON object")
    _only_keys(
        document,
        {"schema_version", "name", "generated_output_policy", "projects"},
        "manifest",
    )
    schema_version = document.get("schema_version")
    if type(schema_version) is not int or schema_version != REAL_WORLD_SCHEMA_VERSION:
        raise ValueError("Unsupported real-world manifest schema")
    if document.get("generated_output_policy") != GENERATED_OUTPUT_POLICY:
        raise ValueError(
            f"Real-world generated_output_policy must be {GENERATED_OUTPUT_POLICY!r}"
        )
    name = _text(document.get("name"), "benchmark name", 200)
    records = document.get("projects")
    if not isinstance(records, list) or not records:
        raise ValueError("Real-world projects must be a non-empty list")
    if len(records) > MAX_PROJECTS:
        raise ValueError(f"Real-world manifest exceeds the {MAX_PROJECTS}-project limit")

    projects: list[RealWorldManifestProject] = []
    ids: set[str] = set()
    repositories: set[str] = set()
    label_paths: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Each real-world project must be an object")
        _only_keys(
            record,
            {"id", "name", "language", "repository", "commit", "license", "labels"},
            "project",
        )
        project_id = _text(record.get("id"), "project ID", 100)
        if SAFE_ID.fullmatch(project_id) is None:
            raise ValueError(f"Invalid real-world project ID: {project_id!r}")
        repository = _text(record.get("repository"), f"repository for {project_id}", 300)
        if GITHUB_REPOSITORY.fullmatch(repository) is None:
            raise ValueError(f"Invalid GitHub repository URL for {project_id}")
        commit = _text(record.get("commit"), f"commit for {project_id}", 40)
        if SAFE_COMMIT.fullmatch(commit) is None:
            raise ValueError(f"Invalid pinned commit for {project_id}")
        license_record = record.get("license")
        if not isinstance(license_record, dict):
            raise ValueError(f"License review for {project_id} must be an object")
        _only_keys(license_record, {"spdx", "path", "sha256"}, "license")
        spdx = _text(license_record.get("spdx"), f"SPDX license for {project_id}", 100)
        if SAFE_SPDX.fullmatch(spdx) is None:
            raise ValueError(f"Invalid SPDX license for {project_id}")
        license_path = _relative_path(
            license_record.get("path"), project_id, "license"
        )
        license_sha = _text(
            license_record.get("sha256"), f"license SHA-256 for {project_id}", 64
        )
        if SAFE_SHA256.fullmatch(license_sha) is None:
            raise ValueError(f"Invalid license SHA-256 for {project_id}")
        labels = _relative_path(record.get("labels"), project_id, "labels")
        if project_id in ids:
            raise ValueError(f"Duplicate real-world project ID: {project_id}")
        if repository in repositories:
            raise ValueError(f"Duplicate real-world repository: {repository}")
        if labels in label_paths:
            raise ValueError(f"Duplicate real-world label path: {labels}")
        ids.add(project_id)
        repositories.add(repository)
        label_paths.add(labels)
        projects.append(
            RealWorldManifestProject(
                id=project_id,
                name=_text(record.get("name"), f"name for {project_id}", 200),
                language=_text(record.get("language"), f"language for {project_id}", 100),
                repository=repository,
                commit=commit,
                license=ReviewedLicense(spdx, license_path, license_sha),
                labels=labels,
            )
        )
    return RealWorldManifest(name, tuple(sorted(projects, key=lambda item: item.id)))


def evaluate_real_world(
    project_root: Path,
    checkouts_root: Path,
    manifest: RealWorldManifest,
    *,
    limit: int = 20,
) -> RealWorldEvaluationResult:
    project_root = project_root.resolve()
    checkouts_root = checkouts_root.resolve()
    if not checkouts_root.is_dir():
        raise ValueError(f"Real-world checkout root does not exist: {checkouts_root.name}")

    projects: list[CorpusProject] = []
    for entry in manifest.projects:
        checkout = _checkout_path(checkouts_root, entry.id)
        _validate_checkout(checkout, entry)
        labels_path = _inside_project(project_root, entry.labels, f"labels for {entry.id}")
        labels = load_evaluation_labels(labels_path)
        expected_target = f"commit:{entry.commit}"
        if not any(case.target == expected_target for case in labels.cases):
            raise ValueError(
                f"Real-world labels for {entry.id} must include {expected_target}"
            )
        graph = scan_repository(checkout, ProjectConfig(git_history_limit=25))
        projects.append(CorpusProject(entry.id, entry.name, graph, labels))

    evaluation = evaluate_corpus(manifest.name, tuple(projects), limit=limit)
    return RealWorldEvaluationResult(manifest.name, manifest.projects, evaluation)


def render_real_world(result: RealWorldEvaluationResult, output_format: str = "text") -> str:
    if output_format == "json":
        return json.dumps(result.to_dict(), indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if output_format != "text":
        raise ValueError(f"Unknown real-world output format: {output_format}")
    lines = [
        f"Real-world recommendation benchmark: {result.name}",
        f"Generated output policy: {GENERATED_OUTPUT_POLICY}",
    ]
    for project in result.projects:
        lines.append(
            f"  {project.id}: {project.repository} @ {project.commit[:12]} "
            f"({project.language}, {project.license.spdx})"
        )
    lines.append(f"Advisory: {ADVISORY}")
    lines.append("")
    lines.append(render_corpus(result.evaluation).rstrip())
    return "\n".join(lines) + "\n"


def _validate_checkout(checkout: Path, project: RealWorldManifestProject) -> None:
    if checkout.is_symlink() or not checkout.is_dir():
        raise ValueError(f"Real-world checkout does not exist for {project.id}")
    git = shutil.which("git")
    if git is None:
        raise ValueError("Git is required to validate real-world checkouts")
    head = _git_value(git, checkout, "rev-parse", "HEAD")
    if head != project.commit:
        raise ValueError(
            f"Real-world checkout {project.id} is at {head or 'an unknown commit'}, "
            f"expected {project.commit}"
        )
    origin = _git_value(git, checkout, "remote", "get-url", "origin").removesuffix(".git")
    if origin != project.repository:
        raise ValueError(f"Real-world checkout {project.id} has an unexpected origin")

    unresolved_license = checkout.joinpath(*PurePosixPath(project.license.path).parts)
    if unresolved_license.is_symlink():
        raise ValueError(f"Reviewed license file is missing for {project.id}")
    try:
        license_path = unresolved_license.resolve(strict=True)
    except OSError as exc:
        raise ValueError(f"Reviewed license file is missing for {project.id}") from exc
    if (
        license_path == checkout
        or checkout not in license_path.parents
        or not license_path.is_file()
    ):
        raise ValueError(f"Reviewed license file is missing for {project.id}")
    try:
        size = license_path.stat().st_size
        if size > MAX_LICENSE_BYTES:
            raise ValueError(
                f"Reviewed license for {project.id} exceeds the {MAX_LICENSE_BYTES}-byte limit"
            )
        digest = hashlib.sha256(license_path.read_bytes()).hexdigest()
    except OSError as exc:
        raise ValueError(f"Cannot inspect reviewed license for {project.id}: {exc}") from exc
    if digest != project.license.sha256:
        raise ValueError(f"Reviewed license hash does not match for {project.id}")
    status = _git_value(git, checkout, "status", "--porcelain", "--untracked-files=all")
    if status:
        raise ValueError(f"Real-world checkout {project.id} must be clean")


def _git_value(git: str, checkout: Path, *arguments: str) -> str:
    command = [
        git,
        "-c",
        f"safe.directory={checkout.as_posix()}",
        "-C",
        str(checkout),
        *arguments,
    ]
    try:
        result = run_bounded_process(
            command,
            max_stdout_bytes=MAX_GIT_OUTPUT_BYTES,
            timeout=10,
        )
    except ProcessCollectionError as exc:
        raise ValueError(f"Cannot inspect real-world checkout {checkout.name}: {exc}") from exc
    if result.returncode != 0:
        raise ValueError(f"Cannot inspect real-world checkout {checkout.name}")
    return result.stdout.decode("utf-8", errors="replace").strip()


def _checkout_path(root: Path, project_id: str) -> Path:
    unresolved = root / project_id
    if unresolved.is_symlink():
        raise ValueError(f"Real-world checkout may not be a symbolic link: {project_id}")
    checkout = unresolved.resolve()
    if checkout == root or root not in checkout.parents:
        raise ValueError(f"Real-world checkout escapes its root: {project_id}")
    return checkout


def _inside_project(root: Path, configured: str, label: str) -> Path:
    unresolved = root.joinpath(*PurePosixPath(configured).parts)
    if unresolved.is_symlink():
        raise ValueError(f"Real-world {label} may not be a symbolic link")
    target = unresolved.resolve()
    if target == root or root not in target.parents:
        raise ValueError(f"Real-world {label} must be below the project root")
    private = (root / "atlas" / "Private").resolve()
    if target == private or private in target.parents:
        raise ValueError(f"Real-world {label} may not be inside atlas/Private")
    if not target.is_file():
        raise ValueError(f"Real-world {label} does not exist")
    return target


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"Duplicate JSON key: {key}")
        value[key] = item
    return value


def _only_keys(value: dict[str, Any], allowed: set[str], label: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise ValueError(f"Unknown real-world {label} field: {unknown[0]}")


def _text(value: Any, label: str, limit: int) -> str:
    if not isinstance(value, str):
        raise ValueError(f"Real-world {label} must be a string")
    text = value.strip()
    if not text or len(text) > limit or any(ord(character) < 32 for character in text):
        raise ValueError(f"Invalid real-world {label}")
    return text


def _relative_path(value: Any, project_id: str, label: str) -> str:
    text = _text(value, f"{label} path for {project_id}", 500)
    pure = PurePosixPath(text)
    if (
        "\\" in text
        or pure.is_absolute()
        or WINDOWS_ABSOLUTE.match(text)
        or ".." in pure.parts
        or pure.as_posix() in {"", "."}
        or pure.as_posix() != text
    ):
        raise ValueError(f"Unsafe real-world {label} path for {project_id}: {text!r}")
    return pure.as_posix()
