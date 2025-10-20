import pytest
import sys
from io import StringIO
from modernProject.lib.progr_bar import ProgressBar, with_bar


def test_progress_bar_creation():
    bar = ProgressBar()
    assert bar.width == 60
    assert bar.empty == '.'
    assert bar.full == '#'
    assert bar.disabled is False


def test_progress_bar_custom_params():
    bar = ProgressBar(width=80, empty='-', full='=', disabled=True)
    assert bar.width == 80
    assert bar.empty == '-'
    assert bar.full == '='
    assert bar.disabled is True


def test_progress_bar_disabled():
    bar = ProgressBar(disabled=True)
    old_stderr = sys.stderr
    try:
        sys.stderr = StringIO()
        bar.progress(50, 100)
        output = sys.stderr.getvalue()
        assert output == ""
    finally:
        sys.stderr = old_stderr


def test_progress_bar_finish():
    bar = ProgressBar(width=10)
    old_stderr = sys.stderr
    try:
        sys.stderr = StringIO()
        bar.finish()
        output = sys.stderr.getvalue()
        assert "##########" in output
        assert "100%" in output
    finally:
        sys.stderr = old_stderr


def test_progress_bar_finish_disabled():
    bar = ProgressBar(disabled=True)
    old_stderr = sys.stderr
    try:
        sys.stderr = StringIO()
        bar.finish()
        output = sys.stderr.getvalue()
        assert output == ""
    finally:
        sys.stderr = old_stderr


def test_with_bar_decorator():
    @with_bar(width=10, disabled=False)
    def process_items(bar, items):
        return len(items)

    old_stderr = sys.stderr
    try:
        sys.stderr = StringIO()
        result = process_items([1, 2, 3, 4, 5])
        assert result == 5
        output = sys.stderr.getvalue()
        assert "100%" in output
    finally:
        sys.stderr = old_stderr


def test_with_bar_decorator_disabled():
    @with_bar(disabled=True)
    def process_items(bar, items):
        return sum(items)

    old_stderr = sys.stderr
    try:
        sys.stderr = StringIO()
        result = process_items([1, 2, 3])
        assert result == 6
        output = sys.stderr.getvalue()
        assert output == ""
    finally:
        sys.stderr = old_stderr


def test_with_bar_decorator_with_exception():
    @with_bar(disabled=True)
    def failing_function(bar):
        raise ValueError("Test error")

    with pytest.raises(ValueError, match="Test error"):
        failing_function()


def test_with_bar_decorator_custom_chars():
    @with_bar(width=5, empty='.', full='*', disabled=False)
    def simple_task(bar):
        return "done"

    old_stderr = sys.stderr
    try:
        sys.stderr = StringIO()
        result = simple_task()
        assert result == "done"
        output = sys.stderr.getvalue()
        assert "*****" in output
    finally:
        sys.stderr = old_stderr


import time
from unittest.mock import patch

def test_progress_bar_throttling_and_output():
    bar = ProgressBar(width=10, full='=', empty='-')
    old_stderr = sys.stderr
    try:
        sys.stderr = StringIO()

        with patch('time.time', return_value=0.0):
            bar.progress(0, 100)
            output = sys.stderr.getvalue()
            sys.stderr.truncate(0)
            sys.stderr.seek(0)

        with patch('time.time', return_value=0.1):
            bar.progress(10, 100)
            output = sys.stderr.getvalue()
            assert output == ""

        with patch('time.time', return_value=0.3):
            bar.progress(50, 100)
            output = sys.stderr.getvalue()
            assert output == "\r[=====-----] 50%"
            sys.stderr.truncate(0)
            sys.stderr.seek(0)

        with patch('time.time', return_value=0.5):
            bar.progress(100, 100)
            output = sys.stderr.getvalue()
            assert output == "\r[==========] 100%"
            sys.stderr.truncate(0)
            sys.stderr.seek(0)

    finally:
        sys.stderr = old_stderr
