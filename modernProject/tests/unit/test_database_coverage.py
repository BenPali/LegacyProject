import os
import tempfile
import pytest
from lib import database, iovalue, secure
from tests.gwb_generator import create_minimal_gwb

def test_patches_from_record_invalid():
    empty_ht = database.PatchesHt.from_record(None)
    assert empty_ht.h_person == ([0], {})

    invalid_dict = {'tag': 0}
    empty_ht2 = database.PatchesHt.from_record(invalid_dict)
    assert empty_ht2.h_person == ([0], {})

    wrong_fields = {'fields': [1, 2, 3]}
    empty_ht3 = database.PatchesHt.from_record(wrong_fields)
    assert empty_ht3.h_person == ([0], {})

def test_patches_to_record_and_back():
    patches = database.empty_patch_ht()
    record = patches.to_record()
    assert isinstance(record, dict)
    assert 'fields' in record
    assert len(record['fields']) == 8

    restored = database.PatchesHt.from_record(record)
    assert restored.h_person == ([0], {})
    assert restored.h_ascend == ([0], {})

def test_apply_patches_with_bytes():
    arr = b"hello"
    patches = {2: ord('X')}
    result = database.apply_patches(arr, patches, 5)
    assert isinstance(result, list)
    assert len(result) == 5
    assert result[0] == ord('h')
    assert result[2] == ord('X')

def test_apply_patches_expand():
    arr = [1, 2, 3]
    patches = {1: 99}
    result = database.apply_patches(arr, patches, 5)
    assert len(result) == 5
    assert result[1] == 99
    assert result[4] is None

def test_base_func_patch_operations():
    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        gwb_path = create_minimal_gwb(tmpdir, "test")

        def callback(base):
            original_person = base.data.persons.get(0)

            new_person = original_person.copy() if isinstance(original_person, dict) else list(original_person)
            if isinstance(new_person, dict):
                new_person['fields'][0] = 99
            else:
                new_person[0] = 99

            base.func.patch_person(0, new_person)

            modified = base.data.persons.get(0)
            if isinstance(modified, dict):
                assert modified['fields'][0] == 99
            else:
                assert modified[0] == 99

            return "success"

        result = database.with_database(gwb_path, callback, read_only=False)
        assert result == "success"

def test_base_func_patch_ascend():
    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        gwb_path = create_minimal_gwb(tmpdir, "test")

        def callback(base):
            original = base.data.ascends.get(0)
            new_ascend = original.copy() if isinstance(original, dict) else list(original)
            base.func.patch_ascend(0, new_ascend)
            return "success"

        result = database.with_database(gwb_path, callback, read_only=False)
        assert result == "success"

def test_base_func_patch_union():
    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        gwb_path = create_minimal_gwb(tmpdir, "test")

        def callback(base):
            original = base.data.unions.get(0)
            new_union = original.copy() if isinstance(original, dict) else list(original)
            base.func.patch_union(0, new_union)
            return "success"

        result = database.with_database(gwb_path, callback, read_only=False)
        assert result == "success"

def test_base_func_patch_family():
    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        gwb_path = create_minimal_gwb(tmpdir, "test")

        def callback(base):
            original = base.data.families.get(0)
            new_family = original.copy() if isinstance(original, dict) else list(original)
            base.func.patch_family(0, new_family)
            return "success"

        result = database.with_database(gwb_path, callback, read_only=False)
        assert result == "success"

def test_base_func_patch_couple():
    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        gwb_path = create_minimal_gwb(tmpdir, "test")

        def callback(base):
            original = base.data.couples.get(0)
            new_couple = original.copy() if isinstance(original, dict) else list(original)
            base.func.patch_couple(0, new_couple)
            return "success"

        result = database.with_database(gwb_path, callback, read_only=False)
        assert result == "success"

def test_base_func_patch_descend():
    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        gwb_path = create_minimal_gwb(tmpdir, "test")

        def callback(base):
            original = base.data.descends.get(0)
            new_descend = original.copy() if isinstance(original, dict) else list(original)
            base.func.patch_descend(0, new_descend)
            return "success"

        result = database.with_database(gwb_path, callback, read_only=False)
        assert result == "success"

def test_base_func_patch_name():
    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        gwb_path = create_minimal_gwb(tmpdir, "test")

        def callback(base):
            base.func.patch_name("TestName", 0)
            return "success"

        result = database.with_database(gwb_path, callback, read_only=False)
        assert result == "success"

def test_base_func_commit_notes_not_implemented():
    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        gwb_path = create_minimal_gwb(tmpdir, "test")

        def callback(base):
            with pytest.raises(NotImplementedError):
                base.func.commit_notes("test_note", "Note content")
            return "success"

        result = database.with_database(gwb_path, callback, read_only=False)
        assert result == "success"

def test_base_func_commit_wiznotes_not_implemented():
    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        gwb_path = create_minimal_gwb(tmpdir, "test")

        def callback(base):
            with pytest.raises(NotImplementedError):
                base.func.commit_wiznotes("test_wiz", "Wiznote content")
            return "success"

        result = database.with_database(gwb_path, callback, read_only=False)
        assert result == "success"

def test_base_func_commit_readonly_check():
    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        gwb_path = create_minimal_gwb(tmpdir, "test")

        def callback(base):
            with pytest.raises(RuntimeError, match="read-only"):
                base.func.commit_notes("test", "content")
            return "success"

        result = database.with_database(gwb_path, callback, read_only=True)
        assert result == "success"

def test_iper_and_ifam_exists():
    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        gwb_path = create_minimal_gwb(tmpdir, "test")

        def callback(base):
            assert base.func.iper_exists(0) is True
            assert base.func.iper_exists(1) is True
            assert base.func.iper_exists(2) is False
            assert base.func.iper_exists(-1) is False

            assert base.func.ifam_exists(0) is True
            assert base.func.ifam_exists(1) is False
            assert base.func.ifam_exists(-1) is False

            return "success"

        result = database.with_database(gwb_path, callback)
        assert result == "success"


def test_person_of_key():
    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        gwb_path = create_minimal_gwb(tmpdir, "test")

        def callback(base):
            result = base.func.person_of_key("John", "Doe", 0)
            assert result == 0

            result_not_found = base.func.person_of_key("NonExistent", "Person", 0)
            assert result_not_found is None

            return "success"

        result = database.with_database(gwb_path, callback)
        assert result == "success"

def test_immut_record_error_handling():
    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        gwb_path = create_minimal_gwb(tmpdir, "test")

        def callback(base):
            with pytest.raises(IndexError):
                base.data.persons.get(999)

            with pytest.raises(IndexError):
                base.data.persons.get(-1)

            return "success"

        result = database.with_database(gwb_path, callback)
        assert result == "success"

def test_record_access_clear_array():
    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)
        gwb_path = create_minimal_gwb(tmpdir, "test")

        def callback(base):
            base.data.persons.load_array()

            base.data.persons.clear_array()

            person0 = base.data.persons.get(0)
            assert isinstance(person0, (list, dict))

            return "success"

        result = database.with_database(gwb_path, callback)
        assert result == "success"

def test_database_make_function():
    persons = [
        {'first_name': 1, 'surname': 2, 'occ': 0}
    ]
    ascends = [{'parents': None}]
    unions = [{'family': []}]
    families = []
    couples = []
    descends = []
    strings = ["", "John", "Doe"]

    from lib.gwdef import BaseNotes
    mock_bnotes = BaseNotes(
        nread=lambda fname, mode: "",
        norigin_file="",
        efiles=lambda: []
    )

    persons_tuple = (persons, ascends, unions)
    families_tuple = (families, couples, descends)
    arrays = (persons_tuple, families_tuple, strings, mock_bnotes)

    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)

        def callback(base):
            assert base.func.nb_of_real_persons() == 1
            assert base.func.iper_exists(0)
            assert not base.func.iper_exists(1)
            assert not base.func.ifam_exists(0)

            base.func.patch_person(0, persons[0])
            base.func.insert_string("NewString")
            base.func.commit_patches()

            return "success"

        result = database.make(tmpdir, [], arrays, callback)
        assert result == "success"

def test_database_make_with_stub_functions():
    persons = []
    ascends = []
    unions = []
    families = []
    couples = []
    descends = []
    strings = [""]

    from lib.gwdef import BaseNotes
    mock_bnotes = BaseNotes(
        nread=lambda fname, mode: "",
        norigin_file="",
        efiles=lambda: []
    )

    persons_tuple = (persons, ascends, unions)
    families_tuple = (families, couples, descends)
    arrays = (persons_tuple, families_tuple, strings, mock_bnotes)

    with tempfile.TemporaryDirectory() as tmpdir:
        secure.add_assets(tmpdir)

        def callback(base):
            result = base.func.persons_of_name("test")
            assert result == []

            result = base.func.strings_of_sname("test")
            assert result == []

            result = base.func.strings_of_fname("test")
            assert result == []

            idx = base.func.persons_of_surname
            result = idx.find(1)
            assert result == []

            idx = base.func.persons_of_first_name
            result = idx.find(1)
            assert result == []

            with pytest.raises(KeyError):
                base.func.persons_of_surname.cursor("test")

            with pytest.raises(KeyError):
                base.func.persons_of_surname.next(1)

            return "success"

        result = database.make(tmpdir, [], arrays, callback)
        assert result == "success"
