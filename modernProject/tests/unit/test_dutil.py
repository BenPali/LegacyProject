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


def test_output_value_no_sharing():
    class MockOutput:
        def __init__(self):
            self.data = []
        def write(self, val):
            self.data.append(val)

    oc = MockOutput()
    dutil.output_value_no_sharing(oc, 42)
    assert len(oc.data) > 0


def test_name_index():
    idx1 = dutil.name_index("Test")
    idx2 = dutil.name_index("Test")
    idx3 = dutil.name_index("Different")
    assert idx1 == idx2
    assert idx1 >= 0
    assert idx3 >= 0


def test_compare_snames_no_particles():
    class MockBaseData:
        def __init__(self):
            self.particles = None

    base_data = MockBaseData()
    result = dutil.compare_snames(base_data, "Smith", "Jones")
    assert isinstance(result, int)


def test_person_to_gen_person_from_tuple():
    person_tuple = (
        "John", "Doe", 0, "", "", [], [], [], [],
        [], [], [], "", 0, 0, None, "", "", "",
        None, "", "", "", None, "", "", "",
        None, "", "", "", [], "", []
    )
    result = dutil.person_to_gen_person(person_tuple, None, 0)
    assert result.first_name == "John"
    assert result.surname == "Doe"


def test_person_to_gen_person_short_tuple():
    person_tuple = ("John", "Doe")
    result = dutil.person_to_gen_person(person_tuple, None, 0)
    assert result == person_tuple


def test_person_to_gen_person_invalid_type():
    result = dutil.person_to_gen_person("invalid", None, 0)
    assert result == "invalid"


def test_ascend_to_gen_ascend_from_tuple():
    ascend_tuple = (None, 0.0)
    result = dutil.ascend_to_gen_ascend(ascend_tuple)
    assert result.parents == None
    assert result.consang == 0.0


def test_ascend_to_gen_ascend_from_dict():
    ascend_dict = {"parents": None, "consang": 0.5}
    result = dutil.ascend_to_gen_ascend(ascend_dict)
    assert result.consang == 0.5


def test_ascend_to_gen_ascend_already_genascend():
    from lib.gwdef import GenAscend
    ascend = GenAscend(parents=None, consang=0.0)
    result = dutil.ascend_to_gen_ascend(ascend)
    assert result == ascend


def test_ascend_to_gen_ascend_invalid_type():
    result = dutil.ascend_to_gen_ascend("invalid")
    assert result == "invalid"


def test_union_to_gen_union_from_tuple():
    union_tuple = ([0, 1, 2],)
    result = dutil.union_to_gen_union(union_tuple)
    assert result.family == [0, 1, 2]


def test_union_to_gen_union_from_dict():
    union_dict = {"family": [3, 4, 5]}
    result = dutil.union_to_gen_union(union_dict)
    assert result.family == [3, 4, 5]


def test_union_to_gen_union_already_genunion():
    from lib.gwdef import GenUnion
    union = GenUnion(family=[])
    result = dutil.union_to_gen_union(union)
    assert result == union


def test_union_to_gen_union_invalid_type():
    result = dutil.union_to_gen_union("invalid")
    assert result == "invalid"


def test_family_to_gen_family_from_tuple():
    family_tuple = (
        None, "", "", "", [], 0, 0,
        [], "", "", []
    )
    result = dutil.family_to_gen_family(family_tuple, None, 0)
    assert result.fam_index == 0


def test_family_to_gen_family_short_tuple():
    family_tuple = (None, "Paris")
    result = dutil.family_to_gen_family(family_tuple, None, 10)
    assert result == family_tuple


def test_family_to_gen_family_invalid_type():
    result = dutil.family_to_gen_family("invalid", None, 0)
    assert result == "invalid"


def test_couple_to_gen_couple_from_tuple():
    couple_tuple = (1, 2)
    result = dutil.couple_to_gen_couple(couple_tuple)
    assert result.father == 1
    assert result.mother == 2


def test_couple_to_gen_couple_from_dict():
    couple_dict = {"father": 3, "mother": 4}
    result = dutil.couple_to_gen_couple(couple_dict)
    assert result.father == 3
    assert result.mother == 4


def test_couple_to_gen_couple_already_couple():
    from lib.adef import Couple
    couple = Couple(father=5, mother=6)
    result = dutil.couple_to_gen_couple(couple)
    assert result == couple


def test_couple_to_gen_couple_invalid_type():
    result = dutil.couple_to_gen_couple("invalid")
    assert result == "invalid"


def test_descend_to_gen_descend_from_tuple():
    descend_tuple = ([0, 1, 2],)
    result = dutil.descend_to_gen_descend(descend_tuple)
    assert result.children == [0, 1, 2]


def test_descend_to_gen_descend_from_dict():
    descend_dict = {"children": [3, 4]}
    result = dutil.descend_to_gen_descend(descend_dict)
    assert result.children == [3, 4]


def test_descend_to_gen_descend_already_gendescend():
    from lib.gwdef import GenDescend
    descend = GenDescend(children=[])
    result = dutil.descend_to_gen_descend(descend)
    assert result == descend


def test_descend_to_gen_descend_invalid_type():
    result = dutil.descend_to_gen_descend("invalid")
    assert result == "invalid"
