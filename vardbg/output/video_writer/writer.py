import collections
import statistics
import textwrap
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from ... import render
from ..writer import Writer

FONT_DIR = Path(__file__).parent / ".." / ".." / ".." / "fonts"
FONT_BODY = (str(FONT_DIR / "FiraMono-Regular.ttf"), 16)
FONT_BODY_BOLD = (str(FONT_DIR / "FiraMono-Bold.ttf"), 16)
FONT_CAPTION = (str(FONT_DIR / "Inter-Regular.ttf"), 16)
FONT_HEAD = (str(FONT_DIR / "Inter-Regular.ttf"), 24)

VID_FPS = 1.5
VID_W = 1920
VID_H = 1080
VID_VAR_X = VID_W * 2 // 3  # 2/3 code, 1/3 variables
VID_VAR_OTHER_Y = VID_H * 1 // 4  # 1/4 last variable, 3/4 other variables

HEADER_PADDING = 20
SECT_PADDING = 20
LINE_HEIGHT = 1.2

# Material dark colors
CLR_BG = (0x12, 0x12, 0x12, 255)
CLR_FG_HEADING = (0xFF, 0xFF, 0xFF, 255)
CLR_FG_BODY = (0xFF, 0xFF, 0xFF, 255 * 70 // 100)  # 70% opacity
CLR_HIGHLIGHT = (0x42, 0x42, 0x42, 255)
CLR_RED = (0xF7, 0x8C, 0x6C, 255)
CLR_GREEN = (0xC3, 0xE8, 0x8D, 255)
CLR_BLUE = (0x82, 0xAA, 0xFF, 255)

VarState = collections.namedtuple("VarState", ("name", "color", "action", "text_lines", "other_text_lines"))


def wrap_text(text, cols, rows):
    lines = text.split("\n")

    # Wrap text
    wrapped_lines = []
    for line in lines:
        line_wrapped = textwrap.wrap(line, width=cols)
        if len(line_wrapped) == 0:
            wrapped_lines.append("")
        else:
            wrapped_lines += line_wrapped

    # Truncate rows and add indicator if necessary
    if len(wrapped_lines) > rows:
        wrapped_lines = wrapped_lines[:rows]
        wrapped_lines[-1] = wrapped_lines[-1][: cols - 5] + " [...]"

    return wrapped_lines


class VideoWriter(Writer):
    def __init__(self, path, config):
        # File contents
        self.file_cache = {}
        # Video writer
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.writer = cv2.VideoWriter(path, fourcc, VID_FPS, (VID_W, VID_H))
        # Fonts
        self.body_font = ImageFont.truetype(*FONT_BODY)
        self.body_bold_font = ImageFont.truetype(*FONT_BODY_BOLD)
        self.caption_font = ImageFont.truetype(*FONT_CAPTION)
        self.head_font = ImageFont.truetype(*FONT_HEAD)
        # Code body size (to be calculated later)
        self.line_height = None
        self.body_cols = None
        self.body_rows = None
        # Variable body start positions
        self.vars_x = None
        self.vars_y = None
        self.ovars_x = None
        self.ovars_y = None
        # Variable body size
        self.vars_cols = None
        self.vars_rows = None
        self.ovars_cols = None
        self.ovars_rows = None
        # Current video frame (image)
        self.frame = None
        # Current stack frame snapshot (info)
        self.frame_info = None
        # Last variable state
        self.last_var = None

    def _draw_text_center(self, x, y, text, font, color):
        w, h = self.draw.textsize(text, font=font)
        self.draw.text((x - w / 2, y - h / 2), text, font=font, fill=color)

    def _start_frame(self):
        # Create image
        self.frame = Image.new("RGBA", (VID_W, VID_H), CLR_BG)
        # Create drawing context
        self.draw = ImageDraw.Draw(self.frame)
        # Calculate code box size (if necessary)
        if self.line_height is None:
            w, h = self.draw.textsize("A", font=self.body_font)

            self.line_height = h * LINE_HEIGHT
            self.body_cols = (VID_VAR_X - SECT_PADDING * 2) // w
            self.body_rows = ((VID_H - SECT_PADDING * 2) / self.line_height) - 1  # Reserve space for caption

        # Draw variable section
        # Vertical divider at 2/3 width
        self.draw.line(((VID_VAR_X, 0), (VID_VAR_X, VID_H)), fill=CLR_FG_BODY, width=1)
        # Label horizontally centered in the variable section and vertically padded
        var_center_x = VID_VAR_X + ((VID_W - VID_VAR_X) / 2)
        self._draw_text_center(var_center_x, HEADER_PADDING, "Last Variable", self.head_font, CLR_FG_HEADING)

        # Draw other variables section
        # Horizontal divider at 1/3 height
        self.draw.line(((VID_VAR_X, VID_VAR_OTHER_Y), (VID_W, VID_VAR_OTHER_Y)), fill=CLR_FG_BODY, width=1)
        # Label similar to the first, but in the others section instead
        ovar_label_y = VID_VAR_OTHER_Y + HEADER_PADDING
        self._draw_text_center(var_center_x, ovar_label_y, "Other Variables", self.head_font, CLR_FG_HEADING)

        # Save variable body start positions and sizes (if necessary)
        if self.vars_x is None:
            # Top-left X and Y for last variable section
            self.vars_x = VID_VAR_X + SECT_PADDING
            hw, hh = self.draw.textsize("A", font=self.head_font)
            self.vars_y = HEADER_PADDING * 2 + hh

            # Columns and rows for last variable section
            vw, vh = self.draw.textsize("A", font=self.body_font)
            self.vars_cols = (VID_W - VID_VAR_X - SECT_PADDING * 2) // vw
            self.vars_rows = int(((VID_VAR_OTHER_Y - SECT_PADDING * 2) / self.line_height) - 1)

            # Top-left X and Y for other variables section
            self.ovars_x = self.vars_x
            self.ovars_y = VID_VAR_OTHER_Y + self.vars_y - self.line_height

            # Columns and rows for other variables section
            self.ovars_cols = self.vars_cols
            ovars_h = VID_H - VID_VAR_OTHER_Y
            self.ovars_rows = int(((ovars_h - SECT_PADDING * 2) / self.line_height) - 1)

    def _finish_frame(self):
        # Bail out if there's no frame to finish
        if self.frame is None:
            return

        # Draw variable state (if available)
        if self.last_var is not None:
            self._draw_variables(self.last_var)

        # Convert PIL -> Numpy array and RGBA -> BGR colors
        cv_img = cv2.cvtColor(np.asarray(self.frame), cv2.COLOR_RGBA2BGR)
        # Write data
        self.writer.write(cv_img)

    def _get_file_lines(self, path):
        if path in self.file_cache:
            return self.file_cache[path]

        lines = Path(path).read_text().splitlines()
        self.file_cache[path] = lines
        return lines

    def _draw_code(self, frame_info):
        # Read lines and current line index
        raw_lines = self._get_file_lines(frame_info.file)
        cur_idx = frame_info.line - 1
        # Construct list of (line, highlighted) tuples
        unwrapped_lines = [(line, i == cur_idx) for i, line in enumerate(raw_lines)]

        # Wrap lines while preserving highlighted status
        wrapped_lines = []
        for line, highlighted in unwrapped_lines:
            line_wrapped = textwrap.wrap(line, width=self.body_cols)
            if len(line_wrapped) == 0:
                # Empty lines still count
                wrapped_lines.append(("", highlighted))
            else:
                for line_seg in line_wrapped:
                    wrapped_lines.append((line_seg, highlighted))

        # Calculate start and end display indexes with an equivalent number of lines on both sides for context
        ctx_side_lines = self.body_rows / 2 - 1
        start_idx = round(cur_idx - ctx_side_lines)
        end_idx = round(cur_idx + ctx_side_lines)
        # Accommodate for situations where not enough lines are available at the beginning
        if start_idx < 0:
            start_extra = abs(start_idx)
            end_idx += start_extra
            start_idx = 0
        end_idx += 1
        # Slice selected section
        display_lines = wrapped_lines[start_idx:end_idx]

        # Render processed lines
        for i, (line, highlighted) in enumerate(display_lines):
            # Calculate line coordinates
            x = SECT_PADDING
            y_top = SECT_PADDING + self.line_height * (i + 1)
            y_bottom = y_top - self.line_height

            # Draw highlight background if necessary
            if highlighted:
                x_max = VID_VAR_X - SECT_PADDING
                self.draw.rectangle(((x, y_top), (x_max, y_bottom)), fill=CLR_HIGHLIGHT)

            # Draw text
            self.draw.text((x, y_bottom), line, font=self.body_font)

    def write_cur_frame(self, frame_info):
        self._finish_frame()
        self._start_frame()
        self._draw_code(frame_info)

    def _draw_exec(self, nr_times, cur, avg, total):
        x = SECT_PADDING
        # Padding + body
        y = SECT_PADDING + self.line_height * self.body_rows

        plural = "" if nr_times == 1 else "s"
        text = f"Line executed {nr_times} time{plural} — current time elapsed: {cur}, average: {avg}, total: {total}"
        self.draw.text((x, y), text, font=self.caption_font)

    def write_frame_exec(self, frame_info, exec_time, exec_times):
        nr_times = len(exec_times)
        avg_time = render.duration_ns(statistics.mean(exec_times))
        total_time = render.duration_ns(sum(exec_times))
        this_time = render.duration_ns(exec_time)

        self._draw_exec(nr_times, this_time, avg_time, total_time)

    def _draw_text_block(self, lines, x_top, y_left):
        for i, line in enumerate(lines):
            # Calculate line coordinates
            x = x_top
            y_top = y_left + self.line_height * (i + 1)
            y_bottom = y_top - self.line_height

            self.draw.text((x, y_bottom), line, fill=CLR_FG_BODY, font=self.body_font)

    def _draw_last_var(self, state):
        # Draw variable name
        nw, nh = self.draw.textsize(state.name + " ", font=self.body_font)
        self.draw.text((self.vars_x, self.vars_y - nh), state.name + " ", fill=CLR_FG_BODY, font=self.body_font)
        # Draw action with color
        self.draw.text((self.vars_x + nw, self.vars_y - nh), state.action, fill=state.color, font=self.body_bold_font)

        # Draw remaining text
        self._draw_text_block(state.text_lines, self.vars_x, self.vars_y)

    def _draw_other_vars(self, state):
        # Draw text
        self._draw_text_block(state.other_text_lines, self.ovars_x, self.ovars_y)

    def _draw_variables(self, state):
        self._draw_last_var(state)
        self._draw_other_vars(state)

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
        wrapped_text = wrap_text(text, int(self.vars_cols), int(self.vars_rows))

        # Render text for "others" section
        other_vars = []
        for var, values in history.other_history:
            var_lines = [var.name + ":"]

            for value in values:
                var_lines.append(repr(value.value))

            other_vars.append("\n    \u2022 ".join(var_lines))

        others_text = "\n\n".join(other_vars)
        wrapped_others_text = wrap_text(others_text, int(self.ovars_cols), int(self.ovars_rows))

        # Save state; this is drawn when the frame is finished
        self.last_var = VarState(name, color, action, wrapped_text, wrapped_others_text)

    def write_add(self, var, val, history, *, action="added", plural):
        self._write_action(var, CLR_GREEN, action, {"Value": repr(val)}, history)

    def write_change(self, var, val_before, val_after, history, *, action="changed"):
        self._write_action(
            var, CLR_BLUE, action, {"From": repr(val_before), "To": repr(val_after)}, history,
        )

    def write_remove(self, var, val, history, *, action="removed"):
        self._write_action(var, CLR_RED, action, {"Last value": repr(val)}, history)

    def write_summary(self, var_history, exec_start_time, exec_stop_time, frame_exec_times):
        # Video doesn't have a summary
        pass

    def close(self):
        # Finish final frame
        self._finish_frame()
        # Close writer
        self.writer.release()
