from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ACTION = ROOT / ".github" / "actions" / "intentatlas-review" / "action.yml"
RUNNER = ACTION.with_name("run.sh")
GITHUB_CONFIG = ROOT / ".github"
PUBLISH_WORKFLOW = GITHUB_CONFIG / "workflows" / "publish.yml"
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


def test_external_actions_are_pinned_to_immutable_full_commit_shas() -> None:
    action_reference = re.compile(r"^\s*-\s+uses:\s*([^\s#]+)", re.MULTILINE)
    references: list[tuple[str, str]] = []
    paths = (*GITHUB_CONFIG.rglob("*.yml"), *GITHUB_CONFIG.rglob("*.yaml"))
    for path in sorted(paths):
        for reference in action_reference.findall(path.read_text(encoding="utf-8")):
            if not reference.startswith("./"):
                references.append((path.name, reference))

    assert references
    for workflow, reference in references:
        assert "@" in reference, f"Unversioned Action in {workflow}: {reference}"
        revision = reference.rsplit("@", maxsplit=1)[1]
        assert re.fullmatch(r"[0-9a-f]{40}", revision), (
            f"Mutable Action reference in {workflow}: {reference}"
        )


def test_trusted_publish_workflow_is_manual_protected_and_hash_bound() -> None:
    document = PUBLISH_WORKFLOW.read_text(encoding="utf-8")

    assert "workflow_dispatch:" in document
    assert "environment: pypi" in document
    assert "id-token: write" in document
    assert "persist-credentials: false" in document
    assert "source_revision:" in document
    assert "wheel_sha256:" in document
    assert "sdist_sha256:" in document
    assert 'test "$APPROVAL" = "publish approved IntentAtlas artifacts"' in document
    assert 'test "$(git rev-parse HEAD)" = "$SOURCE_REVISION"' in document
    assert "--expected-wheel-sha256" in document
    assert "--expected-sdist-sha256" in document
    assert "packages-dir: var/release-a" in document
    assert (
        "pypa/gh-action-pypi-publish@dc37677b2e1c63e2034f94d8a5b11f265b73ba33"
        in document
    )

    trigger = document.split("permissions:", maxsplit=1)[0]
    assert "\n  push:" not in trigger
    assert "\n  pull_request:" not in trigger
    assert "\n  release:" not in trigger
