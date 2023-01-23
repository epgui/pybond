import datetime
from typing import Any

import sample_code.other_package as other_package


def foo(x: Any) -> None:
    response = other_package.make_a_network_request(x, y=None)
    other_package.write_to_disk(response)
    return response


def bar(x: Any) -> None:
    return foo(x)


def try_dangerous_things():
    try:
        return other_package.dangerous_function()
    except Exception as e:
        return e


def use_the_datetime_class_to_get_current_timestamp():
    return datetime.datetime.now()
