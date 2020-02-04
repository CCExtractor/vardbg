from .writer import Writer


class OutputDelegate(Writer):
    def __init__(self, *writers):
        self.writers = writers

    def write_cur_frame(self, *args, **kwargs):
        for writer in self.writers:
            writer.write_cur_frame(*args, **kwargs)

    def write_frame_exec(self, *args, **kwargs):
        for writer in self.writers:
            writer.write_frame_exec(*args, **kwargs)

    def write_add(self, *args, **kwargs):
        for writer in self.writers:
            writer.write_add(*args, **kwargs)

    def write_change(self, *args, **kwargs):
        for writer in self.writers:
            writer.write_change(*args, **kwargs)

    def write_remove(self, *args, **kwargs):
        for writer in self.writers:
            writer.write_remove(*args, **kwargs)

    def write_variable_summary(self, *args, **kwargs):
        for writer in self.writers:
            writer.write_variable_summary(*args, **kwargs)

    def write_profiler_summary(self, *args, **kwargs):
        for writer in self.writers:
            writer.write_profiler_summary(*args, **kwargs)

    def write_time_summary(self, *args, **kwargs):
        for writer in self.writers:
            writer.write_time_summary(*args, **kwargs)

    def close(self, *args, **kwargs):
        for writer in self.writers:
            writer.close(*args, **kwargs)
