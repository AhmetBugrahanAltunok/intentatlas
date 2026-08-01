from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from .evaluation import (
    EvaluationLabels,
    EvaluationTotals,
    evaluate_recommendations,
)
from .graph import AtlasGraph
from .recommendations import MAX_RECOMMENDATIONS

CORPUS_SCHEMA_VERSION = 1
CONFIDENCE_THRESHOLDS = ("low", "medium", "high")
MAX_CORPUS_BYTES = 256_000
MAX_CORPUS_PROJECTS = 50
MAX_CORPUS_CASES = 2_000
MAX_CORPUS_GRAPH_BYTES = 50_000_000
MAX_CORPUS_GRAPH_BYTES_TOTAL = 250_000_000
SAFE_PROJECT_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")
WINDOWS_ABSOLUTE = re.compile(r"^[A-Za-z]:[/\\]")
ADVISORY = (
    "Corpus metrics depend on exhaustive and correct labels; results do not prove accuracy "
    "beyond the evaluated cases."
)


@dataclass(frozen=True, slots=True)
class CorpusManifestProject:
    id: str
    name: str
    graph: str
    labels: str


@dataclass(frozen=True, slots=True)
class CorpusManifest:
    name: str
    projects: tuple[CorpusManifestProject, ...]


@dataclass(frozen=True, slots=True)
class CorpusProject:
    id: str
    name: str
    graph: AtlasGraph
    labels: EvaluationLabels


@dataclass(frozen=True, slots=True)
class CorpusProjectMetrics:
    id: str
    name: str
    case_count: int
    expected_count: int
    recommendation_count: int
    true_positive_count: int
    false_positive_count: int
    false_negative_count: int
    precision: float | None
    recall: float | None

    @classmethod
    def from_totals(
        cls,
        project: CorpusProject,
        totals: EvaluationTotals,
    ) -> CorpusProjectMetrics:
        return cls(project.id, project.name, **totals.to_dict())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CorpusThresholdResult:
    minimum_confidence: str
    projects: tuple[CorpusProjectMetrics, ...]
    totals: EvaluationTotals

    def to_dict(self) -> dict[str, Any]:
        return {
            "minimum_confidence": self.minimum_confidence,
            "projects": [project.to_dict() for project in self.projects],
            "totals": self.totals.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class CorpusEvaluationResult:
    name: str
    limit: int
    project_count: int
    case_count: int
    thresholds: tuple[CorpusThresholdResult, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": CORPUS_SCHEMA_VERSION,
            "advisory": ADVISORY,
            "name": self.name,
            "limit": self.limit,
            "project_count": self.project_count,
            "case_count": self.case_count,
            "thresholds": [threshold.to_dict() for threshold in self.thresholds],
        }


def load_corpus_manifest(path: Path) -> CorpusManifest:
    if path.is_symlink():
        raise ValueError(f"Corpus manifest may not be a symbolic link: {path.name}")
    if not path.is_file():
        raise ValueError(f"Corpus manifest does not exist: {path.name}")
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise ValueError(f"Cannot inspect corpus manifest {path.name}: {exc}") from exc
    if size > MAX_CORPUS_BYTES:
        raise ValueError(f"Corpus manifest exceeds the {MAX_CORPUS_BYTES}-byte limit: {path.name}")
    try:
        document = json.loads(
            path.read_bytes().decode("utf-8"),
            object_pairs_hook=_unique_object,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError(f"Cannot parse corpus manifest {path.name}: {exc}") from exc
    if not isinstance(document, dict):
        raise ValueError("Corpus manifest must be a JSON object")
    _only_keys(document, {"schema_version", "name", "projects"}, "manifest")
    schema_version = document.get("schema_version")
    if type(schema_version) is not int or schema_version != CORPUS_SCHEMA_VERSION:
        raise ValueError("Unsupported corpus manifest schema")
    name = _text(document.get("name"), "corpus name", 200)
    records = document.get("projects")
    if not isinstance(records, list) or not records:
        raise ValueError("Corpus projects must be a non-empty list")
    if len(records) > MAX_CORPUS_PROJECTS:
        raise ValueError(f"Corpus exceeds the {MAX_CORPUS_PROJECTS}-project limit")

    projects: list[CorpusManifestProject] = []
    ids: set[str] = set()
    graphs: set[str] = set()
    labels: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Each corpus project must be an object")
        _only_keys(record, {"id", "name", "graph", "labels"}, "project")
        project_id = _text(record.get("id"), "project ID", 100)
        if SAFE_PROJECT_ID.fullmatch(project_id) is None:
            raise ValueError(f"Invalid corpus project ID: {project_id!r}")
        project_name = _text(record.get("name"), "project name", 200)
        graph = _relative_path(record.get("graph"), project_id, "graph")
        label = _relative_path(record.get("labels"), project_id, "labels")
        if graph == label:
            raise ValueError(f"Corpus graph and labels must differ in project {project_id}")
        if project_id in ids:
            raise ValueError(f"Duplicate corpus project ID: {project_id}")
        if graph in graphs:
            raise ValueError(f"Duplicate corpus graph path: {graph}")
        if label in labels:
            raise ValueError(f"Duplicate corpus label path: {label}")
        ids.add(project_id)
        graphs.add(graph)
        labels.add(label)
        projects.append(CorpusManifestProject(project_id, project_name, graph, label))
    return CorpusManifest(name, tuple(sorted(projects, key=lambda project: project.id)))


def validate_corpus_graph_size(path: Path) -> int:
    if path.is_symlink():
        raise ValueError(f"Corpus graph may not be a symbolic link: {path.name}")
    if not path.is_file():
        raise ValueError(f"Corpus graph does not exist: {path.name}")
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise ValueError(f"Cannot inspect corpus graph {path.name}: {exc}") from exc
    if size > MAX_CORPUS_GRAPH_BYTES:
        raise ValueError(
            f"Corpus graph exceeds the {MAX_CORPUS_GRAPH_BYTES}-byte limit: {path.name}"
        )
    return size


def evaluate_corpus(
    name: str,
    projects: tuple[CorpusProject, ...],
    *,
    limit: int = 20,
) -> CorpusEvaluationResult:
    if not projects:
        raise ValueError("Corpus must contain at least one project")
    if len(projects) > MAX_CORPUS_PROJECTS:
        raise ValueError(f"Corpus exceeds the {MAX_CORPUS_PROJECTS}-project limit")
    if isinstance(limit, bool) or limit < 1 or limit > MAX_RECOMMENDATIONS:
        raise ValueError(f"Corpus limit must be between 1 and {MAX_RECOMMENDATIONS}")
    sorted_projects = tuple(sorted(projects, key=lambda project: project.id))
    ids = [project.id for project in sorted_projects]
    if len(ids) != len(set(ids)):
        raise ValueError("Corpus project IDs must be unique")
    case_count = sum(len(project.labels.cases) for project in sorted_projects)
    if not case_count:
        raise ValueError("Corpus must contain at least one evaluation case")
    if case_count > MAX_CORPUS_CASES:
        raise ValueError(f"Corpus exceeds the {MAX_CORPUS_CASES}-case limit")

    thresholds: list[CorpusThresholdResult] = []
    for minimum_confidence in CONFIDENCE_THRESHOLDS:
        project_metrics: list[CorpusProjectMetrics] = []
        project_totals: list[EvaluationTotals] = []
        for project in sorted_projects:
            try:
                evaluation = evaluate_recommendations(
                    project.graph,
                    project.labels,
                    minimum_confidence=minimum_confidence,
                    limit=limit,
                )
            except ValueError as exc:
                raise ValueError(f"Corpus project {project.id} failed: {exc}") from exc
            project_metrics.append(CorpusProjectMetrics.from_totals(project, evaluation.totals))
            project_totals.append(evaluation.totals)
        thresholds.append(
            CorpusThresholdResult(
                minimum_confidence,
                tuple(project_metrics),
                _aggregate_totals(project_totals),
            )
        )
    return CorpusEvaluationResult(
        name=name,
        limit=limit,
        project_count=len(sorted_projects),
        case_count=case_count,
        thresholds=tuple(thresholds),
    )


def render_corpus(result: CorpusEvaluationResult, output_format: str = "text") -> str:
    if output_format == "json":
        return json.dumps(result.to_dict(), indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if output_format != "text":
        raise ValueError(f"Unknown corpus output format: {output_format}")

    lines = [
        f"Recommendation corpus: {result.name}",
        f"Projects: {result.project_count}, Cases: {result.case_count}",
        f"Per-case recommendation limit: {result.limit}",
    ]
    for threshold in result.thresholds:
        lines.append(f"{threshold.minimum_confidence.upper()} confidence")
        for project in threshold.projects:
            lines.append(
                f"  {project.id}: TP {project.true_positive_count}, "
                f"FP {project.false_positive_count}, FN {project.false_negative_count}, "
                f"precision {_metric(project.precision)}, recall {_metric(project.recall)}"
            )
        totals = threshold.totals
        lines.append(
            f"  Micro: TP {totals.true_positive_count}, FP {totals.false_positive_count}, "
            f"FN {totals.false_negative_count}, precision {_metric(totals.precision)}, "
            f"recall {_metric(totals.recall)}"
        )
    lines.append(f"Advisory: {ADVISORY}")
    return "\n".join(lines) + "\n"


def _aggregate_totals(values: list[EvaluationTotals]) -> EvaluationTotals:
    expected_count = sum(value.expected_count for value in values)
    recommendation_count = sum(value.recommendation_count for value in values)
    true_positive_count = sum(value.true_positive_count for value in values)
    false_positive_count = sum(value.false_positive_count for value in values)
    false_negative_count = sum(value.false_negative_count for value in values)
    return EvaluationTotals(
        case_count=sum(value.case_count for value in values),
        expected_count=expected_count,
        recommendation_count=recommendation_count,
        true_positive_count=true_positive_count,
        false_positive_count=false_positive_count,
        false_negative_count=false_negative_count,
        precision=_ratio(true_positive_count, recommendation_count),
        recall=_ratio(true_positive_count, expected_count),
    )


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
        raise ValueError(f"Unknown corpus {label} field: {unknown[0]}")


def _text(value: Any, label: str, limit: int) -> str:
    if not isinstance(value, str):
        raise ValueError(f"Corpus {label} must be a string")
    text = value.strip()
    if not text or len(text) > limit or any(ord(character) < 32 for character in text):
        raise ValueError(f"Invalid corpus {label}")
    return text


def _relative_path(value: Any, project_id: str, label: str) -> str:
    text = _text(value, f"{label} path in project {project_id}", 500)
    pure = PurePosixPath(text)
    if (
        "\\" in text
        or pure.is_absolute()
        or WINDOWS_ABSOLUTE.match(text)
        or ".." in pure.parts
        or pure.as_posix() in {"", "."}
        or pure.as_posix() != text
    ):
        raise ValueError(f"Unsafe corpus {label} path in project {project_id}: {text!r}")
    return pure.as_posix()


def _ratio(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 6) if denominator else None


def _metric(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.2%}"
