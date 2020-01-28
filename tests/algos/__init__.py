from vardbg import ansi

from .test_misc import test_misc
from .test_searching import test_searching
from .test_sorting import test_sorting


def run_tests():
    print(ansi.bold("SORTING TESTS"))
    print(ansi.bold("============="))
    test_sorting()

    print()
    print()
    print(ansi.bold("SEARCHING TESTS"))
    print(ansi.bold("==============="))
    test_searching()

    print()
    print()
    print(ansi.bold("MISCELLANEOUS TESTS"))
    print(ansi.bold("==================="))
    test_misc()
