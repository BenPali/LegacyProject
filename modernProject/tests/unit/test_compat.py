import pytest
from lib.compat import list_equal


def test_list_equal_empty_lists():
    def eq(a, b):
        return a == b
    assert list_equal(eq, [], [])


def test_list_equal_same_elements():
    def eq(a, b):
        return a == b
    assert list_equal(eq, [1, 2, 3], [1, 2, 3])


def test_list_equal_different_elements():
    def eq(a, b):
        return a == b
    assert not list_equal(eq, [1, 2, 3], [1, 2, 4])


def test_list_equal_different_lengths():
    def eq(a, b):
        return a == b
    assert not list_equal(eq, [1, 2], [1, 2, 3])
    assert not list_equal(eq, [1, 2, 3], [1, 2])


def test_list_equal_custom_equality():
    def case_insensitive_eq(a, b):
        return a.lower() == b.lower()
    assert list_equal(case_insensitive_eq, ["Hello", "World"], ["hello", "world"])


def test_list_equal_custom_equality_fails():
    def case_insensitive_eq(a, b):
        return a.lower() == b.lower()
    assert not list_equal(case_insensitive_eq, ["Hello", "World"], ["hello", "earth"])


def test_list_equal_single_element():
    def eq(a, b):
        return a == b
    assert list_equal(eq, [42], [42])
    assert not list_equal(eq, [42], [43])


def test_list_equal_complex_objects():
    def dict_eq(a, b):
        return a == b
    list1 = [{"a": 1}, {"b": 2}]
    list2 = [{"a": 1}, {"b": 2}]
    list3 = [{"a": 1}, {"b": 3}]
    assert list_equal(dict_eq, list1, list2)
    assert not list_equal(dict_eq, list1, list3)


def test_list_equal_always_true_eq():
    def always_true(a, b):
        return True
    assert list_equal(always_true, [1, 2, 3], [4, 5, 6])


def test_list_equal_always_false_eq():
    def always_false(a, b):
        return False
    assert not list_equal(always_false, [1, 2, 3], [1, 2, 3])
