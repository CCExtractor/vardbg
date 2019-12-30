#!/usr/bin/env python3

import time


# Example function to debug
def test_func():  # sourcery off
    # Simple variable assignments
    y = 9
    x = y * 2
    x *= 2

    # List modification
    # noinspection PyListCreation
    lst = [1]
    lst.append(x)
    lst.append(y)
    del lst[2], lst[1]

    # Set modification
    st = {1}
    st.add(x)
    st.add(y)
    st.update({1, 2, 3, 4, 5})
    st.remove(x)

    # Dict modification
    # noinspection PyDictCreation
    dct = {"a": 1, "b": 2, "c": 3}
    dct["d"] = 4
    del dct["c"]

    # Multiple assignments on a single line
    v1, v2 = 0, 1
    v1, v2 = 1, 2

    # Multiple deletions on a single line
    del v1, v2

    # Executing lines multiple times and profiling them
    for i in range(5):
        time.sleep(0.01)
        pass

    # To facilitate verifying the debugger's values
    print("\nFinal test values:")
    print("\n".join(f"  {var} = {repr(val)}" for var, val in locals().items()))  # Convoluted to avoid mutating locals
