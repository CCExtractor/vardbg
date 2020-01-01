from vardbg.debugger import Debugger


def debug_func(*args, **kwargs):
    with Debugger(live_profiler_output=False) as dbg:
        ret = dbg.run(*args, **kwargs)

    return ret
