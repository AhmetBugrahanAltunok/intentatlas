from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

TEST_OUTCOME_SCHEMA_VERSION = 1
TEST_SET_POLICY = "complete-executed-set"
MAX_OUTCOME_BYTES = 1_000_000
MAX_TEST_OUTCOMES = 10_000
MAX_TEST_PATH_LENGTH = 500
MAX_DURATION_MS = 86_400_000
TEST_STATUSES = {"passed", "failed", "error", "skipped"}
_FULL_COMMIT = re.compile(r"^[0-9a-fA-F]{40}$")
_WINDOWS_ABSOLUTE = re.compile(r"^[A-Za-z]:[/\\]")
_ADVISORY = (
    "Outcome comparison describes one commit-keyed execution set. It does not establish test "
    "necessity, sufficiency, recommendation accuracy, or unaffected behavior."
)


@dataclass(frozen=True, slots=True)
class TestOutcome:
    path: str
    status: str
    duration_ms: int | None = None

    def to_dict(self) -> dict[str, object]:
        value: dict[str, object] = {"path": self.path, "status": self.status}
        if self.duration_ms is not None:
            value["duration_ms"] = self.duration_ms
        return value


@dataclass(frozen=True, slots=True)
class TestOutcomeSet:
    commit: str
    tests: tuple[TestOutcome, ...]
    test_set_policy: str = TEST_SET_POLICY


@dataclass(frozen=True, slots=True)
class TestOutcomeComparison:
    review_head: str
    outcome_commit: str
    freshness: str
    tests: tuple[TestOutcome, ...]
    predicted_and_executed: tuple[str, ...]
    predicted_not_executed: tuple[str, ...]
    executed_not_predicted: tuple[str, ...]
    test_set_policy: str = TEST_SET_POLICY

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": TEST_OUTCOME_SCHEMA_VERSION,
            "advisory": _ADVISORY,
            "review_head": self.review_head,
            "outcome_commit": self.outcome_commit,
            "freshness": self.freshness,
            "test_set_policy": self.test_set_policy,
            "test_count": len(self.tests),
            "tests": [item.to_dict() for item in self.tests],
            "predicted_and_executed": list(self.predicted_and_executed),
            "predicted_not_executed": list(self.predicted_not_executed),
            "executed_not_predicted": list(self.executed_not_predicted),
        }


def load_test_outcomes(path: Path) -> TestOutcomeSet:
    if path.is_symlink():
        raise ValueError(f"Test outcomes may not be a symbolic link: {path.name}")
    if not path.is_file():
        raise ValueError(f"Test outcomes do not exist: {path.name}")
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise ValueError(f"Cannot inspect test outcomes {path.name}: {exc}") from exc
    if size > MAX_OUTCOME_BYTES:
        raise ValueError(
            f"Test outcomes exceed the {MAX_OUTCOME_BYTES}-byte limit: {path.name}"
        )
    try:
        document = json.loads(
            path.read_bytes().decode("utf-8"), object_pairs_hook=_unique_object
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, RecursionError, ValueError) as exc:
        raise ValueError(f"Cannot parse test outcomes {path.name}: {exc}") from exc
    if not isinstance(document, dict):
        raise ValueError("Test outcomes must be a JSON object")
    _only_keys(
        document,
        {"schema_version", "commit", "test_set_policy", "tests"},
        "test outcomes",
    )
    if document.get("schema_version") != TEST_OUTCOME_SCHEMA_VERSION or type(
        document.get("schema_version")
    ) is not int:
        raise ValueError("Unsupported test outcome schema")
    commit = _commit(document.get("commit"), "outcome commit")
    if document.get("test_set_policy") != TEST_SET_POLICY:
        raise ValueError(f"Test outcome test_set_policy must be {TEST_SET_POLICY!r}")
    records = document.get("tests")
    if not isinstance(records, list):
        raise ValueError("Test outcomes tests must be a list")
    if len(records) > MAX_TEST_OUTCOMES:
        raise ValueError(f"Test outcomes exceed the {MAX_TEST_OUTCOMES}-test limit")

    tests: list[TestOutcome] = []
    paths: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Each test outcome must be an object")
        _only_keys(record, {"path", "status", "duration_ms"}, "test outcome")
        test_path = _test_path(record.get("path"))
        if test_path in paths:
            raise ValueError(f"Duplicate test outcome: {test_path}")
        paths.add(test_path)
        status = record.get("status")
        if not isinstance(status, str) or status not in TEST_STATUSES:
            raise ValueError(f"Invalid test outcome status for {test_path}")
        duration = record.get("duration_ms")
        if duration is not None and (
            type(duration) is not int or duration < 0 or duration > MAX_DURATION_MS
        ):
            raise ValueError(f"Invalid test outcome duration for {test_path}")
        tests.append(TestOutcome(test_path, status, duration))
    return TestOutcomeSet(commit, tuple(sorted(tests, key=lambda item: item.path)))


def compare_test_outcomes(
    review_head: str,
    predicted_tests: tuple[str, ...],
    outcomes: TestOutcomeSet,
) -> TestOutcomeComparison:
    normalized_head = _commit(review_head, "review head")
    predicted = tuple(sorted({_test_path(path) for path in predicted_tests}))
    freshness = "aligned" if normalized_head == outcomes.commit else "stale"
    if freshness == "stale":
        matched: tuple[str, ...] = ()
        missing: tuple[str, ...] = ()
        additional: tuple[str, ...] = ()
    else:
        predicted_set = set(predicted)
        executed_set = {item.path for item in outcomes.tests}
        matched = tuple(sorted(predicted_set & executed_set))
        missing = tuple(sorted(predicted_set - executed_set))
        additional = tuple(sorted(executed_set - predicted_set))
    return TestOutcomeComparison(
        normalized_head,
        outcomes.commit,
        freshness,
        outcomes.tests,
        matched,
        missing,
        additional,
    )


def _commit(value: object, label: str) -> str:
    if not isinstance(value, str) or _FULL_COMMIT.fullmatch(value) is None:
        raise ValueError(f"Invalid full {label}")
    return value.lower()


def _test_path(value: object) -> str:
    if not isinstance(value, str) or not value or len(value) > MAX_TEST_PATH_LENGTH:
        raise ValueError("Invalid test outcome path")
    if "\\" in value or _WINDOWS_ABSOLUTE.match(value):
        raise ValueError(f"Unsafe test outcome path: {value!r}")
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or path.as_posix() != value
        or path.as_posix() in {"", "."}
        or ".." in path.parts
        or any(ord(character) < 32 for character in value)
    ):
        raise ValueError(f"Unsafe test outcome path: {value!r}")
    return value


def _only_keys(value: dict[str, Any], allowed: set[str], label: str) -> None:
    unexpected = set(value) - allowed
    if unexpected:
        raise ValueError(f"Unexpected {label} keys: {', '.join(sorted(unexpected))}")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"Duplicate JSON key: {key}")
        value[key] = item
    return value
