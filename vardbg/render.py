from . import ansi


def key_var(var, key):
    return f"{var}[{repr(key)}]"


def val(value):
    return ansi.bold(repr(value))


def duration_ns(t_ns) -> str:
    t_ns = int(t_ns)

    t_us = t_ns / 1000
    t_ms = t_us / 1000
    t_s = t_ms / 1000
    t_m = t_s / 60
    t_h = t_m / 60
    t_d = t_h / 24

    if t_d >= 1:
        rem_h = t_h % 24
        rem_m = t_m % 60
        rem_s = t_s % (24 * 60 * 60) % 60
        return "%dd %dh %dm %ds" % (t_d, rem_h, rem_m, rem_s)
    elif t_h >= 1:
        rem_m = t_m % 60
        rem_s = t_s % (60 * 60) % 60
        return "%dh %dm %ds" % (t_h, rem_m, rem_s)
    elif t_m >= 1:
        rem_s = t_s % 60
        return "%dm %ds" % (t_m, rem_s)
    elif t_s >= 10:
        return "%ds" % t_s
    elif t_ms >= 10:
        return "%d ms" % t_ms
    elif t_us >= 1:
        return "%d μs" % t_us
    else:
        return "%d ns" % t_ns
