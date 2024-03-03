# pybond

[![Build](https://github.com/epgui/pybond/actions/workflows/build.yml/badge.svg)](https://github.com/epgui/pybond/actions/workflows/build.yml)
[![codecov](https://codecov.io/github/epgui/pybond/branch/main/graph/badge.svg?token=tkq655ROg3)](https://app.codecov.io/github/epgui/pybond)

`pybond` is a spying and stubbing library inspired heavily by the
[clojure `bond` library](https://github.com/circleci/bond/).

## Installation

pip

```bash
pip install pybond==0.2.2
```

requirements.txt

```python
pybond==0.2.2
```

pyproject.toml

```toml
pybond = "0.2.2"
```

## Example usage

Let's say you wanted to test the functions in this module:

```python
# /sample_code/my_module.py
from typing import Any

import sample_code.other_package as other_package


def foo(x: Any) -> None:
    response = other_package.make_a_network_request(x)
    other_package.write_to_disk(response)
    return response


def bar(x: Any) -> None:
    return foo(x)
```

With `pybond` you can easily spy on any given function or stub out functions
that perform IO:

```python
# /tests/test_my_module.py
from pybond import calls, called_with_args, spy, stub, times_called

import sample_code.other_package as other_package
import sample_code.my_module as my_module
from sample_code.my_module import bar


def test_foo_is_called():
    with spy(my_module.foo):
        assert times_called(my_module.foo, 0)
        bar(42)
        assert times_called(my_module.foo, 1)
        bar(42)
        bar(42)
        assert times_called(my_module.foo, 3)


def test_bar_handles_response():
    with stub(
        (other_package.make_a_network_request, lambda x: {"result": x * 2}),
        (other_package.write_to_disk, lambda _: None),
    ), spy(
        my_module.foo,
    ):
        assert times_called(my_module.foo, 0)
        assert times_called(other_package.make_a_network_request, 0)
        assert bar(21) == {"result": 42}
        assert times_called(my_module.foo, 1)
        assert times_called(other_package.make_a_network_request, 1)
        assert called_with_args(my_module.foo, args=[21])
        assert bar(20) == {"result": 40}
        assert calls(my_module.foo) == [
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
                "return": None,
                "error": None,
            },
            {
                "args": [{"result": 40}],
                "kwargs": None,
                "return": None,
                "error": None,
            },
        ]
```

## License

Distributed under the
[Eclipse Public License](http://www.eclipse.org/legal/epl-v10.html).
