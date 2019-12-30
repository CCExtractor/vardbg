import abc
from typing import TYPE_CHECKING

from . import ansi, data, render

if TYPE_CHECKING:
    from .debugger import Debugger


class ConsoleOutput(abc.ABC):
    def __init__(self: "Debugger"):
        # Current line output prefix
        self.cur_line = ""

        # Propagate initialization to other mixins
        super().__init__()

    def update_cur_frame(self: "Debugger", frame_info):
        # Construct friendly filename + line number + function string
        self.cur_line = f"{frame_info.file_line} ({frame_info.function})"

    def print_action(self: "Debugger", var, color_func, action, suffix):
        print(f"{self.cur_line} | {ansi.bold(var)} {color_func(action)} {suffix}")

    def print_add(self: "Debugger", var, val, *, action="added", plural=False):
        _plural = "s" if plural else ""
        self.print_action(var, ansi.green, action, f"with value{_plural} {render.val(val)}")

    def print_change(self: "Debugger", var, val_before, val_after, *, action="changed"):
        self.print_action(
            var, ansi.blue, action, f"from {render.val(val_before)} to {render.val(val_after)}",
        )

    def print_remove(self: "Debugger", var, val, *, action="removed"):
        self.print_action(var, ansi.red, action, f"(value: {render.val(val)})")

    def print_summary(self: "Debugger"):
        print()
        print("All variables:")

        for var, values in self.vars.items():
            # Check whether all the values were numbers
            if all(isinstance(val.value, (int, float)) for val in values):
                # Give a min-max range for numbers
                min_val = min(values, key=data.VarValue.value_getter)
                max_val = max(values, key=data.VarValue.value_getter)

                min_desc = f"{render.val(min_val.value)} ({min_val.file_line})"
                max_desc = f"{render.val(max_val.value)} ({max_val.file_line})"
                values_desc = f" between {min_desc} and {max_desc}"
            else:
                # Give a list of values for other objects
                value_lines = [":"]

                for val in values:
                    value_lines.append(f"{render.val(val.value)} ({val.file_line})")

                # Format list
                values_desc = "\n      - ".join(value_lines)

            definition = f"in {var.function} on {ansi.bold(var.file_line)}"
            print(f"  - {ansi.bold(var.name)} {ansi.green('defined')} {definition} with values{values_desc}")

            if var.deleted_line is not None:
                print(f"    ({ansi.red('deleted')} on {var.deleted_line})")
