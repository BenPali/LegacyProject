import pytest
from lib.dutil import array_forall, array_exists, array_associ, array_find_all, sort_uniq


class TestArrayFunctions:
    def test_array_forall(self):
        assert array_forall(lambda x: x > 0, [1, 2, 3])
        assert not array_forall(lambda x: x > 0, [1, -2, 3])

    def test_array_exists(self):
        assert array_exists(lambda x: x > 5, [1, 6, 3])
        assert not array_exists(lambda x: x > 10, [1, 6, 3])

    def test_array_associ(self):
        assert array_associ(lambda x: x == 5, [1, 5, 3]) == 1
        with pytest.raises(ValueError):
            array_associ(lambda x: x == 10, [1, 5, 3])

    def test_array_find_all(self):
        assert array_find_all(lambda x: x > 2, [1, 3, 2, 5]) == [3, 5]

    def test_sort_uniq(self):
        assert sort_uniq(None, [3, 1, 2, 1, 3]) == [1, 2, 3]
