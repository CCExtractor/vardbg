import argparse
import importlib.util
from pathlib import Path

from . import ansi, test
from .debugger import debug


def parse_args():
    parser = argparse.ArgumentParser(
        description="A simple debugger that traces local variable changes, lines, and times."
    )

    parser.add_argument("-f", "--file", nargs="?", type=str, help="Python file to debug")
    parser.add_argument("-n", "--function", nargs="?", type=str, help="function to run from the given file")
    parser.add_argument(
        "-a",
        "--absolute-paths",
        default=False,
        action="store_true",
        help="whether to use absolute paths instead of relative ones",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    # Module defaults to test
    # Function defaults to test_func if no file specified, otherwise main
    if args.file is None:
        mod = test
        if args.function is None:
            args.function = "test_func"
    else:
        if args.function is None:
            args.function = "main"

        mod_name = Path(args.file).stem
        spec = importlib.util.spec_from_file_location(mod_name, args.file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

    # Get the function here regardless of which path we took above
    func = getattr(mod, args.function, None)
    if func is None:
        # Check how many functions are present in the module
        func_syms = [sym for sym in dir(mod) if callable(getattr(mod, sym))]
        if len(func_syms) == 1:
            # Safe to assume that the user wanted this one if it's the only one
            f_sym = func_syms[0]
            func = getattr(mod, f_sym)
            print(ansi.yellow(f"Unable to find function '{args.function}', falling back to the only one: '{f_sym}'"))
            print()
        else:
            # Ambiguous if multiple, so bail out and let the user choose
            print(ansi.red(f"Unable to find function '{args.function}' and multiple are present; aborting."))
            return 1

    # Call the actual debugger with our parameters
    debug(func, relative_paths=not args.absolute_paths)
    return 0
