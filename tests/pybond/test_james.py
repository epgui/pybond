import pytest

import sample_code.my_module as my_module
import sample_code.other_package as other_package
from pybond import calls, spy, stub


def test_spied_function_throws_exception():
    def run_tests():
        assert (
            my_module.try_dangerous_things().args[0]
            == "This is what happens when you don't floss!"
        )
        assert (
            "This is what happens when you don't floss!" in [
                call["error"][1].args[0]
                for call in calls(other_package.dangerous_function)
            ]
        )

    with spy([other_package, "dangerous_function"]):
        run_tests()
    
    with stub([other_package, "dangerous_function", other_package.dangerous_function]):
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
        with stub([target_module, target_function, stub_fn]):
            my_module.bar(42)
            assert True  # No exception is thrown in the line above
    else:
        with pytest.raises(Exception) as e:
            with stub([target_module, target_function, stub_fn]):
                my_module.bar(42)
        assert e.value.args[0].startswith("Stub does not match the signature of")
