from .base import AdapterContext, GraphFragment, LanguageAdapter
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
    "AdapterContext",
    "GoAdapter",
    "GraphFragment",
    "JavaScriptAdapter",
    "LanguageAdapter",
    "PythonAdapter",
]
