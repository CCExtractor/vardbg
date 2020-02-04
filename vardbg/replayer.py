import abc
from typing import TYPE_CHECKING

import jsonpickle

from .output.json_writer import ADD_VARIABLE, CHANGE_VARIABLE, EXECUTE_FRAME, NEW_FRAME, REMOVE_VARIABLE

if TYPE_CHECKING:
    from .debugger import Debugger


class Replayer(abc.ABC):
    def __init__(self: "Debugger"):
        # Propagate initialization to other mixins
        super().__init__()

    def replay_events(self: "Debugger", events):
        for event in events:
            evt_type = event["event"]

            if evt_type == NEW_FRAME:
                self.out.write_cur_frame(event["frame_info"], event["output"])
            elif evt_type == EXECUTE_FRAME:
                frame_info = event["frame_info"]
                exec_time = event["exec_time"]

                self.out.write_frame_exec(frame_info, exec_time, event["exec_times"])

                # Replay changes to frame_exec_times
                if frame_info in self.frame_exec_times:
                    self.frame_exec_times[frame_info].append(exec_time)
                else:
                    self.frame_exec_times[frame_info] = [exec_time]
            elif evt_type == ADD_VARIABLE:
                self.out.write_add(
                    event["var_name"], event["value"], event["history"], action=event["action"], plural=event["plural"],
                )
            elif evt_type == CHANGE_VARIABLE:
                self.out.write_change(
                    event["var_name"],
                    event["value_before"],
                    event["value_after"],
                    event["history"],
                    action=event["action"],
                )
            elif evt_type == REMOVE_VARIABLE:
                self.out.write_remove(event["var_name"], event["value"], event["history"], action=event["action"])
            else:
                raise ValueError(f"Unrecognized JSON event '{evt_type}'")

    def replay_summary(self: "Debugger", data):
        self.vars.update(data["var_history"])
        self.out.write_variable_summary(self.vars)
        if self.profiler_output:
            self.out.write_profiler_summary(self.frame_exec_times)
        self.out.write_time_summary(data["exec_start_time"], data["exec_stop_time"])

    def replay(self: "Debugger", json_path):
        with open(json_path, "r") as f:
            data = jsonpickle.loads(f.read())

        self.replay_events(data["events"])
        self.replay_summary(data)
