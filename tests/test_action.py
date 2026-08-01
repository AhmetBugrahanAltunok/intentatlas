from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ACTION = ROOT / ".github" / "actions" / "intentatlas-review" / "action.yml"
RUNNER = ACTION.with_name("run.sh")
pytestmark = pytest.mark.skipif(not ACTION.exists(), reason="Repository-only Action is absent")


def test_shadow_review_action_is_opt_in_local_and_credential_free() -> None:
    document = ACTION.read_text(encoding="utf-8")
    runner = RUNNER.read_text(encoding="utf-8")
    implementation = document + "\n" + runner

    assert "using: composite" in document
    assert document.count("required: true") == 2
    assert "GITHUB_ACTION_PATH" in document
    assert "GITHUB_WORKSPACE" in implementation
    assert "RUNNER_TEMP" in implementation
    assert 'bash "${GITHUB_ACTION_PATH}/run.sh"' in document
    assert "PYTHONPATH" in runner
    assert "-m intentatlas" in runner
    assert 'review "${GITHUB_WORKSPACE}"' in runner
    assert '--base "${INPUT_BASE}"' in runner
    assert '--head "${INPUT_HEAD}"' in runner
    assert '--format "${INPUT_FORMAT}"' in runner
    assert '--test-outcomes "${INPUT_TEST_OUTCOMES}"' in runner
    assert 'case "${INPUT_FORMAT}" in' in runner
    assert '>> "${GITHUB_OUTPUT}"' in runner

    lowered = implementation.casefold()
    for forbidden in (
        "github_token",
        "github.token",
        "pull-requests:",
        "curl ",
        "wget ",
        "gh ",
        "git push",
        "upload-artifact",
    ):
        assert forbidden not in lowered
