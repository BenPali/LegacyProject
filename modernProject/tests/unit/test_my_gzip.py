import pytest
import gzip
import tempfile
import os
from lib import my_gzip

def test_open_close():
    with tempfile.NamedTemporaryFile(suffix='.gz', delete=False) as f:
        fname = f.name
    try:
        with gzip.open(fname, 'wt', encoding='utf-8') as f:
            f.write("line1\nline2\nline3")

        ic = my_gzip.open_in(fname)
        assert ic is not None
        my_gzip.close_in(ic)
    finally:
        os.unlink(fname)

def test_close_noerr():
    with tempfile.NamedTemporaryFile(suffix='.gz', delete=False) as f:
        fname = f.name
    try:
        with gzip.open(fname, 'wt', encoding='utf-8') as f:
            f.write("test")

        ic = my_gzip.open_in(fname)
        my_gzip.close_in(ic)
        my_gzip.close_in_noerr(ic)
    finally:
        os.unlink(fname)

def test_input_line():
    with tempfile.NamedTemporaryFile(suffix='.gz', delete=False) as f:
        fname = f.name
    try:
        with gzip.open(fname, 'wt', encoding='utf-8') as f:
            f.write("line1\nline2\nline3")

        ic = my_gzip.open_in(fname)
        assert my_gzip.input_line(ic) == "line1"
        assert my_gzip.input_line(ic) == "line2"
        assert my_gzip.input_line(ic) == "line3"
        with pytest.raises(EOFError):
            my_gzip.input_line(ic)
        my_gzip.close_in(ic)
    finally:
        os.unlink(fname)

def test_with_open():
    with tempfile.NamedTemporaryFile(suffix='.gz', delete=False) as f:
        fname = f.name
    try:
        with gzip.open(fname, 'wt', encoding='utf-8') as f:
            f.write("line1\nline2\n")

        lines = []
        with my_gzip.with_open(fname) as ic:
            lines.append(ic.input_line())
            lines.append(ic.input_line())

        assert lines == ["line1", "line2"]
    finally:
        os.unlink(fname)

def test_with_open_exception():
    with tempfile.NamedTemporaryFile(suffix='.gz', delete=False) as f:
        fname = f.name
    try:
        with gzip.open(fname, 'wt', encoding='utf-8') as f:
            f.write("data")

        with pytest.raises(ValueError):
            with my_gzip.with_open(fname) as ic:
                raise ValueError("test error")
    finally:
        os.unlink(fname)

def test_context_manager():
    with tempfile.NamedTemporaryFile(suffix='.gz', delete=False) as f:
        fname = f.name
    try:
        with gzip.open(fname, 'wt', encoding='utf-8') as f:
            f.write("test\n")

        with my_gzip.InChannel(fname) as ic:
            assert ic.input_line() == "test"
    finally:
        os.unlink(fname)

def test_last_line_without_newline():
    with tempfile.NamedTemporaryFile(suffix='.gz', delete=False) as f:
        fname = f.name
    try:
        with gzip.open(fname, 'wt', encoding='utf-8') as f:
            f.write("line1\nline2")

        ic = my_gzip.open_in(fname)
        assert my_gzip.input_line(ic) == "line1"
        assert my_gzip.input_line(ic) == "line2"
        with pytest.raises(EOFError):
            my_gzip.input_line(ic)
        my_gzip.close_in(ic)
    finally:
        os.unlink(fname)
