import pytest
import os
import tempfile
from lib import secure

def test_decompose():
    assert secure.decompose("a/b/c") == ["a", "b", "c"]
    assert secure.decompose("foo") == ["foo"]
    assert secure.decompose("a/b") == ["a", "b"]

def test_decompose_absolute():
    if os.name == 'posix':
        result = secure.decompose("/a/b/c")
        assert "a" in result
        assert "b" in result
        assert "c" in result

def test_assets_default():
    assets = secure.assets()
    assert "gw" in assets

def test_add_assets():
    initial = secure.assets()
    secure.add_assets("test_asset")
    new_assets = secure.assets()
    assert "test_asset" in new_assets
    assert len(new_assets) >= len(initial)

def test_set_base_dir():
    secure.set_base_dir("/tmp/test")
    assert secure.base_dir() == "/tmp/test"

def test_list_check_prefix_match():
    d = ["a", "b"]
    df = ["a", "b", "c", "d"]
    result = secure.list_check_prefix(d, df)
    assert result == ["c", "d"]

def test_list_check_prefix_no_match():
    d = ["a", "x"]
    df = ["a", "b", "c"]
    result = secure.list_check_prefix(d, df)
    assert result is None

def test_list_check_prefix_exact():
    d = ["a", "b", "c"]
    df = ["a", "b", "c"]
    result = secure.list_check_prefix(d, df)
    assert result == []

def test_check_null_byte():
    assert secure.check("file\0name") == False

def test_check_relative_safe():
    assert secure.check("local/file.txt") == True
    assert secure.check("file.txt") == True

def test_check_parent_dir_rejected():
    assert secure.check("../etc/passwd") == False
    assert secure.check("foo/../bar") == False

def test_check_absolute_rejected():
    assert secure.check("/etc/passwd") == False

def test_check_in_allowed_asset():
    secure.add_assets("allowed")
    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        test_file = os.path.join(tmpdir, "test.txt")
        assert secure.check(test_file) == True

def test_check_open_valid():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        fname = f.name
    try:
        if os.path.isabs(fname):
            dirname = os.path.dirname(fname)
            secure.add_assets(dirname)
        secure.check_open(fname)
    finally:
        os.unlink(fname)

def test_check_open_invalid():
    with pytest.raises(OSError):
        secure.check_open("/etc/passwd")

def test_open_in():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        fname = f.name
        f.write("test content")

    try:
        if os.path.isabs(fname):
            secure.add_assets(os.path.dirname(fname))

        with secure.open_in(fname) as ic:
            content = ic.read()
            assert content == "test content"
    finally:
        os.unlink(fname)

def test_with_open_in_text():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        fname = f.name
        f.write("test data")

    try:
        if os.path.isabs(fname):
            secure.add_assets(os.path.dirname(fname))

        result = secure.with_open_in_text(fname, lambda ic: ic.read())
        assert result == "test data"
    finally:
        os.unlink(fname)

def test_open_in_bin():
    with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
        fname = f.name
        f.write(b"binary data")

    try:
        if os.path.isabs(fname):
            secure.add_assets(os.path.dirname(fname))

        with secure.open_in_bin(fname) as ic:
            content = ic.read()
            assert content == b"binary data"
    finally:
        os.unlink(fname)

def test_with_open_in_bin():
    with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
        fname = f.name
        f.write(b"\x00\x01\x02")

    try:
        if os.path.isabs(fname):
            secure.add_assets(os.path.dirname(fname))

        result = secure.with_open_in_bin(fname, lambda ic: ic.read())
        assert result == b"\x00\x01\x02"
    finally:
        os.unlink(fname)

def test_open_out():
    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        fname = os.path.join(tmpdir, "output.txt")

        with secure.open_out(fname) as oc:
            oc.write("output data")

        with open(fname, 'r') as f:
            assert f.read() == "output data"

def test_with_open_out_text():
    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        fname = os.path.join(tmpdir, "output2.txt")

        secure.with_open_out_text(fname, lambda oc: oc.write("text output"))

        with open(fname, 'r') as f:
            assert f.read() == "text output"

def test_open_out_bin():
    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        fname = os.path.join(tmpdir, "binary.bin")

        with secure.open_out_bin(fname) as oc:
            oc.write(b"\x00\xFF")

        with open(fname, 'rb') as f:
            assert f.read() == b"\x00\xFF"

def test_with_open_out_bin():
    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        fname = os.path.join(tmpdir, "binary2.bin")

        secure.with_open_out_bin(fname, lambda oc: oc.write(b"binary"))

        with open(fname, 'rb') as f:
            assert f.read() == b"binary"

def test_open_rejected():
    with pytest.raises(OSError):
        secure.open_in("../../../etc/passwd")

def test_check_base_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        secure.set_base_dir(tmpdir)
        test_file = os.path.join(tmpdir, "test.txt")
        open(test_file, 'w').close()

        assert secure.check(test_file) == True

def test_multiple_assets():
    with tempfile.TemporaryDirectory() as tmpdir1:
        with tempfile.TemporaryDirectory() as tmpdir2:
            secure.add_assets(tmpdir1)
            secure.add_assets(tmpdir2)

            file1 = os.path.join(tmpdir1, "file1.txt")
            file2 = os.path.join(tmpdir2, "file2.txt")

            assert secure.check(file1) == True
            assert secure.check(file2) == True
