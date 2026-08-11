from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from .confidence import CONFIDENCE_RANK
from .graph import AtlasGraph
from .recommendations import MAX_RECOMMENDATIONS, recommend_tests

EVALUATION_SCHEMA_VERSION = 1
LABEL_POLICY = "complete-test-set"
MAX_LABEL_BYTES = 1_000_000
MAX_EVALUATION_CASES = 500
MAX_EXPECTED_TESTS_PER_CASE = 1_000
SAFE_CASE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")
WINDOWS_ABSOLUTE = re.compile(r"^[A-Za-z]:[/\\]")
ADVISORY = (
    "Metrics are valid only if the complete-test-set labels are exhaustive and correct; "
    "this benchmark does not prove accuracy on other repositories."
)


@dataclass(frozen=True, slots=True)
class EvaluationCase:
    id: str
    target: str
    expected_tests: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class EvaluationLabels:
    name: str
    cases: tuple[EvaluationCase, ...]
    label_policy: str = LABEL_POLICY


@dataclass(frozen=True, slots=True)
class CaseEvaluation:
    id: str
    target: str
    expected_tests: tuple[str, ...]
    recommended_tests: tuple[str, ...]
    true_positives: tuple[str, ...]
    false_positives: tuple[str, ...]
    false_negatives: tuple[str, ...]
    precision: float | None
    recall: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class EvaluationTotals:
    case_count: int
    expected_count: int
    recommendation_count: int
    true_positive_count: int
    false_positive_count: int
    false_negative_count: int
    precision: float | None
    recall: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    name: str
    label_policy: str
    minimum_confidence: str
    limit: int
    cases: tuple[CaseEvaluation, ...]
    totals: EvaluationTotals

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": EVALUATION_SCHEMA_VERSION,
            "advisory": ADVISORY,
            "name": self.name,
            "label_policy": self.label_policy,
            "minimum_confidence": self.minimum_confidence,
            "limit": self.limit,
            "cases": [case.to_dict() for case in self.cases],
            "totals": self.totals.to_dict(),
        }


def load_evaluation_labels(path: Path) -> EvaluationLabels:
    if path.is_symlink():
        raise ValueError(f"Evaluation labels may not be a symbolic link: {path.name}")
    if not path.is_file():
        raise ValueError(f"Evaluation labels do not exist: {path.name}")
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise ValueError(f"Cannot inspect evaluation labels {path.name}: {exc}") from exc
    if size > MAX_LABEL_BYTES:
        raise ValueError(
            f"Evaluation labels exceed the {MAX_LABEL_BYTES}-byte limit: {path.name}"
        )
    try:
        document = json.loads(
            path.read_bytes().decode("utf-8"), object_pairs_hook=_unique_object
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError(f"Cannot parse evaluation labels {path.name}: {exc}") from exc
    if not isinstance(document, dict):
        raise ValueError("Evaluation labels must be a JSON object")
    _only_keys(document, {"schema_version", "name", "label_policy", "cases"}, "labels")
    schema_version = document.get("schema_version")
    if type(schema_version) is not int or schema_version != EVALUATION_SCHEMA_VERSION:
        raise ValueError("Unsupported evaluation label schema")
    if document.get("label_policy") != LABEL_POLICY:
        raise ValueError(f"Evaluation label_policy must be {LABEL_POLICY!r}")
    name = _text(document.get("name"), "evaluation name", 200)
    records = document.get("cases")
    if not isinstance(records, list) or not records:
        raise ValueError("Evaluation cases must be a non-empty list")
    if len(records) > MAX_EVALUATION_CASES:
        raise ValueError(
            f"Evaluation labels exceed the {MAX_EVALUATION_CASES}-case limit"
        )

    cases: list[EvaluationCase] = []
    case_ids: set[str] = set()
    targets: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Each evaluation case must be an object")
        _only_keys(record, {"id", "target", "expected_tests"}, "case")
        case_id = _text(record.get("id"), "case ID", 100)
        if SAFE_CASE_ID.fullmatch(case_id) is None:
            raise ValueError(f"Invalid evaluation case ID: {case_id!r}")
        target = _text(record.get("target"), "case target", 500)
        if case_id in case_ids:
            raise ValueError(f"Duplicate evaluation case ID: {case_id}")
        if target in targets:
            raise ValueError(f"Duplicate evaluation target: {target}")
        case_ids.add(case_id)
        targets.add(target)
        raw_tests = record.get("expected_tests")
        if not isinstance(raw_tests, list):
            raise ValueError(f"Expected tests must be a list in case {case_id}")
        if len(raw_tests) > MAX_EXPECTED_TESTS_PER_CASE:
            raise ValueError(
                f"Case {case_id} exceeds the {MAX_EXPECTED_TESTS_PER_CASE}-test limit"
            )
        expected = tuple(_test_path(value, case_id) for value in raw_tests)
        if len(set(expected)) != len(expected):
            raise ValueError(f"Duplicate expected test in case {case_id}")
        cases.append(EvaluationCase(case_id, target, tuple(sorted(expected))))
    return EvaluationLabels(name=name, cases=tuple(sorted(cases, key=lambda case: case.id)))


def evaluate_recommendations(
    graph: AtlasGraph,
    labels: EvaluationLabels,
    *,
    minimum_confidence: str = "medium",
    limit: int = 20,
) -> EvaluationResult:
    if minimum_confidence not in CONFIDENCE_RANK:
        raise ValueError(f"Unknown minimum confidence: {minimum_confidence}")
    if isinstance(limit, bool) or limit < 1 or limit > MAX_RECOMMENDATIONS:
        raise ValueError(f"Evaluation limit must be between 1 and {MAX_RECOMMENDATIONS}")

    results: list[CaseEvaluation] = []
    for case in labels.cases:
        target = graph.nodes.get(case.target)
        if target is None:
            raise ValueError(
                f"Evaluation target is absent from the saved graph in case {case.id}: "
                f"{case.target}. Run `scan` first. If it is still absent, increase "
                "`git_history_limit` to include the pinned commit or refresh the reviewed labels."
            )
        if target.kind not in {"commit", "file", "symbol", "test"}:
            raise ValueError(
                f"Unsupported evaluation target kind in case {case.id}: {target.kind}"
            )
        for expected_path in case.expected_tests:
            expected = graph.nodes.get(f"file:{expected_path}")
            if expected is None or expected.kind != "test" or expected.path != expected_path:
                raise ValueError(
                    f"Expected test is absent from the saved graph in case {case.id}: "
                    f"{expected_path}. Run `scan` first; if it remains absent, refresh the "
                    "reviewed labels for the current test suite."
                )

        recommendation = recommend_tests(
            graph,
            target.id,
            minimum_confidence=minimum_confidence,
            limit=limit,
        )
        recommended: list[str] = []
        for item in recommendation.recommendations:
            if item.test.path is None:
                raise ValueError(f"Recommended test has no path: {item.test.id}")
            recommended.append(item.test.path)
        recommended_tests = tuple(recommended)
        expected_set = set(case.expected_tests)
        recommended_set = set(recommended_tests)
        true_positives = tuple(path for path in recommended_tests if path in expected_set)
        false_positives = tuple(path for path in recommended_tests if path not in expected_set)
        false_negatives = tuple(sorted(expected_set - recommended_set))
        results.append(
            CaseEvaluation(
                id=case.id,
                target=case.target,
                expected_tests=case.expected_tests,
                recommended_tests=recommended_tests,
                true_positives=true_positives,
                false_positives=false_positives,
                false_negatives=false_negatives,
                precision=_ratio(len(true_positives), len(recommended_tests)),
                recall=_ratio(len(true_positives), len(case.expected_tests)),
            )
        )

    cases = tuple(results)
    true_positive_count = sum(len(case.true_positives) for case in cases)
    false_positive_count = sum(len(case.false_positives) for case in cases)
    false_negative_count = sum(len(case.false_negatives) for case in cases)
    recommendation_count = true_positive_count + false_positive_count
    expected_count = true_positive_count + false_negative_count
    totals = EvaluationTotals(
        case_count=len(cases),
        expected_count=expected_count,
        recommendation_count=recommendation_count,
        true_positive_count=true_positive_count,
        false_positive_count=false_positive_count,
        false_negative_count=false_negative_count,
        precision=_ratio(true_positive_count, recommendation_count),
        recall=_ratio(true_positive_count, expected_count),
    )
    return EvaluationResult(
        name=labels.name,
        label_policy=labels.label_policy,
        minimum_confidence=minimum_confidence,
        limit=limit,
        cases=cases,
        totals=totals,
    )


def render_evaluation(result: EvaluationResult, output_format: str = "text") -> str:
    if output_format == "json":
        return json.dumps(result.to_dict(), indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if output_format != "text":
        raise ValueError(f"Unknown evaluation output format: {output_format}")

    lines = [
        f"Recommendation evaluation: {result.name}",
        f"Label policy: {result.label_policy}",
        f"Minimum confidence: {result.minimum_confidence}",
        f"Per-case recommendation limit: {result.limit}",
    ]
    for index, case in enumerate(result.cases, start=1):
        lines.extend(
            [
                f"{index}. {case.id} — {case.target}",
                f"   Expected: {len(case.expected_tests)}",
                f"   Recommended: {len(case.recommended_tests)}",
                f"   TP: {len(case.true_positives)}, FP: {len(case.false_positives)}, "
                f"FN: {len(case.false_negatives)}",
                f"   Precision: {_metric(case.precision)}, Recall: {_metric(case.recall)}",
            ]
        )
        if case.false_positives:
            lines.append(f"   False positives: {', '.join(case.false_positives)}")
        if case.false_negatives:
            lines.append(f"   False negatives: {', '.join(case.false_negatives)}")
    totals = result.totals
    lines.extend(
        [
            "Totals",
            f"  Cases: {totals.case_count}",
            f"  Expected: {totals.expected_count}, Recommended: {totals.recommendation_count}",
            f"  TP: {totals.true_positive_count}, FP: {totals.false_positive_count}, "
            f"FN: {totals.false_negative_count}",
            f"  Micro precision: {_metric(totals.precision)}",
            f"  Micro recall: {_metric(totals.recall)}",
            f"Advisory: {ADVISORY}",
        ]
    )
    return "\n".join(lines) + "\n"


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
        raise ValueError(f"Unknown evaluation {label} field: {unknown[0]}")


def _text(value: Any, label: str, limit: int) -> str:
    if not isinstance(value, str):
        raise ValueError(f"Evaluation {label} must be a string")
    text = value.strip()
    if not text or len(text) > limit or any(ord(character) < 32 for character in text):
        raise ValueError(f"Invalid evaluation {label}")
    return text


def _test_path(value: Any, case_id: str) -> str:
    text = _text(value, f"expected test in case {case_id}", 500)
    pure = PurePosixPath(text)
    if (
        "\\" in text
        or pure.is_absolute()
        or WINDOWS_ABSOLUTE.match(text)
        or ".." in pure.parts
        or pure.as_posix() in {"", "."}
        or pure.as_posix() != text
    ):
        raise ValueError(f"Unsafe expected test path in case {case_id}: {text!r}")
    return pure.as_posix()


def _ratio(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 6) if denominator else None


def _metric(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.2%}"
