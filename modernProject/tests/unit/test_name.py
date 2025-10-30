import pytest
from lib.name import (
    FORBIDDEN_CHAR, unaccent_utf_8, next_chars_if_equiv, lower, title,
    abbrev, strip_c, strip, purge, crush, strip_lower, crush_lower,
    concat, contains_forbidden_char, split_sname, split_fname
)


class TestUnaccentUtf8:
    def test_ascii_char_lower(self):
        result, pos = unaccent_utf_8(True, "Hello", 0)
        assert result == "h"
        assert pos == 1

    def test_ascii_char_no_lower(self):
        result, pos = unaccent_utf_8(False, "Hello", 0)
        assert result == "H"
        assert pos == 1

    def test_accented_char(self):
        result, pos = unaccent_utf_8(True, "été", 0)
        assert result == "e"
        assert pos == 1

    def test_position_increment(self):
        result, pos = unaccent_utf_8(True, "café", 3)
        assert result == "e"
        assert pos == 4


class TestNextCharsIfEquiv:
    def test_equivalent_chars(self):
        result = next_chars_if_equiv("café", 3, "cafe", 3)
        assert result == (4, 4)

    def test_non_equivalent_chars(self):
        result = next_chars_if_equiv("abc", 0, "xyz", 0)
        assert result is None

    def test_out_of_bounds(self):
        result = next_chars_if_equiv("ab", 5, "cd", 0)
        assert result is None


class TestLower:
    def test_simple_lowercase(self):
        assert lower("HELLO") == "hello"

    def test_with_accents(self):
        result = lower("Café")
        assert "caf" in result

    def test_remove_special_chars(self):
        result = lower("hello-world")
        assert "-" not in result or " " in result

    def test_keep_alphanumeric(self):
        result = lower("abc123")
        assert "abc123" in result

    def test_keep_dot(self):
        result = lower("Mr.")
        assert "mr." in result


class TestTitle:
    def test_simple_title(self):
        assert title("hello world") == "Hello World"

    def test_already_titled(self):
        assert title("Hello World") == "Hello World"

    def test_mixed_case(self):
        assert title("hELLO wORLD") == "Hello World"


class TestAbbrev:
    def test_remove_de(self):
        result = abbrev("de la Cruz")
        assert "de" not in result or result.startswith("Cruz")

    def test_saint_to_st(self):
        assert abbrev("saint Martin") == "st Martin"

    def test_sainte_to_ste(self):
        assert abbrev("sainte Marie") == "ste Marie"

    def test_no_abbrev(self):
        assert abbrev("Smith Jones") == "Smith Jones"

    def test_ier_to_i(self):
        result = abbrev("ier something")
        assert result == "i something"


class TestStrip:
    def test_strip_spaces(self):
        assert strip("hello world") == "helloworld"

    def test_strip_c_custom_char(self):
        assert strip_c("hello-world", '-') == "helloworld"

    def test_strip_multiple_spaces(self):
        assert strip("a b c d") == "abcd"

    def test_no_spaces(self):
        assert strip("hello") == "hello"


class TestPurge:
    def test_remove_forbidden_chars(self):
        s = "hello:world@test#foo=bar$baz"
        result = purge(s)
        for char in FORBIDDEN_CHAR:
            assert char not in result

    def test_no_forbidden_chars(self):
        assert purge("hello world") == "hello world"

    def test_all_forbidden(self):
        s = ":@#=$"
        result = purge(s)
        assert result == ""


class TestCrush:
    def test_remove_vowels(self):
        result = crush("hello")
        assert "e" not in result or result[0] == "e"

    def test_keep_initial_vowel(self):
        result = crush("apple")
        assert result[0] == "e"

    def test_k_to_c(self):
        result = crush("king")
        assert "c" in result

    def test_z_to_s(self):
        result = crush("zebra")
        assert "s" in result

    def test_no_spaces(self):
        result = crush("hello world")
        assert " " not in result

    def test_roman_numbers(self):
        result = crush("Louis XIV")
        assert "XIV" in result


class TestStripLower:
    def test_combined_operation(self):
        result = strip_lower("Hello World")
        assert result == "helloworld"

    def test_with_special_chars(self):
        result = strip_lower("Café-Bar")
        assert " " not in result


class TestCrushLower:
    def test_full_pipeline(self):
        result = crush_lower("Saint Marie")
        assert " " not in result
        assert len(result) < len("Saint Marie")


class TestConcat:
    def test_simple_concat(self):
        assert concat("John", "Doe") == "John Doe"

    def test_empty_surname(self):
        assert concat("John", "") == "John"

    def test_both_empty(self):
        assert concat("", "") == ""


class TestContainsForbiddenChar:
    def test_has_forbidden(self):
        assert contains_forbidden_char("hello:world")
        assert contains_forbidden_char("test@example")
        assert contains_forbidden_char("foo#bar")

    def test_no_forbidden(self):
        assert not contains_forbidden_char("hello world")
        assert not contains_forbidden_char("test-example")


class TestSplitSname:
    def test_hyphenated_surname(self):
        result = split_sname("Smith-Jones")
        assert len(result) == 2
        assert "Smith" in result
        assert "Jones" in result

    def test_space_separated(self):
        result = split_sname("Van Der Berg")
        assert len(result) >= 2

    def test_single_name(self):
        result = split_sname("Smith")
        assert result == ["Smith"]

    def test_mixed_separators(self):
        result = split_sname("Foo-Bar Baz")
        assert len(result) >= 2


class TestSplitFname:
    def test_space_separated_names(self):
        result = split_fname("Jean Pierre")
        assert len(result) == 2
        assert "Jean" in result
        assert "Pierre" in result

    def test_hyphenated_first_name(self):
        result = split_fname("Jean-Pierre Marie")
        assert len(result) >= 1
        assert any("Jean" in r and "Pierre" in r for r in result)

    def test_single_name(self):
        result = split_fname("John")
        assert result == ["John"]

    def test_complex_pattern(self):
        result = split_fname("Jean-Pierre Paul Marie")
        assert len(result) >= 2


class TestEdgeCases:
    def test_empty_string_lower(self):
        assert lower("") == ""

    def test_empty_string_strip(self):
        assert strip("") == ""

    def test_empty_string_crush(self):
        assert crush("") == ""

    def test_unicode_lower(self):
        result = lower("Ñoño")
        assert result != ""

    def test_numbers_preserved(self):
        result = lower("abc123xyz")
        assert "123" in result

    def test_dot_preserved_in_lower(self):
        result = lower("Dr.")
        assert "." in result

    def test_split_empty_string(self):
        assert split_sname("") == []
        assert split_fname("") == []
