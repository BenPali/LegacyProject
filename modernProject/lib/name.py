import re
import unicodedata
from typing import List, Tuple, Optional, Callable


FORBIDDEN_CHAR = [':', '@', '#', '=', '$']


def unaccent_utf_8(lower: bool, s: str, i: int) -> Tuple[str, int]:
    if i >= len(s):
        return ("", i)
    char = s[i]
    if ord(char) < 0x80:
        result = char.lower() if lower else char
        return (result, i + 1)
    nfd = unicodedata.normalize('NFD', char)
    ascii_char = ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
    if not ascii_char:
        ascii_char = char
    if lower:
        ascii_char = ascii_char.lower()
    return (ascii_char, i + 1)


def next_chars_if_equiv(s1: str, i1: int, s2: str, i2: int) -> Optional[Tuple[int, int]]:
    if i1 >= len(s1) or i2 >= len(s2):
        return None
    c1, n1 = unaccent_utf_8(True, s1, i1)
    c2, n2 = unaccent_utf_8(True, s2, i2)
    if c1 == c2:
        return (n1, n2)
    return None


def lower(s: str) -> str:
    result = []
    special = False
    i = 0
    while i < len(s):
        c = s[i]
        if ord(c) < 0x80:
            if c.isalnum() or c == '.':
                if special and result:
                    result.append(' ')
                result.append(c.lower())
                special = False
            else:
                special = len(result) > 0
            i += 1
        else:
            if special and result:
                result.append(' ')
            t, j = unaccent_utf_8(True, s, i)
            result.append(t)
            special = False
            i = j
    return ''.join(result)


def title(s: str) -> str:
    result = []
    at_word_start = True
    for char in s:
        if char.isalpha():
            if at_word_start:
                result.append(char.upper())
                at_word_start = False
            else:
                result.append(char.lower())
        else:
            result.append(char)
            at_word_start = True
    return ''.join(result)


ABBREV_LIST = [
    ("a", None),
    ("af", None),
    ("d", None),
    ("de", None),
    ("di", None),
    ("ier", "i"),
    ("of", None),
    ("saint", "st"),
    ("sainte", "ste"),
    ("van", None),
    ("von", None),
    ("zu", None),
    ("zur", None),
]


def _is_word(s: str, i: int, p: str) -> bool:
    if i + len(p) > len(s):
        return False
    if s[i:i+len(p)] != p:
        return False
    end_pos = i + len(p)
    if end_pos == len(s):
        return True
    return s[end_pos] == ' '


def _search_abbrev(s: str, i: int) -> Optional[Tuple[int, Optional[str]]]:
    for word, abbr in ABBREV_LIST:
        if _is_word(s, i, word):
            return (len(word), abbr)
    return None


def abbrev(s: str) -> str:
    result = []
    can_start_abbrev = True
    i = 0
    while i < len(s):
        if s[i] == ' ':
            result.append(' ')
            can_start_abbrev = True
            i += 1
        elif can_start_abbrev:
            match = _search_abbrev(s, i)
            if match:
                n, a = match
                if a:
                    result.append(a)
                can_start_abbrev = a is None
                i += n + (1 if a is None else 0)
            else:
                result.append(s[i])
                can_start_abbrev = False
                i += 1
        else:
            result.append(s[i])
            i += 1
    return ''.join(result)


def strip_c(s: str, c: str) -> str:
    return s.replace(c, '')


def strip(s: str) -> str:
    return strip_c(s, ' ')


def purge(s: str) -> str:
    result = s
    for char in FORBIDDEN_CHAR:
        result = strip_c(result, char)
    return result


def _roman_number(s: str, i: int) -> Optional[int]:
    roman_chars = set('IVXLCDM')
    j = i
    while j < len(s) and s[j] in roman_chars:
        j += 1
    if j == i:
        return None
    if j == len(s) or s[j] == ' ':
        return j
    return None


def crush(s: str) -> str:
    result = []
    i = 0
    prev_lower_cons = None
    while i < len(s):
        c = s[i]
        if c == ' ':
            i += 1
            continue
        if c.isupper():
            roman_end = _roman_number(s, i)
            if roman_end:
                result.append(s[i:roman_end])
                i = roman_end
                prev_lower_cons = None
                continue
        c_lower = c.lower()
        if c_lower in 'aeiouy':
            if not result or (result and result[-1] != 'e'):
                if len(result) == 0:
                    result.append('e')
        elif c_lower == 'k' or c_lower == 'q':
            if prev_lower_cons != 'c':
                result.append('c')
                prev_lower_cons = 'c'
        elif c_lower == 'y':
            pass
        elif c_lower == 'z':
            if prev_lower_cons != 's':
                result.append('s')
                prev_lower_cons = 's'
        elif c_lower == 'h':
            if i + 1 < len(s) and s[i-1:i+1].lower() == 'ph':
                result[-1] = 'f'
                prev_lower_cons = 'f'
        elif c_lower == 's':
            if i + 1 < len(s) and s[i+1] != ' ':
                if prev_lower_cons != 's':
                    result.append('s')
                    prev_lower_cons = 's'
        else:
            if prev_lower_cons != c_lower:
                result.append(c_lower)
                prev_lower_cons = c_lower
        i += 1
    return ''.join(result)


def strip_lower(s: str) -> str:
    return strip(lower(s))


def crush_lower(s: str) -> str:
    return crush(abbrev(lower(s)))


def concat(fn: str, sn: str) -> str:
    return fn + ' ' + sn if sn else fn


def contains_forbidden_char(s: str) -> bool:
    return any(c in s for c in FORBIDDEN_CHAR)


def split_sname_callback(fn: Callable[[int, int], None], s: str) -> None:
    parts = re.split(r'[-\s]+', s)
    start = 0
    for part in parts:
        if part:
            end = start + len(part)
            fn(start, end)
            start = end + 1


def split_fname_callback(fn: Callable[[int, int], None], s: str) -> None:
    i = 0
    start = None
    in_hyphen_group = False
    while i < len(s):
        c = s[i]
        if c == ' ':
            if start is not None and not in_hyphen_group:
                fn(start, i)
                start = None
            in_hyphen_group = False
        elif c == '-':
            in_hyphen_group = True
            if start is None:
                start = i
        else:
            if start is None:
                start = i
        i += 1
    if start is not None:
        fn(start, len(s))


def split_sname(s: str) -> List[str]:
    result = []
    split_sname_callback(lambda start, end: result.append(s[start:end]), s)
    return result


def split_fname(s: str) -> List[str]:
    result = []
    split_fname_callback(lambda start, end: result.append(s[start:end]), s)
    return result
