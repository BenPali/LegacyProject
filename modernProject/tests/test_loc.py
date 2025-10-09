import pytest
from modernProject.lib.loc import (
    SourceFile, SourceRaw, Source, Loc, DUMMY, of_positions
)


def test_source_file_creation():
    src = SourceFile(filename="test.txt")
    assert src.filename == "test.txt"


def test_source_file_frozen():
    src = SourceFile(filename="test.txt")
    with pytest.raises(AttributeError):
        src.filename = "other.txt"


def test_source_raw_creation():
    src = SourceRaw(content="test content")
    assert src.content == "test content"


def test_source_raw_frozen():
    src = SourceRaw(content="test content")
    with pytest.raises(AttributeError):
        src.content = "other content"


def test_loc_creation_with_file():
    src = SourceFile(filename="test.py")
    loc = Loc(src=src, start=10, stop=20)
    assert loc.src == src
    assert loc.start == 10
    assert loc.stop == 20


def test_loc_creation_with_raw():
    src = SourceRaw(content="some code")
    loc = Loc(src=src, start=5, stop=15)
    assert loc.src == src
    assert loc.start == 5
    assert loc.stop == 15


def test_loc_frozen():
    src = SourceFile(filename="test.py")
    loc = Loc(src=src, start=10, stop=20)
    with pytest.raises(AttributeError):
        loc.start = 15


def test_dummy_constant():
    assert isinstance(DUMMY, Loc)
    assert isinstance(DUMMY.src, SourceFile)
    assert DUMMY.src.filename == "<dummy>"
    assert DUMMY.start == -1
    assert DUMMY.stop == -1


def test_of_positions_with_file():
    src = SourceFile(filename="example.py")
    loc = of_positions(src, 100, 200)
    assert loc.src == src
    assert loc.start == 100
    assert loc.stop == 200


def test_of_positions_with_raw():
    src = SourceRaw(content="def foo(): pass")
    loc = of_positions(src, 0, 15)
    assert loc.src == src
    assert loc.start == 0
    assert loc.stop == 15


def test_loc_equality():
    src = SourceFile(filename="test.py")
    loc1 = Loc(src=src, start=10, stop=20)
    loc2 = Loc(src=src, start=10, stop=20)
    assert loc1 == loc2


def test_source_file_equality():
    src1 = SourceFile(filename="test.py")
    src2 = SourceFile(filename="test.py")
    src3 = SourceFile(filename="other.py")
    assert src1 == src2
    assert src1 != src3


def test_source_raw_equality():
    src1 = SourceRaw(content="test")
    src2 = SourceRaw(content="test")
    src3 = SourceRaw(content="other")
    assert src1 == src2
    assert src1 != src3
