import abc


class Writer(abc.ABC):
    @abc.abstractmethod
    def write_cur_frame(self, frame_info):
        pass

    @abc.abstractmethod
    def write_add(self, var, val, *, action, plural):
        pass

    @abc.abstractmethod
    def write_change(self, var, val_before, val_after, *, action):
        pass

    @abc.abstractmethod
    def write_remove(self, var, val, *, action):
        pass

    @abc.abstractmethod
    def write_frame_exec(self, frame_info, exec_time, exec_times):
        pass

    @abc.abstractmethod
    def write_summary(self, var_history, exec_start_time, exec_stop_time, frame_exec_times):
        pass
