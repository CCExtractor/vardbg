import abc
import platform
import time
from typing import TYPE_CHECKING

import sortedcontainers

from . import internal

if TYPE_CHECKING:
    from .debugger import Debugger


# Helper to call a function from the time module with nanosecond precision if possible, and lower prrcision otherwise
def _time_wrap_ns(sym_base):
    sym_ns = sym_base + "_ns"
    if hasattr(time, sym_ns):
        # Use ns function if possible
        return getattr(time, sym_ns)
    else:
        # Otherwise, create a wrapper to convert it
        # This is necessary on Python < 3.7
        func = getattr(time, sym_base)
        return lambda: int(func() * 1_000_000_000)


# Use performance counter on Windows and process time on others for max precision (ref: PEP-564)
if platform.system() == "Windows":
    get_time_ns = _time_wrap_ns("perf_counter")
else:
    get_time_ns = _time_wrap_ns("process_time")


class Profiler(abc.ABC):
    def __init__(self: "Debugger"):
        # Map of FrameInfo objects and a list of their execution times in ns
        self.frame_exec_times = sortedcontainers.SortedDict()
        # When the last frame started executing
        self.prev_frame_start_time = None

        # Overall start and stop times
        self.exec_start_time = None
        self.exec_stop_time = None

        # Propagate initialization to other mixins
        super().__init__()

    def profile_start_frame(self: "Debugger"):
        self.prev_frame_start_time = get_time_ns()

    def profile_complete_frame(self: "Debugger", prev_frame_info):
        exec_time = get_time_ns() - self.prev_frame_start_time

        if prev_frame_info in self.frame_exec_times:
            self.frame_exec_times[prev_frame_info].append(exec_time)
        else:
            self.frame_exec_times[prev_frame_info] = [exec_time]

    def profile_print_frame(self: "Debugger", prev_frame_info):
        if self.live_profiler_output:
            exec_times = self.frame_exec_times[prev_frame_info]
            self.out.write_frame_exec(prev_frame_info, exec_times[-1], exec_times)

    def profile_start_exec(self: "Debugger"):
        self.exec_start_time = time.time_ns()

    def profile_end_exec(self: "Debugger"):
        self.exec_stop_time = time.time_ns()

    internal.add_funcs(profile_start_exec, profile_end_exec)
