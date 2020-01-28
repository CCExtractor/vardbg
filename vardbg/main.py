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
    + " Note that it is recommended to perform video generation while replaying rather running because its overhead ruins profiler results."
)
VIDEO_CONFIG_HELP = "TOML video config overlay to load."

QUIET_DESC = "Silence console output."


@click.group(help=DESC, context_settings={"help_option_names": ("-h", "--help")})
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
@click.option(
    "-P", "--disable-live-profiler", default=False, is_flag=True, help="Disable live profiler output during execution."
)
@click.option("-q", "--quiet", default=False, is_flag=True, help=QUIET_DESC)
def run(file, function, arguments, output, video, video_config, absolute_paths, disable_live_profiler, quiet):
    # Load file as module
    mod_name = Path(file).stem
    spec = importlib.util.spec_from_file_location(mod_name, file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Get the function here regardless of which path we took above
    func = getattr(mod, function, None)
    if func is None:
        # Check how many functions are present in the module
        func_syms = [sym for sym in dir(mod) if callable(getattr(mod, sym))]
        if len(func_syms) == 1:
            # Safe to assume that the user wanted this one if it's the only one
            f_sym = func_syms[0]
            func = getattr(mod, f_sym)
            print(ansi.yellow(f"Unable to find function '{function}', falling back to the only one: '{f_sym}'"))
            print()
        else:
            # Ambiguous if multiple, so bail out and let the user choose
            print(ansi.red(f"Unable to find function '{function}' and multiple are present; aborting."))
            return 1

    # Call the actual debugger with our parameters
    debugger.debug(
        func,
        args=[file or func.__code__.co_filename, *arguments],
        relative_paths=not absolute_paths,
        json_out_path=output,
        video_out_path=video,
        video_config=video_config,
        live_profiler_output=not disable_live_profiler,
        quiet=quiet,
    )


@cli.command(help="Replay the given JSON session recording. The original source files must still be accessible.")
@click.argument("file")
@click.option("-v", "--video", metavar="PATH", help=VIDEO_HELP)
@click.option("-c", "--video-config", metavar="PATH", help=VIDEO_CONFIG_HELP)
@click.option("-q", "--quiet", default=False, is_flag=True, help=QUIET_DESC)
def replay(file, video, video_config, quiet):
    debugger.replay(file, video_out_path=video, video_config=video_config, quiet=quiet)


def main():
    cli()
