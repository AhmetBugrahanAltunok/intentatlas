from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
import subprocess  # nosec B404
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

from .change_analysis import _analyze_change_set_with_graph
from .change_report import build_change_report
from .change_set import collect_change_set
from .config import ProjectConfig
from .graph import AtlasGraph
from .recommendations import MAX_RECOMMENDATIONS, recommend_tests
from .scanner import scan_repository

PILOT_SCHEMA_VERSION = 1
PILOT_LABEL_SCHEMA_VERSION = 1
PILOT_CLASSIFICATION_SCHEMA_VERSION = 1
GENERATED_OUTPUT_POLICY = "ephemeral-only"
LABEL_POLICY = "complete-test-set"
THRESHOLDS = ("low", "medium", "high")
PARTITIONS = ("calibration", "evaluation")
LANGUAGES = ("python", "javascript-typescript", "go")
WORKSPACE_SHAPES = ("single-package", "workspace")
CLASSIFICATION_CATEGORIES = (
    "label-defect",
    "unsupported-construct",
    "stale-evidence",
    "resolver-ambiguity",
    "recommendation-policy-gap",
)
MAX_MANIFEST_BYTES = 512_000
MAX_LABEL_BYTES = 1_000_000
MAX_CLASSIFICATION_BYTES = 2_000_000
MAX_PROJECTS = 50
MAX_CASES = 2_000
MAX_LICENSE_BYTES = 128_000
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")
SAFE_COMMIT = re.compile(r"^[0-9a-f]{40}$")
SAFE_SHA256 = re.compile(r"^[0-9a-f]{64}$")
SAFE_SPDX = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.+-]{0,99}$")
GITHUB_REPOSITORY = re.compile(
    r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$"
)
WINDOWS_ABSOLUTE = re.compile(r"^[A-Za-z]:[/\\]")
ADVISORY = (
    "Longitudinal metrics describe only frozen, independently reviewed cases; they are not a "
    "general accuracy claim or a guarantee that a targeted subset is sufficient."
)


@dataclass(frozen=True, slots=True)
class ReviewedLicense:
    spdx: str
    path: str
    sha256: str
    reviewed_at: str


@dataclass(frozen=True, slots=True)
class PilotProject:
    id: str
    name: str
    language: str
    workspace_shape: str
    repository: str
    revision: str
    history_limit: int
    excluded_paths: tuple[str, ...]
    license: ReviewedLicense
    labels: str
    classifications: str


@dataclass(frozen=True, slots=True)
class PilotManifest:
    name: str
    partition_hashes: dict[str, str]
    projects: tuple[PilotProject, ...]
    thresholds: tuple[str, ...] = THRESHOLDS


@dataclass(frozen=True, slots=True)
class PilotCase:
    id: str
    sequence: int
    revision: str
    committed_at: str
    partition: str
    expected_tests: tuple[str, ...]

    def partition_record(self, project_id: str) -> dict[str, Any]:
        return {
            "committed_at": self.committed_at,
            "expected_tests": list(self.expected_tests),
            "id": self.id,
            "partition": self.partition,
            "project_id": project_id,
            "revision": self.revision,
            "sequence": self.sequence,
        }


@dataclass(frozen=True, slots=True)
class PilotLabels:
    project_id: str
    cases: tuple[PilotCase, ...]


@dataclass(frozen=True, slots=True)
class ClassifiedErrorSet:
    category: str
    paths_sha256: str


@dataclass(frozen=True, slots=True)
class ClassificationObservation:
    case_id: str
    minimum_confidence: str
    false_positives: ClassifiedErrorSet | None
    false_negatives: ClassifiedErrorSet | None


@dataclass(frozen=True, slots=True)
class PilotClassifications:
    project_id: str
    observations: tuple[ClassificationObservation, ...]


@dataclass(frozen=True, slots=True)
class Estimate:
    value: float | None
    lower: float | None
    upper: float | None
    denominator: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PilotCaseResult:
    project_id: str
    language: str
    workspace_shape: str
    case_id: str
    sequence: int
    revision: str
    committed_at: str
    partition: str
    minimum_confidence: str
    expected_tests: tuple[str, ...]
    recommended_tests: tuple[str, ...]
    true_positives: tuple[str, ...]
    false_positives: tuple[str, ...]
    false_negatives: tuple[str, ...]
    false_positive_classifications: dict[str, str]
    false_negative_classifications: dict[str, str]
    precision: float | None
    recall: float | None
    recommendation_covered: bool
    abstained: bool
    analysis_state: str
    freshness: str
    execution_strategy: str
    unclassified_error_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PilotCohortResult:
    cohort: str
    partition: str
    minimum_confidence: str
    project_count: int
    case_count: int
    expected_count: int
    recommendation_count: int
    true_positive_count: int
    false_positive_count: int
    false_negative_count: int
    precision: Estimate
    recall: Estimate
    recommendation_coverage: Estimate
    abstention: Estimate
    analysis_states: dict[str, int]
    freshness_states: dict[str, int]
    execution_strategies: dict[str, int]
    unclassified_error_count: int

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["precision"] = self.precision.to_dict()
        value["recall"] = self.recall.to_dict()
        value["recommendation_coverage"] = self.recommendation_coverage.to_dict()
        value["abstention"] = self.abstention.to_dict()
        return value


@dataclass(frozen=True, slots=True)
class LongitudinalResult:
    name: str
    manifest_sha256: str
    partition_hashes: dict[str, str]
    projects: tuple[PilotProject, ...]
    cases: tuple[PilotCaseResult, ...]
    cohorts: tuple[PilotCohortResult, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": PILOT_SCHEMA_VERSION,
            "advisory": ADVISORY,
            "duration_evidence": None,
            "generated_output_policy": GENERATED_OUTPUT_POLICY,
            "manifest_sha256": self.manifest_sha256,
            "name": self.name,
            "partition_hashes": dict(sorted(self.partition_hashes.items())),
            "projects": [_project_dict(project) for project in self.projects],
            "cases": [case.to_dict() for case in self.cases],
            "cohorts": [cohort.to_dict() for cohort in self.cohorts],
        }


def load_pilot_manifest(path: Path) -> PilotManifest:
    document = _load_json(path, MAX_MANIFEST_BYTES, "pilot manifest")
    _only_keys(
        document,
        {
            "schema_version",
            "name",
            "generated_output_policy",
            "thresholds",
            "partitions",
            "projects",
        },
        "manifest",
    )
    if document.get("schema_version") != PILOT_SCHEMA_VERSION or type(
        document.get("schema_version")
    ) is not int:
        raise ValueError("Unsupported longitudinal pilot manifest schema")
    if document.get("generated_output_policy") != GENERATED_OUTPUT_POLICY:
        raise ValueError(
            f"Pilot generated_output_policy must be {GENERATED_OUTPUT_POLICY!r}"
        )
    thresholds = document.get("thresholds")
    if thresholds != list(THRESHOLDS):
        raise ValueError(f"Pilot thresholds must be exactly {list(THRESHOLDS)!r}")
    raw_partitions = document.get("partitions")
    if not isinstance(raw_partitions, dict):
        raise ValueError("Pilot partitions must be an object")
    _only_keys(raw_partitions, set(PARTITIONS), "partitions")
    partition_hashes: dict[str, str] = {}
    for partition in PARTITIONS:
        record = raw_partitions.get(partition)
        if not isinstance(record, dict):
            raise ValueError(f"Pilot partition {partition} must be an object")
        _only_keys(record, {"sha256"}, "partition")
        digest = _text(record.get("sha256"), f"{partition} partition SHA-256", 64)
        if SAFE_SHA256.fullmatch(digest) is None:
            raise ValueError(f"Invalid {partition} partition SHA-256")
        partition_hashes[partition] = digest

    records = document.get("projects")
    if not isinstance(records, list) or not records:
        raise ValueError("Pilot projects must be a non-empty list")
    if len(records) > MAX_PROJECTS:
        raise ValueError(f"Pilot manifest exceeds the {MAX_PROJECTS}-project limit")
    projects: list[PilotProject] = []
    ids: set[str] = set()
    repositories: set[str] = set()
    paths: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Each pilot project must be an object")
        _only_keys(
            record,
            {
                "id",
                "name",
                "language",
                "workspace_shape",
                "repository",
                "revision",
                "history_limit",
                "excluded_paths",
                "license",
                "labels",
                "classifications",
            },
            "project",
        )
        project_id = _identifier(record.get("id"), "project ID")
        repository = _text(record.get("repository"), f"repository for {project_id}", 300)
        if GITHUB_REPOSITORY.fullmatch(repository) is None:
            raise ValueError(f"Invalid GitHub repository URL for {project_id}")
        revision = _commit(record.get("revision"), f"revision for {project_id}")
        language = _text(record.get("language"), f"language for {project_id}", 40)
        if language not in LANGUAGES:
            raise ValueError(f"Unsupported pilot language for {project_id}: {language}")
        workspace_shape = _text(
            record.get("workspace_shape"), f"workspace shape for {project_id}", 40
        )
        if workspace_shape not in WORKSPACE_SHAPES:
            raise ValueError(f"Unsupported workspace shape for {project_id}")
        history_limit = record.get("history_limit")
        if (
            type(history_limit) is not int
            or history_limit < 1
            or history_limit > 250
        ):
            raise ValueError(f"Pilot history_limit for {project_id} must be 1..250")
        raw_excluded = record.get("excluded_paths")
        if not isinstance(raw_excluded, list) or len(raw_excluded) > 32:
            raise ValueError(f"Pilot excluded_paths for {project_id} must be a bounded list")
        excluded_paths = tuple(
            _relative_path(value, project_id, "excluded") for value in raw_excluded
        )
        if len(excluded_paths) != len(set(excluded_paths)):
            raise ValueError(f"Duplicate excluded path for {project_id}")
        license_record = record.get("license")
        if not isinstance(license_record, dict):
            raise ValueError(f"License review for {project_id} must be an object")
        _only_keys(
            license_record, {"spdx", "path", "sha256", "reviewed_at"}, "license"
        )
        spdx = _text(license_record.get("spdx"), f"SPDX for {project_id}", 100)
        if SAFE_SPDX.fullmatch(spdx) is None:
            raise ValueError(f"Invalid SPDX license for {project_id}")
        license_path = _relative_path(license_record.get("path"), project_id, "license")
        license_sha = _text(
            license_record.get("sha256"), f"license SHA-256 for {project_id}", 64
        )
        if SAFE_SHA256.fullmatch(license_sha) is None:
            raise ValueError(f"Invalid license SHA-256 for {project_id}")
        reviewed_at = _date(license_record.get("reviewed_at"), project_id)
        labels = _relative_path(record.get("labels"), project_id, "labels")
        classifications = _relative_path(
            record.get("classifications"), project_id, "classifications"
        )
        if labels == classifications:
            raise ValueError(f"Pilot labels and classifications must differ for {project_id}")
        if project_id in ids:
            raise ValueError(f"Duplicate pilot project ID: {project_id}")
        if repository in repositories:
            raise ValueError(f"Duplicate pilot repository: {repository}")
        if labels in paths or classifications in paths:
            raise ValueError(f"Duplicate pilot metadata path for {project_id}")
        ids.add(project_id)
        repositories.add(repository)
        paths.update((labels, classifications))
        projects.append(
            PilotProject(
                project_id,
                _text(record.get("name"), f"name for {project_id}", 200),
                language,
                workspace_shape,
                repository,
                revision,
                history_limit,
                excluded_paths,
                ReviewedLicense(spdx, license_path, license_sha, reviewed_at),
                labels,
                classifications,
            )
        )
    return PilotManifest(
        _text(document.get("name"), "pilot name", 200),
        partition_hashes,
        tuple(sorted(projects, key=lambda project: project.id)),
    )


def load_pilot_labels(path: Path, project_id: str) -> PilotLabels:
    document = _load_json(path, MAX_LABEL_BYTES, "pilot labels")
    _only_keys(
        document, {"schema_version", "project_id", "label_policy", "cases"}, "labels"
    )
    if document.get("schema_version") != PILOT_LABEL_SCHEMA_VERSION or type(
        document.get("schema_version")
    ) is not int:
        raise ValueError("Unsupported longitudinal pilot label schema")
    if document.get("project_id") != project_id:
        raise ValueError(f"Pilot labels do not belong to {project_id}")
    if document.get("label_policy") != LABEL_POLICY:
        raise ValueError(f"Pilot label_policy must be {LABEL_POLICY!r}")
    records = document.get("cases")
    if not isinstance(records, list) or not records:
        raise ValueError(f"Pilot labels for {project_id} need a non-empty case list")
    if len(records) > MAX_CASES:
        raise ValueError(f"Pilot labels exceed the {MAX_CASES}-case limit")
    cases: list[PilotCase] = []
    ids: set[str] = set()
    revisions: set[str] = set()
    previous_time: datetime | None = None
    for expected_sequence, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            raise ValueError("Each pilot case must be an object")
        _only_keys(
            record,
            {
                "id",
                "sequence",
                "revision",
                "committed_at",
                "partition",
                "expected_tests",
            },
            "case",
        )
        case_id = _identifier(record.get("id"), "case ID")
        sequence = record.get("sequence")
        if type(sequence) is not int or sequence != expected_sequence:
            raise ValueError(f"Pilot case sequence must be contiguous in {project_id}")
        revision = _commit(record.get("revision"), f"revision for case {case_id}")
        committed_at, timestamp = _timestamp(record.get("committed_at"), case_id)
        if previous_time is not None and timestamp < previous_time:
            raise ValueError(f"Pilot cases must be chronological in {project_id}")
        previous_time = timestamp
        partition = _text(record.get("partition"), f"partition for {case_id}", 20)
        if partition not in PARTITIONS:
            raise ValueError(f"Invalid partition for case {case_id}")
        raw_tests = record.get("expected_tests")
        if not isinstance(raw_tests, list):
            raise ValueError(f"Expected tests must be a list in case {case_id}")
        expected_tests = tuple(sorted(_test_path(value, case_id) for value in raw_tests))
        if len(expected_tests) != len(set(expected_tests)):
            raise ValueError(f"Duplicate expected test in case {case_id}")
        if case_id in ids:
            raise ValueError(f"Duplicate pilot case ID: {case_id}")
        if revision in revisions:
            raise ValueError(f"Duplicate pilot case revision: {revision}")
        ids.add(case_id)
        revisions.add(revision)
        cases.append(
            PilotCase(
                case_id,
                sequence,
                revision,
                committed_at,
                partition,
                expected_tests,
            )
        )
    return PilotLabels(project_id, tuple(cases))


def load_pilot_classifications(path: Path, project_id: str) -> PilotClassifications:
    document = _load_json(path, MAX_CLASSIFICATION_BYTES, "pilot classifications")
    _only_keys(document, {"schema_version", "project_id", "observations"}, "classifications")
    if document.get("schema_version") != PILOT_CLASSIFICATION_SCHEMA_VERSION or type(
        document.get("schema_version")
    ) is not int:
        raise ValueError("Unsupported pilot classification schema")
    if document.get("project_id") != project_id:
        raise ValueError(f"Pilot classifications do not belong to {project_id}")
    records = document.get("observations")
    if not isinstance(records, list):
        raise ValueError("Pilot classification observations must be a list")
    observations: list[ClassificationObservation] = []
    keys: set[tuple[str, str]] = set()
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Each pilot classification observation must be an object")
        _only_keys(
            record,
            {"case_id", "minimum_confidence", "false_positives", "false_negatives"},
            "classification observation",
        )
        case_id = _identifier(record.get("case_id"), "classification case ID")
        threshold = _text(record.get("minimum_confidence"), "classification threshold", 20)
        if threshold not in THRESHOLDS:
            raise ValueError(f"Invalid classification threshold for {case_id}")
        key = (case_id, threshold)
        if key in keys:
            raise ValueError(f"Duplicate classification observation for {case_id} at {threshold}")
        keys.add(key)
        observations.append(
            ClassificationObservation(
                case_id,
                threshold,
                _classification_set(record.get("false_positives"), case_id, "FP"),
                _classification_set(record.get("false_negatives"), case_id, "FN"),
            )
        )
    return PilotClassifications(
        project_id,
        tuple(sorted(observations, key=lambda item: (item.case_id, item.minimum_confidence))),
    )


def evaluate_longitudinal(
    project_root: Path,
    checkouts_root: Path,
    manifest_path: Path,
    manifest: PilotManifest,
    *,
    limit: int = 20,
) -> LongitudinalResult:
    if isinstance(limit, bool) or limit < 1 or limit > MAX_RECOMMENDATIONS:
        raise ValueError(f"Pilot limit must be between 1 and {MAX_RECOMMENDATIONS}")
    project_root = project_root.resolve()
    checkouts_root = checkouts_root.resolve()
    if not checkouts_root.is_dir():
        raise ValueError("Pilot checkout root does not exist")
    manifest_resolved = manifest_path.resolve()
    if manifest_resolved == project_root or project_root not in manifest_resolved.parents:
        raise ValueError("Pilot manifest must be below the project root")

    loaded: list[tuple[PilotProject, PilotLabels, PilotClassifications, Path]] = []
    all_cases: list[tuple[str, PilotCase]] = []
    global_case_ids: set[str] = set()
    for project in manifest.projects:
        labels_path = _inside_project(project_root, project.labels, f"labels for {project.id}")
        classifications_path = _inside_project(
            project_root, project.classifications, f"classifications for {project.id}"
        )
        labels = load_pilot_labels(labels_path, project.id)
        classifications = load_pilot_classifications(classifications_path, project.id)
        for case in labels.cases:
            if case.id in global_case_ids:
                raise ValueError(f"Duplicate global pilot case ID: {case.id}")
            global_case_ids.add(case.id)
            all_cases.append((project.id, case))
        checkout = _checkout_path(checkouts_root, project.id)
        _validate_checkout(checkout, project)
        loaded.append((project, labels, classifications, checkout))
    if len(all_cases) > MAX_CASES:
        raise ValueError(f"Pilot exceeds the {MAX_CASES}-case limit")
    actual_hashes = partition_hashes(tuple(all_cases))
    if actual_hashes != manifest.partition_hashes:
        raise ValueError("Pilot partition hashes do not match the frozen labels")

    results: list[PilotCaseResult] = []
    for project, labels, classifications, checkout in loaded:
        active_config = ProjectConfig(
            git_history_limit=project.history_limit,
            exclude=[*ProjectConfig().exclude, *project.excluded_paths],
        )
        graph = scan_repository(
            checkout,
            active_config,
        )
        classification_map = {
            (item.case_id, item.minimum_confidence): item
            for item in classifications.observations
        }
        label_ids = {case.id for case in labels.cases}
        unknown_classification = sorted(
            key for key in classification_map if key[0] not in label_ids
        )
        if unknown_classification:
            raise ValueError(
                f"Classification references unknown case: {unknown_classification[0][0]}"
            )
        for case in labels.cases:
            _validate_case_against_checkout(checkout, graph, case)
            change_set = collect_change_set(
                checkout,
                scope="commit",
                revision=case.revision,
                excluded_paths=project.excluded_paths,
            )
            analysis = _analyze_change_set_with_graph(
                checkout,
                change_set,
                graph,
                active_config,
            )
            freshness = _aggregate_freshness(analysis.files)
            for threshold in manifest.thresholds:
                recommendation = recommend_tests(
                    graph,
                    f"commit:{case.revision}",
                    minimum_confidence=threshold,
                    limit=limit,
                )
                recommended = tuple(
                    item.test.path
                    for item in recommendation.recommendations
                    if item.test.path is not None
                )
                expected_set = set(case.expected_tests)
                recommended_set = set(recommended)
                true_positives = tuple(path for path in recommended if path in expected_set)
                false_positives = tuple(path for path in recommended if path not in expected_set)
                false_negatives = tuple(sorted(expected_set - recommended_set))
                report = build_change_report(
                    graph,
                    analysis,
                    minimum_confidence=threshold,
                    limit=limit,
                )
                observation = classification_map.get((case.id, threshold))
                unclassified, fp_classifications, fn_classifications = _classification_gap(
                    observation, false_positives, false_negatives, case.id, threshold
                )
                results.append(
                    PilotCaseResult(
                        project.id,
                        project.language,
                        project.workspace_shape,
                        case.id,
                        case.sequence,
                        case.revision,
                        case.committed_at,
                        case.partition,
                        threshold,
                        case.expected_tests,
                        recommended,
                        true_positives,
                        false_positives,
                        false_negatives,
                        fp_classifications,
                        fn_classifications,
                        _ratio(len(true_positives), len(recommended)),
                        _ratio(len(true_positives), len(case.expected_tests)),
                        bool(recommended),
                        report.test_strategy in {"abstain-and-full-suite", "no-targets-found"},
                        analysis.state,
                        freshness,
                        report.test_strategy,
                        unclassified,
                    )
                )
    ordered_results = tuple(
        sorted(
            results,
            key=lambda item: (
                item.project_id,
                item.sequence,
                THRESHOLDS.index(item.minimum_confidence),
            ),
        )
    )
    return LongitudinalResult(
        manifest.name,
        hashlib.sha256(manifest_resolved.read_bytes()).hexdigest(),
        actual_hashes,
        manifest.projects,
        ordered_results,
        _aggregate_cohorts(ordered_results),
    )


def partition_hashes(cases: tuple[tuple[str, PilotCase], ...]) -> dict[str, str]:
    result: dict[str, str] = {}
    for partition in PARTITIONS:
        records = [
            case.partition_record(project_id)
            for project_id, case in cases
            if case.partition == partition
        ]
        records.sort(key=lambda item: (item["project_id"], item["sequence"]))
        payload = json.dumps(
            {
                "schema_version": PILOT_LABEL_SCHEMA_VERSION,
                "partition": partition,
                "cases": records,
            },
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
        result[partition] = hashlib.sha256(payload).hexdigest()
    return result


def error_paths_sha256(paths: tuple[str, ...]) -> str:
    payload = json.dumps(
        sorted(paths),
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(payload).hexdigest()


def render_longitudinal(result: LongitudinalResult, output_format: str = "text") -> str:
    if output_format == "json":
        return json.dumps(result.to_dict(), indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if output_format != "text":
        raise ValueError(f"Unknown longitudinal output format: {output_format}")
    lines = [
        f"Longitudinal recommendation pilot: {result.name}",
        f"Manifest SHA-256: {result.manifest_sha256}",
        f"Calibration SHA-256: {result.partition_hashes['calibration']}",
        f"Evaluation SHA-256: {result.partition_hashes['evaluation']}",
        "Duration/savings: unknown (no aligned execution evidence supplied)",
        "",
    ]
    for cohort in result.cohorts:
        lines.append(
            f"{cohort.cohort} | {cohort.partition} | {cohort.minimum_confidence} | "
            f"projects={cohort.project_count} cases={cohort.case_count} "
            f"TP={cohort.true_positive_count} FP={cohort.false_positive_count} "
            f"FN={cohort.false_negative_count} precision={_estimate_text(cohort.precision)} "
            f"recall={_estimate_text(cohort.recall)} "
            f"coverage={_estimate_text(cohort.recommendation_coverage)} "
            f"abstention={_estimate_text(cohort.abstention)} "
            f"unclassified={cohort.unclassified_error_count}"
        )
    lines.extend(("", f"Advisory: {ADVISORY}"))
    return "\n".join(lines) + "\n"


def _aggregate_cohorts(cases: tuple[PilotCaseResult, ...]) -> tuple[PilotCohortResult, ...]:
    cohort_names = ["overall"]
    cohort_names.extend(f"project:{value}" for value in sorted({case.project_id for case in cases}))
    cohort_names.extend(f"language:{value}" for value in LANGUAGES)
    cohort_names.append("workspace:workspace")
    results: list[PilotCohortResult] = []
    for cohort in cohort_names:
        members = tuple(case for case in cases if _cohort_member(case, cohort))
        if not members:
            continue
        for partition in (*PARTITIONS, "all"):
            partition_members = (
                members
                if partition == "all"
                else tuple(case for case in members if case.partition == partition)
            )
            if not partition_members:
                continue
            for threshold in THRESHOLDS:
                selected = tuple(
                    case
                    for case in partition_members
                    if case.minimum_confidence == threshold
                )
                if not selected:
                    continue
                tp = sum(len(case.true_positives) for case in selected)
                fp = sum(len(case.false_positives) for case in selected)
                fn = sum(len(case.false_negatives) for case in selected)
                recommendation_count = tp + fp
                expected_count = tp + fn
                results.append(
                    PilotCohortResult(
                        cohort,
                        partition,
                        threshold,
                        len({case.project_id for case in selected}),
                        len(selected),
                        expected_count,
                        recommendation_count,
                        tp,
                        fp,
                        fn,
                        _estimate(tp, recommendation_count),
                        _estimate(tp, expected_count),
                        _estimate(
                            sum(case.recommendation_covered for case in selected),
                            len(selected),
                        ),
                        _estimate(sum(case.abstained for case in selected), len(selected)),
                        dict(sorted(Counter(case.analysis_state for case in selected).items())),
                        dict(sorted(Counter(case.freshness for case in selected).items())),
                        dict(sorted(Counter(case.execution_strategy for case in selected).items())),
                        sum(case.unclassified_error_count for case in selected),
                    )
                )
    return tuple(results)


def _cohort_member(case: PilotCaseResult, cohort: str) -> bool:
    if cohort == "overall":
        return True
    kind, value = cohort.split(":", 1)
    if kind == "project":
        return case.project_id == value
    if kind == "language":
        return case.language == value
    return kind == "workspace" and case.workspace_shape == value


def _estimate(successes: int, denominator: int) -> Estimate:
    if denominator == 0:
        return Estimate(None, None, None, 0)
    point = successes / denominator
    z = 1.959964
    z_squared = z * z
    scale = 1 + z_squared / denominator
    center = (point + z_squared / (2 * denominator)) / scale
    margin = (
        z
        * math.sqrt(
            point * (1 - point) / denominator
            + z_squared / (4 * denominator * denominator)
        )
        / scale
    )
    return Estimate(
        round(point, 6),
        round(max(0.0, center - margin), 6),
        round(min(1.0, center + margin), 6),
        denominator,
    )


def _classification_gap(
    observation: ClassificationObservation | None,
    false_positives: tuple[str, ...],
    false_negatives: tuple[str, ...],
    case_id: str,
    threshold: str,
) -> tuple[int, dict[str, str], dict[str, str]]:
    if observation is None:
        return len(false_positives) + len(false_negatives), {}, {}
    fp_classifications = _validated_error_set(
        observation.false_positives,
        false_positives,
        case_id,
        threshold,
        "false positives",
    )
    fn_classifications = _validated_error_set(
        observation.false_negatives,
        false_negatives,
        case_id,
        threshold,
        "false negatives",
    )
    gap = (len(false_positives) if not fp_classifications else 0) + (
        len(false_negatives) if not fn_classifications else 0
    )
    return gap, fp_classifications, fn_classifications


def _classification_set(
    value: Any, case_id: str, kind: str
) -> ClassifiedErrorSet | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ValueError(f"Classified {kind} must be an object or null for {case_id}")
    _only_keys(value, {"category", "paths_sha256"}, "classified error set")
    category = _text(value.get("category"), f"classification for {case_id}", 100)
    if category not in CLASSIFICATION_CATEGORIES:
        raise ValueError(f"Invalid classification category for {case_id}: {category}")
    digest = _text(value.get("paths_sha256"), f"classified path SHA-256 for {case_id}", 64)
    if SAFE_SHA256.fullmatch(digest) is None:
        raise ValueError(f"Invalid classified path SHA-256 for {case_id}")
    return ClassifiedErrorSet(category, digest)


def _validated_error_set(
    reviewed: ClassifiedErrorSet | None,
    actual: tuple[str, ...],
    case_id: str,
    threshold: str,
    label: str,
) -> dict[str, str]:
    if not actual:
        if reviewed is not None:
            raise ValueError(f"Stale {label} classification for {case_id} at {threshold}")
        return {}
    if reviewed is None:
        return {}
    if reviewed.paths_sha256 != error_paths_sha256(actual):
        raise ValueError(f"Stale {label} classification for {case_id} at {threshold}")
    return {path: reviewed.category for path in actual}


def _validate_case_against_checkout(
    checkout: Path, graph: AtlasGraph, case: PilotCase
) -> None:
    git = shutil.which("git")
    if git is None:
        raise ValueError("Git is required to validate pilot cases")
    resolved = _git_value(git, checkout, "rev-parse", case.revision)
    if resolved != case.revision:
        raise ValueError(f"Pilot case revision is unavailable: {case.id}")
    committed_at = _git_value(git, checkout, "show", "-s", "--format=%cI", case.revision)
    _stored_time, expected = _timestamp(case.committed_at, case.id)
    _actual_time, actual = _timestamp(committed_at, case.id)
    if expected != actual:
        raise ValueError(f"Pilot case timestamp does not match Git for {case.id}")
    target = graph.nodes.get(f"commit:{case.revision}")
    if target is None or target.kind != "commit":
        raise ValueError(f"Pilot case revision is outside scanned history: {case.id}")
    for path in case.expected_tests:
        node = graph.nodes.get(f"file:{path}")
        if node is None or node.kind != "test" or node.path != path:
            raise ValueError(f"Unknown expected test in case {case.id}: {path}")


def _validate_checkout(checkout: Path, project: PilotProject) -> None:
    if checkout.is_symlink() or not checkout.is_dir():
        raise ValueError(f"Pilot checkout does not exist for {project.id}")
    git = shutil.which("git")
    if git is None:
        raise ValueError("Git is required to validate pilot checkouts")
    head = _git_value(git, checkout, "rev-parse", "HEAD")
    if head != project.revision:
        raise ValueError(f"Pilot checkout {project.id} is not at its pinned revision")
    origin = _git_value(git, checkout, "remote", "get-url", "origin").removesuffix(".git")
    if origin != project.repository:
        raise ValueError(f"Pilot checkout {project.id} has an unexpected origin")
    license_path = _inside_checkout(checkout, project.license.path, project.id)
    if license_path.stat().st_size > MAX_LICENSE_BYTES:
        raise ValueError(f"Reviewed license for {project.id} exceeds the size limit")
    if hashlib.sha256(license_path.read_bytes()).hexdigest() != project.license.sha256:
        raise ValueError(f"Reviewed license hash does not match for {project.id}")
    if _git_value(git, checkout, "status", "--porcelain", "--untracked-files=all"):
        raise ValueError(f"Pilot checkout {project.id} must be clean")


def _inside_checkout(checkout: Path, relative: str, project_id: str) -> Path:
    unresolved = checkout.joinpath(*PurePosixPath(relative).parts)
    if unresolved.is_symlink():
        raise ValueError(f"Reviewed license file is missing for {project_id}")
    try:
        target = unresolved.resolve(strict=True)
    except OSError as exc:
        raise ValueError(f"Reviewed license file is missing for {project_id}") from exc
    if target == checkout or checkout not in target.parents or not target.is_file():
        raise ValueError(f"Reviewed license file is missing for {project_id}")
    return target


def _checkout_path(root: Path, project_id: str) -> Path:
    unresolved = root / project_id
    if unresolved.is_symlink():
        raise ValueError(f"Pilot checkout may not be a symbolic link: {project_id}")
    checkout = unresolved.resolve()
    if checkout == root or root not in checkout.parents:
        raise ValueError(f"Pilot checkout escapes its root: {project_id}")
    return checkout


def _inside_project(root: Path, configured: str, label: str) -> Path:
    unresolved = root.joinpath(*PurePosixPath(configured).parts)
    if unresolved.is_symlink():
        raise ValueError(f"Pilot {label} may not be a symbolic link")
    target = unresolved.resolve()
    if target == root or root not in target.parents:
        raise ValueError(f"Pilot {label} must be below the project root")
    private = (root / "atlas" / "Private").resolve()
    if target == private or private in target.parents:
        raise ValueError(f"Pilot {label} may not be inside atlas/Private")
    if not target.is_file():
        raise ValueError(f"Pilot {label} does not exist")
    return target


def _load_json(path: Path, limit: int, label: str) -> dict[str, Any]:
    if path.is_symlink():
        raise ValueError(f"{label.title()} may not be a symbolic link: {path.name}")
    if not path.is_file():
        raise ValueError(f"{label.title()} does not exist: {path.name}")
    try:
        if path.stat().st_size > limit:
            raise ValueError(f"{label.title()} exceeds the {limit}-byte limit")
        document = json.loads(
            path.read_bytes().decode("utf-8"), object_pairs_hook=_unique_object
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError(f"Cannot parse {label} {path.name}: {exc}") from exc
    if not isinstance(document, dict):
        raise ValueError(f"{label.title()} must be a JSON object")
    return document


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
        result = subprocess.run(  # noqa: S603  # nosec B603
            command,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            shell=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError(f"Cannot inspect pilot checkout {checkout.name}: {exc}") from exc
    if result.returncode != 0:
        raise ValueError(f"Cannot inspect pilot checkout {checkout.name}")
    return result.stdout.strip()


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
        raise ValueError(f"Unknown longitudinal {label} field: {unknown[0]}")


def _text(value: Any, label: str, limit: int) -> str:
    if not isinstance(value, str):
        raise ValueError(f"Pilot {label} must be a string")
    text = value.strip()
    if not text or len(text) > limit or any(ord(character) < 32 for character in text):
        raise ValueError(f"Invalid pilot {label}")
    return text


def _identifier(value: Any, label: str) -> str:
    text = _text(value, label, 100)
    if SAFE_ID.fullmatch(text) is None:
        raise ValueError(f"Invalid pilot {label}: {text!r}")
    return text


def _commit(value: Any, label: str) -> str:
    text = _text(value, label, 40)
    if SAFE_COMMIT.fullmatch(text) is None:
        raise ValueError(f"Invalid pilot {label}")
    return text


def _date(value: Any, project_id: str) -> str:
    text = _text(value, f"license review date for {project_id}", 10)
    try:
        parsed = datetime.strptime(text, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError(f"Invalid license review date for {project_id}") from exc
    return parsed.strftime("%Y-%m-%d")


def _timestamp(value: Any, case_id: str) -> tuple[str, datetime]:
    text = _text(value, f"timestamp for case {case_id}", 40)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"Invalid timestamp for pilot case {case_id}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"Pilot case timestamp needs an offset: {case_id}")
    return text, parsed


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
        raise ValueError(f"Unsafe pilot {label} path for {project_id}: {text!r}")
    return pure.as_posix()


def _test_path(value: Any, case_id: str) -> str:
    return _relative_path(value, case_id, "expected test")


def _aggregate_freshness(files: tuple[Any, ...]) -> str:
    rank = {"aligned": 0, "stale": 1, "unknown": 2}
    return max((item.freshness for item in files), key=lambda value: rank[value], default="unknown")


def _ratio(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 6) if denominator else None


def _estimate_text(estimate: Estimate) -> str:
    if estimate.value is None:
        return "n/a"
    interval = f"[{estimate.lower:.2%}, {estimate.upper:.2%}]"
    return f"{estimate.value:.2%} {interval} n={estimate.denominator}"


def _project_dict(project: PilotProject) -> dict[str, Any]:
    value = asdict(project)
    value["license"] = asdict(project.license)
    return value
