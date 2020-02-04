from vardbg.debugger import Debugger


def debug_func(*args, **kwargs):
    with Debugger() as dbg:
        ret = dbg.run(*args, **kwargs)

    return ret
