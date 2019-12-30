from .console_output import ConsoleOutput
from .diff_processor import DiffProcessor
from .profiler import Profiler
from .tracer import Tracer


class Debugger(ConsoleOutput, DiffProcessor, Profiler, Tracer):
    def __init__(self, func):
        # Function being debugged
        self.func = func

        # Initialize mixins
        super().__init__()


def debug(func):
    Debugger(func).run()
