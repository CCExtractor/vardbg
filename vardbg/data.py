import os.path
import re
from pathlib import Path

_relative_path_cache = {}


def _get_path(orig_path, relative):
    if relative:
        if orig_path in _relative_path_cache:
            return _relative_path_cache[orig_path]
        else:
            rel = os.path.relpath(orig_path)
            # Once there's 3 .. parts, revert to an absolute path for brevity
            if all(p == ".." for p in Path(rel).parts[:3]):
                rel = orig_path

            # Save path to cache and return
            _relative_path_cache[orig_path] = rel
            return rel
    else:
        return orig_path


class Variable:
    """Holds information about a variable"""

    def __init__(self, name, frame_info):
        # Basic variable info
        self.name = name

        # Extract info from frame
        self._file = frame_info.file
        self.file_line = frame_info.file_line
        self.function = frame_info.function

    def to_tuple(self):
        # This produces an identifying tuple for hashing and equality comparison.
        # We ignore value, type, and line here because they can change
        return self.name, self._file, self.function

    def __hash__(self):
        return hash(self.to_tuple())

    def __eq__(self, other):
        return self.to_tuple() == other.to_tuple()

    def __ne__(self, other):
        return not (self == other)


class VarValues(list):
    def __init__(self, *values, ignored=False):
        super().__init__(values)
        self.ignored = ignored
        self.deleted_line = None  # file:line


class VarValue:
    """Holds information about a variable value"""

    def __init__(self, value, frame_info):
        self.value = value
        self.file_line = frame_info.file_line

    @staticmethod
    def value_getter(val):
        return val.value


class VarHistory:
    """Holds information about a variable's history and its context"""

    def __init__(self, var, full_history):
        self.var = var
        self.var_history = full_history[var] if var in full_history else ()
        other_history = {v: h for v, h in full_history.items() if v != var and v.function == var.function}
        self.other_history = list(other_history.items())


class FrameInfo:
    """Holds basic information about a stack frame"""

    def __init__(self, frame, *, relative=True, file_cache=None):
        self.function = frame.f_code.co_name
        self.file = _get_path(frame.f_code.co_filename, relative)
        self.line = frame.f_lineno

        self.file_line = f"{self.file}:{self.line}"

        # Extract vardbg comment from line
        line = self._get_line(file_cache)
        match = re.match(r"^.+# vardbg: (.+)$", line)
        self.comment = "" if match is None else match.group(1)

    def _get_line(self, file_cache):
        # Read lines from cache if possible, otherwise read from file and save to cache
        if file_cache and self.file in file_cache:
            lines = file_cache[self.file]
        else:
            lines = Path(self.file).read_text().replace("\r", "").splitlines()
            file_cache[self.file] = lines

        return lines[self.line - 1]

    def to_tuple(self):
        # Produce an identifying tuple for hashing and equality comparison
        return self.file, self.line, self.function

    def __hash__(self):
        return hash(self.to_tuple())

    def __eq__(self, other):
        return self.to_tuple() == other.to_tuple()

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        return self.line < other.line
