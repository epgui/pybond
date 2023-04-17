from functools import wraps


def with_decorator(_arg1: str):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapper

    return decorator


@with_decorator("foobar")
def my_adder(x, y):
    return x + y
