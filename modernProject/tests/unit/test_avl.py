import pytest
from lib.avl import AVL


def int_compare(a: int, b: int) -> int:
    return (a > b) - (a < b)


def str_compare(a: str, b: str) -> int:
    return (a > b) - (a < b)


class TestAVLBasics:
    def test_empty_tree_find_raises(self):
        tree = AVL[int, str](int_compare)
        with pytest.raises(KeyError):
            tree.find(1)

    def test_empty_tree_mem(self):
        tree = AVL[int, str](int_compare)
        assert not tree.mem(1)

    def test_add_single_element(self):
        tree = AVL[int, str](int_compare)
        tree.add(5, "five")
        assert tree.find(5) == "five"
        assert tree.mem(5)

    def test_add_multiple_elements(self):
        tree = AVL[int, str](int_compare)
        tree.add(5, "five")
        tree.add(3, "three")
        tree.add(7, "seven")
        assert tree.find(5) == "five"
        assert tree.find(3) == "three"
        assert tree.find(7) == "seven"

    def test_overwrite_existing_key(self):
        tree = AVL[int, str](int_compare)
        tree.add(5, "five")
        tree.add(5, "FIVE")
        assert tree.find(5) == "FIVE"


class TestAVLBalancing:
    def test_right_rotation(self):
        tree = AVL[int, int](int_compare)
        tree.add(3, 3)
        tree.add(2, 2)
        tree.add(1, 1)
        assert tree.find(1) == 1
        assert tree.find(2) == 2
        assert tree.find(3) == 3

    def test_left_rotation(self):
        tree = AVL[int, int](int_compare)
        tree.add(1, 1)
        tree.add(2, 2)
        tree.add(3, 3)
        assert tree.find(1) == 1
        assert tree.find(2) == 2
        assert tree.find(3) == 3

    def test_left_right_rotation(self):
        tree = AVL[int, int](int_compare)
        tree.add(3, 3)
        tree.add(1, 1)
        tree.add(2, 2)
        assert tree.find(1) == 1
        assert tree.find(2) == 2
        assert tree.find(3) == 3

    def test_right_left_rotation(self):
        tree = AVL[int, int](int_compare)
        tree.add(1, 1)
        tree.add(3, 3)
        tree.add(2, 2)
        assert tree.find(1) == 1
        assert tree.find(2) == 2
        assert tree.find(3) == 3

    def test_many_elements_ascending(self):
        tree = AVL[int, int](int_compare)
        for i in range(100):
            tree.add(i, i * 2)
        for i in range(100):
            assert tree.find(i) == i * 2

    def test_many_elements_descending(self):
        tree = AVL[int, int](int_compare)
        for i in range(100, 0, -1):
            tree.add(i, i * 3)
        for i in range(1, 101):
            assert tree.find(i) == i * 3


class TestAVLMembership:
    def test_mem_existing(self):
        tree = AVL[int, str](int_compare)
        tree.add(10, "ten")
        tree.add(20, "twenty")
        assert tree.mem(10)
        assert tree.mem(20)

    def test_mem_nonexisting(self):
        tree = AVL[int, str](int_compare)
        tree.add(10, "ten")
        assert not tree.mem(5)
        assert not tree.mem(15)


class TestAVLKeyAfter:
    def test_key_after_exact_match(self):
        tree = AVL[int, str](int_compare)
        tree.add(5, "five")
        tree.add(3, "three")
        tree.add(7, "seven")
        result = tree.key_after(lambda k: int_compare(k, 5))
        assert result == 5

    def test_key_after_not_found(self):
        tree = AVL[int, str](int_compare)
        tree.add(5, "five")
        with pytest.raises(KeyError):
            tree.key_after(lambda k: 1)


class TestAVLNext:
    def test_next_key(self):
        tree = AVL[int, str](int_compare)
        tree.add(5, "five")
        tree.add(3, "three")
        tree.add(7, "seven")
        tree.add(10, "ten")
        result = tree.next(6)
        assert result == 7

    def test_next_exact_key(self):
        tree = AVL[int, str](int_compare)
        tree.add(5, "five")
        tree.add(7, "seven")
        result = tree.next(5)
        assert result == 7

    def test_next_not_found(self):
        tree = AVL[int, str](int_compare)
        tree.add(5, "five")
        with pytest.raises(KeyError):
            tree.next(10)


class TestAVLStringKeys:
    def test_string_keys(self):
        tree = AVL[str, int](str_compare)
        tree.add("apple", 1)
        tree.add("banana", 2)
        tree.add("cherry", 3)
        assert tree.find("apple") == 1
        assert tree.find("banana") == 2
        assert tree.find("cherry") == 3

    def test_string_keys_ordering(self):
        tree = AVL[str, int](str_compare)
        words = ["dog", "cat", "elephant", "ant", "bear"]
        for i, word in enumerate(words):
            tree.add(word, i)
        for i, word in enumerate(words):
            assert tree.find(word) == i
