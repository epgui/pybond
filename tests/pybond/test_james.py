import pytest

import sample_code.other_package as suspicious
from pybond import calls, spy, stub


def try_dangerous_things():
    try:
        return suspicious.dangerous_function()
    except Exception as e:
        return e


def test_spied_function_throws_exception():
    def run_tests():
        assert (
            try_dangerous_things().args[0]
            == "This is what happens when you don't floss!"
        )
        assert "This is what happens when you don't floss!" in [
            call["error"][1].args[0] for call in calls(suspicious.dangerous_function)
        ]

    with spy([suspicious, "dangerous_function"]):
        run_tests()
    
    with stub([suspicious, "dangerous_function", suspicious.dangerous_function]):
        run_tests()
