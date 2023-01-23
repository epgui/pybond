import builtins
import pytest
import time

from pybond.util import _fn_with_zero_arguments, function_signatures_match


@pytest.mark.parametrize(
    "f, g, args_matching",
    [
        pytest.param(
            lambda: None,
            lambda: None,
            True,
        ),
        pytest.param(
            lambda _: None,
            lambda: None,
            False,
        ),
        pytest.param(
            lambda: None,
            lambda _: None,
            False,
        ),
        pytest.param(
            lambda _: None,
            lambda _: None,
            True,
        ),
        pytest.param(
            lambda _a, _b: None,
            lambda _a: None,
            False,
        ),
        pytest.param(
            lambda _a, _b: None,
            lambda _c, _d: None,
            True,
        ),
    ],
)
def test_args_match(f, g, args_matching):
    assert function_signatures_match(f, g) == args_matching


@pytest.mark.parametrize(
    "f, g, varargs_matching",
    [
        pytest.param(
            lambda: None,
            lambda: None,
            True,
        ),
        pytest.param(
            lambda _: None,
            lambda _: None,
            True,
        ),
        pytest.param(
            lambda _: None,
            lambda _, *args: None,
            False,
        ),
        pytest.param(
            lambda _, *args: None,
            lambda _: None,
            False,
        ),
        pytest.param(
            lambda _, *args: None,
            lambda _, *args: None,
            True,
        ),
        pytest.param(
            lambda _, *some_name: None,
            lambda _, *a_different_name: None,
            True,
        ),
    ],
)
def test_varargs_match(f, g, varargs_matching):
    assert function_signatures_match(f, g) == varargs_matching


@pytest.mark.parametrize(
    "f, g, kwargs_matching",
    [
        pytest.param(
            lambda: None,
            lambda: None,
            True,
        ),
        pytest.param(
            lambda *args: None,
            lambda *args: None,
            True,
        ),
        pytest.param(
            lambda *args, a: None,
            lambda *args: None,
            False,
        ),
        pytest.param(
            lambda *args, a=42: None,
            lambda *args: None,
            False,
        ),
        pytest.param(
            lambda *args: None,
            lambda *args, a: None,
            False,
        ),
        pytest.param(
            lambda *args: None,
            lambda *args, a=42: None,
            False,
        ),
        pytest.param(
            lambda *args, a: None,
            lambda *args, a: None,
            True,
        ),
        pytest.param(
            lambda *args, a=42: None,
            lambda *args, a: None,
            False,
        ),
        pytest.param(
            lambda *args, a: None,
            lambda *args, a=42: None,
            False,
        ),
        pytest.param(
            lambda *args, a, b: None,
            lambda *args, a: None,
            False,
        ),
        pytest.param(
            lambda *args, a, b=42: None,
            lambda *args, a: None,
            False,
        ),
        pytest.param(
            lambda *args, a, b: None,
            lambda *args, a, b: None,
            True,
        ),
    ],
)
def test_kwargs_match(f, g, kwargs_matching):
    assert function_signatures_match(f, g) == kwargs_matching


@pytest.mark.parametrize(
    "f, g, varkwargs_matching",
    [
        pytest.param(
            lambda: None,
            lambda: None,
            True,
        ),
        pytest.param(
            lambda: None,
            lambda **kwargs: None,
            False,
        ),
        pytest.param(
            lambda **kwargs: None,
            lambda: None,
            False,
        ),
        pytest.param(
            lambda **kwargs: None,
            lambda **kwargs_but_with_different_name: None,
            True,
        ),
        pytest.param(
            lambda _: None,
            lambda _: None,
            True,
        ),
        pytest.param(
            lambda _: None,
            lambda _, **kwargs: None,
            False,
        ),
        pytest.param(
            lambda _, **kwargs: None,
            lambda _: None,
            False,
        ),
        pytest.param(
            lambda _, **some_name: None,
            lambda _, **a_different_name: None,
            True,
        ),
        pytest.param(
            lambda _, *args: None,
            lambda _, *args: None,
            True,
        ),
        pytest.param(
            lambda _, *args: None,
            lambda _, *args, **kwargs: None,
            False,
        ),
        pytest.param(
            lambda _, *args, **kwargs: None,
            lambda _, *args: None,
            False,
        ),
        pytest.param(
            lambda _, *args, **kwargs: None,
            lambda _, *args, **kwargs: None,
            True,
        ),
        pytest.param(
            lambda _, *args, k: None,
            lambda _, *args, k: None,
            True,
        ),
        pytest.param(
            lambda _, *args, k, **kwargs: None,
            lambda _, *args, k: None,
            False,
        ),
        pytest.param(
            lambda _, *args, k: None,
            lambda _, *args, k, **kwargs: None,
            False,
        ),
        pytest.param(
            lambda _, *args, k, **kwargs: None,
            lambda _, *args, k, **kwargs: None,
            True,
        ),
    ],
)
def test_var_kwargs_match(f, g, varkwargs_matching):
    assert function_signatures_match(f, g) == varkwargs_matching


@pytest.mark.parametrize(
    "f, g, is_special_case",
    [
        pytest.param(time.time, _fn_with_zero_arguments, True),
        pytest.param(builtins.print, lambda: None, False),
    ],
)
def test_function_signatures_match_for_unsupported_callable_special_cases(
    f,
    g,
    is_special_case,
):
    if is_special_case:
        assert function_signatures_match(f, g)
    else:
        with pytest.raises(Exception) as e:
            function_signatures_match(f, g)
        assert e.value.args[0] == "unsupported callable"


def test_executing_model_functions():
    # Execute these functions just to make sure code coverage is exhaustive
    assert _fn_with_zero_arguments() == None
