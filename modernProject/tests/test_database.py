import os
import tempfile
import struct
from lib import database
from lib import iovalue
from lib.dbdisk import Perm, BaseVersion, BaseData, RecordAccess

def test_check_magic():
    with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
        f.write(database.MAGIC_GNWB0024)
        f.write(b"extra data")
        fname = f.name

    try:
        with open(fname, 'rb') as ic:
            assert database.check_magic(database.MAGIC_GNWB0024, ic)
            assert ic.tell() == len(database.MAGIC_GNWB0024)

        with open(fname, 'rb') as ic:
            assert not database.check_magic(database.MAGIC_GNWB0020, ic)
            assert ic.tell() == 0
    finally:
        os.unlink(fname)

def test_input_output_binary_int():
    with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
        database.output_binary_int(f, 0)
        database.output_binary_int(f, 42)
        database.output_binary_int(f, 1000000)
        database.output_binary_int(f, 0xFFFFFFFF)
        fname = f.name

    try:
        with open(fname, 'rb') as ic:
            assert database.input_binary_int(ic) == 0
            assert database.input_binary_int(ic) == 42
            assert database.input_binary_int(ic) == 1000000
            assert database.input_binary_int(ic) == 0xFFFFFFFF
    finally:
        os.unlink(fname)

def test_empty_patch_ht():
    patches = database.empty_patch_ht()
    assert patches.h_person == ([0], {})
    assert patches.h_ascend == ([0], {})
    assert patches.h_union == ([0], {})
    assert patches.h_family == ([0], {})
    assert patches.h_couple == ([0], {})
    assert patches.h_descend == ([0], {})
    assert patches.h_string == ([0], {})
    assert patches.h_name == {}

def test_move_with_backup():
    with tempfile.TemporaryDirectory() as tmpdir:
        src = os.path.join(tmpdir, "source.txt")
        dst = os.path.join(tmpdir, "dest.txt")
        backup = dst + "~"

        with open(dst, 'w') as f:
            f.write("old content")

        with open(src, 'w') as f:
            f.write("new content")

        database.move_with_backup(src, dst)

        assert not os.path.exists(src)
        assert os.path.exists(dst)
        assert os.path.exists(backup)

        with open(dst, 'r') as f:
            assert f.read() == "new content"

        with open(backup, 'r') as f:
            assert f.read() == "old content"

def test_input_patches_nonexistent():
    with tempfile.TemporaryDirectory() as tmpdir:
        patches = database.input_patches(tmpdir)
        assert patches is not None
        assert patches.h_person == ([0], {})

def test_input_synchro_nonexistent():
    with tempfile.TemporaryDirectory() as tmpdir:
        synchro = database.input_synchro(tmpdir)
        assert synchro.synch_list == []

def test_magic_constants():
    assert database.MAGIC_GNWB0020 == b"GnWb0020"
    assert database.MAGIC_GNWB0021 == b"GnWb0021"
    assert database.MAGIC_GNWB0022 == b"GnWb0022"
    assert database.MAGIC_GNWB0023 == b"GnWb0023"
    assert database.MAGIC_GNWB0024 == b"GnWb0024"
    assert database.MAGIC_PATCH == b"GnPa0001"
    assert len(database.MAGIC_GNWB0024) == 8
    assert len(database.MAGIC_PATCH) == 8

def test_apply_patches():
    arr = [1, 2, 3, 4, 5]
    patches = {1: 20, 3: 40}
    result = database.apply_patches(arr, patches, 5)
    assert result == [1, 20, 3, 40, 5]

    patches_extend = {7: 80}
    result = database.apply_patches(arr, patches_extend, 10)
    assert len(result) == 10
    assert result[7] == 80
    assert result[0] == 1

def test_immut_record_array_loading():
    from lib import iovalue
    import io

    test_data = [b"hello", b"world", b"test"]

    buf = io.BytesIO()
    iovalue.output(buf, test_data)
    buf.seek(0)

    immut = database.ImmutRecord(
        read_only=False,
        ic=buf,
        ic_acc=None,
        shift=0,
        array_pos=0,
        len_val=3,
        name="test"
    )

    arr = immut.im_array()
    assert arr == test_data

    arr2 = immut.im_array()
    assert arr2 is arr

    immut.im_clear_array()
    assert immut.cached_array is None

def test_make_record_access_with_patches():
    from lib import iovalue
    import io

    test_data = [10, 20, 30]
    buf = io.BytesIO()
    iovalue.output(buf, test_data)
    buf.seek(0)

    immut = database.make_immut_record_access(
        read_only=False,
        ic=buf,
        ic_acc=None,
        shift=0,
        array_pos=0,
        len_val=3,
        name="test"
    )

    patches = ([3], {1: 200})
    pending = ([3], {2: 300})

    record = database.make_record_access(immut, patches, pending, 3)

    record.load_array()

    assert record.get(0) == 10
    assert record.get(1) == 200
    assert record.get(2) == 300
    assert record.get_nopending(1) == 200
    assert record.len == 3

def test_name_index():
    result = database.name_index("Smith")
    assert isinstance(result, int)
    assert 0 <= result < database.TABLE_SIZE

    assert database.name_index("Smith") == database.name_index("Smith")

def test_binary_search():
    arr = [(1, 100), (3, 200), (5, 300), (7, 400)]

    idx = database.binary_search(arr, lambda x: 0 if x[0] == 3 else (-1 if x[0] < 3 else 1))
    assert idx == 1
    assert arr[idx][0] == 3

    try:
        database.binary_search(arr, lambda x: 0 if x[0] == 4 else (-1 if x[0] < 4 else 1))
        assert False, "Should raise KeyError"
    except KeyError:
        pass

def test_binary_search_key_after():
    arr = [(1, 100), (5, 200), (10, 300), (15, 400)]

    idx = database.binary_search_key_after(arr, lambda x: -1 if 7 < x[0] else 1 if 7 > x[0] else 0)
    assert arr[idx][0] == 10

    idx = database.binary_search_key_after(arr, lambda x: 0 if x[0] == 1 else (1 if x[0] < 1 else -1))
    assert arr[idx][0] == 1

def test_binary_search_next():
    arr = [(1, 100), (5, 200), (10, 300), (15, 400)]

    idx = database.binary_search_next(arr, lambda x: -1 if 5 < x[0] else 1 if 5 > x[0] else 0)
    assert arr[idx][0] == 10

def test_compare_after_particle():
    result = database.compare_after_particle(["de", "von"], "Smith", "Jones")
    assert result != 0

    result = database.compare_after_particle(["de", "von"], "de Smith", "Smith")
    assert result == 0

    result = database.compare_after_particle(["de"], "von Smith", "Smith")
    assert result != 0

def test_persons_of_name():
    with tempfile.TemporaryDirectory() as tmpdir:
        names_inx_file = os.path.join(tmpdir, "names.inx")
        names_acc_file = os.path.join(tmpdir, "names.acc")

        test_table = [[] for _ in range(database.TABLE_SIZE)]
        test_table[0] = [1, 2, 3]
        test_table[100] = [4, 5]

        with open(names_inx_file, 'wb') as f:
            f.write(struct.pack('>I', 0))
            iovalue.output(f, test_table)

        patches_h_name = {}

        lookup = database.persons_of_name(tmpdir, patches_h_name)

        test_str = ""
        for s in ["test", "sample", "data"]:
            if database.name_index(s) == 0:
                test_str = s
                break

        if test_str:
            result = lookup(test_str)
            assert 1 in result
            assert 2 in result
            assert 3 in result

def test_person_of_key():
    from dataclasses import dataclass

    @dataclass
    class MockPerson:
        first_name: int
        surname: int
        occ: int

    def mock_get_person(i):
        if i == 0:
            return MockPerson(first_name=1, surname=2, occ=0)
        elif i == 5:
            return MockPerson(first_name=1, surname=2, occ=5)
        return None

    def mock_get_string(i):
        if i == 1:
            return "John"
        elif i == 2:
            return "Smith"
        return ""

    def mock_persons_of_name(s):
        if s == "John Smith":
            return [0, 5]
        return []

    mock_persons = RecordAccess(
        load_array=lambda: None,
        get=mock_get_person,
        get_nopending=mock_get_person,
        len=10,
        output_array=lambda oc: None,
        clear_array=lambda: None
    )

    mock_strings = RecordAccess(
        load_array=lambda: None,
        get=mock_get_string,
        get_nopending=mock_get_string,
        len=10,
        output_array=lambda oc: None,
        clear_array=lambda: None
    )

    result = database.person_of_key(mock_persons, mock_strings, mock_persons_of_name, "John", "Smith", 0)
    assert result == 0

    result = database.person_of_key(mock_persons, mock_strings, mock_persons_of_name, "John", "Smith", 1)
    assert result is None

def test_iper_exists():
    patches = {5: None, 10: None}
    pending = {15: None}

    assert database.iper_exists(patches, pending, 20, 5) == True
    assert database.iper_exists(patches, pending, 20, 10) == True
    assert database.iper_exists(patches, pending, 20, 15) == True
    assert database.iper_exists(patches, pending, 20, 3) == True
    assert database.iper_exists(patches, pending, 20, 25) == False
    assert database.iper_exists(patches, pending, 20, -1) == False

def test_ifam_exists():
    patches = {2: None}
    pending = {3: None}

    assert database.ifam_exists(patches, pending, 10, 2) == True
    assert database.ifam_exists(patches, pending, 10, 3) == True
    assert database.ifam_exists(patches, pending, 10, 5) == True
    assert database.ifam_exists(patches, pending, 10, 15) == False

def test_patch_functions_integration():
    patches_ht = database.empty_patch_ht()

    assert patches_ht.h_person[0][0] == 0
    assert len(patches_ht.h_person[1]) == 0

    patches_ht.h_person[0][0] = 5
    patches_ht.h_person[1][3] = "test_person"

    assert patches_ht.h_person[0][0] == 5
    assert patches_ht.h_person[1][3] == "test_person"

def test_strings_of_fsname_callable():
    from dataclasses import dataclass

    @dataclass
    class MockPerson:
        first_name: int
        surname: int

    def mock_get_string(i):
        if i == 0:
            return "Smith"
        elif i == 1:
            return "von Berg"
        return ""

    mock_strings = RecordAccess(
        load_array=lambda: None,
        get=mock_get_string,
        get_nopending=mock_get_string,
        len=10,
        output_array=lambda oc: None,
        clear_array=lambda: None
    )

    person1 = MockPerson(first_name=0, surname=0)
    patches_h_person = ([1], {0: person1})

    lookup_fn = database.strings_of_fsname(
        BaseVersion.GNWB0024, "/nonexistent", mock_strings, patches_h_person,
        1, 0, lambda s: [s], lambda p: p.surname
    )

    assert callable(lookup_fn)

def test_record_access_of():
    test_data = ["string0", "string1", "string2"]
    record = database.record_access_of(test_data)

    assert record.len == 3
    assert record.get(0) == "string0"
    assert record.get(1) == "string1"
    assert record.get(2) == "string2"
    assert record.get_nopending(1) == "string1"

    record.load_array()
    record.clear_array()

def test_make_function():
    from lib.gwdef import BaseNotes

    test_persons = [{"id": 0}, {"id": 1}]
    test_ascends = [{"parents": None}]
    test_unions = [{"family": []}]
    test_families = [{"father": 0}]
    test_couples = [{"person1": 0}]
    test_descends = [{"children": []}]
    test_strings = ["", "John", "Smith"]

    mock_bnotes = BaseNotes(
        nread=lambda fname, mode: "",
        norigin_file="",
        efiles=lambda: []
    )

    persons_tuple = (test_persons, test_ascends, test_unions)
    families_tuple = (test_families, test_couples, test_descends)
    arrays = (persons_tuple, families_tuple, test_strings, mock_bnotes)

    def callback(base):
        assert base.data is not None
        assert base.func is not None
        assert base.version == BaseVersion.GNWB0024
        assert base.data.persons.len == 2
        assert base.data.strings.len == 3
        assert base.data.families.len == 1
        return "success"

    with tempfile.TemporaryDirectory() as tmpdir:
        result = database.make(tmpdir, [], arrays, callback)
        assert result == "success"

        gwb_dir = tmpdir + ".gwb"
        assert os.path.exists(gwb_dir)
        assert os.path.exists(os.path.join(gwb_dir, "notes_d"))
        assert os.path.exists(os.path.join(gwb_dir, "wiznotes"))
        assert os.path.exists(os.path.join(gwb_dir, "notes"))
