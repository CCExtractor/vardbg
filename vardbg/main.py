import importlib.util
from pathlib import Path

import click

from . import ansi, debugger

DESC = "A simple Python debugger and profiler that can generate animated visualizations of program flow."

VIDEO_HELP = (
    "Write a video representation of the program flow (supports MP4, GIF, and WebP formats based on file extension)."
)
VIDEO_RUN_HELP = (
    VIDEO_HELP
    + " Note that it is recommended to perform video generation while replaying rather running because its overhead distorts profiler results."
)
VIDEO_CONFIG_HELP = "TOML video config overlay to load."

QUIET_DESC = "Silence console output."


def err(message):
    click.secho(message, fg="red", bold=True)
    click.get_current_context().abort()


def warn(message):
    click.secho(message, fg="yellow", bold=True)


class PrefixAliasGroup(click.Group):
    def get_command(self, ctx, cmd_name):
        rv = super().get_command(ctx, cmd_name)
        if rv is not None:
            return rv

        matches = [x for x in self.list_commands(ctx) if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return super().get_command(ctx, matches[0])

        ctx.fail("Too many matches: %s" % ", ".join(sorted(matches)))


@click.group(help=DESC, context_settings={"help_option_names": ("-h", "--help")}, cls=PrefixAliasGroup)
def cli():
    pass


@cli.command(help="Run and debug the given Python file.")
@click.argument("file")
@click.argument("function", required=False, default="main")
@click.option("-a", "--arguments", multiple=True, metavar="ARGS", help="Arguments to pass to the program.")
@click.option("-o", "--output", metavar="PATH", help="Write a JSON session recording.")
@click.option("-v", "--video", metavar="PATH", help=VIDEO_RUN_HELP)
@click.option("-c", "--video-config", metavar="PATH", help=VIDEO_CONFIG_HELP)
@click.option(
    "-p", "--absolute-paths", default=False, is_flag=True, help="Use absolute paths instead of relative ones."
)
@click.option("-P", "--enable-profiler", default=False, is_flag=True, help="Enable profiler output.")
@click.option("-q", "--quiet", default=False, is_flag=True, help=QUIET_DESC)
def run(file, function, arguments, output, video, video_config, absolute_paths, enable_profiler, quiet):
    # Load file as module
    mod_name = Path(file).stem
    spec = importlib.util.spec_from_file_location(mod_name, file)
    if spec is None:
        err(f"Module '{file}' not found")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Get the function here regardless of which path we took above
    func = getattr(mod, function, None)
    if func is None:
        err(f"Unable to find function '{function}'")

    # Check whether it's callable
    if not callable(func):
        err(f"Object '{function}' is not callable")

    # Call the actual debugger with our parameters
    debugger.debug(
        func,
        args=[file or func.__code__.co_filename, *arguments],
        relative_paths=not absolute_paths,
        json_out_path=output,
        video_out_path=video,
        video_config=video_config,
        profiler_output=enable_profiler,
        quiet=quiet,
    )


@cli.command(help="Replay the given JSON session recording. The original source files must still be accessible.")
@click.argument("file")
@click.option("-v", "--video", metavar="PATH", help=VIDEO_HELP)
@click.option("-c", "--video-config", metavar="PATH", help=VIDEO_CONFIG_HELP)
@click.option("-P", "--enable-profiler", default=False, is_flag=True, help="Enable profiler output.")
@click.option("-q", "--quiet", default=False, is_flag=True, help=QUIET_DESC)
def replay(file, video, video_config, enable_profiler, quiet):
    debugger.replay(file, video_out_path=video, video_config=video_config, profiler_output=enable_profiler, quiet=quiet)


def main():
    cli()
