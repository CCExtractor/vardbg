from . import ansi


def key_var(var, key):
    return f"{var}[{repr(key)}]"


def val(val):
    return ansi.bold(repr(val))
