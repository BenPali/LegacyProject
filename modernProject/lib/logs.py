import sys
import os
from datetime import datetime
from enum import Enum
from typing import TextIO, Optional


class LogLevel(Enum):
    LOG_EMERG = 0
    LOG_ALERT = 1
    LOG_CRIT = 2
    LOG_ERR = 3
    LOG_WARNING = 4
    LOG_NOTICE = 5
    LOG_INFO = 6
    LOG_DEBUG = 7


class Output:
    pass


class Stdout(Output):
    pass


class Stderr(Output):
    pass


class Channel(Output):
    def __init__(self, oc: TextIO):
        self.oc = oc


verbosity_level = 6
debug_flag = False
output = Stderr()


def to_out_channel(o: Output) -> TextIO:
    if isinstance(o, Stdout):
        return sys.stdout
    elif isinstance(o, Stderr):
        return sys.stderr
    elif isinstance(o, Channel):
        return o.oc
    else:
        return sys.stderr


def close_output(o: Output):
    if isinstance(o, (Stdout, Stderr)):
        to_out_channel(o).flush()
    elif isinstance(o, Channel):
        o.oc.close()


def set_output_channel(o: Output):
    global output
    if output != o:
        close_output(output)
        output = o


def pp_tm(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def syslog(level: LogLevel, msg: str):
    global verbosity_level, debug_flag, output
    
    if verbosity_level < level.value or not msg:
        return
    
    tm = datetime.now()
    level_str = level.name.replace("LOG_", "")
    
    log_file = os.getenv("GW_SYSLOG_FILE")
    
    def print_log(oc: TextIO):
        oc.write(f"{pp_tm(tm)} {level_str} {msg}\n")
        oc.flush()
    
    if log_file:
        with open(log_file, 'a') as f:
            print_log(f)
    else:
        print_log(to_out_channel(output))


def report(level: LogLevel, fmt: str, *args):
    msg = fmt % args if args else fmt
    syslog(level, msg)


def info(msg: str, *args):
    report(LogLevel.LOG_INFO, msg, *args)


def debug(msg: str, *args):
    report(LogLevel.LOG_DEBUG, msg, *args)


def warn(msg: str, *args):
    report(LogLevel.LOG_WARNING, msg, *args)


def err(msg: str, *args):
    report(LogLevel.LOG_ERR, msg, *args)
