from . import ansi


def key_var(var, key):
    return f"{var}[{repr(key)}]"


def val(val):
    return ansi.bold(repr(val))


def file_line(frame):
    return f"{frame.f_code.co_filename}:{frame.f_lineno}"
