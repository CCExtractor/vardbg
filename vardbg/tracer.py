import abc
import copy
import sys
from typing import TYPE_CHECKING

import dictdiffer

from . import data

if TYPE_CHECKING:
    from .debugger import Debugger


class Tracer(abc.ABC):
    def __init__(self: "Debugger"):
        # Function being debugged
        self.func = None

        # Previous frame and its locals
        self.prev_frame_info = None
        self.prev_locals = {}
        # New frame's locals
        self.new_locals = {}

        # Propagate initialization to other mixins
        super().__init__()

    def trace_callback(self: "Debugger", frame, event, arg):
        """Frame execution callback"""

        # Ignore all other functions
        code = frame.f_code
        if code != self.func.__code__:
            return

        # Call profiler first to avoid counting the time it takes to copy locals
        if self.prev_frame_info is not None:
            self.profile_complete_frame()

        # Get new locals and copy them so they don't change on the next frame
        self.new_locals = copy.deepcopy(frame.f_locals)

        # Don't process the first frame since this callback runs *before*
        # frame execution, not after
        if self.prev_frame_info is not None:
            # Render output prefix for this frame
            self.out.write_cur_frame(self.prev_frame_info)

            # Call profiler to print this frame's execution
            self.profile_print_frame()

            # Diff and print changes
            diff = dictdiffer.diff(self.prev_locals, self.new_locals)
            self.process_locals_diff(diff, self.prev_frame_info)

        # Update previous frame info in preparation for the next frame
        self.prev_frame_info = data.FrameInfo(frame, relative=self.use_relative_paths)
        self.prev_locals = self.new_locals
        self.profile_start_frame()

        # Subscribe to the next frame, if any
        return self.trace_callback

    def run(self: "Debugger", func):
        self.func = func

        # Run function with trace callback registered
        sys.settrace(self.trace_callback)
        self.profile_start_exec()
        self.func()
        self.profile_end_exec()
        sys.settrace(None)

        self.out.write_summary(self.vars, self.exec_start_time, self.exec_stop_time, self.frame_exec_times)
