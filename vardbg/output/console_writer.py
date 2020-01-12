import statistics

from .. import ansi, data, render
from .writer import Writer


class ConsoleWriter(Writer):
    def __init__(self):
        # Current line output prefix
        self.cur_line = ""

    def write_cur_frame(self, frame_info):
        # Construct friendly filename + line number + function string
        file_line = "%s:%-2d" % (frame_info.file, frame_info.line)
        self.cur_line = f"{file_line} ({frame_info.function})"

    def write_frame_exec(self, frame_info, exec_time, exec_times):
        nr_times = len(exec_times)
        avg_time = render.duration_ns(statistics.mean(exec_times))
        total_time = render.duration_ns(sum(exec_times))
        this_time = render.duration_ns(exec_time)

        print(f"{self.cur_line} | exec {nr_times}x (time: {this_time}, avg {avg_time}, total {total_time})")

    def _write_action(self, var, color_func, action, suffix):
        print(f"{self.cur_line} | {ansi.bold(var)} {color_func(action)} {suffix}")

    def write_add(self, var, val, history, *, action="added", plural=False):
        _plural = "s" if plural else ""
        self._write_action(var, ansi.green, action, f"with value{_plural} {render.val(val)}")

    def write_change(self, var, val_before, val_after, history, *, action="changed"):
        self._write_action(
            var, ansi.blue, action, f"from {render.val(val_before)} to {render.val(val_after)}",
        )

    def write_remove(self, var, val, history, *, action="removed"):
        self._write_action(var, ansi.red, action, f"(value: {render.val(val)})")

    @staticmethod
    def _write_var_summary(var_history):
        print()
        print("Variables seen:")

        for var, values in var_history.items():
            # Check whether all the values were numbers
            if all(isinstance(val.value, (int, float)) for val in values):
                # Give a min-max range for numbers
                min_val = min(values, key=data.VarValue.value_getter)
                max_val = max(values, key=data.VarValue.value_getter)

                min_desc = f"{render.val(min_val.value)} ({min_val.file_line})"
                max_desc = f"{render.val(max_val.value)} ({max_val.file_line})"
                values_desc = f" between {min_desc} and {max_desc}"
            else:
                # Give a list of values for other objects
                value_lines = [":"]

                for val in values:
                    value_lines.append(f"{render.val(val.value)} ({val.file_line})")

                # Format list
                values_desc = "\n      - ".join(value_lines)

            definition = f"in {var.function} on {ansi.bold(var.file_line)}"
            print(f"  - {ansi.bold(var.name)} {ansi.green('defined')} {definition} with values{values_desc}")

            if var.deleted_line is not None:
                print(f"    ({ansi.red('deleted')} on {var.deleted_line})")

    @staticmethod
    def _write_line_summary(frame_exec_times):
        print()
        print("Lines executed:")

        for frame_info, exec_times in frame_exec_times.items():
            nr_times = len(exec_times)
            avg_time = render.duration_ns(statistics.mean(exec_times))
            total_time = render.duration_ns(sum(exec_times))

            file_line = "%s:%-2d (%s)" % (frame_info.file, frame_info.line, frame_info.function)
            print(f"{file_line} | {ansi.bold(nr_times)}x, avg {ansi.bold(avg_time)}, total {ansi.bold(total_time)}")

    @staticmethod
    def _write_time_summary(exec_start_time, exec_stop_time):
        print()

        exec_time = render.duration_ns(exec_stop_time - exec_start_time)
        print(f"Total execution time: {ansi.bold(exec_time)}")

    def write_summary(self, var_history, exec_start_time, exec_stop_time, frame_exec_times):
        self._write_var_summary(var_history)
        self._write_line_summary(frame_exec_times)
        self._write_time_summary(exec_start_time, exec_stop_time)

    def close(self):
        # We print everything live, so there's nothing to close
        pass
