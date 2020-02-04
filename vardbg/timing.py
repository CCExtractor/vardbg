import time

from . import internal


# Helper to call a function from the time module with nanosecond precision if possible, and lower precision otherwise
def _time_wrap_ns(sym_base):
    sym_ns = sym_base + "_ns"
    if hasattr(time, sym_ns):
        # Use ns function if possible
        return getattr(time, sym_ns)
    else:
        # Otherwise, create a wrapper to convert it
        # This is necessary on Python < 3.7
        func = getattr(time, sym_base)

        def wrapper():
            return int(func() * 1_000_000_000)

        # Mark it as an internal function *before* returning
        internal.add_funcs(wrapper)
        return wrapper


# Profiler: use performance counter for max precision (ref: PEP-564)
profiler_time = _time_wrap_ns("perf_counter")

# Some code requires wall-clock time
wall_time = _time_wrap_ns("time")
