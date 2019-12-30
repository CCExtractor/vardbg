from .console_output import ConsoleOutput
from .diff_processor import DiffProcessor
from .profiler import Profiler
from .tracer import Tracer


class Debugger(ConsoleOutput, DiffProcessor, Profiler, Tracer):
    def __init__(self, func, relative_paths=True):
        # Function being debugged
        self.func = func
        # Whether to use relative paths over absolute ones in output
        self.use_relative_paths = relative_paths

        # Initialize mixins
        super().__init__()


def debug(*args, **kwargs):
    Debugger(*args, **kwargs).run()
