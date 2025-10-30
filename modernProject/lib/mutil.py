import re
import hashlib
from typing import List, Callable, TypeVar


T = TypeVar('T')


def list_iter_first(fn: Callable[[bool, T], None], lst: List[T]) -> None:
    if not lst:
        return
    fn(True, lst[0])
    for item in lst[1:]:
        fn(False, item)


def strip_all_trailing_spaces(s: str) -> str:
    return s.rstrip()


def tr(c1: str, c2: str, s: str) -> str:
    if len(c1) != 1 or len(c2) != 1:
        raise ValueError("c1 and c2 must be single characters")
    if c1 not in s:
        return s
    return s.replace(c1, c2)


def start_with(prefix: str, offset: int, s: str) -> bool:
    if offset < 0 or offset > len(s):
        raise ValueError(f"Invalid offset {offset} for string of length {len(s)}")
    return s[offset:].startswith(prefix)


def start_with_wildcard(prefix: str, offset: int, s: str) -> bool:
    if offset < 0 or offset > len(s):
        raise ValueError(f"Invalid offset {offset} for string of length {len(s)}")
    s = s[offset:]
    pi = 0
    si = 0
    while pi < len(prefix):
        if si >= len(s):
            if pi == len(prefix) - 1 and prefix[pi] == '_':
                return True
            return pi >= len(prefix)
        pc = prefix[pi]
        sc = s[si]
        if pc == '_':
            if sc in ('_', ' '):
                pi += 1
                si += 1
            elif pi == len(prefix) - 1:
                return True
            else:
                return False
        elif pc == sc:
            pi += 1
            si += 1
        else:
            return False
    return True


def contains(s: str, sub: str) -> bool:
    return sub in s


def roman_of_arabian(n: int) -> str:
    if n <= 0 or n >= 4000:
        raise ValueError("Number must be between 1 and 3999")
    values = [
        (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
        (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
        (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')
    ]
    result = []
    for value, numeral in values:
        count = n // value
        if count:
            result.append(numeral * count)
            n -= value * count
    return ''.join(result)


def arabian_of_roman(s: str) -> int:
    s = s.upper()
    values = {
        'I': 1, 'V': 5, 'X': 10, 'L': 50,
        'C': 100, 'D': 500, 'M': 1000
    }
    total = 0
    prev_value = 0
    for char in reversed(s):
        if char not in values:
            raise ValueError(f"Invalid roman numeral character: {char}")
        value = values[char]
        if value < prev_value:
            total -= value
        else:
            total += value
        prev_value = value
    if total > 3999:
        raise ValueError("Roman numeral too large (max 3999)")
    return total


def string_of_int_sep(sep: str, n: int) -> str:
    s = str(n)
    if n < 0:
        sign = '-'
        s = s[1:]
    else:
        sign = ''
    parts = []
    while len(s) > 3:
        parts.append(s[-3:])
        s = s[:-3]
    parts.append(s)
    return sign + sep.join(reversed(parts))


def initial(name: str) -> int:
    for i, char in enumerate(name):
        if 'A' <= char <= 'Z' or '\u00C0' <= char <= '\u00DD':
            return i
    return 0


def surnames_pieces(surname: str) -> List[str]:
    words = surname.split()
    particles = {'saint', 'sainte'}
    pieces = []
    current_piece = []
    for word in words:
        word_lower = word.lower()
        if len(word) >= 4 and word_lower not in particles:
            if current_piece:
                pieces.append(' '.join(current_piece + [word]))
                current_piece = []
            else:
                pieces.append(word)
        else:
            current_piece.append(word)
    if current_piece:
        if pieces:
            pieces[-1] = pieces[-1] + ' ' + ' '.join(current_piece)
        else:
            return []
    return pieces if len(pieces) >= 2 else []


def array_to_list_map(fn: Callable[[T], T], arr: List[T]) -> List[T]:
    return [fn(x) for x in arr]


def array_to_list_rev_map(fn: Callable[[T], T], arr: List[T]) -> List[T]:
    return [fn(x) for x in reversed(arr)]


def array_assoc(key, arr: List[tuple]) -> object:
    for k, v in arr:
        if k == key:
            return v
    raise KeyError(f"Key {key} not found")

def compare_after_particle(particles: List[str], s1: str, s2: str) -> int:
    def skip_particles(s: str) -> str:
        words = s.split()
        if not words:
            return s
        for particle in particles:
            particle_norm = particle.replace('_', ' ')
            particle_words = particle_norm.split()
            if len(words) >= len(particle_words):
                match = True
                for i, pw in enumerate(particle_words):
                    if words[i].lower() != pw.lower():
                        match = False
                        break
                if match and len(words) > len(particle_words):
                    return ' '.join(words[len(particle_words):])
        return s

    s1_stripped = skip_particles(s1)
    s2_stripped = skip_particles(s2)

    if s1_stripped < s2_stripped:
        return -1
    elif s1_stripped > s2_stripped:
        return 1
    return 0

def digest(s: str) -> str:
    return hashlib.md5(s.encode('utf-8')).hexdigest()


def colon_to_at_word(s: str, ibeg: int, iend: int) -> str:
    iendroot = ibeg
    i = ibeg
    while i + 3 < iend:
        if i + 2 < len(s) and s[i] == ':' and s[i + 2] == ':':
            iendroot = i
            break
        i += 1
    else:
        iendroot = iend

    if iendroot == iend:
        return s[ibeg:iend]

    listdecl = []
    maxd = 0
    i = iendroot
    while i < iend:
        inext = i + 3
        while inext + 3 < iend:
            if inext + 2 < len(s) and s[inext] == ':' and s[inext + 2] == ':':
                break
            inext += 1
        else:
            inext = iend

        idx = i + 3
        if idx < inext:
            if s[idx] == '+':
                e = s[idx + 1:inext]
                d = 0
            elif s[idx] == '-':
                n = 0
                while idx < inext and s[idx] == '-':
                    n += 1
                    idx += 1
                e = s[idx:inext]
                d = n
            else:
                e = s[idx:inext]
                d = 1
            listdecl.append((e, d))
            maxd = max(maxd, d)
        i = inext

    root = s[ibeg:iendroot]
    result = [root]
    for d in range(maxd + 1):
        found = None
        for e, ed in listdecl:
            if ed == d:
                found = e
                break
        result.append(found if found else '')

    return '@(' + ','.join(result) + ')'


def colon_to_at(s: str) -> str:
    if not s:
        return ''
    result = []
    ibeg = 0
    i = 0
    while i < len(s):
        if s[i] in (' ', '<', '/'):
            if i > ibeg:
                result.append(colon_to_at_word(s, ibeg, i))
            result.append(s[i])
            i += 1
            ibeg = i
        elif s[i] == '>':
            result.append(s[ibeg:i + 1])
            i += 1
            ibeg = i
        else:
            i += 1
    if i > ibeg:
        result.append(colon_to_at_word(s, ibeg, i))
    return ''.join(result)


def decline(case: str, s: str) -> str:
    transformed = colon_to_at(s) if ':' in s else s
    return f"@(@({case}){transformed})"


def extract_param(name: str, stop_char: str, params: List[str]) -> str:
    name_lower = name.lower()
    for x in params:
        if len(x) >= len(name) and x[:len(name)].lower() == name_lower:
            try:
                i = x.index(stop_char, len(name))
            except ValueError:
                i = len(x)
            return x[len(name):i]
    return ''


def input_lexicon(lang: str, ht: dict, open_fname: callable) -> None:
    ic = open_fname()
    lang_base = lang.split('.')[0] if '.' in lang else lang

    if '-' in lang_base:
        derived_lang = lang_base.split('-')[0]
    elif '_' in lang_base:
        derived_lang = lang_base.split('_')[0]
    else:
        derived_lang = ''

    tmp = {}
    hold = ''

    def process_lines():
        nonlocal hold
        current_key = None

        for line in ic:
            line = line.rstrip('\n\r')
            if len(line) < 4:
                continue

            if line.startswith('    '):
                current_key = line[4:]
                hold = ''
                continue

            if current_key is None:
                continue

            colon_idx = line.find(':')
            if colon_idx == -1:
                continue

            line_lang = line[:colon_idx]
            value = line[colon_idx + 2:] if colon_idx + 1 < len(line) else ''

            if line_lang == lang_base:
                ht[current_key] = value
                continue
            elif derived_lang and line_lang == derived_lang:
                ht[current_key] = value
                continue

            if line.startswith('->: ') and len(line) > 4:
                alias_target = line[4:]
                tmp[current_key] = alias_target
                continue

            if line_lang:
                hold = value

        if current_key and current_key not in ht and hold:
            ht[current_key] = hold

    try:
        process_lines()
    finally:
        ic.close()

    for alias_key, target_key in tmp.items():
        if target_key in ht:
            ht[alias_key] = ht[target_key]
