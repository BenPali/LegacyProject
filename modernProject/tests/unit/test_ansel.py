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
        assert no_accent('\u00f1') == 'n'
        assert no_accent('\u00ff') == 'y'

    def test_uppercase_a_variants(self):
        assert no_accent('\u00c0') == 'A'
        assert no_accent('\u00c5') == 'A'
        assert no_accent('\u00c8') == 'E'
        assert no_accent('\u00c9') == 'E'
        assert no_accent('\u00ca') == 'E'
        assert no_accent('\u00cb') == 'E'
        assert no_accent('\u00cc') == 'I'
        assert no_accent('\u00cd') == 'I'
        assert no_accent('\u00ce') == 'I'
        assert no_accent('\u00cf') == 'I'
        assert no_accent('\u00d1') == 'N'
        assert no_accent('\u00d2') == 'O'
        assert no_accent('\u00d3') == 'O'
        assert no_accent('\u00d4') == 'O'
        assert no_accent('\u00d5') == 'O'
        assert no_accent('\u00d6') == 'O'
        assert no_accent('\u00d9') == 'U'
        assert no_accent('\u00da') == 'U'
        assert no_accent('\u00db') == 'U'
        assert no_accent('\u00dc') == 'U'
        assert no_accent('\u00dd') == 'Y'

    def test_cedilla(self):
        assert no_accent('\u00e7') == 'c'
        assert no_accent('\u00c7') == 'C'

    def test_special_chars(self):
        assert no_accent('\u00ab') == '<'
        assert no_accent('\u00bb') == '>'
        assert no_accent('\u00a8') == ' '
        assert no_accent('\u00b0') == ' '
        assert no_accent('\u00b4') == ' '
        assert no_accent('\u00b8') == ' '

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
        assert accent_code('A') == 0


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

    def test_ansel_conversions_63_123(self):
        assert of_iso_8859_1("\u00e4") == chr(232) + 'a'
        assert of_iso_8859_1("\u00f6") == chr(232) + 'o'
        assert of_iso_8859_1("\u00fc") == chr(232) + 'u'

        assert of_iso_8859_1("\u00c5") == chr(234) + 'A'
        assert of_iso_8859_1("\u00e5") == chr(234) + 'a'

        assert of_iso_8859_1("\u00c7") == chr(240) + 'C'
        assert of_iso_8859_1("\u00e7") == chr(240) + 'c'

        assert of_iso_8859_1("\u00a1") == chr(198)
        assert of_iso_8859_1("\u00a3") == chr(185)
        assert of_iso_8859_1("\u00a4") == chr(0x6f)
        assert of_iso_8859_1("\u00a5") == chr(0x59)
        assert of_iso_8859_1("\u00a6") == chr(0x7c)
        assert of_iso_8859_1("\u00a9") == chr(195)
        assert of_iso_8859_1("\u00aa") == chr(0x61)
        assert of_iso_8859_1("\u00ad") == chr(0x2d)
        assert of_iso_8859_1("\u00ae") == chr(170)
        assert of_iso_8859_1("\u00b1") == chr(171)
        assert of_iso_8859_1("\u00b2") == chr(0x32)
        assert of_iso_8859_1("\u00b3") == chr(0x33)
        assert of_iso_8859_1("\u00b7") == chr(168)
        assert of_iso_8859_1("\u00b9") == chr(0x31)
        assert of_iso_8859_1("\u00bf") == chr(197)
        assert of_iso_8859_1("\u00c6") == chr(165)
        assert of_iso_8859_1("\u00d0") == chr(163)
        assert of_iso_8859_1("\u00f0") == chr(179)
        assert of_iso_8859_1("\u00d8") == chr(162)
        assert of_iso_8859_1("\u00f8") == chr(178)
        assert of_iso_8859_1("\u00de") == chr(164)
        assert of_iso_8859_1("\u00fe") == chr(180)
        assert of_iso_8859_1("\u00df") == chr(207)

    def test_of_iso_8859_1_length_and_identical_update(self):
        result = of_iso_8859_1("\u00e9")
        assert len(result) == 2
        assert ord(result[0]) == 226
        assert result[1] == 'e'

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


class TestAnselCoverage:
    def test_of_iso_8859_1_pairs(self):
        assert of_iso_8859_1(chr(166)) == '|'
        assert of_iso_8859_1(chr(172)) == '\x81'
        assert of_iso_8859_1(chr(173)) == '-'

    def test_to_iso_8859_1_diacritics(self):
        assert to_iso_8859_1(chr(228) + 'a') == '\u00e3'
        assert to_iso_8859_1(chr(228) + 'n') == '\u00f1'
        assert to_iso_8859_1(chr(232) + 'a') == '\u00e4'
        assert to_iso_8859_1(chr(232) + 'e') == '\u00eb'
        assert to_iso_8859_1(chr(232) + 'u') == '\u00fc'
        assert to_iso_8859_1(chr(234) + 'a') == '\u00e5'
        assert to_iso_8859_1(chr(234) + 'A') == '\u00c5'
        assert to_iso_8859_1(chr(240) + 'c') == '\u00e7'
        assert to_iso_8859_1(chr(240) + 'C') == '\u00c7'
        assert to_iso_8859_1(chr(252) + 'o') == '\u00f8'
        assert to_iso_8859_1(chr(252) + 'O') == '\u00d8'
