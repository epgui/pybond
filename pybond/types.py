from types import ModuleType
from typing import Any, Callable, Tuple, TypeAlias, TypedDict

FunctionCall = TypedDict(
    "FunctionCall",
    {
        "args": list[Any],
        "kwargs": dict[str, Any],
        "error": Any,
        "return": Any,
    }
)

SpyableClass: TypeAlias = Any
SpyableFunction: TypeAlias = Callable
Spyable: TypeAlias = SpyableFunction | SpyableClass
SpyTarget: TypeAlias = Tuple[ModuleType, str]
StubTarget: TypeAlias = Tuple[ModuleType, str, Spyable]
