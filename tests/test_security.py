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
