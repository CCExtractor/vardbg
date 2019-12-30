#!/usr/bin/env python3

import copy
import sys

import dictdiffer


RED = "\u001b[1;31m"
GREEN = "\u001b[1;32m"
BLUE = "\u001b[1;34m"
RESET = "\u001b[0m"

# Example function to debug
def test_func():
    y = 9
    x = y * 2
    x *= 2

    lst = [1]
    st = {1}

    v1, v2 = 0, 1
    v1, v2 = 1, 2

    del v1, v2

    print(y, x, lst, st)


def debug_func(func):
    # Previous frame's locals
    fn_locals = {}

    # Frame execution callback
    def trace_callback(frame, event, arg):
        # Inherit fn_locals from debug_func
        nonlocal fn_locals

        # Ignore all other functions
        if frame.f_code != func.__code__:
            return

        # Get new locals and copy them so that they don't change on the next frame
        new_locals = copy.deepcopy(frame.f_locals)
        # Construct friendly filename + line number string
        line = f"{frame.f_code.co_filename}:{frame.f_lineno} |"

        # Diff and print changes
        for action, chg_var, chg in dictdiffer.diff(fn_locals, new_locals):
            if action == dictdiffer.ADD:
                # chg is a list of tuples with variable names and values
                for var, val in chg:
                    print(f"{line} {var} {GREEN}added{RESET} with value {repr(val)}")
            elif action == dictdiffer.CHANGE:
                # chg_var is the variable that was changed
                # chg is a tuple with the before and after values
                before, after = chg
                print(
                    f"{line} {chg_var} {BLUE}changed{RESET} from {repr(before)} to {repr(after)}"
                )
            elif action == dictdiffer.REMOVE:
                # chg is a list of tuples with variable names and values
                for var, val in chg:
                    print(f"{line} {var} {RED}deleted{RESET} (value: {repr(val)})")

        # Update previous locals variable
        fn_locals = new_locals

        # Attach to the next line as well
        return trace_callback

    # Install callback
    sys.settrace(trace_callback)

    # Run function
    func()

    # Remove callback
    sys.settrace(None)


if __name__ == "__main__":
    # Run debugger on test function
    debug_func(test_func)
