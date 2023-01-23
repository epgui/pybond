import pytest

import sample_code.my_module as my_module
from pybond import spy, stub, times_called, was_called


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
