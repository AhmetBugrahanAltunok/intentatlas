from __future__ import annotations

import argparse
import os
import subprocess  # nosec B404
import sys
import tempfile
from pathlib import Path


def _run(command: list[str], environment: dict[str, str]) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(  # noqa: S603  # nosec B603
            command,
            env=environment,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
            shell=False,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError(f"isolated pipx command failed to start: {command[-1]}") from exc
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()[-2_000:]
        raise ValueError(f"isolated pipx command failed ({command[-1]}): {detail}")
    return result


def verify_pipx_lifecycle(wheel: Path, *, base: Path | None = None) -> str:
    resolved_wheel = wheel.resolve(strict=True)
    if resolved_wheel.is_symlink() or not resolved_wheel.is_file():
        raise ValueError("wheel must be one regular file")
    if resolved_wheel.suffix != ".whl":
        raise ValueError("pipx lifecycle verification requires a wheel")
    original_path = os.environ.get("PATH", "")
    temporary_parent = None if base is None else base.resolve()
    if temporary_parent is not None:
        temporary_parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="intentatlas-pipx-", dir=temporary_parent) as value:
        root = Path(value)
        environment = os.environ.copy()
        environment.update(
            {
                "PIPX_HOME": str(root / "home"),
                "PIPX_BIN_DIR": str(root / "bin"),
                "PIPX_MAN_DIR": str(root / "man"),
                "PIP_DISABLE_PIP_VERSION_CHECK": "1",
                "PIP_NO_INPUT": "1",
            }
        )
        pipx = [sys.executable, "-m", "pipx"]
        _run(
            [
                *pipx,
                "install",
                "--force",
                "--pip-args=--no-deps",
                str(resolved_wheel),
            ],
            environment,
        )
        executable = root / "bin" / ("intentatlas.exe" if os.name == "nt" else "intentatlas")
        if not executable.is_file():
            raise ValueError("pipx did not expose the intentatlas console command")
        version = _run([str(executable), "--version"], environment).stdout.strip()
        if not version.startswith("IntentAtlas "):
            raise ValueError("installed console command returned an unexpected version")
        help_output = _run([str(executable), "--help"], environment).stdout
        if "guide" not in help_output or "cache" not in help_output:
            raise ValueError("installed console help is missing Phase 15 commands")
        _run([*pipx, "reinstall", "intentatlas"], environment)
        if _run([str(executable), "--version"], environment).stdout.strip() != version:
            raise ValueError("reinstalled console command changed version")
        _run([*pipx, "uninstall", "intentatlas"], environment)
        if executable.exists():
            raise ValueError("pipx uninstall left the console command behind")
    if os.environ.get("PATH", "") != original_path:
        raise ValueError("pipx lifecycle verification changed the caller PATH")
    return version


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify an IntentAtlas wheel through an isolated pipx lifecycle."
    )
    parser.add_argument("wheel", type=Path)
    parser.add_argument("--temporary-parent", type=Path)
    args = parser.parse_args()
    try:
        version = verify_pipx_lifecycle(args.wheel, base=args.temporary_parent)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"pipx lifecycle verification failed: {exc}\n")
    print(f"Verified isolated pipx install, reinstall, and uninstall: {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
