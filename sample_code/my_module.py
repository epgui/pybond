import datetime
from datetime import datetime as datetime_2
from typing import Any

import sample_code.other_package as other_package
from sample_code.other_package import (
    make_a_network_request as make_a_network_request_2,
    write_to_disk as write_to_disk_2,
    dangerous_function as dangerous_function_2,
)


def foo(x: Any) -> None:
    response = other_package.make_a_network_request(x, y=None)
    other_package.write_to_disk(response)
    return response


def foo_2(x: Any) -> None:
    response = make_a_network_request_2(x, y=None)
    write_to_disk_2(response)
    return response


def bar(x: Any) -> None:
    return foo(x)


def bar_2(x: Any) -> None:
    return foo_2(x)


def try_dangerous_things():
    try:
        return other_package.dangerous_function()
    except Exception as e:
        return e


def try_dangerous_things_2():
    try:
        return dangerous_function_2()
    except Exception as e:
        return e


def use_the_datetime_class_to_get_current_timestamp():
    return datetime.datetime.now()

def use_the_datetime_class_to_get_current_timestamp_2():
    return datetime_2.now()
