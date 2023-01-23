from pybond.james import calls


def was_called(f):
    """
    A predicate to check if `f` was called at least 1 time. Note that `f` must
    be a spied function.
    """
    return len(calls(f)) > 0


def times_called(f, n):
    """
    A predicate to check if `f` was called exactly `n` times. Note that `f` must
    be a spied function.
    """
    return len(calls(f)) == n


def called_with_exact_args_list(f, args_list=None, kwargs_list=None):
    """
    A predicate to check if `f` was called with specific arguments. Return true
    only if arguments match for every function call on `f`. Note that `f` must
    be a spied function.
    """
    fcalls = calls(f)
    if len(fcalls) == 0:
        return False
    args_match = len(fcalls) > 0
    kwargs_match = len(fcalls) > 0
    if args_list is not None:
        args_match = args_list == [fcall["args"] for fcall in fcalls]
    if kwargs_list is not None:
        kwargs_match = kwargs_list == [fcall["kwargs"] for fcall in fcalls]
    return args_match and kwargs_match


def called_exactly_once_with_args(f, args=None, kwargs=None):
    """
    A predicate to check if `f` was called with specific arguments exactly once.
    Note that `f` must be a spied function.
    """
    return called_with_exact_args_list(f, [args], [kwargs])


def called_with_args(f, args=None, kwargs=None):
    """
    A predicate to check if `f` has been called at least once with the given
    arguments. Note that `f` must be a spied function.
    """
    fcalls = calls(f)
    args_match = len(fcalls) > 0
    kwargs_match = len(fcalls) > 0
    if args is not None:
        args_match = args in [fcall["args"] for fcall in fcalls]
    if kwargs is not None:
        kwargs_match = kwargs in [fcall["kwargs"] for fcall in fcalls]
    return args_match and kwargs_match
