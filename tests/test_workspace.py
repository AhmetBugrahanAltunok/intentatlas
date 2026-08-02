from __future__ import annotations

from pathlib import Path

from intentatlas.config import ProjectConfig
from intentatlas.scanner import scan_repository, scan_repository_incremental
from intentatlas.workspace import discover_workspace


def _write(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _files(root: Path) -> dict[str, Path]:
    return {
        path.relative_to(root).as_posix(): path
        for path in root.rglob("*")
        if path.is_file()
    }


def test_python_modules_are_resolved_inside_explicit_source_root_owner(tmp_path) -> None:
    for package in ("alpha", "beta"):
        _write(
            tmp_path,
            f"packages/{package}/pyproject.toml",
            "[project]\n"
            f'name = "{package}"\n'
            "[tool.setuptools.package-dir]\n"
            '"" = "src"\n',
        )
        _write(
            tmp_path,
            f"packages/{package}/src/shared.py",
            f"def value():\n    return {package!r}\n",
        )
        _write(
            tmp_path,
            f"packages/{package}/src/consumer.py",
            "from shared import value\n\ndef consume():\n    return value()\n",
        )

    graph = scan_repository(tmp_path, ProjectConfig(git_history_limit=0))
    imports = {
        (edge.source, edge.target)
        for edge in graph.edges
        if edge.relation == "imports"
    }
    assert (
        "file:packages/alpha/src/consumer.py",
        "symbol:packages/alpha/src/shared.py::value",
    ) in imports
    assert (
        "file:packages/beta/src/consumer.py",
        "symbol:packages/beta/src/shared.py::value",
    ) in imports
    assert not any(
        source.startswith("file:packages/alpha/")
        and "packages/beta/" in target
        for source, target in imports
    )


def test_javascript_aliases_are_owner_scoped_and_ambiguous_targets_abstain(tmp_path) -> None:
    _write(tmp_path, "apps/web/package.json", '{"name":"web"}\n')
    _write(
        tmp_path,
        "apps/web/tsconfig.json",
        '{"compilerOptions":{/* bounded JSONC */"baseUrl":".",'
        '"paths":{"@app/*":["src/*"],},},}\n',
    )
    _write(tmp_path, "apps/web/src/value.ts", "export function value() { return 1 }\n")
    _write(tmp_path, "apps/web/src/main.ts", "import { value } from '@app/value'\n")
    _write(tmp_path, "apps/admin/package.json", '{"name":"admin"}\n')
    _write(tmp_path, "apps/admin/src/value.ts", "export function value() { return 2 }\n")

    graph = scan_repository(tmp_path, ProjectConfig(git_history_limit=0))
    imports = {
        (edge.source, edge.target)
        for edge in graph.edges
        if edge.relation == "imports"
    }
    assert (
        "file:apps/web/src/main.ts",
        "symbol:apps/web/src/value.ts::value",
    ) in imports
    assert not any(
        source == "file:apps/web/src/main.ts" and "apps/admin/" in target
        for source, target in imports
    )

    _write(tmp_path, "apps/web/src/value.js", "export function value() { return 3 }\n")
    ambiguous = scan_repository(tmp_path, ProjectConfig(git_history_limit=0))
    assert not any(
        edge.source == "file:apps/web/src/main.ts"
        and edge.relation == "imports"
        and "src/value" in edge.target
        for edge in ambiguous.edges
    )


def test_go_declared_dependency_crosses_module_boundary_and_unknown_does_not(tmp_path) -> None:
    _write(
        tmp_path,
        "go.mod",
        "module example.test/root\n\n"
        "go 1.22\n\n"
        "require example.test/plugin v0.0.0\n\n"
        "replace example.test/plugin => ./plugin\n",
    )
    _write(tmp_path, "plugin/go.mod", "module example.test/plugin\n\ngo 1.22\n")
    _write(tmp_path, "plugin/api/api.go", "package api\n\nfunc Run() {}\n")
    _write(
        tmp_path,
        "cmd/main.go",
        'package main\n\nimport "example.test/plugin/api"\n\nfunc main() { api.Run() }\n',
    )
    graph = scan_repository(tmp_path, ProjectConfig(git_history_limit=0))
    assert any(
        edge.source == "file:cmd/main.go"
        and edge.target == "file:plugin/api/api.go"
        and edge.relation == "imports"
        for edge in graph.edges
    )

    _write(tmp_path, "go.mod", "module example.test/root\n\ngo 1.22\n")
    abstained = scan_repository(tmp_path, ProjectConfig(git_history_limit=0))
    assert not any(
        edge.source == "file:cmd/main.go" and "plugin/api/api.go" in edge.target
        for edge in abstained.edges
    )


def test_workspace_candidate_sets_and_diagnostics_are_deterministic(tmp_path) -> None:
    _write(tmp_path, "packages/a/package.json", '{"name":"duplicate"}\n')
    _write(tmp_path, "packages/b/package.json", '{"name":"duplicate"}\n')
    _write(tmp_path, "packages/a/src/a.ts", "export const a = 1\n")
    first = discover_workspace(tmp_path, _files(tmp_path))
    second = discover_workspace(tmp_path, _files(tmp_path))
    assert first.diagnostics == second.diagnostics
    assert any(item.code == "duplicate-package-name" for item in first.diagnostics)
    assert first.candidates("packages/a/src/a.ts") == (
        "workspace:javascript-package:packages/a",
    )

    result = scan_repository_incremental(tmp_path, ProjectConfig(git_history_limit=0))
    assert result.statistics.workspace_partitions == (
        "workspace:javascript-package:packages/a",
        "workspace:javascript-package:packages/b",
    )
    assert "duplicate-package-name" in result.statistics.workspace_diagnostics


def test_declared_dependency_cycle_is_reported_deterministically(tmp_path) -> None:
    _write(
        tmp_path,
        "packages/a/package.json",
        '{"name":"a","dependencies":{"b":"workspace:*"}}\n',
    )
    _write(
        tmp_path,
        "packages/b/package.json",
        '{"name":"b","dependencies":{"a":"workspace:*"}}\n',
    )
    _write(tmp_path, "packages/a/index.ts", "export const a = 1\n")
    _write(tmp_path, "packages/b/index.ts", "export const b = 1\n")

    first = discover_workspace(tmp_path, _files(tmp_path))
    second = discover_workspace(tmp_path, _files(tmp_path))
    cycles = [item for item in first.diagnostics if item.code == "cyclic-dependency"]
    assert len(cycles) == 1
    assert cycles == [item for item in second.diagnostics if item.code == "cyclic-dependency"]
    assert cycles[0].candidates == (
        "workspace:javascript-package:packages/a",
        "workspace:javascript-package:packages/b",
    )


def test_workspace_discovery_never_executes_project_tooling(tmp_path, monkeypatch) -> None:
    _write(
        tmp_path,
        "package.json",
        '{"name":"unsafe-scripts","scripts":{"prepare":"exit 99"}}\n',
    )
    _write(tmp_path, "src/index.ts", "export const value = 1\n")

    def forbidden(*_args, **_kwargs):
        raise AssertionError("workspace discovery attempted process execution")

    monkeypatch.setattr("subprocess.run", forbidden)
    monkeypatch.setattr("subprocess.Popen", forbidden)
    model = discover_workspace(tmp_path, _files(tmp_path))
    assert model.unique_owner("src/index.ts") == "workspace:javascript-package:."
