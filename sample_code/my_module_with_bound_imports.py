from datetime import datetime
from typing import Any

from sample_code.other_package import (
    make_a_network_request,
    write_to_disk,
    dangerous_function,
)


def foo(x: Any) -> None:
    response = make_a_network_request(x, y=None)
    write_to_disk(response)
    return response


def bar(x: Any) -> None:
    return foo(x)


def try_dangerous_things():
    try:
        return dangerous_function()
    except Exception as e:
        return e


def use_the_datetime_class_to_get_current_timestamp():
    return datetime.now()
