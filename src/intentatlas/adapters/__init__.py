from .base import AdapterContext, GraphFragment, LanguageAdapter, canonical_graph_fragment
from .conformance import (
    ADAPTER_CONTRACT_VERSION,
    AdapterConformanceError,
    AdapterConformanceReport,
    assert_adapter_conforms,
    validate_adapter_definition,
    validate_adapter_fragment,
)
from .go import GoAdapter
from .javascript import JavaScriptAdapter
from .python import PythonAdapter

BUILTIN_ADAPTERS: tuple[LanguageAdapter, ...] = (
    PythonAdapter(),
    JavaScriptAdapter(),
    GoAdapter(),
)

__all__ = [
    "BUILTIN_ADAPTERS",
    "ADAPTER_CONTRACT_VERSION",
    "AdapterContext",
    "AdapterConformanceError",
    "AdapterConformanceReport",
    "GoAdapter",
    "GraphFragment",
    "JavaScriptAdapter",
    "LanguageAdapter",
    "PythonAdapter",
    "assert_adapter_conforms",
    "canonical_graph_fragment",
    "validate_adapter_definition",
    "validate_adapter_fragment",
]
