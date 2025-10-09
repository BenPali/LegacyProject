import pytest
import os
import tempfile
from modernProject.lib.my_unix import remove_dir


def test_remove_dir_empty():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = os.path.join(tmpdir, "empty_dir")
        os.mkdir(test_dir)
        assert os.path.exists(test_dir)

        remove_dir(test_dir)
        assert not os.path.exists(test_dir)


def test_remove_dir_with_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = os.path.join(tmpdir, "dir_with_files")
        os.mkdir(test_dir)

        file1 = os.path.join(test_dir, "file1.txt")
        file2 = os.path.join(test_dir, "file2.txt")

        with open(file1, 'w') as f:
            f.write("content1")
        with open(file2, 'w') as f:
            f.write("content2")

        assert os.path.exists(file1)
        assert os.path.exists(file2)

        remove_dir(test_dir)
        assert not os.path.exists(test_dir)


def test_remove_dir_nested():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = os.path.join(tmpdir, "parent")
        os.mkdir(test_dir)

        child1 = os.path.join(test_dir, "child1")
        child2 = os.path.join(test_dir, "child2")
        os.mkdir(child1)
        os.mkdir(child2)

        grandchild = os.path.join(child1, "grandchild")
        os.mkdir(grandchild)

        file1 = os.path.join(child1, "file1.txt")
        file2 = os.path.join(grandchild, "file2.txt")
        file3 = os.path.join(child2, "file3.txt")

        with open(file1, 'w') as f:
            f.write("content1")
        with open(file2, 'w') as f:
            f.write("content2")
        with open(file3, 'w') as f:
            f.write("content3")

        assert os.path.exists(test_dir)
        assert os.path.exists(child1)
        assert os.path.exists(child2)
        assert os.path.exists(grandchild)

        remove_dir(test_dir)
        assert not os.path.exists(test_dir)


def test_remove_dir_nonexistent():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = os.path.join(tmpdir, "nonexistent")
        assert not os.path.exists(test_dir)

        remove_dir(test_dir)
        assert not os.path.exists(test_dir)


def test_remove_dir_file_not_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("content")

        assert os.path.exists(test_file)

        remove_dir(test_file)

        assert os.path.exists(test_file)


def test_remove_dir_complex_structure():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = os.path.join(tmpdir, "complex")
        os.mkdir(test_dir)

        for i in range(3):
            dir_level1 = os.path.join(test_dir, f"level1_{i}")
            os.mkdir(dir_level1)

            for j in range(2):
                dir_level2 = os.path.join(dir_level1, f"level2_{j}")
                os.mkdir(dir_level2)

                file_path = os.path.join(dir_level2, f"file_{j}.txt")
                with open(file_path, 'w') as f:
                    f.write(f"content_{i}_{j}")

        assert os.path.exists(test_dir)

        remove_dir(test_dir)
        assert not os.path.exists(test_dir)
