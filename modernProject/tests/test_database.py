import os
import tempfile
import struct
from lib import database
from lib.dbdisk import Perm, BaseVersion

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
