import pytest
from lib.ansel import (
    of_iso_8859_1, to_iso_8859_1, no_accent, accent_code,
    grave, acute, circum, uml, circle, tilde, cedil, slash
)


class TestNoAccent:
    def test_lowercase_a_variants(self):
        assert no_accent('\u00e0') == 'a'
        assert no_accent('\u00e1') == 'a'
        assert no_accent('\u00e2') == 'a'
        assert no_accent('\u00e5') == 'a'

    def test_uppercase_a_variants(self):
        assert no_accent('\u00c0') == 'A'
        assert no_accent('\u00c5') == 'A'

    def test_cedilla(self):
        assert no_accent('\u00e7') == 'c'
        assert no_accent('\u00c7') == 'C'

    def test_special_chars(self):
        assert no_accent('\u00ab') == '<'
        assert no_accent('\u00bb') == '>'

    def test_unchanged(self):
        assert no_accent('x') == 'x'
        assert no_accent('Z') == 'Z'


class TestAccentCode:
    def test_grave_accents(self):
        assert accent_code('\u00e0') == 225
        assert accent_code('\u00e8') == 225
        assert accent_code('\u00ec') == 225

    def test_acute_accents(self):
        assert accent_code('\u00e1') == 226
        assert accent_code('\u00e9') == 226

    def test_circumflex(self):
        assert accent_code('\u00e2') == 227
        assert accent_code('\u00ea') == 227

    def test_tilde(self):
        assert accent_code('\u00e3') == 228
        assert accent_code('\u00f1') == 228

    def test_no_accent_char(self):
        assert accent_code('a') == 0
        assert accent_code('z') == 0


class TestOfIso88591:
    def test_unchanged_string(self):
        s = "hello world"
        assert of_iso_8859_1(s) == s

    def test_single_accent(self):
        result = of_iso_8859_1("\u00e9")
        assert len(result) == 2
        assert ord(result[0]) == 226
        assert result[1] == 'e'

    def test_mixed_string(self):
        result = of_iso_8859_1("caf\u00e9")
        assert result[0] == 'c'
        assert result[1] == 'a'
        assert result[2] == 'f'

    def test_grave_accent_conversion(self):
        result = of_iso_8859_1("\u00e0")
        assert ord(result[0]) == 225
        assert result[1] == 'a'


class TestDiacriticFunctions:
    def test_grave(self):
        assert grave('a') == '\u00e0'
        assert grave('e') == '\u00e8'
        assert grave('A') == '\u00c0'
        assert grave(' ') == '`'
        assert grave('x') == 'x'

    def test_acute(self):
        assert acute('a') == '\u00e1'
        assert acute('e') == '\u00e9'
        assert acute('A') == '\u00c1'
        assert acute(' ') == '\u00b4'

    def test_circum(self):
        assert circum('a') == '\u00e2'
        assert circum('e') == '\u00ea'
        assert circum(' ') == '^'

    def test_uml(self):
        assert uml('a') == '\u00e4'
        assert uml('e') == '\u00eb'
        assert uml('u') == '\u00fc'
        assert uml(' ') == '\u00a8'

    def test_circle(self):
        assert circle('a') == '\u00e5'
        assert circle('A') == '\u00c5'
        assert circle(' ') == '\u00b0'

    def test_tilde(self):
        assert tilde('n') == '\u00f1'
        assert tilde('a') == '\u00e3'
        assert tilde(' ') == '~'

    def test_cedil(self):
        assert cedil('c') == '\u00e7'
        assert cedil('C') == '\u00c7'
        assert cedil(' ') == '\u00b8'

    def test_slash(self):
        assert slash('o') == '\u00f8'
        assert slash('O') == '\u00d8'
        assert slash(' ') == '/'


class TestToIso88591:
    def test_unchanged_string(self):
        s = "hello"
        assert to_iso_8859_1(s) == s

    def test_acute_e(self):
        ansel_e_acute = chr(226) + 'e'
        result = to_iso_8859_1(ansel_e_acute)
        assert result == '\u00e9'

    def test_grave_a(self):
        ansel_a_grave = chr(225) + 'a'
        result = to_iso_8859_1(ansel_a_grave)
        assert result == '\u00e0'

    def test_roundtrip_simple(self):
        original = "caf\u00e9"
        ansel = of_iso_8859_1(original)
        restored = to_iso_8859_1(ansel)
        assert restored == original

    def test_roundtrip_complex(self):
        original = "\u00e0\u00e9\u00ee\u00f4\u00fb"
        ansel = of_iso_8859_1(original)
        restored = to_iso_8859_1(ansel)
        assert restored == original
