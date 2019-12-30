#!/usr/bin/env python3

from debugger import Debugger

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


if __name__ == "__main__":
    # Run debugger on test function
    Debugger(test_func).run()
