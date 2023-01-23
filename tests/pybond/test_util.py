import pytest

import sample_code.my_module as my_module
import sample_code.other_package as other_package
from pybond.util import (
    _args_match,
    function_signatures_match,
)


@pytest.mark.parametrize(
    "f, g, args_matching",
    [
        pytest.param(lambda: None, lambda: None, True),
        pytest.param(lambda _: None, lambda: None, False),
        pytest.param(lambda: None, lambda _: None, False),
        pytest.param(lambda _: None, lambda _: None, True),
        pytest.param(lambda _a, _b: None, lambda _a: None, False),
        pytest.param(lambda _a, _b: None, lambda _c, _d: None, True),
    ],
)
def test_args_match(f, g, args_matching):
    assert function_signatures_match(f, g) == args_matching


@pytest.mark.parametrize(
    "f, g, varargs_matching",
    [
        pytest.param(lambda: None, lambda: None, True),
        pytest.param(lambda _: None, lambda _: None, True),
        pytest.param(lambda _: None, lambda _, *args: None, False),
        pytest.param(lambda _, *args: None, lambda _: None, False),
        pytest.param(lambda _, *args: None, lambda _, *args: None, True),
        pytest.param(lambda _, *name_a: None, lambda _, *name_b: None, True),
    ],
)
def test_varargs_match(f, g, varargs_matching):
    assert function_signatures_match(f, g) == varargs_matching
