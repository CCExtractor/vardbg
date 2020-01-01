from .sorting import bubble_sort, merge_sort, insertion_sort, shell_sort, selection_sort
from .run import debug_func
from vardbg import ansi

SORT_FUNCS = (bubble_sort, merge_sort, insertion_sort, shell_sort, selection_sort)
SAMPLE_LIST = [19, 2, 31, 45, 6, 11, 121, 27]


def test_sorting():
    for func in SORT_FUNCS:
        print("\n" + ansi.bold(func.__name__.replace("_", " ").title()))
        sorted_list = debug_func(func, SAMPLE_LIST.copy())

        print(sorted_list)
        print()
