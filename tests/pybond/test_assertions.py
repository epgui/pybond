import pytest

import sample_code.my_module as my_module
import sample_code.other_package as other_package
from pybond import (
    called_exactly_once_with_args,
    called_with_args,
    spy,
    stub,
    times_called,
    was_called,
)


def test_was_called():
    def run_tests():
        assert not was_called(my_module.foo)
        my_module.bar(42)
        assert was_called(my_module.foo)

    with spy([my_module, "foo"]):
        run_tests()

    with stub([my_module, "foo", my_module.foo]):
        run_tests()


def test_was_called_throws_on_unspied_functions():
    my_module.bar(42)
    with pytest.raises(Exception) as e:
        was_called(my_module.foo)
    assert e.value.args[0].startswith("The argument is not a spied function.")


def test_times_called():
    def run_tests():
        assert times_called(my_module.foo, 0)
        my_module.bar(42)
        assert times_called(my_module.foo, 1)
        my_module.bar(42)
        my_module.bar(42)
        my_module.bar(42)
        assert times_called(my_module.foo, 4)

    with spy([my_module, "foo"]):
        run_tests()

    with stub([my_module, "foo", my_module.foo]):
        run_tests()


def test_times_called_throws_on_unspied_functions():
    my_module.bar(42)
    with pytest.raises(Exception) as e:
        times_called(my_module.foo, 1)
    assert e.value.args[0].startswith("The argument is not a spied function.")


def test_called_with_args():
    # When there is only one function call
    with spy([other_package, "make_a_network_request"]):
        assert not called_with_args(
            other_package.make_a_network_request,
            args=[42, 12],
            kwargs={"y": "y", "other_arg": True},
        )
        other_package.make_a_network_request(42, 12, y="y", other_arg=True)
        assert called_with_args(
            other_package.make_a_network_request,
            args=[42, 12],
            kwargs={"y": "y", "other_arg": True},
        )

    # When there are multiple function calls (order doesn't matter)
    with spy([other_package, "make_a_network_request"]):
        other_package.make_a_network_request(0, y=None)
        other_package.make_a_network_request(0, y="elephant")
        other_package.make_a_network_request(42, 12, y="y", other_arg=True)
        other_package.make_a_network_request(0, y="giraffe")
        assert called_with_args(
            other_package.make_a_network_request,
            args=[0],
            kwargs={"y": "elephant"},
        )
        assert called_with_args(
            other_package.make_a_network_request,
            args=[0],
            kwargs={"y": "giraffe"},
        )
        assert called_with_args(
            other_package.make_a_network_request,
            args=[0],
            kwargs={"y": None},
        )
        assert called_with_args(
            other_package.make_a_network_request,
            args=[42, 12],
            kwargs={"y": "y", "other_arg": True},
        )
        assert not called_with_args(
            other_package.make_a_network_request,
            args=[0],
            kwargs={"y": "sloth"},
        )


def test_called_with_args_throws_on_unspied_functions():
    other_package.make_a_network_request(42, 12, y="y", other_arg=True)
    with pytest.raises(Exception) as e:
        called_with_args(
            other_package.make_a_network_request,
            args=["this doesn't matter"],
            kwargs={"nor": "does this"},
        )
    assert e.value.args[0].startswith("The argument is not a spied function.")


def test_called_exactly_once_with_args():
    # When there is only one function call
    with spy([other_package, "make_a_network_request"]):
        assert not called_exactly_once_with_args(
            other_package.make_a_network_request,
            args=[42, 12],
            kwargs={"y": "y", "other_arg": True},
        )
        other_package.make_a_network_request(42, 12, y="y", other_arg=True)
        assert called_exactly_once_with_args(
            other_package.make_a_network_request,
            args=[42, 12],
            kwargs={"y": "y", "other_arg": True},
        )

    # When there are multiple function calls (order doesn't matter)
    with spy([other_package, "make_a_network_request"]):
        other_package.make_a_network_request(0, y=None)
        other_package.make_a_network_request(0, y="elephant")
        other_package.make_a_network_request(42, 12, y="y", other_arg=True)
        other_package.make_a_network_request(0, y="giraffe")
        assert not called_exactly_once_with_args(
            other_package.make_a_network_request,
            args=[0],
            kwargs={"y": "elephant"},
        )
        assert not called_exactly_once_with_args(
            other_package.make_a_network_request,
            args=[0],
            kwargs={"y": "giraffe"},
        )
        assert not called_exactly_once_with_args(
            other_package.make_a_network_request,
            args=[0],
            kwargs={"y": None},
        )
        assert not called_exactly_once_with_args(
            other_package.make_a_network_request,
            args=[42, 12],
            kwargs={"y": "y", "other_arg": True},
        )
        assert not called_exactly_once_with_args(
            other_package.make_a_network_request,
            args=[0],
            kwargs={"y": "sloth"},
        )


def test_called_exactly_once_with_args_throws_on_unspied_functions():
    other_package.make_a_network_request(42, 12, y="y", other_arg=True)
    with pytest.raises(Exception) as e:
        called_exactly_once_with_args(
            other_package.make_a_network_request,
            args=["this doesn't matter"],
            kwargs={"nor": "does this"},
        )
    assert e.value.args[0].startswith("The argument is not a spied function.")
