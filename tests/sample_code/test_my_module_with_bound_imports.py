from pybond import calls, called_with_args, spy, stub, times_called

import sample_code.other_package as other_package
import sample_code.my_module_with_bound_imports as my_module_with_bound_imports
from sample_code.my_module_with_bound_imports import bar
from tests.sample_code.mocks import (
    mock_make_a_network_request,
    mock_write_to_disk,
)


def test_foo_is_called_when_module_uses_bound_imports():
    with spy(my_module_with_bound_imports.foo):
        assert times_called(my_module_with_bound_imports.foo, 0)
        bar(42)
        assert times_called(my_module_with_bound_imports.foo, 1)
        bar(42)
        bar(42)
        assert times_called(my_module_with_bound_imports.foo, 3)


def test_bar_handles_response_when_module_uses_bound_imports():
    with stub(
        (other_package.make_a_network_request, mock_make_a_network_request),
        (other_package.write_to_disk, mock_write_to_disk),
    ), spy(
        my_module_with_bound_imports.foo,
    ):
        assert times_called(my_module_with_bound_imports.foo, 0)
        assert times_called(other_package.make_a_network_request, 0)
        assert bar(21) == {"result": 42}
        assert times_called(my_module_with_bound_imports.foo, 1)
        assert times_called(other_package.make_a_network_request, 1)
        assert called_with_args(my_module_with_bound_imports.foo, args=[21])
        assert bar(20) == {"result": 40}
        assert calls(my_module_with_bound_imports.foo) == [
            {
                "args": [21],
                "kwargs": None,
                "return": {"result": 42},
                "error": None,
            },
            {
                "args": [20],
                "kwargs": None,
                "return": {"result": 40},
                "error": None,
            },
        ]
        assert calls(other_package.write_to_disk) == [
            {
                "args": [{"result": 42}],
                "kwargs": None,
                "return": "Wrote to disk!",
                "error": None,
            },
            {
                "args": [{"result": 40}],
                "kwargs": None,
                "return": "Wrote to disk!",
                "error": None,
            },
        ]
