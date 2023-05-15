import warnings

from pybond.types import SpyableClass, SpyableFunction
from pybond.util import (
    function_signatures_match,
    is_wrapped_function,
    list_class_attributes,
    list_class_methods,
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


def check_if_function_is_instrumentable(
    original_obj: SpyableFunction,
    stub_obj: SpyableFunction,
    strict: bool = True,
) -> None:
    if strict and not _function_signatures_match(original_obj, stub_obj):
        raise ValueError(
            f"Stub does not match the signature of {original_obj.__name__}."
        )


def _check_if_class_methods_are_instrumentable(
    method_names: list[str],
    original_obj: SpyableClass,
    stub_obj: SpyableClass,
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


def check_if_class_is_instrumentable(
    original_obj: SpyableClass,
    stub_obj: SpyableClass,
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
