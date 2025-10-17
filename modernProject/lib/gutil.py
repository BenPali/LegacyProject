from typing import Optional, List, Tuple, Callable, Any
from lib import name
from lib import date
from lib import buff
from lib import mutil
from lib import adef


def father(cpl):
    return adef.couple(cpl.father, cpl.mother).father


def mother(cpl):
    return adef.couple(cpl.father, cpl.mother).mother


def couple(multi: bool, fath, moth):
    if not multi:
        return adef.couple(fath, moth)
    else:
        return adef.multi_couple(fath, moth)


def parent_array(cpl):
    return adef.parent_array(cpl)


def spouse(ip, cpl):
    if ip == cpl.father:
        return cpl.mother
    else:
        return cpl.father


def designation(base, p) -> str:
    first_name = base.p_first_name(p)
    nom = base.p_surname(p)
    return f"{first_name}.{base.get_occ(p)} {nom}"


def person_is_key(base, p, k: str) -> bool:
    k_lower = name.crush_lower(k)
    full_name = f"{base.p_first_name(p)} {base.p_surname(p)}"
    if k_lower == name.crush_lower(full_name):
        return True
    misc_names = base.person_misc_names(p, lambda p: base.get_titles(p))
    return any(k_lower == name.crush_lower(x) for x in misc_names)


def find_num(s: str, i: int) -> Optional[Tuple[int, int]]:
    start = i
    while i < len(s):
        if i < len(s) and s[i].isdigit():
            i += 1
        else:
            c = s[i] if i < len(s) else ''
            if i == start:
                if c == ' ':
                    start += 1
                    i = start
                else:
                    return None
            else:
                return (int(s[start:i]), i)
    if i > start:
        return (int(s[start:i]), i)
    return None


def split_key(s: str, i: int) -> Optional[Tuple[int, str, int, str]]:
    while i < len(s):
        if s[i] == '.':
            num_result = find_num(s, i + 1)
            if num_result:
                occ, j = num_result
                first_name = s[0:i]
                surname = s[j:len(s)]
                return (i, first_name, occ, surname)
            else:
                i += 1
        else:
            i += 1
    return None


def person_of_string_key(base, s: str) -> Optional[Any]:
    i = 0
    while True:
        result = split_key(s, i)
        if result:
            pos, first_name, occ, surname = result
            person_result = base.person_of_key(first_name, surname.strip(), occ)
            if person_result:
                return person_result
            i = pos + 1
        else:
            return None


def rsplit_key(s: str) -> Optional[Tuple[str, int, str]]:
    i = len(s) - 1
    while i >= 0:
        if s[i] == '.':
            num_result = find_num(s, i + 1)
            if num_result:
                occ, j = num_result
                first_name = s[0:i]
                surname = s[j:len(s)]
                return (first_name, occ, surname)
            i -= 1
        else:
            i -= 1
    return None


def person_of_string_dot_key(base, s: str) -> Optional[Any]:
    result = rsplit_key(s)
    if result:
        first_name, occ, surname = result
        return base.person_of_key(first_name, surname.strip(), occ)
    return None


def person_not_a_key_find_all(base, s: str) -> List[Any]:
    ipl = base.persons_of_name(s)
    result = []
    for ip in ipl:
        p = base.poi(ip)
        if person_is_key(base, p, s):
            if ip not in result:
                result.append(ip)
    return result


def person_ht_find_all(base, s: str) -> List[Any]:
    p = person_of_string_key(base, s)
    if p:
        return [p]
    return person_not_a_key_find_all(base, s)


def find_same_name(base, p) -> List[Any]:
    f = base.p_first_name(p)
    s = base.p_surname(p)
    ipl = person_ht_find_all(base, f + " " + s)
    f_lower = name.strip_lower(f)
    s_lower = name.strip_lower(s)
    pl = []
    for ip in ipl:
        person = base.poi(ip)
        if (name.strip_lower(base.p_first_name(person)) == f_lower and
            name.strip_lower(base.p_surname(person)) == s_lower):
            pl.append(person)
    return sorted(pl, key=lambda p1: base.get_occ(p1))


def trim_trailing_spaces(s: str) -> str:
    len_s = len(s)
    i = len_s - 1
    while i >= 0:
        c = s[i]
        if c not in [' ', '\r', '\n', '\t']:
            break
        i -= 1
    len_prime = i + 1
    if len_prime == 0:
        return ""
    elif len_prime == len_s:
        return s
    else:
        return s[0:len_prime]


def alphabetic_utf_8(n1: str, n2: str) -> int:
    if n1 == n2:
        return 0
    i1, i2 = 0, 0
    while True:
        if i1 >= len(n1) and i2 >= len(n2):
            return i1 - i2
        if i1 >= len(n1):
            return -1
        if i2 >= len(n2):
            return 1
        cv1, ii1 = name.unaccent_utf_8(False, n1, i1)
        cv2, ii2 = name.unaccent_utf_8(False, n2, i2)
        if cv1 == cv2:
            substr1 = n1[i1:ii1]
            substr2 = n2[i2:ii2]
            if substr1 < substr2:
                c = -1
            elif substr1 > substr2:
                c = 1
            else:
                c = 0
        else:
            if cv1 < cv2:
                c = -1
            elif cv1 > cv2:
                c = 1
            else:
                c = 0
        if c != 0:
            return c
        i1, i2 = ii1, ii2


def _alphabetic_value_table():
    tab = [10 * i for i in range(256)]
    tab[ord('\xE0')] = tab[ord('a')] + 1
    tab[ord('\xE1')] = tab[ord('a')] + 2
    tab[ord('\xE2')] = tab[ord('a')] + 3
    tab[ord('\xE8')] = tab[ord('e')] + 1
    tab[ord('\xE9')] = tab[ord('e')] + 2
    tab[ord('\xEA')] = tab[ord('e')] + 3
    tab[ord('\xEB')] = tab[ord('e')] + 4
    tab[ord('\xF4')] = tab[ord('o')] + 1
    tab[ord('\xC1')] = tab[ord('A')] + 2
    tab[ord('\xC6')] = tab[ord('A')] + 5
    tab[ord('\xC8')] = tab[ord('E')] + 1
    tab[ord('\xC9')] = tab[ord('E')] + 2
    tab[ord('\xD6')] = tab[ord('O')] + 4
    tab[ord('?')] = 3000
    return tab


_ALPHABETIC_VALUE_TABLE = _alphabetic_value_table()


def alphabetic_value(x: str) -> int:
    if len(x) == 0:
        return 0
    return _ALPHABETIC_VALUE_TABLE[ord(x[0])]


def alphabetic_iso_8859_1(n1: str, n2: str) -> int:
    if n1 == n2:
        return 0
    i1 = mutil.initial(n1)
    i2 = mutil.initial(n2)
    while True:
        if i1 == len(n1) and i2 == len(n2):
            return i1 - i2
        if i1 == len(n1):
            return -1
        if i2 == len(n2):
            return 1
        c1 = n1[i1]
        c2 = n2[i2]
        v1 = alphabetic_value(c1)
        v2 = alphabetic_value(c2)
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1
        else:
            i1 += 1
            i2 += 1


def alphabetic(n1: str, n2: str) -> int:
    return alphabetic_iso_8859_1(n1, n2)


def alphabetic_order(n1: str, n2: str) -> int:
    return alphabetic_utf_8(n1, n2)


def arg_list_of_string(line: str) -> List[str]:
    result = []
    i = 0
    length = 0
    quote = None
    while i < len(line):
        c = line[i]
        if quote:
            if c == quote:
                quote = None
            else:
                length = buff.store(length, c)
        elif c == ' ':
            if length > 0:
                result.append(buff.get(length))
                length = 0
        elif c in ['"', "'"]:
            quote = c
        else:
            length = buff.store(length, c)
        i += 1
    if length > 0:
        result.append(buff.get(length))
    return result


def sort_person_list_aux(sort_fn: Callable, base) -> Callable:
    from functools import cmp_to_key

    def default(p1, p2):
        surname_cmp = alphabetic(base.p_surname(p1), base.p_surname(p2))
        if surname_cmp != 0:
            return surname_cmp
        fname_cmp = alphabetic(base.p_first_name(p1), base.p_first_name(p2))
        if fname_cmp != 0:
            return fname_cmp
        occ_cmp = base.get_occ(p1) - base.get_occ(p2)
        if occ_cmp != 0:
            return occ_cmp
        iper1 = base.get_iper(p1)
        iper2 = base.get_iper(p2)
        if iper1 < iper2:
            return -1
        elif iper1 > iper2:
            return 1
        return 0

    def compare(p1, p2):
        iper1 = base.get_iper(p1)
        iper2 = base.get_iper(p2)
        if iper1 == iper2:
            return 0
        d1_birth = date.od_of_cdate(base.get_birth(p1))
        d1_death = base.get_death(p1)
        d2_birth = date.od_of_cdate(base.get_birth(p2))
        d2_death = base.get_death(p2)
        date_cmp = 0
        if d1_birth and d2_birth:
            date_cmp = date.compare_date(d1_birth, d2_birth)
        elif d1_birth and hasattr(d2_death, 'date'):
            date_cmp = date.compare_date(d1_birth, date.date_of_cdate(d2_death.date))
        elif hasattr(d1_death, 'date') and d2_birth:
            date_cmp = date.compare_date(date.date_of_cdate(d1_death.date), d2_birth)
        elif hasattr(d1_death, 'date') and hasattr(d2_death, 'date'):
            date_cmp = date.compare_date(date.date_of_cdate(d1_death.date), date.date_of_cdate(d2_death.date))
        elif d1_birth:
            date_cmp = 1
        elif hasattr(d1_death, 'date'):
            date_cmp = 1
        elif d2_birth:
            date_cmp = -1
        elif hasattr(d2_death, 'date'):
            date_cmp = -1
        if date_cmp != 0:
            return date_cmp
        return default(p1, p2)

    return lambda pl: sort_fn(pl, cmp_to_key(compare))


def sort_person_list(base):
    def sorter(pl, key_fn):
        return sorted(pl, key=key_fn)
    return sort_person_list_aux(sorter, base)


def sort_uniq_person_list(base):
    def sorter(pl, key_fn):
        sorted_list = sorted(pl, key=key_fn)
        if not sorted_list:
            return []
        result = [sorted_list[0]]
        for item in sorted_list[1:]:
            if base.get_iper(item) != base.get_iper(result[-1]):
                result.append(item)
        return result
    return sort_person_list_aux(sorter, base)


def find_free_occ(base, f: str, s: str) -> int:
    ipl = base.persons_of_name(f + " " + s)
    first_name_lower = name.lower(f)
    surname_lower = name.lower(s)
    list_occ = []
    for ip in ipl:
        p = base.poi(ip)
        p_first_lower = name.lower(base.p_first_name(p))
        p_surname_lower = name.lower(base.p_surname(p))
        occ = base.get_occ(p)
        if occ not in list_occ and p_first_lower == first_name_lower and p_surname_lower == surname_lower:
            list_occ.append(occ)
    list_occ.sort()
    cnt = 0
    for occ in list_occ:
        if cnt == occ:
            cnt += 1
        else:
            break
    return cnt


def get_birth_death_date(base, p) -> Tuple[Optional[Any], Optional[Any], bool]:
    birth_date = date.od_of_cdate(base.get_birth(p))
    approx = False
    if birth_date is None:
        birth_date = date.od_of_cdate(base.get_baptism(p))
        approx = True
    death_obj = base.get_death(p)
    death_date = None
    if hasattr(death_obj, 'date'):
        death_date = date.od_of_cdate(death_obj.date)
    if death_date is None:
        burial = base.get_burial(p)
        if hasattr(burial, 'date'):
            death_date = date.od_of_cdate(burial.date)
            approx = True
    return (birth_date, death_date, approx)
