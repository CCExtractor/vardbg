#!/usr/bin/env python3

import copy
import sys

import dictdiffer


RED = "\u001b[1;31m"
GREEN = "\u001b[1;32m"
BLUE = "\u001b[1;34m"
BOLD = "\u001b[1m"
RESET = "\u001b[0m"

# Example function to debug
def test_func():
    y = 9
    x = y * 2
    x *= 2

    lst = [1]
    lst.append(x)
    lst.append(y)
    del lst[2], lst[1]

    st = {1}
    st.add(x)
    st.add(y)
    st.update({1, 2, 3, 4, 5})
    st.remove(x)

    dct = {"a": 1, "b": 2, "c": 3}
    dct["d"] = 4
    del dct["c"]

    v1, v2 = 0, 1
    v1, v2 = 1, 2

    del v1, v2

    print(y, x, lst, st, dct)


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
                # If we have a changed variable, elements were added to a list/set/dict
                if chg_var:
                    # Get a reference to the container to check its type
                    container = new_locals[chg_var]

                    # chg is a list of tuples with keys (index, key, etc.) and values
                    for key, val in chg:
                        if isinstance(container, set):
                            # Show it as an extension for sets
                            print(f"{line} {BOLD}{chg_var}{RESET} {GREEN}extended{RESET} with {BOLD}{repr(val)}{RESET}")
                        else:
                            # Render it as var[key] for lists, dicts, etc.
                            print(f"{line} {BOLD}{chg_var}[{repr(key)}]{RESET} {GREEN}added{RESET} with value {BOLD}{repr(val)}{RESET}")
                # Otherwise, it's a new variable
                else:
                    # chg is a list of tuples with variable names and values
                    for var, val in chg:
                        print(f"{line} {BOLD}{var}{RESET} {GREEN}added{RESET} with value {BOLD}{repr(val)}{RESET}")
            elif action == dictdiffer.CHANGE:
                # If the changed variable is given as a list, a list/set/dict element was changed
                if isinstance(chg_var, list):
                    # chg_var is a tuple with the variable name and key
                    var_name, key = chg_var
                    # Render it as var_name[key]
                    chg_var = f"{var_name}[{repr(key)}]"

                # chg_var is the variable that was changed
                # chg is a tuple with the before and after values
                before, after = chg
                print(f"{line} {BOLD}{chg_var}{RESET} {BLUE}changed{RESET} from {BOLD}{repr(before)}{RESET} to {BOLD}{repr(after)}{RESET}")
            elif action == dictdiffer.REMOVE:
                # If we have a changed variable, elements were removed from a list/set/dict
                if chg_var:
                    for key, val in chg:
                        print(f"{line} {BOLD}{chg_var}[{repr(key)}]{RESET} {RED}removed{RESET} (value: {BOLD}{repr(val)}{RESET})")
                # Otherwise, a variable was deleted
                else:
                    # chg is a list of tuples with variable names and values
                    for var, val in chg:
                        print(f"{line} {BOLD}{var}{RESET} {RED}deleted{RESET} (value: {BOLD}{repr(val)}{RESET})")

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
