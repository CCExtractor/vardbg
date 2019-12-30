import copy
import sys

import dictdiffer


RED = "\u001b[1;31m"
GREEN = "\u001b[1;32m"
BLUE = "\u001b[1;34m"
BOLD = "\u001b[1m"
RESET = "\u001b[0m"


def render_key_var(var, key):
    return f"{var}[{repr(key)}]"


def render_val(val):
    return f"{BOLD}{repr(val)}{RESET}"


class Debugger:
    def __init__(self, func):
        # Function being debugged
        self.func = func
        # Previous frame's locals
        self.prev_locals = {}
        # New frame's locals
        self.new_locals = {}
        # Current line output prefix
        self.cur_line = ""

    def print_action(self, var, color, action, suffix):
        print(f"{self.cur_line} | {BOLD}{var}{RESET} {color}{action}{RESET} {suffix}")

    def print_add(self, var, val, *, action="added", plural=False):
        _plural = "s" if plural else ""
        self.print_action(var, GREEN, action, f"with value{_plural} {render_val(val)}")

    def print_change(self, var, val_before, val_after, *, action="changed"):
        self.print_action(var, BLUE, action, f"from {render_val(val_before)} to {render_val(val_after)}")

    def print_remove(self, var, val, *, action="removed", plural=False):
        self.print_action(var, RED, action, f"(value: {render_val(val)})")

    def process_add(self, chg_var, chg):
        # If we have a changed variable, elements were added to a list/set/dict
        if chg_var:
            # Get a reference to the container to check its type
            container = self.new_locals[chg_var]

            # chg is a list of tuples with keys (index, key, etc.) and values
            for key, val in chg:
                if isinstance(container, set):
                    # Move value out of set if there's only 1
                    if len(val) == 1:
                        val = val.pop()

                    # Show it as an extension for sets
                    self.print_add(chg_var, val, action="extended", plural=isinstance(val, set))
                else:
                    # Render it as var[key] for lists, dicts, etc.
                    self.print_add(render_key_var(chg_var, key), val)

        # Otherwise, it's a new variable
        else:
            # chg is a list of tuples with variable names and values
            for var, val in chg:
                self.print_add(var, val)

    def process_change(self, chg_var, chg):
        # If the changed variable is given as a list, a list/set/dict element was changed
        if isinstance(chg_var, list):
            # chg_var is a tuple with the variable name and key
            var_name, key = chg_var
            # Render it as var_name[key]
            chg_var = f"{var_name}[{repr(key)}]"

        # chg_var is the variable that was changed
        # chg is a tuple with the before and after values
        before, after = chg
        self.print_change(chg_var, before, after)

    def process_remove(self, chg_var, chg):
        # If we have a changed variable, elements were removed from a list/set/dict
        if chg_var:
            for key, val in chg:
                self.print_remove(render_key_var(chg_var, key), val)

        # Otherwise, a variable was deleted
        else:
            # chg is a list of tuples with variable names and values
            for var, val in chg:
                self.print_remove(var, val, action="deleted")

    def process_locals_diff(self, diff):
        for action, chg_var, chg in diff:
            if action == dictdiffer.ADD:
                self.process_add(chg_var, chg)
            elif action == dictdiffer.CHANGE:
                self.process_change(chg_var, chg)
            elif action == dictdiffer.REMOVE:
                self.process_remove(chg_var, chg)

    def trace_callback(self, frame, event, arg):
        """Frame execution callback"""

        # Ignore all other functions
        code = frame.f_code
        if code != self.func.__code__:
            return

        # Get new locals and copy them so they don't change on the next frame
        self.new_locals = copy.deepcopy(frame.f_locals)

        # Construct friendly filename + line number + function string
        self.cur_line = f"{code.co_filename}:{frame.f_lineno} ({code.co_name})"

        # Diff and print changes
        diff = dictdiffer.diff(self.prev_locals, self.new_locals)
        self.process_locals_diff(diff)

        # Update previous locals in preparation for the next frame
        self.prev_locals = self.new_locals
        # Attach to the next line as well
        return self.trace_callback

    def run(self):
        # Run function with trace callback registered
        sys.settrace(self.trace_callback)
        self.func()
        sys.settrace(None)
