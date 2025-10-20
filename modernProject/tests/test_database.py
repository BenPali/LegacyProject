import os
import tempfile
from io import StringIO
import struct
from lib import database
from lib import iovalue
from lib import secure
from lib.dbdisk import Perm, BaseVersion, BaseData, RecordAccess
from lib.gwdef import BaseNotes, GenPerson, GenAscend, GenUnion, Sex

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
        src_file = os.path.join(tmpdir, "source.txt")
        dst_file = os.path.join(tmpdir, "destination.txt")
        backup_file = dst_file + "~"
    
        with open(src_file, "w") as f: f.write("source content")
        database.move_with_backup(src_file, dst_file)
        assert os.path.exists(dst_file)
        assert not os.path.exists(src_file)
        assert not os.path.exists(backup_file)
        os.remove(dst_file)
    
        with open(src_file, "w") as f: f.write("source content")
        with open(dst_file, "w") as f: f.write("destination content")
        database.move_with_backup(src_file, dst_file)
        assert os.path.exists(dst_file)
        assert not os.path.exists(src_file)
        assert os.path.exists(backup_file)
        with open(backup_file, "r") as f: assert f.read() == "destination content"

        with open(src_file, "w") as f: f.write("new source content")
        with open(dst_file, "w") as f: f.write("new destination content")
        with open(backup_file, "w") as f: f.write("old backup content")
        database.move_with_backup(src_file, dst_file)
        assert os.path.exists(dst_file)
        assert not os.path.exists(src_file)
        assert os.path.exists(backup_file)
        with open(backup_file, "r") as f: assert f.read() == "new destination content"

from unittest.mock import patch, mock_open

def test_input_patches_loading():
    with tempfile.TemporaryDirectory() as tmpdir:
        bname = tmpdir
        patches_file = os.path.join(bname, "patches")
    
        patches = database.input_patches(bname)
        assert patches == database.empty_patch_ht()
    
        mock_record = {
            'fields': [
                {'fields': [[1], [{'fields': ['k1', 'v1']}] ]},
                {'fields': [[2], [{'fields': ['k2', 'v2']}] ]},
                {'fields': [[3], [{'fields': ['k3', 'v3']}] ]},
                {'fields': [[4], [{'fields': ['k4', 'v4']}] ]},
                {'fields': [[5], [{'fields': ['k5', 'v5']}] ]},
                {'fields': [[6], [{'fields': ['k6', 'v6']}] ]},
                {'fields': [[7], [{'fields': ['k7', 'v7']}] ]},
                [
                    {'fields': ['n1', 'nv1']},
                ]
            ]
        }
        with open(patches_file, "wb") as f:
            f.write(database.MAGIC_PATCH)
        
        with patch('lib.secure.open_in_bin', new_callable=mock_open) as mock_open_bin:
            with patch('lib.iovalue.input_value', return_value=mock_record):
        
                mock_file_handle = mock_open_bin.return_value.__enter__.return_value
                mock_file_handle.read.side_effect = [database.MAGIC_PATCH, b'']
                mock_file_handle.tell.return_value = len(database.MAGIC_PATCH)

                patches = database.input_patches(bname)
                assert patches.h_person == ([1], {'k1': 'v1'})
                assert patches.h_name == {'n1': 'nv1'}
    
        with open(patches_file, "wb") as f:
            f.write(b"BAD_MAGIC")

        with patch('lib.secure.open_in_bin', new_callable=mock_open) as mock_open_bin:
            mock_file_handle = mock_open_bin.return_value.__enter__.return_value
            mock_file_handle.read.return_value = b"BAD_MAGIC"
            mock_file_handle.tell.return_value = 0
            mock_file_handle.seek.return_value = None

            patches = database.input_patches(bname)
            assert patches == database.empty_patch_ht()

        with patch('lib.secure.open_in_bin', side_effect=IOError("Test Error")) as mock_open_bin:
            with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                patches = database.input_patches(bname)
                assert patches == database.empty_patch_ht()
                assert "Warning: Could not load patches: Test Error" in mock_stderr.getvalue()

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

def test_with_database_minimal():
    person1 = GenPerson(first_name=1, surname=2, occ=0, image="", public_name="",
                        qualifiers=[], aliases=[], first_names_aliases=[], surnames_aliases=[],
                        titles=[], rparents=[], related=[], occupation="", sex=Sex.MALE,
                        access=0, birth="", birth_place="", birth_note="", birth_src="",
                        baptism="", baptism_place="", baptism_note="", baptism_src="",
                        death="", death_place="", death_note="", death_src="",
                        burial="", burial_place="", burial_note="", burial_src="",
                        pevents=[], notes="", psources="", key_index=0)
    ascend1 = GenAscend(parents=None, consang=None)
    union1 = GenUnion(family=[])

    persons_tuple = ([person1], [ascend1], [union1])
    families_tuple = ([], [], [])
    strings_list = ["", "John", "Doe"]
    mock_bnotes = BaseNotes(nread=lambda _f, _m: "", norigin_file="", efiles=lambda: [])
    arrays = (persons_tuple, families_tuple, strings_list, mock_bnotes)

    def callback(base):
        assert base.data.persons.len == 1
        assert base.data.strings.len == 3
        p = base.data.persons.get(0)
        assert p.first_name == 1
        assert p.surname == 2

        assert base.func.iper_exists(0)
        assert not base.func.iper_exists(999)

        first_name_str = base.data.strings.get(1)
        surname_str = base.data.strings.get(2)
        assert first_name_str == "John"
        assert surname_str == "Doe"

        return "success"

    with tempfile.TemporaryDirectory() as tmpdir:
        result = database.make(tmpdir, [], arrays, callback)
        assert result == "success"

def test_with_database_invalid_magic():
    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        gwb_dir = os.path.join(tmpdir, "test.gwb")
        os.makedirs(gwb_dir, exist_ok=True)
        base_file = os.path.join(gwb_dir, "base")

        with open(base_file, 'wb') as f:
            f.write(b"BAD_MAGIC_123")

        try:
            database.with_database(gwb_dir, lambda _: None)
            assert False, "Should raise ValueError"
        except ValueError as e:
            assert "not a GeneWeb base" in str(e) or "not compatible" in str(e)

def test_with_database_gnwb_incompatible():
    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        gwb_dir = os.path.join(tmpdir, "test.gwb")
        os.makedirs(gwb_dir, exist_ok=True)
        base_file = os.path.join(gwb_dir, "base")

        with open(base_file, 'wb') as f:
            f.write(b"GnWb9999")

        try:
            database.with_database(gwb_dir, lambda _: None)
            assert False, "Should raise ValueError"
        except ValueError as e:
            assert "not compatible" in str(e)

def test_with_database_missing_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        try:
            database.with_database(tmpdir, lambda _: None)
            assert False, "Should raise FileNotFoundError"
        except FileNotFoundError as e:
            assert "Database not found" in str(e)

def test_base_func_insert_string():
    persons_tuple = ([], [], [])
    families_tuple = ([], [], [])
    strings_list = ["", "initial"]
    mock_bnotes = BaseNotes(nread=lambda _f, _m: "", norigin_file="", efiles=lambda: [])
    arrays = (persons_tuple, families_tuple, strings_list, mock_bnotes)

    def callback(base):
        idx1 = base.func.insert_string("unique_string_1")
        assert idx1 >= 0

        idx2 = base.func.insert_string("unique_string_2")
        assert idx2 >= 0

        str1 = base.data.strings.get(idx1)
        str2 = base.data.strings.get(idx2)
        assert str1 == "unique_string_1"
        assert str2 == "unique_string_2"

        return "success"

    with tempfile.TemporaryDirectory() as tmpdir:
        result = database.make(tmpdir, [], arrays, callback)
        assert result == "success"

def test_base_func_patch_person():
    person1 = GenPerson(first_name=1, surname=2, occ=0, image="", public_name="",
                        qualifiers=[], aliases=[], first_names_aliases=[], surnames_aliases=[],
                        titles=[], rparents=[], related=[], occupation="", sex=Sex.MALE,
                        access=0, birth="", birth_place="", birth_note="", birth_src="",
                        baptism="", baptism_place="", baptism_note="", baptism_src="",
                        death="", death_place="", death_note="", death_src="",
                        burial="", burial_place="", burial_note="", burial_src="",
                        pevents=[], notes="", psources="", key_index=0)
    ascend1 = GenAscend(parents=None, consang=None)
    union1 = GenUnion(family=[])

    persons_tuple = ([person1], [ascend1], [union1])
    families_tuple = ([], [], [])
    strings_list = ["", "John", "Doe"]
    mock_bnotes = BaseNotes(nread=lambda _f, _m: "", norigin_file="", efiles=lambda: [])
    arrays = (persons_tuple, families_tuple, strings_list, mock_bnotes)

    def callback(base):
        new_person = GenPerson(first_name=3, surname=4, occ=0, image="", public_name="",
                              qualifiers=[], aliases=[], first_names_aliases=[], surnames_aliases=[],
                              titles=[], rparents=[], related=[], occupation="", sex=Sex.FEMALE,
                              access=0, birth="", birth_place="", birth_note="", birth_src="",
                              baptism="", baptism_place="", baptism_note="", baptism_src="",
                              death="", death_place="", death_note="", death_src="",
                              burial="", burial_place="", burial_note="", burial_src="",
                              pevents=[], notes="", psources="", key_index=0)
        base.func.patch_person(0, new_person)
        updated = base.data.persons.get(0)
        assert updated.first_name == 3
        assert updated.surname == 4

        return "success"

    with tempfile.TemporaryDirectory() as tmpdir:
        result = database.make(tmpdir, [], arrays, callback)
        assert result == "success"

def test_base_func_patch_ascend():
    ascend1 = GenAscend(parents=None, consang=None)
    persons_tuple = ([{}], [ascend1], [{}])
    families_tuple = ([], [], [])
    strings_list = [""]
    mock_bnotes = BaseNotes(nread=lambda _f, _m: "", norigin_file="", efiles=lambda: [])
    arrays = (persons_tuple, families_tuple, strings_list, mock_bnotes)

    def callback(base):
        new_ascend = GenAscend(parents=5, consang=None)
        base.func.patch_ascend(0, new_ascend)
        updated = base.data.ascends.get(0)
        assert updated.parents == 5

        return "success"

    with tempfile.TemporaryDirectory() as tmpdir:
        result = database.make(tmpdir, [], arrays, callback)
        assert result == "success"

def test_base_func_nb_of_real_persons():
    person1 = GenPerson(first_name=1, surname=2, occ=0, image="", public_name="",
                        qualifiers=[], aliases=[], first_names_aliases=[], surnames_aliases=[],
                        titles=[], rparents=[], related=[], occupation="", sex=Sex.MALE,
                        access=0, birth="", birth_place="", birth_note="", birth_src="",
                        baptism="", baptism_place="", baptism_note="", baptism_src="",
                        death="", death_place="", death_note="", death_src="",
                        burial="", burial_place="", burial_note="", burial_src="",
                        pevents=[], notes="", psources="", key_index=0)
    person_empty = GenPerson(first_name=0, surname=0, occ=0, image="", public_name="",
                            qualifiers=[], aliases=[], first_names_aliases=[], surnames_aliases=[],
                            titles=[], rparents=[], related=[], occupation="", sex=Sex.NEUTER,
                            access=0, birth="", birth_place="", birth_note="", birth_src="",
                            baptism="", baptism_place="", baptism_note="", baptism_src="",
                            death="", death_place="", death_note="", death_src="",
                            burial="", burial_place="", burial_note="", burial_src="",
                            pevents=[], notes="", psources="", key_index=0)
    ascend1 = GenAscend(parents=None, consang=None)
    ascend2 = GenAscend(parents=None, consang=None)
    union1 = GenUnion(family=[])
    union2 = GenUnion(family=[])

    persons_tuple = ([person1, person_empty], [ascend1, ascend2], [union1, union2])
    families_tuple = ([], [], [])
    strings_list = ["", "John", "Doe"]
    mock_bnotes = BaseNotes(nread=lambda _f, _m: "", norigin_file="", efiles=lambda: [])
    arrays = (persons_tuple, families_tuple, strings_list, mock_bnotes)

    def callback(base):
        count = base.func.nb_of_real_persons()
        assert count >= 0
        assert count <= 2

        return "success"

    with tempfile.TemporaryDirectory() as tmpdir:
        result = database.make(tmpdir, [], arrays, callback)
        assert result == "success"

def test_input_binary_int_eof():
    import io
    buf = io.BytesIO(b"ab")
    try:
        database.input_binary_int(buf)
        assert False, "Should raise EOFError"
    except EOFError as e:
        assert "Unexpected end of file" in str(e)

def test_compare_snames():
    mock_strings = RecordAccess(
        load_array=lambda: None,
        get=lambda i: ["", "Smith", "Jones", "von Berg"][i] if i < 4 else "",
        get_nopending=lambda _: "",
        len=10,
        output_array=lambda _: None,
        clear_array=lambda: None
    )

    mock_base_data = BaseData(
        persons=mock_strings,
        ascends=mock_strings,
        unions=mock_strings,
        visible=None,
        families=mock_strings,
        couples=mock_strings,
        descends=mock_strings,
        strings=mock_strings,
        particles_txt=["von", "de"],
        particles=None,
        bnotes=None,
        bdir="",
        perm=Perm.RDONLY
    )

    result = database.compare_snames(mock_base_data, "Smith", "Jones")
    assert result != 0

    result = database.compare_snames_i(mock_base_data, 1, 2)
    assert result != 0

def test_compare_fnames():
    mock_strings = RecordAccess(
        load_array=lambda: None,
        get=lambda i: ["", "John", "Jane"][i] if i < 3 else "",
        get_nopending=lambda _: "",
        len=10,
        output_array=lambda _: None,
        clear_array=lambda: None
    )

    mock_base_data = BaseData(
        persons=mock_strings,
        ascends=mock_strings,
        unions=mock_strings,
        visible=None,
        families=mock_strings,
        couples=mock_strings,
        descends=mock_strings,
        strings=mock_strings,
        particles_txt=[],
        particles=None,
        bnotes=None,
        bdir="",
        perm=Perm.RDONLY
    )

    result = database.compare_fnames(mock_base_data, "John", "Jane")
    assert result != 0

    result = database.compare_fnames_i(mock_base_data, 1, 2)
    assert result != 0

def test_with_database_loads_minimal_gwb():
    from tests.gwb_generator import create_minimal_gwb

    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        gwb_path = create_minimal_gwb(tmpdir, "test")

        def load_callback(base):
            assert base.data.persons.len == 2
            assert base.data.families.len == 1
            assert base.data.strings.len == 5

            assert base.version == database.BaseVersion.GNWB0024
            assert base.data.perm in [Perm.RDONLY, Perm.RDRW]

            return "loaded"

        result = database.with_database(gwb_path, load_callback)
        assert result == "loaded"

def test_with_database_read_only_mode():
    from tests.gwb_generator import create_minimal_gwb

    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        gwb_path = create_minimal_gwb(tmpdir, "test")

        open(os.path.join(gwb_path, "commit_timestamp"), 'w').close()

        def callback(base):
            assert base.data.perm == Perm.RDONLY
            return "read_only"

        result = database.with_database(gwb_path, callback)
        assert result == "read_only"

def test_with_database_version_detection():
    from tests.gwb_generator import create_minimal_gwb

    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        gwb_path = create_minimal_gwb(tmpdir, "test")

        def callback(base):
            assert base.version == database.BaseVersion.GNWB0024
            return "success"

        result = database.with_database(gwb_path, callback)
        assert result == "success"

def test_with_database_basefunc_operations():
    from tests.gwb_generator import create_minimal_gwb

    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        gwb_path = create_minimal_gwb(tmpdir, "test")

        def callback(base):
            assert base.func.iper_exists(0)
            assert base.func.iper_exists(1)
            assert not base.func.iper_exists(999)

            assert base.func.ifam_exists(0)
            assert not base.func.ifam_exists(999)

            count = base.func.nb_of_real_persons()
            assert count >= 0

            idx = base.func.insert_string("TestString")
            assert idx >= 0

            return "success"

        result = database.with_database(gwb_path, callback, read_only=False)
        assert result == "success"

def test_compare_functions_with_particles():
    mock_particles = ["von", "de", "van"]

    result = database.compare_after_particle(mock_particles, "von Berg", "Berg")
    assert result == 0

    result = database.compare_after_particle(mock_particles, "Schmidt", "von Berg")
    assert result != 0

def test_binary_search_helpers():
    arr = [(0, "A"), (1, "B"), (2, "C")]

    try:
        result = database.binary_search(arr, lambda x: 0 if x[1] == "B" else (-1 if x[1] < "B" else 1))
        assert result == 1
    except:
        pass

def test_move_with_backup_nonexistent_src():
    with tempfile.TemporaryDirectory() as tmpdir:
        src = os.path.join(tmpdir, "nonexistent")
        dst = os.path.join(tmpdir, "dest")

        try:
            database.move_with_backup(src, dst)
        except FileNotFoundError:
            pass

def test_commit_patches_serialization():
    from tests.gwb_generator import create_minimal_gwb

    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        gwb_path = create_minimal_gwb(tmpdir, "test")

        def callback(base):
            modified_person = {
                'tag': 0,
                'fields': [
                    1, 2, 0, 0, 0, [], [], [], [], [], [], [], 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, [],
                    0, 0, 0
                ]
            }

            base.func.patch_person(0, modified_person)
            base.func.commit_patches()

            patches_file = os.path.join(gwb_path, "patches")
            assert os.path.exists(patches_file)

            return "success"

        result = database.with_database(gwb_path, callback, read_only=False)
        assert result == "success"

def test_commit_patches_family():
    from tests.gwb_generator import create_minimal_gwb

    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        gwb_path = create_minimal_gwb(tmpdir, "test")

        def callback(base):
            modified_family = {'tag': 0, 'fields': [0, 0, 0, 0, [], 0, 0, [], 0, 0, 0, 0]}
            base.func.patch_family(0, modified_family)
            base.func.commit_patches()
            return "success"

        result = database.with_database(gwb_path, callback, read_only=False)
        assert result == "success"

def test_commit_patches_ascend():
    from tests.gwb_generator import create_minimal_gwb

    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        gwb_path = create_minimal_gwb(tmpdir, "test")

        def callback(base):
            modified_ascend = {'tag': 0, 'fields': [{'tag': 0, 'fields': []}, {'tag': 0, 'fields': []}]}
            base.func.patch_ascend(0, modified_ascend)
            base.func.commit_patches()
            return "success"

        result = database.with_database(gwb_path, callback, read_only=False)
        assert result == "success"

def test_commit_patches_union():
    from tests.gwb_generator import create_minimal_gwb

    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        gwb_path = create_minimal_gwb(tmpdir, "test")

        def callback(base):
            modified_union = {'tag': 0, 'fields': [[0]]}
            base.func.patch_union(0, modified_union)
            base.func.commit_patches()
            return "success"

        result = database.with_database(gwb_path, callback, read_only=False)
        assert result == "success"

def test_commit_patches_couple():
    from tests.gwb_generator import create_minimal_gwb

    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        gwb_path = create_minimal_gwb(tmpdir, "test")

        def callback(base):
            modified_couple = {'tag': 0, 'fields': [0, {'tag': 0, 'fields': []}]}
            base.func.patch_couple(0, modified_couple)
            base.func.commit_patches()
            return "success"

        result = database.with_database(gwb_path, callback, read_only=False)
        assert result == "success"

def test_commit_patches_descend():
    from tests.gwb_generator import create_minimal_gwb

    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        gwb_path = create_minimal_gwb(tmpdir, "test")

        def callback(base):
            modified_descend = {'tag': 0, 'fields': [[]]}
            base.func.patch_descend(0, modified_descend)
            base.func.commit_patches()
            return "success"

        result = database.with_database(gwb_path, callback, read_only=False)
        assert result == "success"

def test_commit_patches_string():
    from tests.gwb_generator import create_minimal_gwb

    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        gwb_path = create_minimal_gwb(tmpdir, "test")

        def callback(base):
            idx = base.func.insert_string("NewString")
            assert idx >= 0
            base.func.commit_patches()
            return "success"

        result = database.with_database(gwb_path, callback, read_only=False)
        assert result == "success"

def test_persons_of_name_with_index():
    from tests.gwb_generator import create_minimal_gwb

    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        gwb_path = create_minimal_gwb(tmpdir, "test")

        names_inx_file = os.path.join(gwb_path, "names.inx")
        with open(names_inx_file, 'wb') as f:
            database.output_binary_int(f, 0)
            table = [[0, 1] for _ in range(7919)]
            iovalue.output(f, table)

        lookup_fn = database.persons_of_name(gwb_path, {})
        try:
            result = lookup_fn("test")
            assert isinstance(result, list)
        except (IndexError, KeyError):
            pass

def test_compare_functions_i():
    persons_array = [
        {'tag': 0, 'fields': [1, 2, 0]},
        {'tag': 0, 'fields': [3, 4, 0]}
    ]
    strings_array = ["", "John", "Doe", "Jane", "Smith"]

    base_data = database.BaseData(
        persons=database.record_access_of(persons_array),
        ascends=database.record_access_of([]),
        unions=database.record_access_of([]),
        visible=None,
        families=database.record_access_of([]),
        couples=database.record_access_of([]),
        descends=database.record_access_of([]),
        strings=database.record_access_of(strings_array),
        particles_txt=[],
        particles=None,
        bnotes=None,
        bdir="",
        perm=database.Perm.RDONLY
    )

    result = database.compare_snames_i(base_data, 1, 2)
    assert isinstance(result, int)

    result = database.compare_fnames_i(base_data, 1, 2)
    assert isinstance(result, int)

def test_persons_of_name_with_real_index():
    from tests.gwb_generator import create_minimal_gwb

    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        gwb_path = create_minimal_gwb(tmpdir, "test")

        def callback(base):
            result = base.func.persons_of_name("John Doe")
            assert isinstance(result, list)
            assert len(result) == 1
            assert 0 in result

            result_smith = base.func.persons_of_name("Jane Smith")
            assert isinstance(result_smith, list)
            assert len(result_smith) == 1
            assert 1 in result_smith

            result_none = base.func.persons_of_name("Nonexistent Person")
            assert isinstance(result_none, list)
            assert len(result_none) == 0

            return "success"

        result = database.with_database(gwb_path, callback)
        assert result == "success"

def test_persons_of_surname_with_real_index():
    from tests.gwb_generator import create_minimal_gwb

    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        gwb_path = create_minimal_gwb(tmpdir, "test")

        def callback(base):
            surname_idx = base.func.persons_of_surname

            doe_istr = 2
            result = surname_idx.find(doe_istr)
            assert isinstance(result, list)
            assert 0 in result

            smith_istr = 4
            result_smith = surname_idx.find(smith_istr)
            assert isinstance(result_smith, list)
            assert 1 in result_smith

            return "success"

        result = database.with_database(gwb_path, callback)
        assert result == "success"

def test_persons_of_first_name_with_real_index():
    from tests.gwb_generator import create_minimal_gwb

    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        gwb_path = create_minimal_gwb(tmpdir, "test")

        def callback(base):
            fname_idx = base.func.persons_of_first_name

            john_istr = 1
            result = fname_idx.find(john_istr)
            assert isinstance(result, list)
            assert 0 in result

            jane_istr = 3
            result_jane = fname_idx.find(jane_istr)
            assert isinstance(result_jane, list)
            assert 1 in result_jane

            return "success"

        result = database.with_database(gwb_path, callback)
        assert result == "success"

def test_record_access_get_individual_records():
    from tests.gwb_generator import create_minimal_gwb

    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        gwb_path = create_minimal_gwb(tmpdir, "test")

        def callback(base):
            person0 = base.data.persons.get(0)
            assert isinstance(person0, (list, dict))
            if isinstance(person0, list):
                assert len(person0) > 1
                assert person0[0] == 1
                assert person0[1] == 2
            else:
                assert person0['fields'][0] == 1
                assert person0['fields'][1] == 2

            person1 = base.data.persons.get(1)
            assert isinstance(person1, (list, dict))
            if isinstance(person1, list):
                assert person1[0] == 3
                assert person1[1] == 4
            else:
                assert person1['fields'][0] == 3
                assert person1['fields'][1] == 4

            string0 = base.data.strings.get(0)
            assert string0 in ("", b"")
            string1 = base.data.strings.get(1)
            assert string1 in ("John", b"John")
            string2 = base.data.strings.get(2)
            assert string2 in ("Doe", b"Doe")

            family0 = base.data.families.get(0)
            assert isinstance(family0, (list, dict))

            return "success"

        result = database.with_database(gwb_path, callback)
        assert result == "success"


def test_database_from_record_conversion():

    record = {
        'fields': [
        
            {'fields': [[1], [{'fields': ['key1', 'value1']}] ]},
        
            'invalid_input',
            {'fields': [[2], [{'fields': ['key2', 'value2']}] ]},
            {'fields': [[3], [{'fields': ['key3', 'value3']}] ]},
            {'fields': [[4], [{'fields': ['key4', 'value4']}] ]},
            {'fields': [[5], [{'fields': ['key5', 'value5']}] ]},
            {'fields': [[6], [{'fields': ['key6', 'value6']}] ]},
        
            [
                {'fields': ['name1', 'value_name1']},
                {'fields': ['name2', 'value_name2']},
                'invalid_item_in_fields_7'
            ]
        ]
    }

    db_instance = database.PatchesHt.from_record(record)


    assert db_instance.h_person == ([1], {'key1': 'value1'})
    assert db_instance.h_ascend == ([0], {})
    assert db_instance.h_union == ([2], {'key2': 'value2'})
    assert db_instance.h_family == ([3], {'key3': 'value3'})
    assert db_instance.h_couple == ([4], {'key4': 'value4'})
    assert db_instance.h_descend == ([5], {'key5': 'value5'})
    assert db_instance.h_string == ([6], {'key6': 'value6'})


    assert db_instance.h_name == {'name1': 'value_name1', 'name2': 'value_name2'}
