import copy

import jsonpickle

from ..timing import wall_time
from .writer import Writer

NEW_FRAME = "new_frame"
EXECUTE_FRAME = "exec_frame"

ADD_VARIABLE = "add_var"
CHANGE_VARIABLE = "change_var"
REMOVE_VARIABLE = "remove_var"


class JsonWriter(Writer):
    def __init__(self, output_path):
        self.output_path = output_path

        self.data = {"events": []}
        self._step = 0

    def step(self):
        self._step += 1
        return self._step

    def write_event(self, evt_name, **kwargs):
        event = {"step": self.step(), "time": wall_time(), "event": evt_name}
        event.update(kwargs)

        self.data["events"].append(event)

    def write_cur_frame(self, frame_info, output):
        self.write_event(NEW_FRAME, frame_info=frame_info, output=output)

    def write_frame_exec(self, frame_info, exec_time, exec_times):
        # exec_times needs to be copied to preserve the *current* state
        self.write_event(EXECUTE_FRAME, frame_info=frame_info, exec_time=exec_time, exec_times=exec_times.copy())

    def write_add(self, var, val, history, *, action, plural):
        self.write_event(
            ADD_VARIABLE, var_name=var, value=val, history=copy.deepcopy(history), action=action, plural=plural,
        )

    def write_change(self, var, val_before, val_after, history, *, action):
        self.write_event(
            CHANGE_VARIABLE,
            var_name=var,
            value_before=val_before,
            value_after=val_after,
            history=copy.deepcopy(history),
            action=action,
        )

    def write_remove(self, var, val, history, *, action):
        self.write_event(REMOVE_VARIABLE, var_name=var, value=val, history=copy.deepcopy(history), action=action)

    def write_variable_summary(self, var_history):
        self.data["var_history"] = list(var_history.items())

    def write_profiler_summary(self, frame_exec_times):
        # frame_exec_times is skipped because it can be readily reconstructed during replay
        pass

    def write_time_summary(self, exec_start_time, exec_stop_time):
        self.data["exec_start_time"] = exec_start_time
        self.data["exec_stop_time"] = exec_stop_time

    def close(self):
        # Write all the collected data out together
        with open(self.output_path, "w+") as f:
            f.write(jsonpickle.dumps(self.data))
