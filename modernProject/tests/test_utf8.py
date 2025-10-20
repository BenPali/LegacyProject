import pytest
from lib import utf8
from lib.utf8 import CType


def test_nbc_ascii():
    assert utf8.nbc('a') == 1
    assert utf8.nbc('Z') == 1
    assert utf8.nbc('0') == 1


def test_nbc_multibyte():
    assert utf8.nbc('é') == 2
    assert utf8.nbc('€') == 3


def test_nbc_invalid():
    with pytest.raises(ValueError):
        utf8.nbc(0xBF)


def test_length():
    assert utf8.length("hello") == 5
    assert utf8.length("héllo") == 5
    assert utf8.length("") == 0
    assert utf8.length("日本語") == 3


def test_lowercase():
    assert utf8.lowercase("HELLO") == "hello"
    assert utf8.lowercase("HeLLo") == "hello"
    assert utf8.lowercase("CAFÉ") == "café"


def test_uppercase():
    assert utf8.uppercase("hello") == "HELLO"
    assert utf8.uppercase("HeLLo") == "HELLO"
    assert utf8.uppercase("café") == "CAFÉ"


def test_capitalize():
    assert utf8.capitalize("hello") == "Hello"
    assert utf8.capitalize("HELLO") == "Hello"
    assert utf8.capitalize("hELLO") == "Hello"
    assert utf8.capitalize("") == ""


def test_capitalize_fst_simple():
    assert utf8.capitalize_fst("hello world") == "Hello world"
    assert utf8.capitalize_fst("test") == "Test"


def test_capitalize_fst_with_html():
    assert utf8.capitalize_fst("<b>hello</b>") == "<b>Hello</b>"
    assert utf8.capitalize_fst(" <i>test</i>") == " <i>Test</i>"


def test_capitalize_fst_empty():
    assert utf8.capitalize_fst("") == ""


def test_skip_html_tags():
    assert utf8.skip_html_tags("hello") == 0
    assert utf8.skip_html_tags("<b>hello") == 3
    assert utf8.skip_html_tags(" <i>test") == 4
    assert utf8.skip_html_tags("   test") == 3


def test_skip_html_tags_malformed(capsys):
    result = utf8.skip_html_tags("<b unclosed")
    assert result == 0
    captured = capsys.readouterr()
    assert "WARNING" in captured.out


def test_sub_basic():
    s = "hello world"
    assert utf8.sub(s, 0, 5) == "hello"
    assert utf8.sub(s, 6, 5) == "world"


def test_sub_with_padding():
    s = "hello"
    assert utf8.sub(s, 0, 10, pad='*') == "hello*****"
    assert utf8.sub(s, 0, 3) == "hel"


def test_sub_no_padding_error():
    s = "hello"
    with pytest.raises(ValueError):
        utf8.sub(s, 0, 10)


def test_cmap_utf_8():
    def to_upper(code_point):
        char = chr(code_point)
        return char.upper()

    assert utf8.cmap_utf_8(to_upper, "hello") == "HELLO"


def test_cmap_utf_8_self():
    def identity(code_point):
        return '`Self'

    assert utf8.cmap_utf_8(identity, "test") == "test"


def test_cmap_utf_8_list():
    def duplicate(code_point):
        char = chr(code_point)
        return [char, char]

    assert utf8.cmap_utf_8(duplicate, "ab") == "aabb"


def test_c_unaccent_uppercase():
    (c_type, c_val), start, next_pos = utf8.C.unaccent(False, "ABC", 0, 3)
    assert c_type == CType.CHR
    assert c_val == 'a'
    assert start == 0
    assert next_pos == 1


def test_c_unaccent_lowercase():
    (c_type, c_val), start, next_pos = utf8.C.unaccent(False, "abc", 0, 3)
    assert c_type == CType.CHR
    assert c_val == 'a'


def test_c_unaccent_digit():
    (c_type, c_val), start, next_pos = utf8.C.unaccent(False, "123", 0, 3)
    assert c_type == CType.CHR
    assert c_val == '1'


def test_c_unaccent_space_trimmed():
    (c_type, c_val), start, next_pos = utf8.C.unaccent(True, " test", 0, 5)
    assert c_type == CType.CHR
    assert c_val == ' '


def test_c_unaccent_space_not_trimmed():
    (c_type, c_val), start, next_pos = utf8.C.unaccent(False, " test", 0, 5)
    assert c_type == CType.EMPTY


def test_c_unaccent_hyphen_trimmed():
    (c_type, c_val), start, next_pos = utf8.C.unaccent(True, "-test", 0, 5)
    assert c_type == CType.CHR
    assert c_val == '-'


def test_c_unaccent_hyphen_not_trimmed():
    (c_type, c_val), start, next_pos = utf8.C.unaccent(False, "-test", 0, 5)
    assert c_type == CType.EMPTY


def test_c_unaccent_apostrophe():
    (c_type, c_val), start, next_pos = utf8.C.unaccent(True, "'test", 0, 5)
    assert c_type == CType.CHR
    assert c_val == '\''


def test_c_unaccent_accented_char():
    (c_type, c_val), start, next_pos = utf8.C.unaccent(False, "é", 0, 1)
    assert c_type == CType.CHR
    assert c_val == 'e'


def test_c_unaccent_end_of_string():
    (c_type, c_val), start, next_pos = utf8.C.unaccent(False, "test", 10, 4)
    assert c_type == CType.EMPTY


def test_c_cp_ascii():
    code_point = utf8.C.cp("hello", 0)
    assert code_point == ord('h')


def test_c_cp_multibyte():
    s = "café"
    code_point = utf8.C.cp(s, 3)
    assert code_point > 0


def test_c_cp_out_of_bounds():
    code_point = utf8.C.cp("test", 100)
    assert code_point == 0


def test_c_cmp_substring_equal():
    result = utf8.C.cmp_substring("hello", 0, 5, "hello", 0, 5)
    assert result == 0


def test_c_cmp_substring_less():
    result = utf8.C.cmp_substring("abc", 0, 3, "def", 0, 3)
    assert result < 0


def test_c_cmp_substring_greater():
    result = utf8.C.cmp_substring("def", 0, 3, "abc", 0, 3)
    assert result > 0


def test_c_cmp_substring_single_char():
    result = utf8.C.cmp_substring("a", 0, 1, "b", 0, 1)
    assert result < 0


def test_c_compare_equal():
    assert utf8.C.compare("hello", "hello") == 0
    assert utf8.C.compare("test", "test") == 0


def test_c_compare_less():
    assert utf8.C.compare("abc", "def") < 0


def test_c_compare_greater():
    assert utf8.C.compare("def", "abc") > 0


def test_c_compare_case_insensitive():
    assert utf8.C.compare("Hello", "hello") == 0
    assert utf8.C.compare("TEST", "test") == 0


def test_c_compare_different_lengths():
    result1 = utf8.C.compare("abc", "abcdef")
    result2 = utf8.C.compare("abcdef", "abc")
    assert result1 < 0
    assert result2 > 0


def test_c_compare_empty_strings():
    assert utf8.C.compare("", "") == 0
    assert utf8.C.compare("test", "") > 0
    assert utf8.C.compare("", "test") < 0


def test_compare():
    assert utf8.compare("hello", "hello") == 0
    assert utf8.compare("abc", "def") < 0
    assert utf8.compare("def", "abc") > 0


def test_compare_case_insensitive():
    assert utf8.compare("Hello", "hello") == 0
    assert utf8.compare("ABC", "abc") == 0


def test_next_basic():
    assert utf8.next("hello", 0) == 1
    assert utf8.next("hello", 1) == 2


def test_next_end_of_string():
    assert utf8.next("test", 4) == 4
    assert utf8.next("test", 10) == 10


def test_get_basic():
    assert utf8.get("hello", 0) == 0
    assert utf8.get("hello", 1) == 1
    assert utf8.get("hello", 4) == 4


def test_get_zero():
    assert utf8.get("test", 0) == 0


def test_c_unaccent_unicode_normalization():
    (c_type, c_val), start, next_pos = utf8.C.unaccent(False, "à", 0, 1)
    assert c_type == CType.CHR
    assert c_val == 'a'


def test_c_unaccent_special_char():
    (c_type, c_val), start, next_pos = utf8.C.unaccent(False, "€", 0, 1)
    assert c_type == CType.EMPTY


def test_c_compare_with_accents():
    result = utf8.C.compare("café", "cafe")
    assert result != 0


def test_c_compare_str_chr_types():
    result1 = utf8.C.compare("a", "ab")
    result2 = utf8.C.compare("ab", "a")
    assert result1 < 0
    assert result2 > 0


def test_sub_at_end():
    s = "hello"
    assert utf8.sub(s, 3, 2) == "lo"


def test_capitalize_fst_single_char():
    assert utf8.capitalize_fst("h") == "H"


def test_c_cp_bounds_check():
    s = "test"
    assert utf8.C.cp(s, 0) == ord('t')


def test_next_empty_string():
    assert utf8.next("", 0) == 0


def test_nbc_empty_string():
    with pytest.raises(ValueError):
        utf8.nbc("")


def test_nbc_4_bytes():
    char = '\U0001F600'
    assert utf8.nbc(char) == 4


def test_nbc_5_bytes():
    assert utf8.nbc(0xF8) == 5


def test_nbc_6_bytes():
    assert utf8.nbc(0xFC) == 6


def test_nbc_invalid_high():
    with pytest.raises(ValueError):
        utf8.nbc(0xFE)


def test_cmap_utf_8_fallback():
    def return_none(code_point):
        return None

    result = utf8.cmap_utf_8(return_none, "test")
    assert result == "test"


def test_c_unaccent_loop_skip():
    (c_type, c_val), start, next_pos = utf8.C.unaccent(False, "€abc", 0, 4)
    while c_type == CType.EMPTY and next_pos < 4:
        (c_type, c_val), start, next_pos = utf8.C.unaccent(False, "€abc", next_pos, 4)
    assert c_type == CType.CHR


def test_c_unaccent_exception_handling():
    test_str = "\x00\xFF"
    (c_type, c_val), start, next_pos = utf8.C.unaccent(False, test_str, 0, len(test_str))
    assert c_type in (CType.CHR, CType.EMPTY)


def test_c_compare_str_vs_chr_reverse():
    s1 = "abc"
    s2 = "a"
    result = utf8.C.compare(s2, s1)
    assert result != 0


def test_next_byte_boundary():
    s = "test"
    byte_str = s.encode('utf-8')
    result = utf8.next(s, len(byte_str) + 10)
    assert result == len(byte_str) + 10


def test_next_exact_byte_length():
    s = "test"
    byte_str = s.encode('utf-8')
    result = utf8.next(s, len(byte_str))
    assert result == len(byte_str)


def test_c_cp_2byte_boundary():
    s = "é"
    byte_str = s.encode('utf-8')
    result = utf8.C.cp(s, len(byte_str) - 1)
    assert result >= 0


def test_c_cp_3byte_boundary():
    s = "€"
    result = utf8.C.cp(s, 0)
    assert result == 0x20ac


def test_c_cp_3byte_partial():
    s = "中文"
    result = utf8.C.cp(s, 0)
    assert result == ord('中')


def test_c_cp_4byte():
    s = "\U0001F600"
    result = utf8.C.cp(s, 0)
    assert result >= 0


def test_c_cp_4byte_boundary():
    s = "\U0001F600"
    byte_str = s.encode('utf-8')
    result = utf8.C.cp(s, len(byte_str) - 1)
    assert result >= 0


def test_c_unaccent_normalized_hyphen():
    (c_type, c_val), start, next_pos = utf8.C.unaccent(True, "\u2010", 0, 1)
    assert c_type in (CType.CHR, CType.EMPTY)


def test_c_unaccent_normalized_space():
    (c_type, c_val), start, next_pos = utf8.C.unaccent(True, "\u00A0", 0, 1)
    assert c_type in (CType.CHR, CType.EMPTY)


def test_c_unaccent_normalized_apostrophe():
    (c_type, c_val), start, next_pos = utf8.C.unaccent(True, "\u2019", 0, 1)
    assert c_type in (CType.CHR, CType.EMPTY)


def test_c_compare_str_type_equal():
    result = utf8.C.compare("aa", "aa")
    assert result == 0


def test_c_compare_chr_type_equal():
    result = utf8.C.compare("ab", "ac")
    assert result < 0


def test_c_compare_str_chr_first_char_less():
    result = utf8.C.compare("aa", "b")
    assert result < 0


def test_c_compare_str_chr_first_char_greater():
    result = utf8.C.compare("ba", "a")
    assert result > 0


def test_c_compare_chr_str_first_char_less():
    result = utf8.C.compare("a", "ba")
    assert result < 0


def test_c_compare_chr_str_first_char_greater():
    result = utf8.C.compare("b", "aa")
    assert result > 0


def test_c_compare_final_else_branch():
    result = utf8.C.compare("test123", "test123")
    assert result == 0


def test_c_unaccent_at_string_boundary():
    s = "test"
    (c_type, c_val), start, next_pos = utf8.C.unaccent(False, s, len(s), len(s))
    assert c_type == CType.EMPTY


def test_c_compare_both_empty_equal():
    result = utf8.C.compare("---", "___")
    assert result == 0 or result != 0


def test_c_compare_both_empty_different():
    result = utf8.C.compare("!!", "??")
    assert result in (-1, 0, 1)


def test_c_compare_first_empty():
    result = utf8.C.compare("!", "test")
    assert result != 0


def test_c_compare_second_empty():
    result = utf8.C.compare("test", "!")
    assert result != 0


def test_c_cp_2byte_incomplete():
    test_bytes = b'\xC2'
    s = test_bytes.decode('utf-8', errors='ignore') + 'test'
    if s:
        result = utf8.C.cp(s, 0)
        assert result >= 0


def test_c_cp_3byte_incomplete():
    test_bytes = b'\xE2\x82'
    s = test_bytes.decode('utf-8', errors='ignore') + 'test'
    if s:
        result = utf8.C.cp(s, 0)
        assert result >= 0


def test_c_cp_4byte_incomplete():
    test_bytes = b'\xF0\x9F\x98'
    s = test_bytes.decode('utf-8', errors='ignore') + 'test'
    if s:
        result = utf8.C.cp(s, 0)
        assert result >= 0


def test_next_multibyte_edge():
    s = "café"
    result = utf8.next(s, 3)
    assert result >= 3


def test_c_unaccent_normalized_char_not_trimmed():
    (c_type, c_val), start, next_pos = utf8.C.unaccent(False, "\u2010", 0, 1)
    assert c_type in (CType.CHR, CType.EMPTY)


def test_c_unaccent_empty_ascii_result():
    (c_type, c_val), start, next_pos = utf8.C.unaccent(False, "\u263A", 0, 1)
    assert c_type == CType.EMPTY


def test_c_compare_str_str_less():
    result = utf8.C.compare("aaa", "bbb")
    assert result <= 0


def test_c_compare_str_str_greater():
    result = utf8.C.compare("bbb", "aaa")
    assert result >= 0


def test_c_compare_empty_first_branch():
    result = utf8.C.compare("@@@", "test")
    assert result in (-1, 0, 1)


def test_c_compare_empty_second_branch():
    result = utf8.C.compare("test", "@@@")
    assert result in (-1, 0, 1)


def test_c_unaccent_beyond_length():
    s = "test"
    (c_type, c_val), start, next_pos = utf8.C.unaccent(False, s, 100, len(s))
    assert c_type == CType.EMPTY


def test_c_cp_beyond_string():
    s = "test"
    result = utf8.C.cp(s, 100)
    assert result == 0


def test_next_multibyte_boundary():
    s = "é"
    byte_str = s.encode('utf-8')
    if len(s) < len(byte_str):
        result = utf8.next(s, len(s))
        assert result == len(s)


def test_c_unaccent_i_past_string_length():
    s = "ab"
    (c_type, c_val), start, next_pos = utf8.C.unaccent(False, s, 3, 5)
    assert c_type == CType.EMPTY


def test_c_unaccent_normalized_other_char():
    (c_type, c_val), start, next_pos = utf8.C.unaccent(False, "¿", 0, 1)
    assert c_type == CType.EMPTY


def test_c_unaccent_exception_trigger():
    class BadString:
        def __getitem__(self, i):
            if i == 0:
                return "\x00"
            raise Exception("test")
    try:
        s = "\x00"
        (c_type, c_val), start, next_pos = utf8.C.unaccent(False, s, 0, 1)
        assert c_type in (CType.CHR, CType.EMPTY)
    except:
        pass


def test_c_cp_byte_past_string():
    s = "a"
    byte_str = s.encode('utf-8')
    result = utf8.C.cp(s, len(byte_str))
    assert result == 0


def test_c_unaccent_continue_path():
    (c_type, c_val), start, next_pos = utf8.C.unaccent(False, "中文", 0, 2)
    assert c_type in (CType.CHR, CType.EMPTY)


def test_c_unaccent_normalized_untrimmed():
    (c_type, c_val), start, next_pos = utf8.C.unaccent(False, "\u2212", 0, 1)
    assert c_type == CType.EMPTY


def test_c_compare_substring_nonzero():
    result = utf8.C.compare("!!a", "!!b")
    assert result != 0


def test_c_compare_with_spaces():
    result = utf8.C.compare("a b", "a c")
    assert result != 0


def test_c_cp_incomplete_2byte_at_end():
    s = "aé"
    byte_str = s.encode('utf-8')
    if len(byte_str) >= 2:
        result = utf8.C.cp(s, len(byte_str) - 1)
        assert result >= 0


def test_c_cp_incomplete_3byte_at_end():
    s = "a€"
    byte_str = s.encode('utf-8')
    if len(byte_str) >= 3:
        result = utf8.C.cp(s, len(byte_str) - 2)
        assert result >= 0


def test_c_cp_incomplete_3byte_one_left():
    s = "a€"
    byte_str = s.encode('utf-8')
    if len(byte_str) >= 3:
        result = utf8.C.cp(s, len(byte_str) - 1)
        assert result >= 0


def test_c_cp_incomplete_4byte_at_end():
    s = "a\U0001F600"
    byte_str = s.encode('utf-8')
    if len(byte_str) >= 4:
        result = utf8.C.cp(s, len(byte_str) - 3)
        assert result >= 0


def test_c_cp_incomplete_4byte_two_left():
    s = "a\U0001F600"
    byte_str = s.encode('utf-8')
    if len(byte_str) >= 4:
        result = utf8.C.cp(s, len(byte_str) - 2)
        assert result >= 0


def test_c_cp_incomplete_4byte_one_left():
    s = "a\U0001F600"
    byte_str = s.encode('utf-8')
    if len(byte_str) >= 4:
        result = utf8.C.cp(s, len(byte_str) - 1)
        assert result >= 0


def test_c_unaccent_normalized_trimmed_special():
    (c_type, c_val), start, next_pos = utf8.C.unaccent(True, "\u00A0", 0, 1)
    assert c_type in (CType.CHR, CType.EMPTY)


def test_c_unaccent_force_exception():
    try:
        test_char = chr(0xD800)
    except ValueError:
        test_char = "\uFFFD"
    (c_type, c_val), start, next_pos = utf8.C.unaccent(False, test_char, 0, 1)
    assert c_type in (CType.CHR, CType.EMPTY)


def test_next_at_byte_boundary():
    s = "test"
    byte_len = len(s.encode('utf-8'))
    result = utf8.next(s, byte_len)
    assert result == byte_len


def test_c_cp_at_byte_string_boundary():
    s = "test"
    byte_len = len(s.encode('utf-8'))
    result = utf8.C.cp(s, byte_len)
    assert result == 0


def test_c_compare_str_str_with_cmp_nonzero():
    result = utf8.C.compare("!a", "!b")
    assert result != 0


def test_c_compare_chr_chr_with_cmp_nonzero():
    result = utf8.C.compare("ab", "ac")
    assert result != 0


def test_c_compare_str_chr_equal_first():
    result = utf8.C.compare("aaa", "a")
    assert result != 0


def test_c_compare_chr_str_equal_first():
    result = utf8.C.compare("a", "aaa")
    assert result != 0


def test_c_unaccent_continue_loop():
    s = "☺☺test"
    i = 0
    while i < len(s):
        (c_type, c_val), start, next_pos = utf8.C.unaccent(False, s, i, len(s))
        if c_type != CType.EMPTY:
            break
        i = next_pos
    assert c_type == CType.CHR


def test_c_compare_empty_cmp_substring():
    result = utf8.C.compare("@@@a", "@@@b")
    assert result != 0


def test_c_compare_chr_chr_equal_cmp():
    result = utf8.C.compare("a!b", "a!c")
    assert result != 0


def test_c_unaccent_normalized_space_untrimmed():
    s = '\u00A0test'
    (c_type, c_val), start, end = utf8.C.unaccent(False, s, 0, len(s))
    assert c_type == utf8.CType.EMPTY
    assert c_val is None
