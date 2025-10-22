import pytest
from modernProject.lib import difference


def test_empty_arrays():
    first_array = []
    second_array = []
    differences_in_first, differences_in_second = difference.f(first_array, second_array)
    assert differences_in_first == []
    assert differences_in_second == []


def test_identical_arrays():
    first_array = ['a', 'b', 'c', 'd']
    second_array = ['a', 'b', 'c', 'd']
    differences_in_first, differences_in_second = difference.f(first_array, second_array)
    assert differences_in_first == [False, False, False, False]
    assert differences_in_second == [False, False, False, False]


def test_completely_different():
    first_array = ['a', 'b', 'c']
    second_array = ['x', 'y', 'z']
    differences_in_first, differences_in_second = difference.f(first_array, second_array)
    assert differences_in_first == [True, True, True]
    assert differences_in_second == [True, True, True]


def test_first_empty():
    empty_array = []
    non_empty_array = ['x', 'y', 'z']
    differences_in_first, differences_in_second = difference.f(empty_array, non_empty_array)
    assert differences_in_first == []
    assert differences_in_second == [True, True, True]


def test_second_empty():
    non_empty_array = ['a', 'b', 'c']
    empty_array = []
    differences_in_first, differences_in_second = difference.f(non_empty_array, empty_array)
    assert differences_in_first == [True, True, True]
    assert differences_in_second == []


def test_some_common_elements():
    first_array = ['a', 'b', 'c', 'd']
    second_array = ['b', 'd', 'e']
    differences_in_first, differences_in_second = difference.f(first_array, second_array)
    assert differences_in_first == [True, False, True, False]
    assert differences_in_second == [False, False, True]


def test_insertion_at_beginning():
    original = ['a', 'b', 'c']
    with_insertion = ['x', 'a', 'b', 'c']
    differences_in_original, differences_in_modified = difference.f(original, with_insertion)
    assert differences_in_original == [False, False, False]
    assert differences_in_modified == [True, False, False, False]


def test_insertion_at_end():
    original = ['a', 'b', 'c']
    with_insertion = ['a', 'b', 'c', 'x']
    differences_in_original, differences_in_modified = difference.f(original, with_insertion)
    assert differences_in_original == [False, False, False]
    assert differences_in_modified == [False, False, False, True]


def test_insertion_in_middle():
    original = ['a', 'b', 'c']
    with_insertion = ['a', 'x', 'b', 'c']
    differences_in_original, differences_in_modified = difference.f(original, with_insertion)
    assert differences_in_original == [False, False, False]
    assert differences_in_modified == [False, True, False, False]


def test_deletion_at_beginning():
    original = ['x', 'a', 'b', 'c']
    with_deletion = ['a', 'b', 'c']
    differences_in_original, differences_in_modified = difference.f(original, with_deletion)
    assert differences_in_original == [True, False, False, False]
    assert differences_in_modified == [False, False, False]


def test_deletion_at_end():
    original = ['a', 'b', 'c', 'x']
    with_deletion = ['a', 'b', 'c']
    differences_in_original, differences_in_modified = difference.f(original, with_deletion)
    assert differences_in_original == [False, False, False, True]
    assert differences_in_modified == [False, False, False]


def test_deletion_in_middle():
    original = ['a', 'x', 'b', 'c']
    with_deletion = ['a', 'b', 'c']
    differences_in_original, differences_in_modified = difference.f(original, with_deletion)
    assert differences_in_original == [False, True, False, False]
    assert differences_in_modified == [False, False, False]


def test_multiple_insertions():
    original = ['a', 'b']
    with_insertions = ['x', 'a', 'y', 'b', 'z']
    differences_in_original, differences_in_modified = difference.f(original, with_insertions)
    assert differences_in_original == [False, False]
    assert differences_in_modified == [True, False, True, False, True]


def test_multiple_deletions():
    original = ['x', 'a', 'y', 'b', 'z']
    with_deletions = ['a', 'b']
    differences_in_original, differences_in_modified = difference.f(original, with_deletions)
    assert differences_in_original == [True, False, True, False, True]
    assert differences_in_modified == [False, False]


def test_replacement():
    original = ['a', 'b', 'c']
    with_replacement = ['a', 'x', 'c']
    differences_in_original, differences_in_modified = difference.f(original, with_replacement)
    assert differences_in_original == [False, True, False]
    assert differences_in_modified == [False, True, False]


def test_numbers():
    first_numbers = [1, 2, 3, 4]
    second_numbers = [2, 3, 5, 6]
    differences_in_first, differences_in_second = difference.f(first_numbers, second_numbers)
    assert differences_in_first == [True, False, False, True]
    assert differences_in_second == [False, False, True, True]


def test_single_element_same():
    first_array = ['a']
    second_array = ['a']
    differences_in_first, differences_in_second = difference.f(first_array, second_array)
    assert differences_in_first == [False]
    assert differences_in_second == [False]


def test_single_element_different():
    first_array = ['a']
    second_array = ['b']
    differences_in_first, differences_in_second = difference.f(first_array, second_array)
    assert differences_in_first == [True]
    assert differences_in_second == [True]


def test_reordered_elements():
    first_array = ['a', 'b', 'c']
    second_array = ['c', 'b', 'a']
    differences_in_first, differences_in_second = difference.f(first_array, second_array)
    assert differences_in_first == [True, True, False]
    assert differences_in_second == [False, True, True]


def test_duplicate_elements():
    first_array = ['a', 'b', 'a']
    second_array = ['a', 'c', 'a']
    differences_in_first, differences_in_second = difference.f(first_array, second_array)
    assert differences_in_first == [False, True, False]
    assert differences_in_second == [False, True, False]


def test_long_common_sequence():
    first_array = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
    second_array = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
    differences_in_first, differences_in_second = difference.f(first_array, second_array)
    assert all(not x for x in differences_in_first)
    assert all(not x for x in differences_in_second)


def test_long_different_sequence():
    first_numbers = list(range(100))
    second_numbers = list(range(100, 200))
    differences_in_first, differences_in_second = difference.f(first_numbers, second_numbers)
    assert all(x for x in differences_in_first)
    assert all(x for x in differences_in_second)


def test_mixed_types_in_sequence():
    first_lines = ['line1', 'line2', 'line3', 'line4']
    second_lines = ['line1', 'line2_modified', 'line3', 'line5']
    differences_in_first, differences_in_second = difference.f(first_lines, second_lines)
    assert differences_in_first == [False, True, False, True]
    assert differences_in_second == [False, True, False, True]


def test_file_diff_simulation():
    file1 = [
        'import sys',
        'def hello():',
        '    print("Hello")',
        'hello()'
    ]
    file2 = [
        'import sys',
        'import os',
        'def hello():',
        '    print("Hello World")',
        'hello()'
    ]
    differences_in_file1, differences_in_file2 = difference.f(file1, file2)
    assert differences_in_file1 == [False, False, True, False]
    assert differences_in_file2 == [False, True, False, True, False]


def test_strings_as_char_arrays():
    first_chars = list('hello')
    second_chars = list('hallo')
    differences_in_first, differences_in_second = difference.f(first_chars, second_chars)
    assert differences_in_first == [False, True, False, False, False]
    assert differences_in_second == [False, True, False, False, False]


def test_ensure_same_false_count():
    first_array = ['a', 'b', 'c', 'd']
    second_array = ['a', 'x', 'c', 'y']
    differences_in_first, differences_in_second = difference.f(first_array, second_array)
    false_count_in_first = sum(1 for x in differences_in_first if not x)
    false_count_in_second = sum(1 for x in differences_in_second if not x)
    assert false_count_in_first == false_count_in_second


def test_complex_diff():
    first_array = ['a', 'b', 'c', 'd', 'e', 'f']
    second_array = ['b', 'c', 'x', 'e', 'f', 'g']
    differences_in_first, differences_in_second = difference.f(first_array, second_array)
    assert differences_in_first == [True, False, False, True, False, False]
    assert differences_in_second == [False, False, True, False, False, True]
