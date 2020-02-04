import collections
import re
import statistics
import textwrap
from pathlib import Path

import pygments
from pygments.lexers.python import PythonLexer
from pygments.token import Token

from ... import render
from ..writer import Writer
from .renderer import FrameRenderer

VarState = collections.namedtuple("VarState", ("name", "color", "action", "value", "ref", "text", "other_history"))


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


def split_lexed_lines(lst):
    lines = []
    line = []

    for tok, txt in lst:
        while "\n" in txt:
            nl_idx = txt.index("\n")
            line_seg = txt[: nl_idx + 1]
            line.append((tok, line_seg))
            lines.append(line)
            line = []
            txt = txt[nl_idx + 1 :]

        if txt:
            line.append((tok, txt))

    return lines


class VideoWriter(Writer):
    def __init__(self, path, config_path, show_profile):
        # File contents
        self.file_cache = {}
        # Current stack frame snapshot (info)
        self.frame_info = None
        # Last variable state
        self.last_var = None
        # Frame renderer
        self.render = FrameRenderer(path, config_path, show_profile)

    def get_file_lines(self, path):
        if path in self.file_cache:
            return self.file_cache[path]

        lexed = pygments.lex(Path(path).read_text(), PythonLexer())
        lines = split_lexed_lines(lexed)
        self.file_cache[path] = lines
        return lines

    def write_cur_frame(self, frame_info, output):
        self.frame_info = frame_info
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

    def _write_action(self, name, val, color, action, fields, history):
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

        # Parse reference comments
        match = re.match(r"^ref (.+)\[(.+)\]$", self.frame_info.comment)
        if match is None:
            ref = None
        else:
            # Extract values
            container = match.group(1)
            key = match.group(2)

            # Make sure both the key matches this variable and the container exists in this scope
            if key == name and any(var.name == container for var, values in history.other_history):
                ref = container
            else:
                ref = None

        # Save state; this is drawn when the frame is finished
        self.last_var = VarState(name, self.render.get_color(color), action, val, ref, text, history.other_history)

    def write_add(self, var, val, history, *, action="added", plural):
        self._write_action(var, val, self.render.GREEN, action, {"Value": repr(val)}, history)

    def write_change(self, var, val_before, val_after, history, *, action="changed"):
        self._write_action(
            var, val_after, self.render.BLUE, action, {"From": repr(val_before), "To": repr(val_after)}, history,
        )

    def write_remove(self, var, val, history, *, action="removed"):
        self._write_action(var, val, self.render.RED, action, {"Last value": repr(val)}, history)

    def write_variable_summary(self, var_history):
        # Videos don't have summaries
        pass

    def write_profiler_summary(self, frame_exec_times):
        pass

    def write_time_summary(self, exec_start_time, exec_stop_time):
        pass

    def close(self):
        self.render.close(self.last_var)
