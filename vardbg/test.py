#!/usr/bin/env python3

import math
import sys
import time


# Sample function to get the value of tau (pi * 2)
def get_tau():
    x = math.pi
    x *= 2
    return x


# Example function to debug
def test_func():  # sourcery off
    # Print given arguments
    print("Arguments:", " ".join(sys.argv[1:]))

    # Simple variable assignments
    y = 9
    x = y * 2
    x *= 2
    print("x =", x)

    # Hidden variable
    c = 1  # vardbg: ignore

    # Adding to a list
    # noinspection PyListCreation
    lst = [1]
    lst.append(x)
    lst.append(y)

    # Deleting from a list
    del lst[2], lst[1]
    print("lst =", lst)

    # Set modification
    st = {1}
    st.add(x)
    st.add(y)
    st.update({1, 2, 3, 4, 5})
    st.remove(x)
    print("st =", st)

    # Dict modification
    # noinspection PyDictCreation
    dct = {"a": 1, "b": 2, "c": 3}
    dct["d"] = 4
    del dct["c"]
    print("dct =", dct)

    # Multiple assignments on a single line
    v1, v2 = 0, 1
    v1, v2 = 1, 2

    # Multiple deletions on a single line
    del v1, v2

    # Executing lines multiple times and profiling them
    lst += [6, 7, 12, 14]
    # Variable relationships
    for i in range(len(lst)):  # vardbg: ref lst[i]
        print("i =", i)
        time.sleep(0.01)
        pass  # This is an intentionally very long line that exists solely for the purpose of testing line wrapping functionality in the video output writer's text renderer, ignore and do not wrap this line so that it remains useful for its purpose

    # Get tau from another function
    tau = get_tau()
    print("tau =", tau)

    # To facilitate verifying the debugger's values
    print("\nFinal test values:")
    print("\n".join(f"  {var} = {repr(val)}" for var, val in locals().items()))  # Convoluted to avoid mutating locals
