import pytest
from modernProject.lib.wserver_util import pp_exception, format_exception


def test_pp_exception_basic():
    exc = ValueError("test error")
    backtrace = "line1\nline2\nline3"
    result = pp_exception(exc, backtrace)
    assert "test error" in result
    assert "line1" in result
    assert "line2" in result
    assert "line3" in result


def test_pp_exception_contains_process_id():
    exc = RuntimeError("error")
    backtrace = ""
    result = pp_exception(exc, backtrace)
    assert "Exception uncaught in process" in result


def test_pp_exception_empty_backtrace():
    exc = KeyError("missing key")
    backtrace = ""
    result = pp_exception(exc, backtrace)
    assert "missing key" in result


def test_pp_exception_none_backtrace():
    exc = TypeError("type error")
    backtrace = None
    result = pp_exception(exc, backtrace)
    assert "type error" in result


def test_format_exception_with_traceback():
    try:
        raise ValueError("test exception")
    except ValueError as e:
        result = format_exception(e)
        assert "test exception" in result
        assert "Exception uncaught in process" in result


def test_format_exception_nested():
    try:
        try:
            raise KeyError("inner")
        except KeyError:
            raise ValueError("outer")
    except ValueError as e:
        result = format_exception(e)
        assert "outer" in result


def test_format_exception_with_function_call():
    def failing_function():
        raise RuntimeError("function failed")

    try:
        failing_function()
    except RuntimeError as e:
        result = format_exception(e)
        assert "function failed" in result
        assert "failing_function" in result
