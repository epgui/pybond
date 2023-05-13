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

Spyable = Any
ObjectMap = list[tuple[Spyable, Spyable]]


def _function_call(args, kwargs, error, return_value) -> dict:
    return {
        "args": args,
        "kwargs": kwargs,
        "error": error,
        "return": return_value,
    }


def _spy_function(f: Callable) -> Callable:
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
        non_mutated_args = deepcopy(list(args)) if args else None
        non_mutated_kwargs = deepcopy(dict(kwargs)) if kwargs else None
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


def calls(f: Callable) -> list[dict[str, Any]]:
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


def _function_signatures_match(originalf: Spyable, stubf: Spyable) -> bool:
    """
    Supports both regular functions and decorated functions using
    functools.wraps
    """
    return (
        (
            is_wrapped_function(originalf)
            and function_signatures_match(originalf.__wrapped__, stubf)
        ) or (
            not is_wrapped_function(originalf)
            and function_signatures_match(originalf, stubf)
        )
    )


def _check_if_class_is_instrumentable(original_obj, stub_obj, strict):
    # TODO: implement spying on classes and class methods
    return


def _check_if_function_is_instrumentable(original_obj, stub_obj, strict=True):
    if strict and not _function_signatures_match(original_obj, stub_obj):
        raise ValueError(
            f"Stub does not match the signature of {original_obj.__name__}."
        )


def _instrumented_obj(original_obj, stub_obj, strict=True):
    if isclass(original_obj):
        # TODO: implement spying on classes and class methods
        _check_if_class_is_instrumentable(original_obj, stub_obj, strict)
        return stub_obj
    elif callable(original_obj):
        _check_if_function_is_instrumentable(original_obj, stub_obj, strict)
        return _spy_function(stub_obj)
    else:
        raise ValueError(
            f"Object of type {type(original_obj)} is not supported by pybond."
        )


@contextmanager
def stub(*targets, strict=True):
    """
    Context manager which takes a list of targets to stub and spy on.

    Example usage:

    ```
    import my_module

    with stub([my_module, "test_function", lambda x: 42]):
        assert my_module.test_function("abc") == 42  # True
        function_calls = calls(my_module.test_function)
    ```
    """
    with MonkeyPatch.context() as m:
        try:
            for module, obj_name, stub_obj in targets:
                original_obj = getattr(module, obj_name)
                new_obj = _instrumented_obj(original_obj, stub_obj, strict)

                # The following only covers imports in the form:
                #     `import some_module`
                m.setattr(target=module, name=obj_name, value=new_obj)

                # The following covers bound imports in the form:
                #     `from some_module import some_object`
                replace_bound_references_in_memory(m, original_obj, new_obj)

            yield
        except Exception:
            raise


@contextmanager
def spy(*targets):
    """
    Context manager which takes a list of targets to spy on.

    Example usage:

    ```
    import my_module
    with spy([my_module, "test_function"]):
        my_module.test_function("abc")
        function_calls = calls(my_module.test_function)
    ```
    """
    with stub(
        *[[m, fname, _spy_function(getattr(m, fname))] for m, fname in targets],
        strict=False,
    ):
        yield
