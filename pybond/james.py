"""This module is inspired by clojure's bond library."""

import sys
from contextlib import contextmanager
from copy import deepcopy
from functools import wraps
from inspect import isclass
from typing import Any, Callable

from pytest import MonkeyPatch

from pybond.memory import replace_bound_references_in_memory
from pybond.util import function_signatures_match, is_wrapped_function
from pybond.types import FunctionCall, Spyable, SpyTarget, StubTarget


def _function_call(args, kwargs, error, return_value) -> FunctionCall:
    return {
        "args": args,
        "kwargs": kwargs,
        "error": error,
        "return": return_value,
    }


def maybe_deepcopy(obj: Any) -> Any:
    try:
        return deepcopy(obj)
    except Exception:
        return obj


def _spy_function(f: Callable) -> Spyable:
    """
    Wrap f, returning a new function that keeps track of its call count and
    arguments.
    """
    _calls = []

    def calls():
        return _calls

    @wraps(f)
    def handle_function_call(*args, **kwargs):
        # Assume the worst: f might mutate its arguments
        non_mutated_args = maybe_deepcopy(list(args)) if args else None
        non_mutated_kwargs = maybe_deepcopy(dict(kwargs)) if kwargs else None
        try:
            return_value = f(*args, **kwargs)
            _calls.append(
                _function_call(
                    args=non_mutated_args,
                    kwargs=non_mutated_kwargs,
                    error=None,
                    return_value=return_value,
                )
            )
            return return_value
        except Exception:
            _calls.append(
                _function_call(
                    args=non_mutated_args,
                    kwargs=non_mutated_kwargs,
                    error=sys.exc_info(),
                    return_value=None,
                )
            )
            raise

    handle_function_call.__wrapped__ = f
    setattr(handle_function_call, "calls", calls)
    return handle_function_call


def calls(f: Spyable) -> list[FunctionCall]:
    """
    Takes one arg, a function that has previously been spied. Returns a list of
    function call dicts, one per call. Each object contains the keys `args`,
    `kwargs`, `error` and `return_value`.

    If the function has not been spied, raises an exception.
    """
    if hasattr(f, "calls") and callable(f):
        return getattr(f, "calls")()
    else:
        raise ValueError(
            "The argument is not a spied function. Calls of an unspied "
            "function are not tracked and are therefore not known."
        )


def _function_signatures_match(originalf: Callable, stubf: Callable) -> bool:
    """
    Supports both regular functions and decorated functions using
    functools.wraps
    """
    return function_signatures_match(
        originalf.__wrapped__ if is_wrapped_function(originalf) else originalf,
        stubf.__wrapped__ if is_wrapped_function(stubf) else stubf
    )


def _check_if_class_is_instrumentable(
    original_obj: Spyable,
    stub_obj: Spyable,
    strict: bool = True,
) -> None:
    # TODO: implement spying on classes and class methods
    return


def _check_if_function_is_instrumentable(
    original_obj: Callable,
    stub_obj: Callable,
    strict: bool = True,
) -> None:
    if strict and not _function_signatures_match(original_obj, stub_obj):
        raise ValueError(
            f"Stub does not match the signature of {original_obj.__name__}."
        )


def _instrumented_obj(
    original_obj: Spyable,
    stub_obj: Spyable,
    strict: bool = True,
) -> Spyable:
    if isclass(original_obj):
        # TODO: implement spying on classes and class methods
        _check_if_class_is_instrumentable(original_obj, stub_obj, strict)
        return stub_obj
    elif callable(original_obj) and callable(stub_obj):
        _check_if_function_is_instrumentable(original_obj, stub_obj, strict)
        return _spy_function(stub_obj)
    elif callable(original_obj) and not callable(stub_obj):
        raise ValueError(
            f"Provided stub for Callable {original_obj.__name__} of type "
            f"{type(stub_obj)} is invalid: pybond expected a Callable type."
        )
    else:
        raise ValueError(
            f"Object of type {type(original_obj)} is not supported by pybond."
        )


@contextmanager
def stub(*targets: StubTarget, strict: bool = True):
    """
    Context manager which takes a list of targets to stub and spy on.

    Example usage:

    ```
    import my_module

    with stub((my_module.test_function, lambda x: 42)):
        assert my_module.test_function("abc") == 42  # True
        function_calls = calls(my_module.test_function)
    ```
    """
    with MonkeyPatch.context() as m:
        try:
            for target, stub_obj in targets:
                new_obj = _instrumented_obj(target, stub_obj, strict)

                # The following only covers imports in the form:
                #     `import some_module`
                m.setattr(
                    target=sys.modules[target.__module__],
                    name=target.__name__,
                    value=new_obj,
                )

                # The following covers bound imports in the form:
                #     `from some_module import some_object`
                replace_bound_references_in_memory(m, target, new_obj)

            yield
        except Exception:
            raise


@contextmanager
def spy(*targets: SpyTarget):
    """
    Context manager which takes a list of targets to spy on.

    Example usage:

    ```
    import my_module
    with spy(my_module.test_function):
        my_module.test_function("abc")
        function_calls = calls(my_module.test_function)
    ```
    """
    with stub(*[(t, t) for t in targets]):
        yield
