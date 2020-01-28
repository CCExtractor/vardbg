# vardbg

A simple Python debugger and profiler that generates animated visualizations of program flow.

**Python 3.6** or newer is required due to the use of f-strings.

This project was created during [Google Code-in](https://codein.withgoogle.com/) 2019 for [CCExtractor Development](https://ccextractor.org/).

## Demo

![Demo Video](https://user-images.githubusercontent.com/7930239/72689524-12691180-3ac7-11ea-9547-861454b1496d.gif)

## Features

- Tracking the history of each variable and its contents
- Tracking elements within containers (lists, sets, dicts, etc.)
- Ignoring specific variables
- Profiling the execution of each line
- Summarizing all variables and execution times after execution
- Passing arguments to debugged programs
- Exporting execution history in JSON format and replaying (including program output)
- Creating videos that show program flow, execution times, variables (with relationships), and output
- Writing videos in MP4, GIF, and WebP formats

## Installation

The latest tagged version can be obtained from PyPI:

```bash
pip install vardbg
```

Alternatively, one can clone this repository and run it directly after installing dependencies:

```bash
git clone https://github.com/CCExtractor/vardbg
cd vardbg
python3 -m venv venv
source venv/bin/activate
pip install poetry
poetry install .
./debug.py [...]
```

The above instructions assume the use of a virtual environment to avoid interfering with the system install of Python.

## Usage

All of the program's options are documented in the usage help:

```
$ vardbg --help
usage: vardbg [-h] [-n [FUNCTION]] [-o [OUTPUT]] [-v [VIDEO]] [-c [CONFIG]] [-a [ARGS [ARGS ...]]] [-p] [-P] FILE

A simple Python debugger and profiler that can generate animated visualizations of program flow.

positional arguments:
  FILE                  Python file to debug or JSON file to replay

optional arguments:
  -h, --help            show this help message and exit
  -n [FUNCTION], --function [FUNCTION]
                        function to run from the given file (if applicable, default main)
  -o [OUTPUT], --output-file [OUTPUT]
                        path to write JSON output file to (will be truncated/created if necessary)
  -v [VIDEO], --video [VIDEO]
                        path to write a video representation of the program flow to (supports MP4, GIF, and WebP formats based on file extension)
  -c [CONFIG], --video-config [CONFIG]
                        path to the TOML video output config
  -a [ARGS [ARGS ...]], --args [ARGS [ARGS ...]]
                        list of arguments to pass to the running program
  -p, --absolute-paths  use absolute paths instead of relative ones
  -P, --disable-live-profiler
                        disable live profiler output during execution
```

For example, this command will debug the function `quick_sort` from the file `sort.py` with the arguments `9 3 5 1` and create a JSON file called `sort1.json`:

```bash
vardbg sort.py -n quick_sort -o qsort.json -a 9 3 5 1
```

A video can then be generated from the above JSON:

```bash
vardbg qsort.json -v sort_vis.mp4
```

It is possible to generate videos live while running the debugged program, but this is discouraged because the overhead of video creation inflates execution times greatly and thus ruins profiler results. However, if profiling is not important to you, it is a valid use case.

## Configuration

The video generator has many options: resolution, speed, fonts, and sizes. These options can be modified using a [TOML](https://learnxinyminutes.com/docs/toml/) config file. The [default config](https://github.com/CCExtractor/vardbg/blob/master/vardbg/output/video_writer/default_config.toml) documents the available options, which can be customized in an minimal overlay config without having to duplicate the entire config. The config can then be used by passing the `-c` argument on the command line.

An example of a simple overlay is the [config](https://github.com/CCExtractor/vardbg/blob/master/demo_config.toml) used to generate official demo videos for embedding in READMEs. This simple config increases the speed (FPS) slightly and adds an intro screen at the beginning of the video.

## Behavior Control

Special comments can be added to lines of code that define variables to control how vardbg handles said variable:

- `# vardbg: ignore` — do not display this variable or track its values
- `# vardbg: ref lst[i]` — treat variable `i` as the index/key of an element in container `lst` (only shown in videos)

## Contributing

Feel free to contribute to this project! You can add features, fix bugs, or make any other improvements you see fit. We just ask that you follow the [code style guidelines](https://github.com/CCExtractor/vardbg/blob/master/CODE_STYLE.md) to keep the code consistent and coherent. Once your contribution meets the guidelines, [open a pull request](https://github.com/CCExtractor/vardbg/compare) to make things official.
