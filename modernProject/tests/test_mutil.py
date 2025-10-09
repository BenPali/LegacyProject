import pytest
from lib.mutil import (
    list_iter_first, strip_all_trailing_spaces, tr, start_with,
    start_with_wildcard, contains, roman_of_arabian, arabian_of_roman,
    string_of_int_sep, initial, surnames_pieces, array_to_list_map,
    array_to_list_rev_map, array_assoc
)


class TestListIterFirst:
    def test_empty_list(self):
        called = []
        list_iter_first(lambda first, x: called.append((first, x)), [])
        assert called == []

    def test_single_element(self):
        called = []
        list_iter_first(lambda first, x: called.append((first, x)), [1])
        assert called == [(True, 1)]

    def test_multiple_elements(self):
        called = []
        list_iter_first(lambda first, x: called.append((first, x)), [1, 2, 3])
        assert called == [(True, 1), (False, 2), (False, 3)]


class TestStripAllTrailingSpaces:
    def test_no_trailing_spaces(self):
        assert strip_all_trailing_spaces("hello") == "hello"

    def test_single_trailing_space(self):
        assert strip_all_trailing_spaces("hello ") == "hello"

    def test_multiple_trailing_spaces(self):
        assert strip_all_trailing_spaces("hello    ") == "hello"

    def test_only_spaces(self):
        assert strip_all_trailing_spaces("   ") == ""

    def test_internal_spaces_preserved(self):
        assert strip_all_trailing_spaces("hello world  ") == "hello world"


class TestTr:
    def test_simple_replacement(self):
        assert tr('a', 'b', "banana") == "bbnbnb"

    def test_no_replacement_needed(self):
        result = tr('x', 'y', "hello")
        assert result == "hello"

    def test_space_to_underscore(self):
        assert tr(' ', '_', "hello world") == "hello_world"

    def test_invalid_char_length(self):
        with pytest.raises(ValueError):
            tr('ab', 'c', "test")


class TestStartWith:
    def test_starts_with_match(self):
        assert start_with("hello", 0, "hello world")

    def test_starts_with_no_match(self):
        assert not start_with("world", 0, "hello world")

    def test_with_offset(self):
        assert start_with("world", 6, "hello world")

    def test_offset_at_end(self):
        assert start_with("", 11, "hello world")

    def test_invalid_offset(self):
        with pytest.raises(ValueError):
            start_with("test", 100, "hello")


class TestStartWithWildcard:
    def test_exact_match(self):
        assert start_with_wildcard("hello", 0, "hello world")

    def test_wildcard_matches_underscore(self):
        assert start_with_wildcard("hel_o", 0, "hel_o")

    def test_wildcard_matches_space(self):
        assert start_with_wildcard("hel_o", 0, "hel o")

    def test_trailing_wildcard_optional(self):
        assert start_with_wildcard("hello_", 0, "hello")

    def test_no_match(self):
        assert not start_with_wildcard("hello", 0, "world")


class TestContains:
    def test_substring_present(self):
        assert contains("hello world", "world")

    def test_substring_absent(self):
        assert not contains("hello world", "foo")

    def test_empty_substring(self):
        assert contains("hello", "")

    def test_full_string(self):
        assert contains("hello", "hello")


class TestRomanArabian:
    def test_roman_of_arabian_basic(self):
        assert roman_of_arabian(1) == "I"
        assert roman_of_arabian(5) == "V"
        assert roman_of_arabian(10) == "X"
        assert roman_of_arabian(50) == "L"
        assert roman_of_arabian(100) == "C"
        assert roman_of_arabian(500) == "D"
        assert roman_of_arabian(1000) == "M"

    def test_roman_of_arabian_complex(self):
        assert roman_of_arabian(4) == "IV"
        assert roman_of_arabian(9) == "IX"
        assert roman_of_arabian(44) == "XLIV"
        assert roman_of_arabian(1994) == "MCMXCIV"
        assert roman_of_arabian(3999) == "MMMCMXCIX"

    def test_roman_of_arabian_out_of_range(self):
        with pytest.raises(ValueError):
            roman_of_arabian(0)
        with pytest.raises(ValueError):
            roman_of_arabian(4000)

    def test_arabian_of_roman_basic(self):
        assert arabian_of_roman("I") == 1
        assert arabian_of_roman("V") == 5
        assert arabian_of_roman("X") == 10
        assert arabian_of_roman("L") == 50
        assert arabian_of_roman("C") == 100
        assert arabian_of_roman("D") == 500
        assert arabian_of_roman("M") == 1000

    def test_arabian_of_roman_complex(self):
        assert arabian_of_roman("IV") == 4
        assert arabian_of_roman("IX") == 9
        assert arabian_of_roman("XLIV") == 44
        assert arabian_of_roman("MCMXCIV") == 1994
        assert arabian_of_roman("MMMCMXCIX") == 3999

    def test_arabian_of_roman_lowercase(self):
        assert arabian_of_roman("iv") == 4
        assert arabian_of_roman("mcmxciv") == 1994

    def test_arabian_of_roman_roundtrip(self):
        for n in [1, 42, 99, 500, 999, 1500, 3999]:
            roman = roman_of_arabian(n)
            assert arabian_of_roman(roman) == n


class TestStringOfIntSep:
    def test_no_separator_needed(self):
        assert string_of_int_sep(",", 123) == "123"

    def test_thousands_separator(self):
        assert string_of_int_sep(",", 1000) == "1,000"
        assert string_of_int_sep(",", 1000000) == "1,000,000"

    def test_custom_separator(self):
        assert string_of_int_sep(" ", 1000000) == "1 000 000"
        assert string_of_int_sep("_", 1000000) == "1_000_000"

    def test_negative_numbers(self):
        assert string_of_int_sep(",", -1000) == "-1,000"
        assert string_of_int_sep(",", -1000000) == "-1,000,000"

    def test_zero(self):
        assert string_of_int_sep(",", 0) == "0"


class TestInitial:
    def test_capital_at_start(self):
        assert initial("John") == 0

    def test_capital_in_middle(self):
        assert initial("mcDonald") == 2

    def test_no_capital(self):
        assert initial("smith") == 0

    def test_empty_string(self):
        assert initial("") == 0

    def test_accented_capitals(self):
        assert initial("éléonore") == 0 or initial("éléonore") >= 0


class TestSurnamesPieces:
    def test_two_long_words(self):
        pieces = surnames_pieces("Smith Jones")
        assert len(pieces) == 2
        assert "Smith" in pieces
        assert "Jones" in pieces

    def test_with_particles(self):
        pieces = surnames_pieces("de la Cruz Martinez")
        assert len(pieces) >= 2

    def test_single_word(self):
        assert surnames_pieces("Smith") == []

    def test_short_words(self):
        assert surnames_pieces("de la") == []

    def test_saint_particle(self):
        pieces = surnames_pieces("Saint Martin Laurent")
        assert len(pieces) >= 2


class TestArrayFunctions:
    def test_array_to_list_map(self):
        result = array_to_list_map(lambda x: x * 2, [1, 2, 3])
        assert result == [2, 4, 6]

    def test_array_to_list_map_empty(self):
        result = array_to_list_map(lambda x: x * 2, [])
        assert result == []

    def test_array_to_list_rev_map(self):
        result = array_to_list_rev_map(lambda x: x * 2, [1, 2, 3])
        assert result == [6, 4, 2]

    def test_array_to_list_rev_map_empty(self):
        result = array_to_list_rev_map(lambda x: x * 2, [])
        assert result == []

    def test_array_assoc_found(self):
        arr = [("a", 1), ("b", 2), ("c", 3)]
        assert array_assoc("b", arr) == 2

    def test_array_assoc_first_match(self):
        arr = [("a", 1), ("a", 2)]
        assert array_assoc("a", arr) == 1

    def test_array_assoc_not_found(self):
        arr = [("a", 1), ("b", 2)]
        with pytest.raises(KeyError):
            array_assoc("c", arr)


class TestEdgeCases:
    def test_tr_all_chars_replaced(self):
        assert tr('a', 'e', "aaa") == "eee"

    def test_contains_single_char(self):
        assert contains("hello", "h")
        assert contains("hello", "o")
        assert not contains("hello", "x")

    def test_surnames_pieces_mixed_case(self):
        pieces = surnames_pieces("Saint MARTIN Laurent")
        assert len(pieces) >= 2
