import time
import jsonpickle

from .writer import Writer


class JsonWriter(Writer):
    def __init__(self, output_path):
        self.output_path = output_path

        self.events = []
        self._step = 0

    def step(self):
        self._step += 1
        return self._step

    def write_event(self, evt_name, **kwargs):
        # Add step and time *first* so it's ordered like that in the JSON
        event = {"step": self.step(), "time": time.time_ns(), "event": evt_name}
        event.update(kwargs)

        self.events.append(event)

    def write_cur_frame(self, frame_info):
        self.write_event("new_frame", frame_info=frame_info)

    def write_add(self, var, val, *, action="added", plural=False):
        self.write_event("add_var", var_name=var, value=val, action=action, plural=plural)

    def write_change(self, var, val_before, val_after, *, action="changed"):
        self.write_event(
            "change_var", var_name=var, value_before=val_before, value_after=val_after, action=action,
        )

    def write_remove(self, var, val, *, action="removed"):
        self.write_event("remove_var", var_name=var, value=val, action=action)

    def write_frame_exec(self, frame_info, exec_time, exec_times):
        self.write_event("frame_exec", frame_info=frame_info, exec_time=exec_time, exec_times=exec_times)

    def write_summary(self, var_history, exec_start_time, exec_stop_time, frame_exec_times):
        # Our JSON format doesn't include a summary
        pass

    def close(self):
        # Write all the collected events out together
        with open(self.output_path, "w+") as f:
            f.write(jsonpickle.dumps(self.events))
