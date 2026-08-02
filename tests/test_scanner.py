from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

import intentatlas.scanner as scanner_module
from intentatlas.config import ProjectConfig
from intentatlas.recommendations import recommend_tests
from intentatlas.scanner import scan_repository
from intentatlas.vault import ProjectVault

TYPESCRIPT_FIXTURE = Path(__file__).parent / "fixtures" / "typescript_project"
GO_FIXTURE = Path(__file__).parent / "fixtures" / "go_project"


def build_python_project(tmp_path) -> None:
    (tmp_path / "src" / "demo").mkdir(parents=True)
    (tmp_path / "tests").mkdir()
    (tmp_path / "src" / "demo" / "__init__.py").write_text(
        "from .core import Greeter\n", encoding="utf-8"
    )
    (tmp_path / "src" / "demo" / "core.py").write_text(
        "class Greeter:\n    def hello(self, name: str) -> str:\n        return f'Hello {name}'\n",
        encoding="utf-8",
    )
    (tmp_path / "src" / "demo" / "cli.py").write_text(
        "from .core import Greeter\n\ndef main():\n    return Greeter().hello('Atlas')\n",
        encoding="utf-8",
    )
    (tmp_path / "tests" / "test_core.py").write_text(
        "from demo.core import Greeter\n\ndef test_hello():\n    assert Greeter().hello('A')\n",
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "ignored.py").write_text("raise Exception\n", encoding="utf-8")
    (tmp_path / ".obsidian").mkdir()
    (tmp_path / ".obsidian" / "ignored.md").write_text("# Wrong vault\n", encoding="utf-8")


def test_scanner_connects_python_symbols_imports_and_tests(tmp_path) -> None:
    build_python_project(tmp_path)
    graph = scan_repository(tmp_path, ProjectConfig(git_history_limit=0))
    assert "file:src/demo/core.py" in graph.nodes
    assert "symbol:src/demo/core.py::Greeter" in graph.nodes
    assert "symbol:src/demo/core.py::Greeter.hello" in graph.nodes
    assert graph.nodes["symbol:src/demo/core.py::Greeter"].metadata["end_line"] == 3
    assert graph.nodes["symbol:src/demo/core.py::Greeter.hello"].metadata == {
        "symbol_kind": "function",
        "line": 2,
        "end_line": 3,
        "owner": "scanner",
    }
    assert "file:.venv/ignored.py" not in graph.nodes
    assert "file:.obsidian/ignored.md" not in graph.nodes

    relationships = {(edge.source, edge.target, edge.relation) for edge in graph.edges}
    assert (
        "file:src/demo/cli.py",
        "file:src/demo/core.py",
        "imports",
    ) in relationships
    assert (
        "file:tests/test_core.py",
        "file:src/demo/core.py",
        "tests",
    ) in relationships


def test_scanner_connects_typescript_javascript_symbols_imports_and_tests() -> None:
    first = scan_repository(TYPESCRIPT_FIXTURE, ProjectConfig(git_history_limit=0))
    second = scan_repository(TYPESCRIPT_FIXTURE, ProjectConfig(git_history_limit=0))

    assert first.to_dict()["nodes"] == second.to_dict()["nodes"]
    assert first.to_dict()["edges"] == second.to_dict()["edges"]
    for node_id in (
        "symbol:src/math.ts::Calculator",
        "symbol:src/math.ts::Numeric",
        "symbol:src/math.ts::Operation",
        "symbol:src/math.ts::add",
        "symbol:src/components/index.ts::Card",
        "symbol:src/main.ts::boot",
        "symbol:src/card.tsx::CardView",
        "symbol:src/view.jsx::View",
        "symbol:src/comments.ts::VisibleShape",
        "symbol:src/multiline.ts::createCard",
        "symbol:src/dynamic.ts::loadMath",
    ):
        assert node_id in first.nodes
    assert "symbol:src/comments.ts::Phantom" not in first.nodes
    assert "symbol:src/comments.ts::TemplatePhantom" not in first.nodes
    assert "symbol:src/comments.ts::StringPhantom" not in first.nodes
    assert first.nodes["file:src/main.test.ts"].kind == "test"
    assert first.nodes["file:src/main.test.ts"].metadata["language"] == "TypeScript"
    assert first.nodes["file:src/view.jsx"].metadata["language"] == "JavaScript"

    relationships = {
        (edge.source, edge.target, edge.relation, edge.evidence) for edge in first.edges
    }
    assert (
        "file:src/main.ts",
        "file:src/math.ts",
        "imports",
        "javascript-structural",
    ) in relationships
    assert (
        "file:src/main.ts",
        "file:src/components/index.ts",
        "imports",
        "javascript-structural",
    ) in relationships
    assert (
        "file:src/legacy.js",
        "file:src/math.ts",
        "imports",
        "javascript-structural",
    ) in relationships
    assert (
        "file:src/multiline.ts",
        "file:src/components/index.ts",
        "imports",
        "javascript-structural",
    ) in relationships
    assert (
        "file:src/main.test.ts",
        "file:src/main.ts",
        "tests",
        "javascript-structural",
    ) in relationships
    assert (
        "file:src/main.test.ts",
        "symbol:src/main.ts::boot",
        "tests",
        "javascript-symbol-reference",
    ) in relationships
    assert (
        "file:src/main.ts",
        "symbol:src/math.ts::add",
        "imports",
        "javascript-symbol-reference",
    ) in relationships
    assert (
        "file:src/math.test.ts",
        "file:src/math.ts",
        "tests",
        "filename-convention",
    ) in relationships
    assert not any(
        edge.source == "file:src/main.ts" and edge.target == "file:src/react.ts"
        for edge in first.edges
    )
    assert not any(
        edge.source == "file:src/escape.ts" and edge.target == "file:outside.ts"
        for edge in first.edges
    )
    assert not any(
        edge.source == "file:src/ambiguous.ts"
        and edge.target in {"file:src/dual.ts", "file:src/dual.js"}
        for edge in first.edges
    )
    assert not any(
        edge.source == "file:src/dynamic.ts" and edge.relation in {"imports", "tests"}
        for edge in first.edges
    )

    calculator = recommend_tests(first, "symbol:src/math.ts::Calculator")
    assert [item.test.id for item in calculator.recommendations] == [
        "file:src/main.test.ts"
    ]
    assert calculator.recommendations[0].score == 65
    assert all(
        item.test.id != "file:src/math.test.ts"
        for item in calculator.recommendations
    )


def test_scanner_resolves_python_reexports_to_exact_symbols(tmp_path) -> None:
    (tmp_path / "src" / "sample").mkdir(parents=True)
    (tmp_path / "tests").mkdir()
    (tmp_path / "src" / "sample" / "__init__.py").write_text(
        "from .core import Context as Context\n", encoding="utf-8"
    )
    (tmp_path / "src" / "sample" / "core.py").write_text(
        "class Context:\n    def close(self):\n        return None\n",
        encoding="utf-8",
    )
    (tmp_path / "tests" / "test_context.py").write_text(
        "import sample\nfrom sample import Context\n\ndef test_context():\n"
        "    assert sample.Context is Context\n",
        encoding="utf-8",
    )

    graph = scan_repository(tmp_path, ProjectConfig(git_history_limit=0))
    relationships = {
        (edge.source, edge.target, edge.relation, edge.evidence) for edge in graph.edges
    }

    assert (
        "file:tests/test_context.py",
        "symbol:src/sample/core.py::Context",
        "tests",
        "python-symbol-reference",
    ) in relationships


def test_python_adapter_abstains_when_root_and_src_modules_collide(tmp_path) -> None:
    (tmp_path / "pkg").mkdir()
    (tmp_path / "src" / "pkg").mkdir(parents=True)
    (tmp_path / "tests").mkdir()
    (tmp_path / "pkg" / "a.py").write_text("class Target:\n    pass\n", encoding="utf-8")
    (tmp_path / "src" / "pkg" / "a.py").write_text(
        "class Target:\n    pass\n", encoding="utf-8"
    )
    (tmp_path / "pkg" / "__init__.py").write_text(
        "from .a import Target as Target\n", encoding="utf-8"
    )
    (tmp_path / "src" / "pkg" / "__init__.py").write_text(
        "from .a import Target as Target\n", encoding="utf-8"
    )
    (tmp_path / "tests" / "test_imports.py").write_text(
        "from pkg import Target as Exported\nfrom pkg.a import Target\n\n"
        "def test_target():\n    assert Target is Exported\n",
        encoding="utf-8",
    )

    first = scan_repository(tmp_path, ProjectConfig(git_history_limit=0))
    second = scan_repository(tmp_path, ProjectConfig(git_history_limit=0))
    ambiguous_targets = {
        "file:pkg/__init__.py",
        "file:pkg/a.py",
        "file:src/pkg/__init__.py",
        "file:src/pkg/a.py",
        "symbol:pkg/a.py::Target",
        "symbol:src/pkg/a.py::Target",
    }

    assert not any(
        edge.source == "file:tests/test_imports.py"
        and edge.target in ambiguous_targets
        and edge.evidence in {"python-ast", "python-symbol-reference"}
        for edge in first.edges
    )
    assert first.to_dict()["nodes"] == second.to_dict()["nodes"]
    assert first.to_dict()["edges"] == second.to_dict()["edges"]


@pytest.mark.parametrize(
    "package_source",
    [
        "class Target:\n    pass\nfrom .core import Target\n",
        "from .core import Target\nclass Target:\n    pass\n",
    ],
)
def test_python_adapter_abstains_on_direct_and_reexport_binding_collision(
    tmp_path, package_source
) -> None:
    (tmp_path / "src" / "sample").mkdir(parents=True)
    (tmp_path / "tests").mkdir()
    (tmp_path / "src" / "sample" / "__init__.py").write_text(
        package_source, encoding="utf-8"
    )
    (tmp_path / "src" / "sample" / "core.py").write_text(
        "class Target:\n    pass\n", encoding="utf-8"
    )
    (tmp_path / "tests" / "test_target.py").write_text(
        "from sample import Target\n\ndef test_target():\n    assert Target\n",
        encoding="utf-8",
    )

    graph = scan_repository(tmp_path, ProjectConfig(git_history_limit=0))

    assert not any(
        edge.source == "file:tests/test_target.py"
        and edge.target
        in {
            "symbol:src/sample/__init__.py::Target",
            "symbol:src/sample/core.py::Target",
        }
        and edge.evidence == "python-symbol-reference"
        for edge in graph.edges
    )


def test_python_adapter_resolves_unique_namespace_modules_across_root_and_src(
    tmp_path,
) -> None:
    (tmp_path / "ns").mkdir()
    (tmp_path / "src" / "ns").mkdir(parents=True)
    (tmp_path / "tests").mkdir()
    (tmp_path / "ns" / "alpha.py").write_text(
        "class Alpha:\n    pass\n", encoding="utf-8"
    )
    (tmp_path / "src" / "ns" / "beta.py").write_text(
        "class Beta:\n    pass\n", encoding="utf-8"
    )
    (tmp_path / "tests" / "test_namespace.py").write_text(
        "from ns.alpha import Alpha\nfrom ns.beta import Beta\n\n"
        "def test_namespace():\n    assert Alpha and Beta\n",
        encoding="utf-8",
    )

    graph = scan_repository(tmp_path, ProjectConfig(git_history_limit=0))
    relationships = {
        (edge.source, edge.target, edge.relation, edge.evidence) for edge in graph.edges
    }

    assert (
        "file:tests/test_namespace.py",
        "symbol:ns/alpha.py::Alpha",
        "tests",
        "python-symbol-reference",
    ) in relationships
    assert (
        "file:tests/test_namespace.py",
        "symbol:src/ns/beta.py::Beta",
        "tests",
        "python-symbol-reference",
    ) in relationships


def test_python_adapter_does_not_guess_nested_monorepo_source_roots(tmp_path) -> None:
    first = tmp_path / "apps" / "one" / "src" / "shared" / "api.py"
    second = tmp_path / "apps" / "two" / "src" / "shared" / "api.py"
    test = tmp_path / "tests" / "test_api.py"
    first.parent.mkdir(parents=True)
    second.parent.mkdir(parents=True)
    test.parent.mkdir()
    first.write_text("class Target:\n    pass\n", encoding="utf-8")
    second.write_text("class Target:\n    pass\n", encoding="utf-8")
    test.write_text(
        "from shared.api import Target\n\ndef test_target():\n    assert Target\n",
        encoding="utf-8",
    )

    graph = scan_repository(tmp_path, ProjectConfig(git_history_limit=0))

    assert not any(
        edge.source == "file:tests/test_api.py"
        and edge.target
        in {
            "file:apps/one/src/shared/api.py",
            "file:apps/two/src/shared/api.py",
            "symbol:apps/one/src/shared/api.py::Target",
            "symbol:apps/two/src/shared/api.py::Target",
        }
        for edge in graph.edges
    )


def test_scanner_recognizes_root_test_javascript_file(tmp_path) -> None:
    (tmp_path / "index.js").write_text(
        "export default function value() { return 1; }\n",
        encoding="utf-8",
    )
    (tmp_path / "test.js").write_text(
        "import value from './index.js';\nvalue();\n",
        encoding="utf-8",
    )

    graph = scan_repository(tmp_path, ProjectConfig(git_history_limit=0))

    assert graph.nodes["file:test.js"].kind == "test"
    assert any(
        edge.source == "file:test.js"
        and edge.target == "file:index.js"
        and edge.relation == "tests"
        and edge.evidence == "javascript-structural"
        for edge in graph.edges
    )


def test_scanner_connects_go_symbols_local_imports_and_tests() -> None:
    first = scan_repository(GO_FIXTURE, ProjectConfig(git_history_limit=0))
    second = scan_repository(GO_FIXTURE, ProjectConfig(git_history_limit=0))

    assert first.to_dict()["nodes"] == second.to_dict()["nodes"]
    assert first.to_dict()["edges"] == second.to_dict()["edges"]
    for node_id in (
        "symbol:internal/math/add.go::Calculator",
        "symbol:internal/math/add.go::Calculator.Sum",
        "symbol:internal/math/add.go::Number",
        "symbol:internal/math/add.go::Operation",
        "symbol:internal/math/add.go::Add",
        "symbol:cmd/app/main.go::main",
        "symbol:internal/math/add_test.go::TestAdd",
    ):
        assert node_id in first.nodes
    assert "symbol:internal/math/comments.go::Phantom" not in first.nodes
    assert "symbol:internal/math/comments.go::RawPhantom" not in first.nodes
    assert first.nodes["file:go.mod"].kind == "config"
    assert first.nodes["file:go.mod"].metadata["language"] == "Go Modules"
    assert first.nodes["file:internal/math/add_test.go"].kind == "test"
    assert first.nodes["file:internal/math/add.go"].metadata["language"] == "Go"

    relationships = {
        (edge.source, edge.target, edge.relation, edge.evidence) for edge in first.edges
    }
    assert (
        "file:cmd/app/main.go",
        "file:internal/math/add.go",
        "imports",
        "go-structural",
    ) in relationships
    assert (
        "file:cmd/app/main.go",
        "file:internal/math/comments.go",
        "imports",
        "go-structural",
    ) in relationships
    assert (
        "file:internal/math/integration_test.go",
        "file:internal/math/add.go",
        "tests",
        "go-symbol-reference",
    ) in relationships
    assert not any(
        edge.source == "file:internal/math/integration_test.go"
        and edge.target == "file:internal/math/comments.go"
        for edge in first.edges
    )
    assert (
        "file:internal/math/add_test.go",
        "file:internal/math/add.go",
        "tests",
        "go-symbol-reference",
    ) in relationships
    assert (
        "file:internal/math/add_test.go",
        "file:internal/math/add.go",
        "tests",
        "filename-convention",
    ) in relationships
    assert not any(
        edge.source == "file:cmd/app/external_fixture.go"
        and edge.target == "file:third_party/external.go"
        for edge in first.edges
    )
    assert (
        "file:cmd/app/main.go",
        "file:submodule/worker/worker.go",
        "imports",
        "go-structural",
    ) in relationships
    assert not any(
        edge.source == "file:internal/math/comments.go"
        and edge.target == "file:submodule/worker/worker.go"
        for edge in first.edges
    )
    recommendations = recommend_tests(first, "file:internal/math/add.go")
    add_test = next(
        item
        for item in recommendations.recommendations
        if item.test.id == "file:internal/math/add_test.go"
    )
    assert (add_test.score, add_test.confidence) == (65, "medium")
    assert "go-symbol-reference" in add_test.reasons[0].evidence

    calculator = recommend_tests(first, "symbol:internal/math/add.go::Calculator")
    assert calculator.recommendations == ()

    exact_add = recommend_tests(first, "symbol:internal/math/add.go::Add")
    assert {
        (item.test.id, item.score) for item in exact_add.recommendations
    } == {
        ("file:internal/math/add_test.go", 80),
        ("file:internal/math/integration_test.go", 80),
    }
    assert all(
        reason.path.nodes[-2] == "symbol:internal/math/add.go::Add"
        for item in exact_add.recommendations
        for reason in item.reasons
    )


def test_go_recommendations_follow_one_exact_intra_package_caller(tmp_path) -> None:
    (tmp_path / "go.mod").write_text("module example.com/calls\n", encoding="utf-8")
    (tmp_path / "service.go").write_text(
        "package calls\n\n"
        "func hidden() int { return 1 }\n\n"
        "func Public() int { return hidden() }\n",
        encoding="utf-8",
    )
    (tmp_path / "service_test.go").write_text(
        "package calls\n\n"
        "import \"testing\"\n\n"
        "func TestPublic(t *testing.T) {\n"
        "\tif Public() != 1 { t.Fatal(\"unexpected\") }\n"
        "}\n",
        encoding="utf-8",
    )

    graph = scan_repository(tmp_path, ProjectConfig(git_history_limit=0))

    assert any(
        edge.source == "symbol:service.go::Public"
        and edge.target == "symbol:service.go::hidden"
        and edge.relation == "calls"
        and edge.evidence == "go-call-reference"
        for edge in graph.edges
    )
    result = recommend_tests(graph, "symbol:service.go::hidden")
    assert [(item.test.id, item.score) for item in result.recommendations] == [
        ("file:service_test.go", 65)
    ]
    reason = result.recommendations[0].reasons[0]
    assert reason.signal == "direct-symbol-caller-test"
    assert reason.path.relations[-2:] == ("called-by", "tested-by")


@pytest.mark.skipif(shutil.which("git") is None, reason="Git is required")
def test_scanner_maps_git_hunks_only_to_exact_python_symbols(tmp_path) -> None:
    def git(*arguments: str) -> str:
        result = subprocess.run(
            ["git", *arguments],
            cwd=tmp_path,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return result.stdout.strip()

    (tmp_path / "src").mkdir()
    auth = tmp_path / "src" / "auth.py"
    javascript = tmp_path / "src" / "app.js"
    auth.write_text(
        "class Auth:\n"
        "    def requirement_nine(self):\n"
        "        return 'old'\n\n"
        "    def requirement_eighteen(self):\n"
        "        return 'stable'\n",
        encoding="utf-8",
    )
    javascript.write_text("export function run() { return 1; }\n", encoding="utf-8")
    git("init", "-q")
    git("config", "user.name", "IntentAtlas Test")
    git("config", "user.email", "intentatlas-test@example.invalid")
    git("add", "src/auth.py", "src/app.js")
    git("commit", "-q", "-m", "initial")

    auth.write_text(
        "class Auth:\n"
        "    def requirement_nine(self):\n"
        "        return 'new'\n\n"
        "    def requirement_eighteen(self):\n"
        "        return 'stable'\n",
        encoding="utf-8",
    )
    git("add", "src/auth.py")
    git("commit", "-q", "-m", "change one Python symbol")
    python_commit = git("rev-parse", "HEAD")

    javascript.write_text("export function run() { return 2; }\n", encoding="utf-8")
    git("add", "src/app.js")
    git("commit", "-q", "-m", "change JavaScript without spans")
    javascript_commit = git("rev-parse", "HEAD")

    graph = scan_repository(tmp_path, ProjectConfig(git_history_limit=3))
    relationships = {
        (edge.source, edge.target, edge.relation, edge.evidence) for edge in graph.edges
    }

    assert (
        f"commit:{python_commit}",
        "symbol:src/auth.py::Auth.requirement_nine",
        "modifies",
        "git-diff-hunk",
    ) in relationships
    assert not any(
        source == f"commit:{python_commit}"
        and target
        in {
            "symbol:src/auth.py::Auth",
            "symbol:src/auth.py::Auth.requirement_eighteen",
        }
        and relation == "modifies"
        for source, target, relation, _evidence in relationships
    )
    assert (
        f"commit:{python_commit}",
        "file:src/auth.py",
        "changes",
        "git-log",
    ) in relationships
    assert (
        f"commit:{javascript_commit}",
        "file:src/app.js",
        "changes",
        "git-log",
    ) in relationships
    assert not any(
        source == f"commit:{javascript_commit}" and relation == "modifies"
        for source, _target, relation, _evidence in relationships
    )

    auth.write_text(
        "class Auth:\n"
        "    def requirement_nine(self):\n"
        "        return 'new'\n\n"
        "    def requirement_eighteen(self):\n"
        "        return 'changed later'\n",
        encoding="utf-8",
    )
    git("add", "src/auth.py")
    git("commit", "-q", "-m", "change the sibling later")
    later_commit = git("rev-parse", "HEAD")

    later_graph = scan_repository(tmp_path, ProjectConfig(git_history_limit=4))
    later_relationships = {
        (edge.source, edge.target, edge.relation, edge.evidence)
        for edge in later_graph.edges
    }
    assert not any(
        source == f"commit:{python_commit}" and relation == "modifies"
        for source, _target, relation, _evidence in later_relationships
    )
    assert (
        f"commit:{later_commit}",
        "symbol:src/auth.py::Auth.requirement_eighteen",
        "modifies",
        "git-diff-hunk",
    ) in later_relationships
    assert not any(
        source == f"commit:{later_commit}"
        and target
        in {
            "symbol:src/auth.py::Auth",
            "symbol:src/auth.py::Auth.requirement_nine",
        }
        and relation == "modifies"
        for source, target, relation, _evidence in later_relationships
    )


def test_scanner_reads_user_vault_links_without_enumerating_private(
    tmp_path, monkeypatch
) -> None:
    build_python_project(tmp_path)
    config = ProjectConfig(git_history_limit=0)
    vault = ProjectVault(config.vault_path(tmp_path))
    vault.initialize()
    requirement = config.vault_path(tmp_path) / "Requirements" / "REQ-001.md"
    requirement.write_text(
        "---\nid: REQ-001\ntype: requirement\nstatus: accepted\n---\n"
        "# Test requirement\n\nReferences [[Decisions/ADR-001]].\n",
        encoding="utf-8",
    )
    decision = config.vault_path(tmp_path) / "Decisions" / "ADR-001.md"
    decision.write_text(
        "---\nid: ADR-001\ntype: decision\nstatus: accepted\n---\n"
        "# Test decision\n\nSupports [[Requirements/REQ-001]].\n",
        encoding="utf-8",
    )
    private = config.vault_path(tmp_path) / "Private" / "secret.md"
    private.parent.mkdir()
    private.write_text("password=hunter2", encoding="utf-8")

    original_scandir = os.scandir
    private_root = private.parent.resolve()

    def guarded_scandir(path):
        candidate = Path(path).resolve()
        if candidate == private_root or private_root in candidate.parents:
            raise AssertionError("scanner enumerated atlas/Private")
        return original_scandir(path)

    monkeypatch.setattr(scanner_module.os, "scandir", guarded_scandir)

    graph = scan_repository(tmp_path, config)
    assert "REQ-001" in graph.nodes
    assert "ADR-001" in graph.nodes
    assert all("secret" not in node.id.casefold() for node in graph.nodes.values())
    assert any(
        edge.source == "REQ-001" and edge.target == "ADR-001" and edge.relation == "references"
        for edge in graph.edges
    )


def test_scanner_prunes_literal_private_boundary_with_custom_vault_and_excludes(
    tmp_path, monkeypatch
) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("value = 1\n", encoding="utf-8")
    private_root = tmp_path / "atlas" / "Private"
    private_root.mkdir(parents=True)
    (private_root / "secret.py").write_text("password = 'hidden'\n", encoding="utf-8")
    original_scandir = os.scandir
    blocked = private_root.resolve()

    def guarded_scandir(path):
        candidate = Path(path).resolve()
        if candidate == blocked or blocked in candidate.parents:
            raise AssertionError("scanner enumerated literal atlas/Private")
        return original_scandir(path)

    monkeypatch.setattr(scanner_module.os, "scandir", guarded_scandir)
    graph = scan_repository(
        tmp_path,
        ProjectConfig(vault="project-vault", exclude=[], git_history_limit=0),
    )

    assert "file:src/app.py" in graph.nodes
    assert "file:atlas/Private/secret.py" not in graph.nodes


def test_scanner_prunes_configured_nested_excludes_before_descent(tmp_path, monkeypatch) -> None:
    (tmp_path / "vendor" / "generated").mkdir(parents=True)
    (tmp_path / "vendor" / "keep.py").write_text("value = 1\n", encoding="utf-8")
    (tmp_path / "vendor" / "generated" / "secret.py").write_text(
        "password = 'do-not-read'\n", encoding="utf-8"
    )
    blocked = (tmp_path / "vendor" / "generated").resolve()
    original_scandir = os.scandir

    def guarded_scandir(path):
        candidate = Path(path).resolve()
        if candidate == blocked or blocked in candidate.parents:
            raise AssertionError("scanner descended into configured exclude")
        return original_scandir(path)

    monkeypatch.setattr(scanner_module.os, "scandir", guarded_scandir)
    config = ProjectConfig(exclude=["vendor/generated"], git_history_limit=0)
    graph = scan_repository(tmp_path, config)

    assert "file:vendor/keep.py" in graph.nodes
    assert "file:vendor/generated/secret.py" not in graph.nodes


def test_scanner_rejects_reserved_user_note_ids(tmp_path) -> None:
    config = ProjectConfig(git_history_limit=0)
    vault = ProjectVault(config.vault_path(tmp_path))
    vault.initialize()
    (config.vault_path(tmp_path) / "Requirements" / "Collision.md").write_text(
        "---\nid: file:README.md\ntype: requirement\n---\n# Collision\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Reserved graph node ID"):
        scan_repository(tmp_path, config)


def test_scanner_only_reads_ids_from_frontmatter(tmp_path) -> None:
    config = ProjectConfig(git_history_limit=0)
    vault = ProjectVault(config.vault_path(tmp_path))
    vault.initialize()
    note = config.vault_path(tmp_path) / "Requirements" / "Body ID.md"
    note.write_text("# Body ID\n\nid: file:README.md\n", encoding="utf-8")
    malformed = config.vault_path(tmp_path) / "Requirements" / "Malformed frontmatter.md"
    malformed.write_text("---\n# Not closed\nid: file:README.md\n", encoding="utf-8")

    graph = scan_repository(tmp_path, config)

    assert "note:Requirements/Body ID" in graph.nodes
    assert "note:Requirements/Malformed frontmatter" in graph.nodes


def test_scanner_preserves_explicit_typed_intent_links(tmp_path) -> None:
    build_python_project(tmp_path)
    config = ProjectConfig(git_history_limit=0)
    vault = ProjectVault(config.vault_path(tmp_path))
    vault.initialize()
    (vault.root / "Requirements" / "REQ-Typed.md").write_text(
        "---\nid: REQ-TYPED\ntype: requirement\n---\n"
        "# Typed requirement\n\n- drives:: [[Decisions/ADR-Typed]]\n"
        "- unknown:: [[Evidence/EVD-Typed]]\n",
        encoding="utf-8",
    )
    (vault.root / "Decisions" / "ADR-Typed.md").write_text(
        "---\nid: ADR-TYPED\ntype: decision\n---\n"
        "# Typed decision\n\n- tracked-by:: [[Issues/ISSUE-Typed]]\n",
        encoding="utf-8",
    )
    (vault.root / "Issues" / "ISSUE-Typed.md").write_text(
        "---\nid: ISSUE-TYPED\ntype: issue\n---\n"
        "# Typed issue\n\n- implemented-by:: [[Code/src - demo - core.py]]\n",
        encoding="utf-8",
    )
    (vault.root / "Evidence" / "EVD-Typed.md").write_text(
        "---\nid: EVD-TYPED\ntype: evidence\n---\n"
        "# Typed evidence\n\n- proves:: [[Requirements/REQ-Typed]]\n"
        "- proves:: [[Tests/tests - test_core.py]]\n",
        encoding="utf-8",
    )

    graph = scan_repository(tmp_path, config)
    assert graph.nodes["ISSUE-TYPED"].kind == "issue"
    relationships = {(edge.source, edge.target, edge.relation) for edge in graph.edges}
    assert ("REQ-TYPED", "ADR-TYPED", "drives") in relationships
    assert ("ADR-TYPED", "ISSUE-TYPED", "tracked-by") in relationships
    assert ("ISSUE-TYPED", "file:src/demo/core.py", "implemented-by") in relationships
    assert ("EVD-TYPED", "REQ-TYPED", "proves") in relationships
    assert ("EVD-TYPED", "file:tests/test_core.py", "proves") in relationships
    assert ("REQ-TYPED", "EVD-TYPED", "references") in relationships
