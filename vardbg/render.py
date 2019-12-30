from . import ansi


def key_var(var, key):
    return f"{var}[{repr(key)}]"


def val(value):
    return ansi.bold(repr(value))
