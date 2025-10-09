import os
import traceback


def pp_exception(exception, backtrace_string):
    pid = os.getpid()
    lines = backtrace_string.split('\n') if backtrace_string else []
    result = f"Exception uncaught in process {pid}:\n"
    result += f"{str(exception)}\n"
    result += '\n'.join(lines)
    return result


def format_exception(exc):
    tb_str = ''.join(traceback.format_tb(exc.__traceback__))
    return pp_exception(exc, tb_str)
