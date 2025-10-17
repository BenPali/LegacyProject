from enum import Enum, auto
from typing import Optional, Callable, Union, Tuple
import unicodedata


def nbc(c: Union[str, int]) -> int:
    if isinstance(c, str):
        if not c:
            raise ValueError("nbc: empty string")
        code = c.encode('utf-8')[0]
    else:
        code = c

    if code < 0x80:
        return 1
    elif code < 0xC0:
        raise ValueError("nbc: invalid UTF-8 start byte")
    elif code < 0xE0:
        return 2
    elif code < 0xF0:
        return 3
    elif code < 0xF8:
        return 4
    elif code < 0xFC:
        return 5
    elif code < 0xFE:
        return 6
    else:
        raise ValueError("nbc: invalid UTF-8 start byte")


def next(s: str, i: int) -> int:
    if i >= len(s):
        return i
    byte_str = s.encode('utf-8')
    if i >= len(byte_str):
        return i
    return i + nbc(byte_str[i])


def get(s: str, n: int) -> int:
    i = 0
    k = n
    while k > 0:
        i = next(s, i)
        k -= 1
    return i


def length(s: str) -> int:
    return len(s)


def sub(s: str, start: int, length: int, pad: Optional[str] = None) -> str:
    strlen = len(s)
    n = 0
    i = start

    while n < length and i < strlen:
        n += 1
        i = next(s, i)

    if n == length:
        return s[start:i]
    else:
        if pad is None:
            raise ValueError("str_sub: string too short and no padding provided")
        result = s[start:i]
        result += pad * (length - n)
        return result


def cmap_utf_8(cmap: Callable[[int], Union[str, list]], s: str) -> str:
    result = []
    for char in s:
        code_point = ord(char)
        mapped = cmap(code_point)
        if isinstance(mapped, str):
            if mapped == '`Self':
                result.append(char)
            else:
                result.append(mapped)
        elif isinstance(mapped, list):
            result.extend(mapped)
        else:
            result.append(char)
    return ''.join(result)


def lowercase(s: str) -> str:
    return s.lower()


def uppercase(s: str) -> str:
    return s.upper()


def skip_html_tags(s: str) -> int:
    i = 0
    while i < len(s):
        if s[i] == ' ':
            i += 1
        elif s[i] == '<':
            try:
                j = s.index('>', i)
                i = j + 1
            except ValueError:
                print(f"WARNING: badly formed string {s}")
                return 0
        else:
            return i
    return i


def capitalize_fst(s: str) -> str:
    i = skip_html_tags(s)
    head = s[:i]
    tail = s[i:]

    if not tail:
        return s

    first_char = tail[0]
    rest = tail[1:]
    return head + first_char.upper() + rest


def capitalize(s: str) -> str:
    if not s:
        return s
    return s[0].upper() + s[1:].lower()


class CType(Enum):
    STR = auto()
    CHR = auto()
    EMPTY = auto()


class C:
    @staticmethod
    def unaccent(trimmed: bool, s: str, i0: int, slen: int) -> Tuple[Union[Tuple[CType, str], Tuple[CType, None]], int, int]:
        i = i0
        while i < slen:
            if i >= len(s):
                return ((CType.EMPTY, None), i0, slen)

            c = s[i]
            code = ord(c)

            if 0x41 <= code <= 0x5A:
                return ((CType.CHR, chr(code + 32)), i, i + 1)
            elif (0x61 <= code <= 0x7A) or (0x30 <= code <= 0x39):
                return ((CType.CHR, c), i, i + 1)
            elif code in (0x2D, 0x20, 0x27):
                if trimmed:
                    return ((CType.CHR, c), i, i + 1)
                else:
                    return ((CType.EMPTY, None), i, i + 1)
            else:
                try:
                    normalized = unicodedata.normalize('NFKD', c)
                    ascii_char = normalized.encode('ascii', 'ignore').decode('ascii')
                    if ascii_char:
                        lower_char = ascii_char[0].lower()
                        if ('a' <= lower_char <= 'z') or ('0' <= lower_char <= '9'):
                            return ((CType.CHR, lower_char), i, i + 1)
                        elif lower_char in ('-', ' ', '\''):
                            if trimmed:
                                return ((CType.CHR, lower_char), i, i + 1)
                            else:
                                return ((CType.EMPTY, None), i, i + 1)
                        else:
                            return ((CType.EMPTY, None), i, i + 1)
                    else:
                        i += 1
                        continue
                except:
                    return ((CType.EMPTY, None), i, i + 1)

        return ((CType.EMPTY, None), i0, slen)

    @staticmethod
    def cp(s: str, i: int) -> int:
        if i >= len(s):
            return 0
        byte_str = s.encode('utf-8')
        if i >= len(byte_str):
            return 0

        n = byte_str[i]
        if n < 0x80:
            return n
        elif n <= 0xdf:
            if i + 1 >= len(byte_str):
                return n
            return ((n - 0xc0) << 6) | (0x7f & byte_str[i + 1])
        elif n <= 0xef:
            if i + 2 >= len(byte_str):
                return n
            n_prime = n - 0xe0
            m = byte_str[i + 1]
            n_prime = (n_prime << 6) | (0x7f & m)
            m = byte_str[i + 2]
            return (n_prime << 6) | (0x7f & m)
        else:
            if i + 3 >= len(byte_str):
                return n
            n_prime = n - 0xf0
            m = byte_str[i + 1]
            n_prime = (n_prime << 6) | (0x7f & m)
            m = byte_str[i + 2]
            n_prime = (n_prime << 6) | (0x7f & m)
            m = byte_str[i + 3]
            return (n_prime << 6) | (0x7f & m)

    @staticmethod
    def cmp_substring(s1: str, i1: int, j1: int, s2: str, i2: int, j2: int) -> int:
        l1 = j1 - i1
        l2 = j2 - i2

        if l1 == 1 and l2 == 1:
            c1 = s1[i1].lower() if i1 < len(s1) else ''
            c2 = s2[i2].lower() if i2 < len(s2) else ''
            if c1 < c2:
                return -1
            elif c1 > c2:
                return 1
            else:
                return 0
        else:
            substr1 = s1[i1:j1] if j1 <= len(s1) else s1[i1:]
            substr2 = s2[i2:j2] if j2 <= len(s2) else s2[i2:]

            norm1 = unicodedata.normalize('NFKD', substr1).lower()
            norm2 = unicodedata.normalize('NFKD', substr2).lower()

            if norm1 < norm2:
                return -1
            elif norm1 > norm2:
                return 1
            else:
                return 0

    @staticmethod
    def compare(n1: str, n2: str) -> int:
        if n1 == n2:
            return 0

        trimmed1 = False
        trimmed2 = False
        i1 = 0
        i2 = 0

        while True:
            if i1 >= len(n1) and i2 >= len(n2):
                return i1 - i2
            elif i1 >= len(n1):
                return -1
            elif i2 >= len(n2):
                return 1

            (c1_type, c1_val), start1, ii1 = C.unaccent(trimmed1, n1, i1, len(n1))
            (c2_type, c2_val), start2, ii2 = C.unaccent(trimmed2, n2, i2, len(n2))

            trimmed1 = True
            trimmed2 = True

            if c1_type == CType.EMPTY and c2_type == CType.EMPTY:
                cmp = C.cmp_substring(n1, start1, ii1, n2, start2, ii2)
                if cmp == 0:
                    i1 = ii1
                    i2 = ii2
                else:
                    return cmp
            elif c1_type == CType.EMPTY:
                return 1
            elif c2_type == CType.EMPTY:
                return -1
            elif c1_type == CType.STR and c2_type == CType.STR:
                if c1_val < c2_val:
                    return -1
                elif c1_val > c2_val:
                    return 1
                else:
                    cmp = C.cmp_substring(n1, start1, ii1, n2, start2, ii2)
                    if cmp == 0:
                        i1 = ii1
                        i2 = ii2
                    else:
                        return cmp
            elif c1_type == CType.CHR and c2_type == CType.CHR:
                if c1_val < c2_val:
                    return -1
                elif c1_val > c2_val:
                    return 1
                else:
                    cmp = C.cmp_substring(n1, start1, ii1, n2, start2, ii2)
                    if cmp == 0:
                        i1 = ii1
                        i2 = ii2
                    else:
                        return cmp
            elif c1_type == CType.STR and c2_type == CType.CHR:
                first_char = c1_val[0] if c1_val else ''
                if first_char < c2_val:
                    return -1
                elif first_char > c2_val:
                    return 1
                else:
                    return 1
            elif c1_type == CType.CHR and c2_type == CType.STR:
                first_char = c2_val[0] if c2_val else ''
                if c1_val < first_char:
                    return -1
                elif c1_val > first_char:
                    return 1
                else:
                    return -1
            else:
                i1 = ii1
                i2 = ii2


def compare(a: str, b: str) -> int:
    return C.compare(a, b)
