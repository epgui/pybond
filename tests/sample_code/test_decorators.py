from pybond import stub
import sample_code.decorators as decorators


def test_decorated_functions():
    with stub((decorators, "my_adder", lambda a, b: a * b)):
        assert decorators.my_adder(2, 3) == 6
