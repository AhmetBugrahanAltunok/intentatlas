import os

import pytest

from intentatlas.safe_io import read_bounded_regular_file
from intentatlas.security import redact


def test_redact_nested_values_and_common_token_shapes() -> None:
    value = {
        "api_key": "visible",
        "nested": ["password=hunter2", "ghp_" + "abcdefghijklmnopqrstuvwxyz1234"],
    }
    assert redact(value) == {
        "api_key": "[REDACTED]",
        "nested": ["password=[REDACTED]", "[REDACTED]"],
    }


def test_redact_preserves_non_strings() -> None:
    assert redact(42) == 42
    assert redact("ordinary commit subject") == "ordinary commit subject"


def test_bounded_regular_reader_rejects_growth_and_identity_changes(
    tmp_path, monkeypatch
) -> None:
    report = tmp_path / "report.json"
    replacement = tmp_path / "replacement.json"
    report.write_bytes(b"1234")
    replacement.write_bytes(b"5678")

    assert read_bounded_regular_file(report, 4) == b"1234"
    assert read_bounded_regular_file(report, 3) is None

    original_stat = type(report).stat
    calls = 0

    def changing_stat(path, *args, **kwargs):
        nonlocal calls
        if path == report:
            calls += 1
            if calls == 2:
                return original_stat(replacement, *args, **kwargs)
        return original_stat(path, *args, **kwargs)

    monkeypatch.setattr(type(report), "stat", changing_stat)
    assert read_bounded_regular_file(report, 4) is None


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="FIFO support is unavailable")
def test_bounded_regular_reader_rejects_fifo_without_blocking(tmp_path) -> None:
    fifo = tmp_path / "intentatlas.json"
    os.mkfifo(fifo)

    assert read_bounded_regular_file(fifo, 1024) is None
