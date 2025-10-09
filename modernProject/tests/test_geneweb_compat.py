import pytest
import tempfile
import os
from lib.geneweb_compat import InChannel, OutChannel, ListCompat

def test_in_channel_with_open_bin():
    with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
        fname = f.name
        f.write(b"binary content")

    try:
        result = InChannel.with_open_bin(fname, lambda ic: ic.read())
        assert result == b"binary content"
    finally:
        os.unlink(fname)

def test_in_channel_with_open_text():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        fname = f.name
        f.write("text content")

    try:
        result = InChannel.with_open_text(fname, lambda ic: ic.read())
        assert result == "text content"
    finally:
        os.unlink(fname)

def test_in_channel_input():
    with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
        fname = f.name
        f.write(b"test data")

    try:
        def read_to_buf(ic):
            buf = bytearray(10)
            n = InChannel.input(ic, buf, 0, 5)
            return n, bytes(buf[:n])

        n, data = InChannel.with_open_bin(fname, read_to_buf)
        assert n == 5
        assert data == b"test "
    finally:
        os.unlink(fname)

def test_out_channel_with_open_bin():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        fname = f.name

    try:
        OutChannel.with_open_bin(fname, lambda oc: oc.write(b"output"))

        with open(fname, 'rb') as f:
            assert f.read() == b"output"
    finally:
        os.unlink(fname)

def test_out_channel_with_open_text():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        fname = f.name

    try:
        OutChannel.with_open_text(fname, lambda oc: oc.write("text output"))

        with open(fname, 'r') as f:
            assert f.read() == "text output"
    finally:
        os.unlink(fname)

def test_out_channel_output():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        fname = f.name

    try:
        def write_buf(oc):
            buf = b"hello world"
            OutChannel.output(oc, buf, 0, 5)

        OutChannel.with_open_bin(fname, write_buf)

        with open(fname, 'rb') as f:
            assert f.read() == b"hello"
    finally:
        os.unlink(fname)

def test_out_channel_flush():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        fname = f.name

    try:
        def write_and_flush(oc):
            oc.write(b"test")
            OutChannel.flush(oc)

        OutChannel.with_open_bin(fname, write_and_flush)

        with open(fname, 'rb') as f:
            assert f.read() == b"test"
    finally:
        os.unlink(fname)

def test_list_equal_same():
    l1 = [1, 2, 3]
    l2 = [1, 2, 3]
    assert ListCompat.equal(lambda a, b: a == b, l1, l2) == True

def test_list_equal_different():
    l1 = [1, 2, 3]
    l2 = [1, 2, 4]
    assert ListCompat.equal(lambda a, b: a == b, l1, l2) == False

def test_list_equal_different_lengths():
    l1 = [1, 2, 3]
    l2 = [1, 2]
    assert ListCompat.equal(lambda a, b: a == b, l1, l2) == False

def test_list_equal_empty():
    l1 = []
    l2 = []
    assert ListCompat.equal(lambda a, b: a == b, l1, l2) == True

def test_list_equal_custom_comparator():
    l1 = ["hello", "world"]
    l2 = ["HELLO", "WORLD"]
    assert ListCompat.equal(lambda a, b: a.lower() == b.lower(), l1, l2) == True

def test_in_channel_exception_closes_file():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        fname = f.name
        f.write("test")

    try:
        with pytest.raises(ValueError):
            InChannel.with_open_text(fname, lambda ic: raise_error())
    finally:
        os.unlink(fname)

def raise_error():
    raise ValueError("test error")

def test_out_channel_exception_closes_file():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        fname = f.name

    try:
        with pytest.raises(ValueError):
            OutChannel.with_open_text(fname, lambda oc: raise_error())
    finally:
        os.unlink(fname)
