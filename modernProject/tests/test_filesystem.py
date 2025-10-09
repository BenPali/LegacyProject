import pytest
import os
import tempfile
import shutil
from lib.filesystem import *

def test_create_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test.txt")
        create_file(path)
        assert os.path.exists(path)
        assert os.path.isfile(path)

def test_create_file_exists():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test.txt")
        create_file(path)
        create_file(path)
        assert os.path.exists(path)

def test_create_file_not_regular():
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(FileError):
            create_file(tmpdir)

def test_create_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "testdir")
        create_dir(path)
        assert os.path.exists(path)
        assert os.path.isdir(path)

def test_create_dir_parent():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "a", "b", "c")
        create_dir(path, parent=True)
        assert os.path.exists(path)
        assert os.path.isdir(path)

def test_create_dir_empty_path():
    with pytest.raises(ValueError):
        create_dir("")

def test_walk_folder():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.makedirs(os.path.join(tmpdir, "sub"))
        open(os.path.join(tmpdir, "file1.txt"), 'w').close()
        open(os.path.join(tmpdir, "sub", "file2.txt"), 'w').close()

        files = []
        dirs = []
        def collector(entry, acc):
            if isinstance(entry, FileEntry):
                files.append(entry.path)
            elif isinstance(entry, DirEntry):
                dirs.append(entry.path)
            return acc

        walk_folder(collector, tmpdir, None, recursive=False)
        assert len(files) == 1
        assert len(dirs) == 1

def test_walk_folder_recursive():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.makedirs(os.path.join(tmpdir, "sub"))
        open(os.path.join(tmpdir, "file1.txt"), 'w').close()
        open(os.path.join(tmpdir, "sub", "file2.txt"), 'w').close()

        files = []
        def collector(entry, acc):
            if isinstance(entry, FileEntry):
                files.append(entry.path)
            return acc

        walk_folder(collector, tmpdir, None, recursive=True)
        assert len(files) == 2

def test_copy_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        src = os.path.join(tmpdir, "src.txt")
        dst = os.path.join(tmpdir, "dst.txt")
        with open(src, 'w') as f:
            f.write("test content")

        copy_file(src, dst)
        assert os.path.exists(dst)
        with open(dst, 'r') as f:
            assert f.read() == "test content"

def test_copy_file_no_overwrite():
    with tempfile.TemporaryDirectory() as tmpdir:
        src = os.path.join(tmpdir, "src.txt")
        dst = os.path.join(tmpdir, "dst.txt")
        with open(src, 'w') as f:
            f.write("source")
        with open(dst, 'w') as f:
            f.write("dest")

        with pytest.raises(FileExistsError):
            copy_file(src, dst, overwrite=False)
