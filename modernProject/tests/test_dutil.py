import pytest
from lib import dutil
from lib.dbdisk import RecordAccess


class TestArrayFunctions:
    def test_array_forall(self):
        assert dutil.array_forall(lambda x: x > 0, [1, 2, 3])
        assert not dutil.array_forall(lambda x: x > 0, [1, -2, 3])
        assert dutil.array_forall(lambda x: x < 10, [])

    def test_array_exists(self):
        assert dutil.array_exists(lambda x: x > 5, [1, 6, 3])
        assert not dutil.array_exists(lambda x: x > 10, [1, 6, 3])
        assert not dutil.array_exists(lambda x: x > 0, [])

    def test_array_associ(self):
        assert dutil.array_associ(lambda x: x == 5, [1, 5, 3]) == 1
        assert dutil.array_associ(lambda x: x > 15, [10, 20, 30]) == 1
        with pytest.raises(ValueError):
            dutil.array_associ(lambda x: x == 10, [1, 5, 3])

    def test_array_find_all(self):
        assert dutil.array_find_all(lambda x: x > 2, [1, 3, 2, 5]) == [3, 5]
        assert dutil.array_find_all(lambda x: x < 0, [1, 2, 3]) == []
        assert dutil.array_find_all(lambda x: x % 2 == 0, [1, 2, 3, 4]) == [2, 4]

    def test_sort_uniq(self):
        assert dutil.sort_uniq(None, [3, 1, 2, 1, 3]) == [1, 2, 3]
        assert dutil.sort_uniq(None, []) == []
        assert dutil.sort_uniq(None, [5, 5, 5]) == [5]

def test_name_index():
    idx1 = dutil.name_index("Smith")
    idx2 = dutil.name_index("Smith")
    idx3 = dutil.name_index("Jones")
    assert idx1 == idx2
    assert 0 <= idx1 < 0x3FFF
    assert 0 <= idx3 < 0x3FFF

def test_compare_fnames():
    assert dutil.compare_fnames("Alice", "Bob") < 0
    assert dutil.compare_fnames("Bob", "Alice") > 0
    assert dutil.compare_fnames("Alice", "Alice") == 0
    assert dutil.compare_fnames("", "A") < 0

def test_compare_fnames_i():
    strings = RecordAccess(
        load_array=lambda: None,
        get=lambda i: ["", "Alice", "Bob", "Charlie"][i],
        get_nopending=lambda i: ["", "Alice", "Bob", "Charlie"][i],
        len=4,
        output_array=lambda oc: None,
        clear_array=lambda: None
    )

    class MockBaseData:
        pass

    base_data = MockBaseData()
    base_data.strings = strings

    assert dutil.compare_fnames_i(base_data, 1, 2) < 0
    assert dutil.compare_fnames_i(base_data, 2, 1) > 0
    assert dutil.compare_fnames_i(base_data, 1, 1) == 0
    assert dutil.compare_fnames_i(base_data, 3, 3) == 0

def test_compare_snames():
    class MockBaseData:
        def __init__(self):
            self.particles = ["de", "von", "van"]

    base_data = MockBaseData()

    assert dutil.compare_snames(base_data, "Smith", "Jones") != 0
    assert dutil.compare_snames(base_data, "de Smith", "Smith") == 0
    assert dutil.compare_snames(base_data, "Smith", "Smith") == 0

def test_compare_snames_i():
    strings = RecordAccess(
        load_array=lambda: None,
        get=lambda i: ["", "Smith", "de Smith", "Jones"][i],
        get_nopending=lambda i: ["", "Smith", "de Smith", "Jones"][i],
        len=4,
        output_array=lambda oc: None,
        clear_array=lambda: None
    )

    class MockBaseData:
        def __init__(self):
            self.particles = ["de", "von"]
            self.strings = strings

    base_data = MockBaseData()

    assert dutil.compare_snames_i(base_data, 1, 1) == 0
    assert dutil.compare_snames_i(base_data, 1, 2) == 0
    assert dutil.compare_snames_i(base_data, 1, 3) != 0
