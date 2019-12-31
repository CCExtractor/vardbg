from . import output
from .diff_processor import DiffProcessor
from .profiler import Profiler
from .tracer import Tracer


class Debugger(DiffProcessor, Profiler, Tracer):
    def __init__(self, relative_paths=True):
        # Whether to use relative paths over absolute ones in output
        self.use_relative_paths = relative_paths

        # Output writer
        self.out = output.OutputDelegate(output.ConsoleWriter())

        # Initialize mixins
        super().__init__()


def debug(func, *args, **kwargs):
    Debugger(*args, **kwargs).run(func)
