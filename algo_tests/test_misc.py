from .misc import knapsack
from .run import debug_func
from vardbg import ansi

# | Item | Weight | Value |
# |------|--------|-------|
# | 1    | 2      | 1     |
# | 2    | 10     | 20    |
# | 3    | 3      | 3     |
# | 4    | 6      | 14    |
# | 5    | 18     | 100   |

# Put a placeholder 0 weight, 0 value item to max
# these line up better with the 1D memoization table K
KS_WEIGHTS = [0, 2, 10, 3, 6, 18]
KS_VALUES = [0, 1, 20, 3, 14, 100]


def test_misc():
    print(ansi.bold("Knapsack"))
    debug_func(knapsack, KS_WEIGHTS, KS_VALUES)
