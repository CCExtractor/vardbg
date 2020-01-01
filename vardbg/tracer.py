import abc
import copy
import sys
from typing import TYPE_CHECKING

import dictdiffer

from . import data, internal

if TYPE_CHECKING:
    from .debugger import Debugger


ALLOWED_EVENTS = {"call", "line", "return"}


class Tracer(abc.ABC):
    def __init__(self: "Debugger"):
        # Function being debugged
        self.func = None

        # Previous frame and its locals
        self.prev_frame_info = None
        self.prev_event = None
        self.prev_locals = {}
        # New frame's locals
        self.new_locals = {}

        # Propagate initialization to other mixins
        super().__init__()

    def trace_callback(self: "Debugger", frame, event, arg):
        """Frame execution callback"""

        # Ignore irrelevant events, but still attach to the next one
        if event not in ALLOWED_EVENTS:
            return self.trace_callback

        # Ignore all other functions
        code = frame.f_code
        if code != self.func.__code__:
            return

        # The first frame is when function arguments are populated, so it's important
        # Set itself to the previous frame since its line number *is* where function arguments are defined
        frame_info = data.FrameInfo(frame, relative=self.use_relative_paths)
        if self.prev_frame_info is None:
            self.prev_frame_info = frame_info
            self.prev_event = event

        # Only invoke profiler if the last event was *not* a function call since nothing's executed yet
        should_profile = self.prev_event != "call"
        if should_profile:
            # Call profiler first to avoid counting the time it takes to copy locals
            self.profile_complete_frame()

        # Get new locals and copy them so they don't change on the next frame
        self.new_locals = copy.deepcopy(frame.f_locals)

        # Render output prefix for this frame
        self.out.write_cur_frame(self.prev_frame_info)

        # Skip profiler for the first frame since it's before any real execution (just the function call)
        if should_profile:
            # Call profiler to print the last frame's execution
            self.profile_print_frame()

        # Diff and print changes
        diff = dictdiffer.diff(self.prev_locals, self.new_locals)
        self.process_locals_diff(diff, self.prev_frame_info)

        # Update previous frame info in preparation for the next frame
        self.prev_frame_info = frame_info
        self.prev_event = event
        self.prev_locals = self.new_locals
        if event != "call":
            self.profile_start_frame()

        # Subscribe to the next frame, if any
        return self.trace_callback

    def run(self: "Debugger", func, *args, **kwargs):
        self.func = func

        # Run function with trace callback registered
        sys.settrace(self.trace_callback)
        self.profile_start_exec()
        ret = self.func(*args, **kwargs)
        self.profile_end_exec()
        sys.settrace(None)

        self.out.write_summary(self.vars, self.exec_start_time, self.exec_stop_time, self.frame_exec_times)
        return ret

    internal.add_funcs(run)
