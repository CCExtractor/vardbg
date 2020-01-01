from . import output
from .diff_processor import DiffProcessor
from .profiler import Profiler
from .replayer import Replayer
from .tracer import Tracer


class Debugger(DiffProcessor, Profiler, Replayer, Tracer):
    def __init__(self, relative_paths=True, json_output_path=None, live_profiler_output=True):
        # Whether to use relative paths over absolute ones in output
        self.use_relative_paths = relative_paths

        # Whether to print profiler output live during execution
        self.live_profiler_output = live_profiler_output

        # Output writers
        writers = [output.ConsoleWriter()]
        if json_output_path is not None:
            writers.append(output.JsonWriter(json_output_path))
        self.out = output.OutputDelegate(*writers)

        # Initialize mixins
        super().__init__()

    def close(self):
        self.out.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def debug(func, *args, **kwargs):
    with Debugger(*args, **kwargs) as dbg:
        dbg.run(func)


def replay(json_path, *args, **kwargs):
    with Debugger(*args, **kwargs) as dbg:
        dbg.replay(json_path)
