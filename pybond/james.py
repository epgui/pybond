"""This module is inspired by clojure's bond library."""

import warnings
from contextlib import contextmanager
from copy import deepcopy
from functools import wraps
from inspect import isclass
from sys import exc_info

from pytest import MonkeyPatch

from pybond.memory import replace_bound_references_in_memory
from pybond.util import (
    function_signatures_match,
    is_wrapped_function,
    list_class_attributes,
    list_class_methods,
)
from pybond.types import (
    FunctionCall,
    Spyable,
    SpyableClass,
    SpyableFunction,
    SpyTarget,
    StubTarget,
)


def _function_call(args, kwargs, error, return_value) -> FunctionCall:
    return {
        "args": args,
        "kwargs": kwargs,
        "error": error,
        "return": return_value,
    }


def _spy_function(f: SpyableFunction) -> Spyable:
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
                    error=exc_info(),
                    return_value=None,
                )
            )
            raise

    handle_function_call.__wrapped__ = f
    setattr(handle_function_call, "calls", calls)
    return handle_function_call


def _spy_all_methods(obj: SpyableClass) -> SpyableClass:
    obj_methods = list_class_methods(obj)
    for method_name in obj_methods:
        setattr(obj, method_name, _spy_function(getattr(obj, method_name)))
    return obj


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


def _function_signatures_match(
    originalf: SpyableFunction,
    stubf: SpyableFunction,
) -> bool:
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


def _check_if_class_methods_are_instrumentable(
    method_names: list[str],
    original_obj: Spyable,
    stub_obj: Spyable,
) -> None:
    unsupported_callables = []
    for method_name in method_names:
        try:
            if not _function_signatures_match(
                getattr(original_obj, method_name),
                getattr(stub_obj, method_name),
            ):
                raise ValueError(
                    f"Stub method {stub_obj.__name__}.{method_name} does not "
                    "match the signature of the original "
                    f"{original_obj.__name__}.{method_name} class method. "
                    "Please ensure the implementation of the provided stub "
                    "matches that of the original class, or set the 'strict' "
                    "option to False."
                )
        except TypeError as e:
            if str(e) == "unsupported callable":
                unsupported_callables.append(method_name)

    if len(unsupported_callables) > 0:
        PYBOND_WARNING__unsupported_callables = (
            "The following methods' signatures cannot be checked: "
            f"{unsupported_callables}."
        )
        warnings.warn(PYBOND_WARNING__unsupported_callables)


def _check_if_class_is_instrumentable(
    original_obj: Spyable,
    stub_obj: Spyable,
    strict: bool = True,
) -> None:
    original_obj_attributes = list_class_attributes(original_obj)
    original_obj_methods = list_class_methods(original_obj)
    stub_obj_attributes = list_class_attributes(stub_obj)
    stub_obj_methods = list_class_methods(stub_obj)
    if strict:
        if set(original_obj_attributes) != set(stub_obj_attributes):
            raise ValueError(
                f"Stub object '{stub_obj.__name__}' does not have the same set "
                f"of attributes as the original '{original_obj.__name__}' "
                "class. Please ensure the implementation of the provided stub "
                "matches that of the original class, or set the 'strict' "
                "option to False.\n"
                f"Original: {original_obj_attributes}\n"
                f"Provided: {stub_obj_attributes}"
            )
        if set(original_obj_methods) != set(stub_obj_methods):
            raise ValueError(
                f"Stub object '{stub_obj.__name__}' does not have the same set "
                f"of methods as the original '{original_obj.__name__}' class. "
                "Please ensure the implementation of the provided stub matches "
                "that of the original class, or set the 'strict' option to "
                "False.\n"
                f"Original: {original_obj_methods}\n"
                f"Provided: {stub_obj_methods}"
            )
        _check_if_class_methods_are_instrumentable(
            method_names=original_obj_methods,
            original_obj=original_obj,
            stub_obj=stub_obj,
        )


def _check_if_function_is_instrumentable(
    original_obj: SpyableFunction,
    stub_obj: SpyableFunction,
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
        _check_if_class_is_instrumentable(original_obj, stub_obj, strict)
        return _spy_all_methods(stub_obj)
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
def spy(*targets: SpyTarget):
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
    with stub(*[(m, n, deepcopy(getattr(m, n))) for m, n in targets]):
        yield
