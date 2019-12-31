from .test_misc import test_misc
from .test_searching import test_searching
from .test_sorting import test_sorting
from vardbg import ansi


def run_tests():
    print(ansi.bold("SORTING TESTS"))
    print(ansi.bold("============="))
    test_sorting()

    print()
    print(ansi.bold("SEARCHING TESTS"))
    print(ansi.bold("==============="))
    test_searching()

    print()
    print(ansi.bold("MISCELLANEOUS TESTS"))
    print(ansi.bold("==================="))
    test_misc()
