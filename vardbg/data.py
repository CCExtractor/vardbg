class Variable:
    """Holds information about a variable"""

    def __init__(self, name, frame_info):
        # Basic variable info
        self.name = name
        self.deleted_line = None  # file:line

        # Extract info from frame
        self._file = frame_info.file
        self.file_line = frame_info.file_line
        self.function = frame_info.function

    def to_tuple(self):
        # This produces an identifying tuple for hashing and equality comparison.
        # We ignore value, type, and line here because they can change
        return (self.name, self._file, self.function)

    def __hash__(self):
        return hash(self.to_tuple())

    def __eq__(self, other):
        return self.to_tuple() == other.to_tuple()

    def __ne__(self, other):
        return not (self == other)


class VarValue:
    """Holds information about a variable value"""

    def __init__(self, value, frame_info):
        self.value = value
        self.file_line = frame_info.file_line

    @staticmethod
    def value_getter(val):
        return val.value


class FrameInfo:
    """Holds basic information about a stack frame"""

    def __init__(self, frame):
        self.function = frame.f_code.co_name
        self.file = frame.f_code.co_filename
        self.line = frame.f_lineno

        self.file_line = f"{self.file}:{self.line}"
