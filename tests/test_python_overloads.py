from __future__ import annotations

from pathlib import Path
from types import MappingProxyType

from intentatlas.adapters import AdapterContext, PythonAdapter
from intentatlas.change_analysis import _exact_symbols
from intentatlas.change_set import ChangeFile, DiffHunk
from intentatlas.graph import AtlasGraph
from intentatlas.models import Edge, Node


def test_python_adapter_keeps_overload_implementations_and_abstains_on_duplicates(
    tmp_path: Path,
) -> None:
    source = (
        "from typing import overload as typed_overload\n"
        "import typing as type_api\n"
        "from typing_extensions import overload as extension_overload\n\n"
        "def unrelated(typed_overload):\n"
        "    return typed_overload\n\n"
        "@typed_overload\n"
        "def parse(value: int) -> int: ...\n\n"
        "@typed_overload\n"
        "def parse(value: str) -> str: ...\n\n"
        "def parse(value):\n"
        "    return value\n\n"
        "class Store:\n"
        "    @type_api.overload\n"
        "    def get(self, key: int) -> int: ...\n\n"
        "    @type_api.overload\n"
        "    def get(self, key: str) -> str: ...\n\n"
        "    def get(self, key):\n"
        "        return key\n\n"
        "@extension_overload\n"
        "def convert(value: bytes) -> str: ...\n\n"
        "def convert(value):\n"
        "    return str(value)\n\n"
        "def ambiguous():\n"
        "    return 1\n\n"
        "def ambiguous():\n"
        "    return 2\n\n"
        "@typed_overload\n"
        "def declaration_only(value: int) -> int: ...\n\n"
        "@typed_overload\n"
        "def declaration_only(value: str) -> str: ...\n"
    )
    path = tmp_path / "service.py"
    path.write_text(source, encoding="utf-8")
    consumer = tmp_path / "consumer.py"
    consumer.write_text("from service import parse\n", encoding="utf-8")
    context = AdapterContext(
        files=MappingProxyType({"consumer.py": consumer, "service.py": path}),
        kinds=MappingProxyType({"consumer.py": "file", "service.py": "file"}),
        max_parse_bytes=10_000,
        workspace_owners=MappingProxyType(
            {"consumer.py": ("root",), "service.py": ("root",)}
        ),
        source_roots=MappingProxyType({"root": ("",)}),
    )

    fragment = PythonAdapter().scan(context)
    assert fragment == PythonAdapter().scan(context)
    symbols = {node.id: node for node in fragment.nodes}

    assert set(symbols) == {
        "symbol:service.py::Store",
        "symbol:service.py::Store.get",
        "symbol:service.py::convert",
        "symbol:service.py::parse",
        "symbol:service.py::unrelated",
    }
    lines = source.splitlines()
    assert symbols["symbol:service.py::parse"].metadata["line"] == lines.index(
        "def parse(value):"
    ) + 1
    assert symbols["symbol:service.py::Store.get"].metadata["line"] == lines.index(
        "    def get(self, key):"
    ) + 1
    assert symbols["symbol:service.py::convert"].metadata["line"] == lines.index(
        "def convert(value):"
    ) + 1
    assert "symbol:service.py::ambiguous" not in symbols
    assert "symbol:service.py::declaration_only" not in symbols
    assert (
        "file:consumer.py",
        "symbol:service.py::parse",
        "imports",
        "python-symbol-reference",
    ) in {
        (edge.source, edge.target, edge.relation, edge.evidence)
        for edge in fragment.edges
    }


def test_python_adapter_abstains_if_overloads_have_multiple_implementations(
    tmp_path: Path,
) -> None:
    sources = {
        "ambiguous.py": (
            "from typing import overload\n\n"
            "@overload\n"
            "def resolve(value: int) -> int: ...\n\n"
            "def resolve(value):\n"
            "    return value\n\n"
            "def resolve(value):\n"
            "    return value\n"
        ),
        "conditional.py": (
            "from typing import overload\n\n"
            "@overload\n"
            "def platform(value: int) -> int: ...\n\n"
            "if ENABLED:\n"
            "    def platform(value):\n"
            "        return value\n"
        ),
        "shadowed.py": (
            "from typing import overload\n"
            "overload = custom_overload\n\n"
            "@overload\n"
            "def shadowed(value: int) -> int: ...\n\n"
            "def shadowed(value):\n"
            "    return value\n"
        ),
        "parents.py": (
            "class Duplicate:\n"
            "    def first(self):\n"
            "        return 1\n\n"
            "class Duplicate:\n"
            "    def second(self):\n"
            "        return 2\n"
        ),
    }
    files = {}
    for relative, source in sources.items():
        path = tmp_path / relative
        path.write_text(source, encoding="utf-8")
        files[relative] = path
    fragment = PythonAdapter().scan(
        AdapterContext(
            files=MappingProxyType(files),
            kinds=MappingProxyType({relative: "file" for relative in files}),
            max_parse_bytes=10_000,
        )
    )

    symbol_ids = {node.id for node in fragment.nodes}
    assert "symbol:ambiguous.py::resolve" not in symbol_ids
    assert "symbol:conditional.py::platform" not in symbol_ids
    assert "symbol:shadowed.py::shadowed" not in symbol_ids
    assert not any(node_id.startswith("symbol:parents.py::Duplicate") for node_id in symbol_ids)


def test_overload_implementation_span_keeps_change_analysis_completeness_honest(
    tmp_path: Path,
) -> None:
    source = (
        "from typing import overload\n\n"
        "@overload\n"
        "def parse(value: int) -> int: ...\n\n"
        "@overload\n"
        "def parse(value: str) -> str: ...\n\n"
        "def parse(value):\n"
        "    return value\n"
    )
    path = tmp_path / "service.py"
    path.write_text(source, encoding="utf-8")
    fragment = PythonAdapter().scan(
        AdapterContext(
            files=MappingProxyType({"service.py": path}),
            kinds=MappingProxyType({"service.py": "file"}),
            max_parse_bytes=10_000,
        )
    )
    file_node = Node("file:service.py", "file", "service.py", path="service.py")
    graph = AtlasGraph()
    graph.extend(
        [file_node, *fragment.nodes],
        [Edge(file_node.id, node.id, "defines", "python-ast") for node in fragment.nodes],
    )
    lines = source.splitlines()
    declaration_line = lines.index("def parse(value: int) -> int: ...") + 1
    implementation_line = lines.index("def parse(value):") + 1

    exact = _exact_symbols(
        graph,
        file_node,
        ChangeFile(
            "modified",
            "service.py",
            hunks=(DiffHunk("service.py", implementation_line, 1),),
        ),
    )
    declaration_only = _exact_symbols(
        graph,
        file_node,
        ChangeFile(
            "modified",
            "service.py",
            hunks=(DiffHunk("service.py", declaration_line, 1),),
        ),
    )
    partial = _exact_symbols(
        graph,
        file_node,
        ChangeFile(
            "modified",
            "service.py",
            hunks=(
                DiffHunk("service.py", declaration_line, 1),
                DiffHunk("service.py", implementation_line, 1),
            ),
        ),
    )

    assert exact == (("symbol:service.py::parse",), True)
    assert declaration_only == ((), False)
    assert partial == (("symbol:service.py::parse",), False)
