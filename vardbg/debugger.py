from .console_output import ConsoleOutput
from .diff_processor import DiffProcessor
from .profiler import Profiler
from .tracer import Tracer


class Debugger(ConsoleOutput, DiffProcessor, Profiler, Tracer):
    def __init__(self, func):
        # Function being debugged
        self.func = func
        # Current line output prefix
        self.cur_line = ""

        # Initialize mixins
        super().__init__()
