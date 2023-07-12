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

Spyable: TypeAlias = Callable | Any
SpyTarget: TypeAlias = Spyable
StubTarget: TypeAlias = Tuple[Spyable, Spyable]
