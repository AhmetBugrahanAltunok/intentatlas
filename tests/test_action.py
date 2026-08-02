from __future__ import annotations

import re
import shlex
from pathlib import Path
from typing import Any

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
ACTION = ROOT / ".github" / "actions" / "intentatlas-review" / "action.yml"
RUNNER = ACTION.with_name("run.sh")
GITHUB_CONFIG = ROOT / ".github"
PUBLISH_WORKFLOW = GITHUB_CONFIG / "workflows" / "publish.yml"
CI_WORKFLOW = GITHUB_CONFIG / "workflows" / "ci.yml"
pytestmark = pytest.mark.skipif(not ACTION.exists(), reason="Repository-only Action is absent")


def _load_yaml(path: Path) -> dict[object, Any]:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(document, dict), f"Expected a YAML mapping in {path}"
    return document


def _mapping_children(value: object):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _mapping_children(child)
    elif isinstance(value, list):
        for child in value:
            yield from _mapping_children(child)


def _uses_references(document: object) -> list[str]:
    references: list[str] = []
    for mapping in _mapping_children(document):
        reference = mapping.get("uses")
        if reference is not None:
            assert isinstance(reference, str)
            references.append(reference)
    return references


def _workflow_triggers(document: dict[object, Any]) -> dict[str, Any]:
    trigger = document.get("on", document.get(True))
    assert isinstance(trigger, dict)
    assert all(isinstance(key, str) for key in trigger)
    return trigger


def _job_steps(job: dict[object, Any]) -> list[dict[object, Any]]:
    steps = job.get("steps")
    assert isinstance(steps, list)
    assert all(isinstance(step, dict) for step in steps)
    return steps


def _named_step(job: dict[object, Any], name: str) -> dict[object, Any]:
    matches = [step for step in _job_steps(job) if step.get("name") == name]
    assert len(matches) == 1, f"Expected exactly one workflow step named {name!r}"
    return matches[0]


def _shell_commands(step: dict[object, Any]) -> tuple[str, ...]:
    run = step.get("run")
    assert isinstance(run, str)
    return tuple(
        line.strip()
        for line in run.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    )


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
    references: list[tuple[str, str]] = []
    paths = (*GITHUB_CONFIG.rglob("*.yml"), *GITHUB_CONFIG.rglob("*.yaml"))
    for path in sorted(paths):
        for reference in _uses_references(_load_yaml(path)):
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
    workflow = _load_yaml(PUBLISH_WORKFLOW)
    jobs = workflow.get("jobs")
    assert isinstance(jobs, dict)
    build_job = jobs.get("build-approved-artifacts")
    publish_job = jobs.get("publish")
    assert isinstance(build_job, dict)
    assert isinstance(publish_job, dict)

    triggers = _workflow_triggers(workflow)
    assert set(triggers) == {"workflow_dispatch"}
    dispatch = triggers["workflow_dispatch"]
    assert isinstance(dispatch, dict)
    inputs = dispatch.get("inputs")
    assert isinstance(inputs, dict)
    assert set(inputs) == {
        "source_revision",
        "source_date_epoch",
        "wheel_sha256",
        "sdist_sha256",
        "approval",
    }
    for definition in inputs.values():
        assert isinstance(definition, dict)
        assert definition.get("required") is True
        assert definition.get("type") == "string"

    assert build_job.get("if") == "github.ref == 'refs/heads/main'"
    assert publish_job.get("environment") == "pypi"
    assert publish_job.get("if") == "github.ref == 'refs/heads/main'"
    assert publish_job.get("permissions") == {"actions": "read", "id-token": "write"}
    assert set(publish_job) == {
        "name",
        "needs",
        "if",
        "runs-on",
        "environment",
        "permissions",
        "steps",
    }
    assert [step.get("name") for step in _job_steps(publish_job)] == [
        "Download the verified artifact bundle",
        "Recheck the transferred file set and approved hashes",
        "Publish the already verified bytes with trusted identity",
    ]

    approval_step = _named_step(build_job, "Validate the approval inputs")
    assert approval_step.get("shell") == "bash"
    assert approval_step.get("env") == {
        "APPROVAL": "${{ inputs.approval }}",
        "DISPATCH_REVISION": "${{ github.sha }}",
        "SOURCE_REVISION": "${{ inputs.source_revision }}",
        "SOURCE_DATE_EPOCH": "${{ inputs.source_date_epoch }}",
        "EXPECTED_WHEEL_SHA256": "${{ inputs.wheel_sha256 }}",
        "EXPECTED_SDIST_SHA256": "${{ inputs.sdist_sha256 }}",
    }
    assert _shell_commands(approval_step) == (
        'test "$APPROVAL" = "publish approved IntentAtlas artifacts"',
        '[[ "$SOURCE_REVISION" =~ ^[0-9a-f]{40}$ ]]',
        'test "$SOURCE_REVISION" = "$DISPATCH_REVISION"',
        '[[ "$SOURCE_DATE_EPOCH" =~ ^[0-9]+$ ]]',
        '[[ "$EXPECTED_WHEEL_SHA256" =~ ^[0-9a-f]{64}$ ]]',
        '[[ "$EXPECTED_SDIST_SHA256" =~ ^[0-9a-f]{64}$ ]]',
    )

    checkout_steps = [
        step
        for step in _job_steps(build_job)
        if str(step.get("uses", "")).startswith("actions/checkout@")
    ]
    assert len(checkout_steps) == 1
    assert checkout_steps[0].get("with") == {
        "ref": "${{ inputs.source_revision }}",
        "persist-credentials": False,
    }

    identity_step = _named_step(
        build_job, "Validate the approved source and artifact identities"
    )
    assert identity_step.get("env") == {
        "SOURCE_REVISION": "${{ inputs.source_revision }}"
    }
    assert _shell_commands(identity_step) == (
        'test "$(git rev-parse HEAD)" = "$SOURCE_REVISION"',
    )

    verifier_step = _named_step(
        build_job, "Match the exact approved artifacts and write provenance"
    )
    assert verifier_step.get("env") == {
        "SOURCE_REVISION": "${{ inputs.source_revision }}",
        "SOURCE_DATE_EPOCH": "${{ inputs.source_date_epoch }}",
        "EXPECTED_WHEEL_SHA256": "${{ inputs.wheel_sha256 }}",
        "EXPECTED_SDIST_SHA256": "${{ inputs.sdist_sha256 }}",
    }
    verifier_command = verifier_step.get("run")
    assert isinstance(verifier_command, str)
    assert shlex.split(verifier_command) == [
        "python",
        "tools/verify_release.py",
        "var/release-a",
        "var/release-b",
        "--write-provenance",
        "var/release-provenance.json",
        "--source-revision",
        "$SOURCE_REVISION",
        "--source-date-epoch",
        "$SOURCE_DATE_EPOCH",
        "--expected-wheel-sha256",
        "$EXPECTED_WHEEL_SHA256",
        "--expected-sdist-sha256",
        "$EXPECTED_SDIST_SHA256",
    ]

    upload_step = _named_step(
        build_job, "Transfer only the verified artifacts and provenance"
    )
    assert upload_step.get("uses") == (
        "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02"
    )
    upload_options = upload_step.get("with")
    assert isinstance(upload_options, dict)
    assert upload_options == {
        "name": "intentatlas-release-${{ inputs.source_revision }}",
        "path": (
            "var/release-a/*.whl\n"
            "var/release-a/*.tar.gz\n"
            "var/release-provenance.json\n"
        ),
        "if-no-files-found": "error",
        "retention-days": 1,
        "compression-level": 0,
    }

    download_step = _named_step(publish_job, "Download the verified artifact bundle")
    assert download_step.get("uses") == (
        "actions/download-artifact@d3f86a106a0bac45b974a628896c90dbdf5c8093"
    )
    assert download_step.get("with") == {
        "name": "intentatlas-release-${{ inputs.source_revision }}",
        "path": "var/approved",
    }
    recheck_step = _named_step(
        publish_job, "Recheck the transferred file set and approved hashes"
    )
    assert recheck_step.get("shell") == "bash"
    assert recheck_step.get("env") == {
        "EXPECTED_WHEEL_SHA256": "${{ inputs.wheel_sha256 }}",
        "EXPECTED_SDIST_SHA256": "${{ inputs.sdist_sha256 }}",
    }
    assert _shell_commands(recheck_step) == (
        'test -z "$(find var/approved -type l -print -quit)"',
        "mapfile -t files < <(find var/approved -type f -print | sort)",
        "mapfile -t wheels < <(find var/approved/release-a -maxdepth 1 -type f "
        "-name '*.whl' -print)",
        "mapfile -t sdists < <(find var/approved/release-a -maxdepth 1 -type f "
        "-name '*.tar.gz' -print)",
        'test "${#files[@]}" -eq 3',
        'test "${#wheels[@]}" -eq 1',
        'test "${#sdists[@]}" -eq 1',
        "test -f var/approved/release-provenance.json",
        'test "$(sha256sum "${wheels[0]}" | cut -d\' \' -f1)" '
        '= "$EXPECTED_WHEEL_SHA256"',
        'test "$(sha256sum "${sdists[0]}" | cut -d\' \' -f1)" '
        '= "$EXPECTED_SDIST_SHA256"',
    )
    publisher_step = _named_step(
        publish_job, "Publish the already verified bytes with trusted identity"
    )
    assert publisher_step.get("uses") == (
        "pypa/gh-action-pypi-publish@"
        "dc37677b2e1c63e2034f94d8a5b11f265b73ba33"
    )
    assert publisher_step.get("with") == {"packages-dir": "var/approved/release-a"}

def test_publish_identity_is_isolated_from_build_and_project_execution() -> None:
    workflow = _load_yaml(PUBLISH_WORKFLOW)
    jobs = workflow["jobs"]
    assert isinstance(jobs, dict)
    build_job = jobs["build-approved-artifacts"]
    publish_job = jobs["publish"]
    assert isinstance(build_job, dict)
    assert isinstance(publish_job, dict)

    assert build_job.get("permissions") == {"contents": "read"}
    assert build_job.get("if") == "github.ref == 'refs/heads/main'"
    assert "environment" not in build_job
    build_references = _uses_references(build_job)
    assert any(reference.startswith("actions/upload-artifact@") for reference in build_references)
    build_text = str(build_job)
    assert "--expected-wheel-sha256" in build_text
    assert "--expected-sdist-sha256" in build_text

    assert publish_job.get("environment") == "pypi"
    assert publish_job.get("if") == "github.ref == 'refs/heads/main'"
    assert publish_job.get("permissions") == {"actions": "read", "id-token": "write"}
    publish_references = _uses_references(publish_job)
    assert any(
        reference.startswith("actions/download-artifact@")
        for reference in publish_references
    )
    assert any(
        reference.startswith("pypa/gh-action-pypi-publish@")
        for reference in publish_references
    )
    publish_text = str(publish_job)
    for forbidden in (
        "actions/checkout@",
        "actions/setup-python@",
        "pip install",
        "python -m",
        "python tools/",
        "git ",
    ):
        assert forbidden not in publish_text


def test_security_job_audits_release_tools_and_third_party_environment() -> None:
    workflow = _load_yaml(CI_WORKFLOW)
    jobs = workflow.get("jobs")
    assert isinstance(jobs, dict)
    security_job = jobs.get("security")
    assert isinstance(security_job, dict)
    commands = [step.get("run") for step in _job_steps(security_job) if "run" in step]

    assert commands == [
        'python -m pip install -e ".[dev,release,security,typing]"',
        "python -m bandit -q -r src tools",
        "python -m pip_audit --skip-editable",
    ]


def test_static_type_job_installs_release_tool_imports() -> None:
    workflow = _load_yaml(CI_WORKFLOW)
    jobs = workflow.get("jobs")
    assert isinstance(jobs, dict)
    static_job = jobs.get("static-types")
    assert isinstance(static_job, dict)
    commands = [step.get("run") for step in _job_steps(static_job) if "run" in step]

    assert commands == [
        'python -m pip install -e ".[release,typing]"',
        "python -m mypy",
    ]


def test_action_policy_parser_observes_semantically_spaced_yaml_keys() -> None:
    document = yaml.safe_load(
        "jobs:\n  injected:\n    permissions:\n      id-token : write\n"
        "    steps:\n      - uses : attacker/example@main\n"
    )

    assert _uses_references(document) == ["attacker/example@main"]
    assert document["jobs"]["injected"]["permissions"] == {"id-token": "write"}
