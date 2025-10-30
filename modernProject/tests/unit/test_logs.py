import pytest
import sys
import os
import tempfile
from io import StringIO
from datetime import datetime
from lib import logs
from lib.logs import (
    LogLevel, Output, Stdout, Stderr, Channel,
    to_out_channel, close_output, set_output_channel,
    pp_tm, syslog, report, info, debug, warn, err
)


def test_log_level_enum():
    assert LogLevel.LOG_EMERG.value == 0
    assert LogLevel.LOG_ALERT.value == 1
    assert LogLevel.LOG_CRIT.value == 2
    assert LogLevel.LOG_ERR.value == 3
    assert LogLevel.LOG_WARNING.value == 4
    assert LogLevel.LOG_NOTICE.value == 5
    assert LogLevel.LOG_INFO.value == 6
    assert LogLevel.LOG_DEBUG.value == 7


def test_stdout_class():
    out = Stdout()
    assert isinstance(out, Output)


def test_stderr_class():
    out = Stderr()
    assert isinstance(out, Output)


def test_channel_class():
    buf = StringIO()
    chan = Channel(buf)
    assert isinstance(chan, Output)
    assert chan.oc is buf


def test_to_out_channel_stdout():
    out = Stdout()
    channel = to_out_channel(out)
    assert channel is sys.stdout


def test_to_out_channel_stderr():
    out = Stderr()
    channel = to_out_channel(out)
    assert channel is sys.stderr


def test_to_out_channel_custom():
    buf = StringIO()
    out = Channel(buf)
    channel = to_out_channel(out)
    assert channel is buf


def test_close_output_stdout():
    out = Stdout()
    close_output(out)


def test_close_output_stderr():
    out = Stderr()
    close_output(out)


def test_close_output_channel():
    buf = StringIO()
    out = Channel(buf)
    close_output(out)
    assert buf.closed


def test_set_output_channel():
    original = logs.output
    try:
        new_out = Stdout()
        set_output_channel(new_out)
        assert logs.output == new_out
    finally:
        logs.output = original


def test_pp_tm():
    dt = datetime(2023, 12, 25, 14, 30, 45)
    result = pp_tm(dt)
    assert result == "2023-12-25 14:30:45"


def test_syslog_below_verbosity():
    original_verbosity = logs.verbosity_level
    original_output = logs.output
    try:
        logs.verbosity_level = 3
        buf = StringIO()
        logs.output = Channel(buf)

        syslog(LogLevel.LOG_DEBUG, "test message")

        output = buf.getvalue()
        assert output == ""
    finally:
        logs.verbosity_level = original_verbosity
        logs.output = original_output


def test_syslog_above_verbosity():
    original_verbosity = logs.verbosity_level
    original_output = logs.output
    try:
        logs.verbosity_level = 6
        buf = StringIO()
        logs.output = Channel(buf)

        syslog(LogLevel.LOG_INFO, "test message")

        output = buf.getvalue()
        assert "INFO" in output
        assert "test message" in output
    finally:
        logs.verbosity_level = original_verbosity
        logs.output = original_output


def test_syslog_empty_message():
    original_output = logs.output
    try:
        buf = StringIO()
        logs.output = Channel(buf)

        syslog(LogLevel.LOG_INFO, "")

        output = buf.getvalue()
        assert output == ""
    finally:
        logs.output = original_output


def test_syslog_to_file():
    original_env = os.environ.get("GW_SYSLOG_FILE")
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            log_file = f.name

        os.environ["GW_SYSLOG_FILE"] = log_file

        syslog(LogLevel.LOG_INFO, "test file message")

        with open(log_file, 'r') as f:
            content = f.read()

        assert "INFO" in content
        assert "test file message" in content

        os.unlink(log_file)
    finally:
        if original_env:
            os.environ["GW_SYSLOG_FILE"] = original_env
        elif "GW_SYSLOG_FILE" in os.environ:
            del os.environ["GW_SYSLOG_FILE"]


def test_report_with_args():
    original_output = logs.output
    try:
        buf = StringIO()
        logs.output = Channel(buf)

        report(LogLevel.LOG_INFO, "Value: %d, Name: %s", 42, "test")

        output = buf.getvalue()
        assert "Value: 42, Name: test" in output
    finally:
        logs.output = original_output


def test_report_without_args():
    original_output = logs.output
    try:
        buf = StringIO()
        logs.output = Channel(buf)

        report(LogLevel.LOG_INFO, "Simple message")

        output = buf.getvalue()
        assert "Simple message" in output
    finally:
        logs.output = original_output


def test_info_function():
    original_output = logs.output
    try:
        buf = StringIO()
        logs.output = Channel(buf)

        info("Info message")

        output = buf.getvalue()
        assert "INFO" in output
        assert "Info message" in output
    finally:
        logs.output = original_output


def test_debug_function():
    original_output = logs.output
    original_verbosity = logs.verbosity_level
    try:
        logs.verbosity_level = 7
        buf = StringIO()
        logs.output = Channel(buf)

        debug("Debug message")

        output = buf.getvalue()
        assert "DEBUG" in output
        assert "Debug message" in output
    finally:
        logs.output = original_output
        logs.verbosity_level = original_verbosity


def test_warn_function():
    original_output = logs.output
    try:
        buf = StringIO()
        logs.output = Channel(buf)

        warn("Warning message")

        output = buf.getvalue()
        assert "WARNING" in output
        assert "Warning message" in output
    finally:
        logs.output = original_output


def test_err_function():
    original_output = logs.output
    try:
        buf = StringIO()
        logs.output = Channel(buf)

        err("Error message")

        output = buf.getvalue()
        assert "ERR" in output
        assert "Error message" in output
    finally:
        logs.output = original_output
