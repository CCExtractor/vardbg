TRUNC_SUFFIX = " [...]"


class TextPainter:
    def __init__(self, renderer, x_start, y_start, cols, rows, color=None, x_end=None, show_truncate=True):
        self.render = renderer
        self.draw = renderer.draw
        self.font = renderer.body_font
        self.bold_font = renderer.body_bold_font
        self.line_height = renderer.line_height
        self.color = color or renderer.cfg.fg_body

        self.show_truncate = show_truncate

        self.x_start = x_start
        self.y_start = y_start
        self.cols = cols
        self.rows = rows
        self.x_end = x_end or x_start

        self.full = False
        self.cols_used = 0
        self.rows_used = 0
        self.cur_x = x_start
        self.cur_y = y_start
        self.last_line_y = None

    def new_line(self):
        self.rows_used += 1
        if self.rows_used == self.rows:
            # Show truncation indicator if requested and enough space remains
            if self.show_truncate and self.cols_used < self.cols - len(TRUNC_SUFFIX):
                self.write(TRUNC_SUFFIX)

            self.full = True
        else:
            self.cols_used = 0
            self.cur_x = self.x_start
            self.cur_y += self.line_height

    def write(self, text, bold=False, color=None, bg_color=None, return_pos="V"):
        font = self.bold_font if bold else self.font
        color = color or self.color
        last_draw_x = self.cur_x
        last_draw_y = self.cur_y
        tw = 0

        lines = text.split("\n")
        for idx, line in enumerate(lines):
            while not self.full and line:
                # Calculate space and coordinates
                cols_remaining = self.cols - self.cols_used
                y_bottom = self.cur_y - self.line_height
                is_continuation = self.cols_used != 0

                # Draw background if requested
                if bg_color is not None:
                    self.draw.rectangle(((self.cur_x, self.cur_y), (self.x_end, y_bottom)), fill=bg_color)

                draw_seg = line[:cols_remaining]
                # Get text size and center it vertically
                tw, th = self.render.text_size(draw_seg, font=font)
                if is_continuation:
                    center_y = self.last_line_y
                else:
                    center_y = y_bottom + ((self.line_height - th) / 2)
                # Draw text
                self.draw.text((self.cur_x, center_y), draw_seg, font=font, fill=color)
                # Account for drawn text
                self.cur_x += tw
                self.cols_used += len(draw_seg)
                line = line[cols_remaining:]
                self.last_line_y = center_y

                # Advance line if text is remaining
                if line:
                    self.new_line()

            last_draw_x = self.cur_x
            last_draw_y = self.cur_y

            # Advance line if there are more lines
            if idx != len(lines) - 1:
                self.new_line()

        # Return requested position
        if return_pos == "H":
            return last_draw_x - tw / 2, last_draw_y - self.line_height
        elif return_pos == "V":
            return last_draw_x, last_draw_y - self.line_height / 2
