import textwrap
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

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


class FrameRenderer:
    RED = 0
    GREEN = 1
    BLUE = 2

    # noinspection PyUnresolvedReferences
    def __init__(self, path, config):
        # Video writer
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.writer = cv2.VideoWriter(path, fourcc, VID_FPS, (VID_W, VID_H))
        # Drawing context
        self.draw = None
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

    @classmethod
    def get_color(cls, col):
        if col == cls.RED:
            return CLR_RED
        elif col == cls.GREEN:
            return CLR_GREEN
        else:
            return CLR_BLUE

    def draw_text_center(self, x, y, text, font, color):
        w, h = self.draw.textsize(text, font=font)
        self.draw.text((x - w / 2, y - h / 2), text, font=font, fill=color)

    def start_frame(self):
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
        self.draw_text_center(var_center_x, HEADER_PADDING, "Last Variable", self.head_font, CLR_FG_HEADING)

        # Draw other variables section
        # Horizontal divider at 1/3 height
        self.draw.line(((VID_VAR_X, VID_VAR_OTHER_Y), (VID_W, VID_VAR_OTHER_Y)), fill=CLR_FG_BODY, width=1)
        # Label similar to the first, but in the others section instead
        ovar_label_y = VID_VAR_OTHER_Y + HEADER_PADDING
        self.draw_text_center(var_center_x, ovar_label_y, "Other Variables", self.head_font, CLR_FG_HEADING)

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

    def finish_frame(self, var_state):
        # Bail out if there's no frame to finish
        if self.frame is None:
            return

        # Draw variable state (if available)
        if var_state is not None:
            self.draw_variables(var_state)

        # Convert PIL -> Numpy array and RGBA -> BGR colors
        # noinspection PyUnresolvedReferences
        cv_img = cv2.cvtColor(np.asarray(self.frame), cv2.COLOR_RGBA2BGR)
        # Write data
        self.writer.write(cv_img)

    def draw_code(self, lines, cur_line):
        cur_idx = cur_line - 1

        # Construct list of (line, highlighted) tuples
        unwrapped_lines = [(line, i == cur_idx) for i, line in enumerate(lines)]

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

    def draw_exec(self, nr_times, cur, avg, total):
        x = SECT_PADDING
        # Padding + body
        y = SECT_PADDING + self.line_height * self.body_rows

        plural = "" if nr_times == 1 else "s"
        text = f"Line executed {nr_times} time{plural} — current time elapsed: {cur}, average: {avg}, total: {total}"
        self.draw.text((x, y), text, font=self.caption_font)

    def draw_text_block(self, lines, x_top, y_left):
        for i, line in enumerate(lines):
            # Calculate line coordinates
            x = x_top
            y_top = y_left + self.line_height * (i + 1)
            y_bottom = y_top - self.line_height

            self.draw.text((x, y_bottom), line, fill=CLR_FG_BODY, font=self.body_font)

    def draw_last_var(self, state):
        # Draw variable name
        nw, nh = self.draw.textsize(state.name + " ", font=self.body_font)
        self.draw.text((self.vars_x, self.vars_y - nh), state.name + " ", fill=CLR_FG_BODY, font=self.body_font)
        # Draw action with color
        self.draw.text((self.vars_x + nw, self.vars_y - nh), state.action, fill=state.color, font=self.body_bold_font)

        # Draw remaining text
        self.draw_text_block(state.text_lines, self.vars_x, self.vars_y)

    def draw_other_vars(self, state):
        # Draw text
        self.draw_text_block(state.other_text_lines, self.ovars_x, self.ovars_y)

    def draw_variables(self, state):
        self.draw_last_var(state)
        self.draw_other_vars(state)

    def close(self, var_state):
        # Finish final frame
        self.finish_frame(var_state)
        # Close writer
        self.writer.release()
