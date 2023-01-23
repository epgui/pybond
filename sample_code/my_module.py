from typing import Any
import sample_code.other_package as other_package


def foo(x: Any) -> None:
    response = other_package.make_a_network_request(x)
    other_package.write_to_disk(response)
    return response


def bar(x: Any) -> None:
    return foo(x)
