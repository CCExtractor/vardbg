# Set of code objects of internal debugger functions that are called when tracing is active
INTERNAL_FUNC_CODES = set()


def add_funcs(*funcs):
    INTERNAL_FUNC_CODES.update(set(fn.__code__ for fn in funcs))
