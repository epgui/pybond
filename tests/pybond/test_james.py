import datetime
import pytest
import time

import sample_code.my_module as my_module
import sample_code.other_package as other_package
from tests.sample_code.mocks import create_mock_datetime
from pybond import calls, spy, stub
from pybond.james import _instrumented_obj


def test_spied_function_throws_exception():
    def run_tests():
        exception = my_module.try_dangerous_things()
        assert exception.args[0] == "This is what happens when you don't floss!"
        assert (
            "This is what happens when you don't floss!" in [
                call["error"][1].args[0]
                for call in calls(other_package.dangerous_function)
            ]
        )

    with spy((other_package, "dangerous_function")):
        run_tests()
    
    with stub((other_package, "dangerous_function", other_package.dangerous_function)):
        run_tests()


@pytest.mark.parametrize(
    "target_module, target_function, stub_fn, signature_matching",
    [
        pytest.param(other_package, "write_to_disk", lambda: None, False),
        pytest.param(other_package, "write_to_disk", lambda x: None, True),
        pytest.param(other_package, "write_to_disk", lambda *x: None, False),
        pytest.param(other_package, "write_to_disk", lambda **x: None, False),
        pytest.param(other_package, "write_to_disk", lambda a, b: None, False),
        pytest.param(other_package, "write_to_disk", lambda x, *a: None, False),
        pytest.param(other_package, "write_to_disk", lambda x, **a: None, False),
    ],
)
def test_stub_function_signature_should_match(
    target_module,
    target_function,
    stub_fn,
    signature_matching,
):
    if signature_matching:
        with stub((target_module, target_function, stub_fn)):
            my_module.bar(42)
            assert True  # No exception is thrown in the line above
    else:
        with pytest.raises(Exception) as e:
            with stub((target_module, target_function, stub_fn)):
                my_module.bar(42)
        assert e.value.args[0].startswith("Stub does not match the signature of")


def test_class_stubbing():
    mock_now = datetime.datetime.now()
    with stub((datetime, "datetime", create_mock_datetime(mock_now))):
        time.sleep(2)
        assert (
            my_module.use_the_datetime_class_to_get_current_timestamp()
            == mock_now
        )


@pytest.mark.parametrize(
    "original_obj, stub_obj, error_message",
    [
        pytest.param(
            other_package.write_to_disk,
            lambda _: None,
            None,
        ),
        pytest.param(
            other_package.write_to_disk,
            lambda _, __: None,
            "Stub does not match the signature of write_to_disk.",
        ),
        pytest.param(
            other_package.write_to_disk,
            "This is not a Callable, it's a string.",
            "pybond expected a Callable type.",
        ),
        pytest.param(
            "This is not a Callable, it's a string.",
            "This is not a Callable, it's a string.",
            "Object of type <class 'str'> is not supported by pybond."
        )
    ],
)
def test_instrumented_obj(original_obj, stub_obj, error_message):
    if not error_message:
        _instrumented_obj(original_obj, stub_obj)
        assert True
    else:
        with pytest.raises(Exception) as e:
            _instrumented_obj(original_obj, stub_obj)
        assert error_message in e.value.args[0]
