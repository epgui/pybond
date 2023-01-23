from inspect import getfullargspec


def _args_match(fsig, gsig) -> bool:
    if len(fsig.args) == 0 or len(gsig.args) == 0:
        return fsig.args == gsig.args
    else:
        return len(fsig.args) == len(gsig.args)


def _varargs_match(fsig, gsig) -> bool:
    if None in [fsig.varargs, gsig.varargs]:
        return fsig.varargs == gsig.varargs
    else:
        return True


def _kwargs_match(fsig, gsig) -> bool:
    if len(fsig.kwonlyargs) == 0 or len(gsig.kwonlyargs) == 0:
        return fsig.kwonlyargs == gsig.kwonlyargs
    else:
        f_required = set(fsig.kwonlyargs) - set(fsig.kwonlydefaults.keys())
        g_required = set(gsig.kwonlyargs) - set(gsig.kwonlydefaults.keys())
        return f_required == g_required


def _varkwargs_match(fsig, gsig) -> bool:
    if None in [fsig.varkw, gsig.varkw]:
        return fsig.varkw == gsig.varkw
    else:
        return True


def _fn_with_zero_arguments():
    return None


def function_signatures_match(f, g):
    try:
        fsig = getfullargspec(f)
        gsig = getfullargspec(g)
        return (
            _args_match(fsig, gsig)
            and _kwargs_match(fsig, gsig)
            and _varargs_match(fsig, gsig)
            and _varkwargs_match(fsig, gsig)
        )
    except TypeError as e:
        # Some callables may not be introspectable in certain implementations of
        # Python. For example, in CPython, some built-in functions defined in C
        # provide no metadata about their arguments.
        if str(e) == "unsupported callable":
            if [f.__module__, f.__name__] == ["time", "time"]:
                return function_signatures_match(_fn_with_zero_arguments, g)
            # Add other specific cases here
            else:
                raise
        else:
            raise
