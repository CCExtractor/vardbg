import collections
import statistics
import textwrap
from pathlib import Path

from ... import render
from ..writer import Writer
from .renderer import FrameRenderer

VarState = collections.namedtuple("VarState", ("name", "color", "action", "text_lines", "other_text_lines"))


def wrap_text(text, cols, rows=None):
    lines = text.replace("\r", "").split("\n")

    # Wrap text
    wrapped_lines = []
    for line in lines:
        line_wrapped = textwrap.wrap(line, width=cols)
        if len(line_wrapped) == 0:
            wrapped_lines.append("")
        else:
            wrapped_lines += line_wrapped

    # Truncate rows and add indicator if necessary
    if rows is not None and len(wrapped_lines) > rows:
        wrapped_lines = wrapped_lines[:rows]
        wrapped_lines[-1] = wrapped_lines[-1][: cols - 5] + " [...]"

    return wrapped_lines


class VideoWriter(Writer):
    def __init__(self, path, config_path):
        # File contents
        self.file_cache = {}
        # Current stack frame snapshot (info)
        self.frame_info = None
        # Last variable state
        self.last_var = None
        # Frame renderer
        self.render = FrameRenderer(path, config_path)

    def get_file_lines(self, path):
        if path in self.file_cache:
            return self.file_cache[path]

        lines = Path(path).read_text().splitlines()
        self.file_cache[path] = lines
        return lines

    def write_cur_frame(self, frame_info, output):
        self.render.finish_frame(self.last_var)
        self.render.start_frame()
        self.render.draw_code(self.get_file_lines(frame_info.file), frame_info.line)
        self.render.draw_output(wrap_text(output, self.render.out_cols))

    def write_frame_exec(self, frame_info, exec_time, exec_times):
        nr_times = len(exec_times)
        avg_time = render.duration_ns(statistics.mean(exec_times))
        total_time = render.duration_ns(sum(exec_times))
        this_time = render.duration_ns(exec_time)

        self.render.draw_exec(nr_times, this_time, avg_time, total_time)

    def _write_action(self, name, color, action, fields, history):
        # Render fields
        fields_text = "\n".join(f"{field}: {value}" for field, value in fields.items())

        if history.var_history:
            values = ["\n\nHistory:"]

            for value in history.var_history:
                values.append(repr(value.value))

            history_text = "\n    \u2022 ".join(values)
        else:
            history_text = ""

        # Render and split full text
        text = fields_text + history_text
        wrapped_text = wrap_text(text, int(self.render.vars_cols), int(self.render.vars_rows))

        # Render text for "others" section
        other_vars = []
        for var, values in history.other_history:
            var_lines = [var.name + ":"]

            for value in values:
                var_lines.append(repr(value.value))

            other_vars.append("\n    \u2022 ".join(var_lines))

        others_text = "\n\n".join(other_vars)
        wrapped_others_text = wrap_text(others_text, int(self.render.ovars_cols), int(self.render.ovars_rows))

        # Save state; this is drawn when the frame is finished
        self.last_var = VarState(name, self.render.get_color(color), action, wrapped_text, wrapped_others_text)

    def write_add(self, var, val, history, *, action="added", plural):
        self._write_action(var, self.render.GREEN, action, {"Value": repr(val)}, history)

    def write_change(self, var, val_before, val_after, history, *, action="changed"):
        self._write_action(
            var, self.render.BLUE, action, {"From": repr(val_before), "To": repr(val_after)}, history,
        )

    def write_remove(self, var, val, history, *, action="removed"):
        self._write_action(var, self.render.RED, action, {"Last value": repr(val)}, history)

    def write_summary(self, var_history, exec_start_time, exec_stop_time, frame_exec_times):
        # Video doesn't have a summary
        pass

    def close(self):
        self.render.close(self.last_var)
