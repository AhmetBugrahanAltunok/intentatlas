from __future__ import annotations

import json

import pytest

from intentatlas.test_outcomes import (
    MAX_OUTCOME_BYTES,
    compare_test_outcomes,
    load_test_outcomes,
)


def write_outcomes(tmp_path, document: object):
    path = tmp_path / "test-outcomes.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def valid_document() -> dict[str, object]:
    return {
        "schema_version": 1,
        "commit": "A" * 40,
        "test_set_policy": "complete-executed-set",
        "tests": [
            {"path": "tests/test_profile.py", "status": "failed", "duration_ms": 12},
            {"path": "tests/test_auth.py", "status": "passed"},
            {"path": "tests/test_extra.py", "status": "skipped", "duration_ms": 0},
        ],
    }


def test_outcomes_load_strict_bounded_commit_keyed_evidence(tmp_path) -> None:
    outcomes = load_test_outcomes(write_outcomes(tmp_path, valid_document()))

    assert outcomes.commit == "a" * 40
    assert outcomes.test_set_policy == "complete-executed-set"
    assert [item.path for item in outcomes.tests] == [
        "tests/test_auth.py",
        "tests/test_extra.py",
        "tests/test_profile.py",
    ]
    assert outcomes.tests[0].duration_ms is None
    assert outcomes.tests[2].status == "failed"

    comparison = compare_test_outcomes(
        "a" * 40,
        ("tests/test_auth.py", "tests/test_profile.py", "tests/test_missing.py"),
        outcomes,
    )
    assert comparison.freshness == "aligned"
    assert comparison.predicted_and_executed == (
        "tests/test_auth.py",
        "tests/test_profile.py",
    )
    assert comparison.predicted_not_executed == ("tests/test_missing.py",)
    assert comparison.executed_not_predicted == ("tests/test_extra.py",)
    assert comparison.to_dict()["tests"][2]["status"] == "failed"


def test_stale_outcomes_never_create_prediction_comparison_claims(tmp_path) -> None:
    outcomes = load_test_outcomes(write_outcomes(tmp_path, valid_document()))
    comparison = compare_test_outcomes("b" * 40, ("tests/test_auth.py",), outcomes)

    assert comparison.freshness == "stale"
    assert comparison.predicted_and_executed == ()
    assert comparison.predicted_not_executed == ()
    assert comparison.executed_not_predicted == ()
    assert comparison.to_dict()["review_head"] == "b" * 40


@pytest.mark.parametrize(
    ("field", "value", "message"),
    (
        ("schema_version", 2, "schema"),
        ("commit", "HEAD", "commit"),
        ("test_set_policy", "partial", "test_set_policy"),
        ("tests", "not-a-list", "tests must be a list"),
    ),
)
def test_outcomes_reject_invalid_top_level_contract(
    tmp_path, field: str, value: object, message: str
) -> None:
    document = valid_document()
    document[field] = value
    with pytest.raises(ValueError, match=message):
        load_test_outcomes(write_outcomes(tmp_path, document))


@pytest.mark.parametrize(
    ("record", "message"),
    (
        ({"path": "../secret.py", "status": "passed"}, "path"),
        ({"path": "C:/secret.py", "status": "passed"}, "path"),
        ({"path": "tests/test_auth.py", "status": "unknown"}, "status"),
        ({"path": "tests/test_auth.py", "status": "passed", "duration_ms": -1}, "duration"),
        ({"path": "tests/test_auth.py", "status": "passed", "output": "secret"}, "keys"),
    ),
)
def test_outcomes_reject_unsafe_or_unbounded_test_records(
    tmp_path, record: dict[str, object], message: str
) -> None:
    document = valid_document()
    document["tests"] = [record]
    with pytest.raises(ValueError, match=message):
        load_test_outcomes(write_outcomes(tmp_path, document))


def test_outcomes_reject_duplicate_paths_and_duplicate_json_keys(tmp_path) -> None:
    document = valid_document()
    document["tests"] = [
        {"path": "tests/test_auth.py", "status": "passed"},
        {"path": "tests/test_auth.py", "status": "failed"},
    ]
    with pytest.raises(ValueError, match="Duplicate test outcome"):
        load_test_outcomes(write_outcomes(tmp_path, document))

    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text(
        '{"schema_version":1,"schema_version":1,"commit":"' + "a" * 40 + '",'
        '"test_set_policy":"complete-executed-set","tests":[]}',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Duplicate JSON key"):
        load_test_outcomes(duplicate)


def test_outcomes_reject_oversized_or_non_object_documents(tmp_path) -> None:
    oversized = tmp_path / "oversized.json"
    oversized.write_bytes(b"x" * (MAX_OUTCOME_BYTES + 1))
    with pytest.raises(ValueError, match="byte limit"):
        load_test_outcomes(oversized)

    non_object = tmp_path / "list.json"
    non_object.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="JSON object"):
        load_test_outcomes(non_object)
