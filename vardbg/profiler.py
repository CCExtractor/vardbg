import abc
from typing import TYPE_CHECKING

import sortedcontainers

from . import internal
from .timing import profiler_time

if TYPE_CHECKING:
    from .debugger import Debugger


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
        self.prev_frame_start_time = profiler_time()

    def profile_complete_frame(self: "Debugger", prev_frame_info, end_time):
        exec_time = end_time - self.prev_frame_start_time

        if prev_frame_info in self.frame_exec_times:
            self.frame_exec_times[prev_frame_info].append(exec_time)
        else:
            self.frame_exec_times[prev_frame_info] = [exec_time]

    def profile_print_frame(self: "Debugger", prev_frame_info):
        if self.profiler_output:
            exec_times = self.frame_exec_times[prev_frame_info]
            self.out.write_frame_exec(prev_frame_info, exec_times[-1], exec_times)

    def profile_start_exec(self: "Debugger"):
        self.exec_start_time = profiler_time()

    def profile_end_exec(self: "Debugger"):
        self.exec_stop_time = profiler_time()

    internal.add_funcs(profile_start_exec, profile_end_exec)
