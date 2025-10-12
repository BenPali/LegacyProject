import os
import tempfile
import io
from lib import outbase
from lib import database
from lib import iovalue
from lib import secure
from lib.gwdef import BaseNotes, GenPerson, GenAscend, GenUnion, GenFamily, GenCouple, GenDescend, Sex
from lib.dbdisk import RecordAccess, BaseData, Perm

def test_is_prime():
    assert outbase.is_prime(2)
    assert outbase.is_prime(3)
    assert outbase.is_prime(5)
    assert outbase.is_prime(7)
    assert outbase.is_prime(11)
    assert outbase.is_prime(13)
    assert not outbase.is_prime(1)
    assert not outbase.is_prime(4)
    assert not outbase.is_prime(6)
    assert not outbase.is_prime(8)
    assert not outbase.is_prime(9)
    assert not outbase.is_prime(10)

def test_prime_after():
    assert outbase.prime_after(2) == 2
    assert outbase.prime_after(3) == 3
    assert outbase.prime_after(4) == 5
    assert outbase.prime_after(6) == 7
    assert outbase.prime_after(8) == 11
    assert outbase.prime_after(10) == 11
    assert outbase.prime_after(12) == 13

def test_output_particles_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        fname = os.path.join(tmpdir, "particles.txt")
        outbase.output_particles_file(["de", "von", "van der"], fname)
        with open(fname, 'r') as f:
            lines = f.readlines()
            assert lines[0].strip() == "de"
            assert lines[1].strip() == "von"
            assert lines[2].strip() == "van_der"

def test_output_particles_file_empty():
    with tempfile.TemporaryDirectory() as tmpdir:
        fname = os.path.join(tmpdir, "particles.txt")
        outbase.output_particles_file([], fname)
        with open(fname, 'r') as f:
            assert f.read() == ""

def test_safe_rename():
    with tempfile.TemporaryDirectory() as tmpdir:
        src = os.path.join(tmpdir, "source.txt")
        dst = os.path.join(tmpdir, "dest.txt")
        with open(src, 'w') as f:
            f.write("content")
        outbase.safe_rename(src, dst)
        assert not os.path.exists(src)
        assert os.path.exists(dst)
        with open(dst, 'r') as f:
            assert f.read() == "content"

def test_safe_rename_overwrites_existing():
    with tempfile.TemporaryDirectory() as tmpdir:
        src = os.path.join(tmpdir, "source.txt")
        dst = os.path.join(tmpdir, "dest.txt")
        with open(src, 'w') as f:
            f.write("new")
        with open(dst, 'w') as f:
            f.write("old")
        outbase.safe_rename(src, dst)
        assert not os.path.exists(src)
        with open(dst, 'r') as f:
            assert f.read() == "new"

def test_output_binary_int():
    buf = io.BytesIO()
    outbase.output_binary_int(buf, 0)
    outbase.output_binary_int(buf, 42)
    outbase.output_binary_int(buf, 1000000)
    outbase.output_binary_int(buf, 0xFFFFFFFF)
    buf.seek(0)
    assert outbase.input_binary_int(buf) == 0
    assert outbase.input_binary_int(buf) == 42
    assert outbase.input_binary_int(buf) == 1000000
    assert outbase.input_binary_int(buf) == 0xFFFFFFFF

def test_input_binary_int_eof():
    buf = io.BytesIO(b"\x00\x00")
    import pytest
    with pytest.raises(EOFError):
        outbase.input_binary_int(buf)

def test_make_name_index_basic():
    test_persons = [{"first_name": 2, "surname": 3, "key_index": 0}]
    test_ascends = [{"parents": None}]
    test_unions = [{"family": []}]
    test_families = []
    test_couples = []
    test_descends = []
    test_strings = ["", "?", "John", "Smith"]

    mock_bnotes = BaseNotes(
        nread=lambda fname, mode: "",
        norigin_file="",
        efiles=lambda: []
    )

    persons_tuple = (test_persons, test_ascends, test_unions)
    families_tuple = (test_families, test_couples, test_descends)
    arrays = (persons_tuple, families_tuple, test_strings, mock_bnotes)

    def callback(base):
        ni = outbase.make_name_index(base)
        assert isinstance(ni, list)
        assert len(ni) == database.TABLE_SIZE
        for entry in ni:
            assert isinstance(entry, list)
        return "success"

    with tempfile.TemporaryDirectory() as tmpdir:
        result = database.make(tmpdir, [], arrays, callback)
        assert result == "success"

def test_make_name_index_question_mark():
    test_persons = [{"first_name": 1, "surname": 1, "key_index": 0}]
    test_ascends = [{"parents": None}]
    test_unions = [{"family": []}]
    test_families = []
    test_couples = []
    test_descends = []
    test_strings = ["", "?"]

    mock_bnotes = BaseNotes(
        nread=lambda fname, mode: "",
        norigin_file="",
        efiles=lambda: []
    )

    persons_tuple = (test_persons, test_ascends, test_unions)
    families_tuple = (test_families, test_couples, test_descends)
    arrays = (persons_tuple, families_tuple, test_strings, mock_bnotes)

    def callback(base):
        ni = outbase.make_name_index(base)
        for entry in ni:
            assert len(entry) == 0
        return "success"

    with tempfile.TemporaryDirectory() as tmpdir:
        result = database.make(tmpdir, [], arrays, callback)
        assert result == "success"

def test_make_strings_of_fname():
    test_persons = [{"first_name": 2, "surname": 3}]
    test_strings = ["", "?", "John", "Smith"]

    strings_rec = RecordAccess(
        load_array=lambda: None,
        get=lambda i: test_strings[i],
        get_nopending=lambda i: test_strings[i],
        len=len(test_strings),
        output_array=lambda oc: None,
        clear_array=lambda: None
    )
    persons_rec = RecordAccess(
        load_array=lambda: None,
        get=lambda i: test_persons[i],
        get_nopending=lambda i: test_persons[i],
        len=len(test_persons),
        output_array=lambda oc: None,
        clear_array=lambda: None
    )

    class MockBaseData:
        pass

    class MockBase:
        pass

    base = MockBase()
    base.data = MockBaseData()
    base.data.persons = persons_rec
    base.data.strings = strings_rec

    result = outbase.make_strings_of_fname(base)
    assert isinstance(result, list)
    assert len(result) == database.TABLE_SIZE

def test_make_strings_of_sname():
    test_persons = [{"first_name": 2, "surname": 3}]
    test_strings = ["", "?", "John", "Smith"]

    strings_rec = RecordAccess(
        load_array=lambda: None,
        get=lambda i: test_strings[i],
        get_nopending=lambda i: test_strings[i],
        len=len(test_strings),
        output_array=lambda oc: None,
        clear_array=lambda: None
    )
    persons_rec = RecordAccess(
        load_array=lambda: None,
        get=lambda i: test_persons[i],
        get_nopending=lambda i: test_persons[i],
        len=len(test_persons),
        output_array=lambda oc: None,
        clear_array=lambda: None
    )

    class MockBaseData:
        pass

    class MockBase:
        pass

    base = MockBase()
    base.data = MockBaseData()
    base.data.persons = persons_rec
    base.data.strings = strings_rec

    result = outbase.make_strings_of_sname(base)
    assert isinstance(result, list)
    assert len(result) == database.TABLE_SIZE

def test_dsk_person_misc_names():
    class MockPerson:
        def __init__(self):
            self.first_name = 1
            self.surname = 2

    test_strings = ["", "John", "Smith"]
    strings_rec = RecordAccess(
        load_array=lambda: None,
        get=lambda i: test_strings[i],
        get_nopending=lambda i: test_strings[i],
        len=len(test_strings),
        output_array=lambda oc: None,
        clear_array=lambda: None
    )

    class MockBaseData:
        pass

    class MockBase:
        pass

    base = MockBase()
    base.data = MockBaseData()
    base.data.strings = strings_rec

    p = MockPerson()
    names = outbase.dsk_person_misc_names(base, p)
    assert isinstance(names, list)
    assert len(names) > 0
    assert "John Smith" in names

