"""This module is inspired by clojure's bond library."""

import sys
from contextlib import contextmanager
from copy import deepcopy
from functools import wraps
from inspect import isclass
from typing import Any, Callable

from pytest import MonkeyPatch

from pybond.util import function_signatures_match


def _function_call(args, kwargs, error, return_value):
    return {
        "args": args,
        "kwargs": kwargs,
        "error": error,
        "return": return_value,
    }


def _spy(f: Callable):
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
    handle_function_call.calls = calls
    return handle_function_call


def calls(f: Callable) -> list[dict[str, Any]]:
    """
    Takes one arg, a function that has previously been spied. Returns a list of
    FunctionCall objects, one per call. Each object contains the keys `args`,
    `kwargs`, `error` and `return_value`.

    If the function has not been spied, raises an exception.
    """
    try:
        function_calls = f.calls()
        return function_calls
    except Exception:
        raise ValueError(
            "The argument is not a spied function. Calls of an unspied "
            "function are not tracked and are therefore not known."
        )


@contextmanager
def stub(*targets, check_function_signatures=True):
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
            for module, fname, stubf in targets:
                originalf = getattr(module, fname)
                # Don't bother checking classes, only check functions
                if check_function_signatures and not isclass(originalf):
                    if not function_signatures_match(originalf, stubf):
                        raise ValueError(
                            f"Stub does not match the signature of {fname}."
                        )
                m.setattr(target=module, name=fname, value=_spy(stubf))
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
        *[[m, fname, _spy(getattr(m, fname))] for m, fname in targets],
        check_function_signatures=False,
    ):
        yield
