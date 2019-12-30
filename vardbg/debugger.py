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


def render_file_line(frame):
    return f"{frame.f_code.co_filename}:{frame.f_lineno}"


class Variable:
    """Holds information about a variable"""

    def __init__(self, name, frame):
        # Basic variable info
        self.name = name
        self.deleted_line = None  # file:line

        # Extract info from frame
        self._file = frame.f_code.co_filename
        self.file_line = render_file_line(frame)
        self.function = frame.f_code.co_name

    def to_tuple(self):
        # This produces an identifying tuple for hashing and equality comparison.
        # We ignore value, type, and line here because they can change
        return (self.name, self._file, self.function)

    def __hash__(self):
        return hash(self.to_tuple())

    def __eq__(self, other):
        return self.to_tuple() == other.to_tuple()

    def __ne__(self, other):
        return not (self == other)


class VarValue:
    """Holds information about a variable value"""

    def __init__(self, value, frame):
        self.value = value
        self.file_line = render_file_line(frame)

    @staticmethod
    def value_getter(val):
        return val.value


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
        # Full variable + values map
        self.vars = {}

    def print_action(self, var, color, action, suffix):
        print(f"{self.cur_line} | {BOLD}{var}{RESET} {color}{action}{RESET} {suffix}")

    def print_add(self, var, val, *, action="added", plural=False):
        _plural = "s" if plural else ""
        self.print_action(var, GREEN, action, f"with value{_plural} {render_val(val)}")

    def print_change(self, var, val_before, val_after, *, action="changed"):
        self.print_action(var, BLUE, action, f"from {render_val(val_before)} to {render_val(val_after)}")

    def print_remove(self, var, val, *, action="removed", plural=False):
        self.print_action(var, RED, action, f"(value: {render_val(val)})")

    def process_add(self, chg_name, chg, frame):
        # If we have a changed variable, elements were added to a list/set/dict
        if chg_name:
            # Get a reference to the container to check its type
            container = self.new_locals[chg_name]

            # chg is a list of tuples with keys (index, key, etc.) and values
            for key, val in chg:
                if isinstance(container, set):
                    # Move value out of set if there's only 1
                    if len(val) == 1:
                        val = val.pop()

                    # Show it as an extension for sets
                    self.print_add(chg_name, val, action="extended", plural=isinstance(val, set))
                else:
                    # Render it as var[key] for lists, dicts, etc.
                    self.print_add(render_key_var(chg_name, key), val)

            self.vars[Variable(chg_name, frame)].append(VarValue(container, frame))

        # Otherwise, it's a new variable
        else:
            # chg is a list of tuples with variable names and values
            for name, val in chg:
                self.print_add(name, val)
                self.vars[Variable(name, frame)] = [VarValue(val, frame)]

    def process_change(self, chg_name, chg, frame):
        # If the changed variable is given as a list, a list/set/dict element was changed
        if isinstance(chg_name, list):
            # chg_name is a tuple with the variable name and key
            var_name, key = chg_name
            # Render it as var_name[key]
            chg_name = f"{var_name}[{repr(key)}]"
        else:
            var_name = chg_name

        # chg_name is the variable that was changed
        # chg is a tuple with the before and after values
        before, after = chg
        self.print_change(chg_name, before, after)
        self.vars[Variable(var_name, frame)].append(VarValue(after, frame))

    def process_remove(self, chg_name, chg, frame):
        # If we have a changed variable, elements were removed from a list/set/dict
        if chg_name:
            for key, val in chg:
                self.print_remove(render_key_var(chg_name, key), val)

        # Otherwise, a variable was deleted
        else:
            # chg is a list of tuples with variable names and values
            for name, val in chg:
                self.print_remove(name, val, action="deleted")

                # Find existing equivalent variable object
                new_var = Variable(name, frame)
                var = list(filter(lambda v: v == new_var, self.vars.keys()))[0]
                var.deleted_line = render_file_line(frame)

    def process_locals_diff(self, diff, frame):
        for action, chg_var, chg in diff:
            if action == dictdiffer.ADD:
                self.process_add(chg_var, chg, frame)
            elif action == dictdiffer.CHANGE:
                self.process_change(chg_var, chg, frame)
            elif action == dictdiffer.REMOVE:
                self.process_remove(chg_var, chg, frame)

    def trace_callback(self, frame, event, arg):
        """Frame execution callback"""

        # Ignore all other functions
        code = frame.f_code
        if code != self.func.__code__:
            return

        # Get new locals and copy them so they don't change on the next frame
        self.new_locals = copy.deepcopy(frame.f_locals)

        # Construct friendly filename + line number + function string
        self.cur_line = f"{render_file_line(frame)} ({code.co_name})"

        # Diff and print changes
        diff = dictdiffer.diff(self.prev_locals, self.new_locals)
        self.process_locals_diff(diff, frame)

        # Update previous locals in preparation for the next frame
        self.prev_locals = self.new_locals
        # Subscribe to the next frame, if any
        return self.trace_callback

    def print_summary(self):
        print()
        print("All variables:")

        for var, values in self.vars.items():
            # Check whether all the values were numbers
            if all(isinstance(val.value, (int, float)) for val in values):
                # Give a min-max range for numbers
                min_val = min(values, key=VarValue.value_getter)
                max_val = max(values, key=VarValue.value_getter)

                min_desc = f"{render_val(min_val.value)} ({min_val.file_line})"
                max_desc = f"{render_val(max_val.value)} ({max_val.file_line})"
                values_desc = f" between {min_desc} and {max_desc}"
            else:
                # Give a list of values for other objects
                value_lines = [":"]

                for val in values:
                    value_lines.append(f"{render_val(val.value)} ({val.file_line})")

                # Format list
                values_desc = "\n      - ".join(value_lines)

            definition = f"in {var.function} on {BOLD}{var.file_line}{RESET}"
            print(f"  - {BOLD}{var.name}{RESET} {GREEN}defined{RESET} {definition} with values{values_desc}")

            if var.deleted_line is not None:
                print(f"    ({RED}deleted{RESET} on {var.deleted_line})")

    def run(self):
        # Run function with trace callback registered
        sys.settrace(self.trace_callback)
        self.func()
        sys.settrace(None)

        self.print_summary()
