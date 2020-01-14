# vardbg

A simple Python debugger and profiler that generates animated visualizations of program flow.

**Python 3.6** or newer is required due to the use of f-strings.

This project was created during [Google Code-in](https://codein.withgoogle.com/) 2019 for [CCExtractor Development](https://ccextractor.org/).

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

## Usage

All of the program's options are documented in the usage help:

```
$ vardbg --help
usage: vardbg [-h] [-f [FILE]] [-n [FUNCTION]] [-o [OUTPUT_FILE]] [-v [PATH]] [-c [CONFIG]]
              [-a [ARGS [ARGS ...]]] [-p] [-P]

A simple debugger that traces local variable changes, lines, and times.

optional arguments:
  -h, --help            show this help message and exit
  -f [FILE], --file [FILE]
                        Python file to debug, or JSON result file to read
  -n [FUNCTION], --function [FUNCTION]
                        function to run from the given file (if applicable)
  -o [OUTPUT_FILE], --output-file [OUTPUT_FILE]
                        path to write JSON output file to, default debug_results.json (will be truncated if it
                        already exists and created otherwise)
  -v [PATH], --video [PATH]
                        path to write a video representation of the program execution to (MP4 and GIF formats
                        are supported, depending on file extension)
  -c [CONFIG], --video-config [CONFIG]
                        path to the TOML config for the video output format, default video.toml
  -a [ARGS [ARGS ...]], --args [ARGS [ARGS ...]]
                        list of arguments to pass to the running program
  -p, --absolute-paths  use absolute paths instead of relative ones
  -P, --disable-live-profiler
                        disable live profiler output during execution
```

## Comments

Special comments can be added to lines of code that define variables to control how vardbg handles said variable:

- `# vardbg: ignore` — do not display this variable or track its values
