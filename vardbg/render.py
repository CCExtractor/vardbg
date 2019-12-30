from . import ansi


def key_var(var, key):
    return f"{var}[{repr(key)}]"


def val(val):
    return f"{ansi.BOLD}{repr(val)}{ansi.RESET}"


def file_line(frame):
    return f"{frame.f_code.co_filename}:{frame.f_lineno}"
