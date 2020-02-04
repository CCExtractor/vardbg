from . import output
from .diff_processor import DiffProcessor
from .profiler import Profiler
from .replayer import Replayer
from .tracer import Tracer


class Debugger(DiffProcessor, Profiler, Replayer, Tracer):
    def __init__(
        self,
        args=None,
        relative_paths=True,
        json_out_path=None,
        video_out_path=None,
        video_config=None,
        profiler_output=False,
        quiet=False,
    ):
        # Arguments to pass to snippet (handled in run())
        self.args = args

        # Whether to use relative paths over absolute ones in output
        self.use_relative_paths = relative_paths

        # Whether to show profiler output
        self.profiler_output = profiler_output

        # Output writers
        writers = []
        if not quiet:
            writers.append(output.ConsoleWriter())
        if json_out_path is not None:
            writers.append(output.JsonWriter(json_out_path))
        if video_out_path is not None:
            writers.append(output.VideoWriter(video_out_path, video_config, profiler_output))
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
