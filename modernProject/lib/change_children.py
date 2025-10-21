from typing import List, Tuple, Optional
from modernProject.lib import driver, mutil, name, gutil


class ChangeChildrenConflict(Exception):
    def __init__(self, person1, person2):
        self.person1 = person1
        self.person2 = person2
        super().__init__(f"Change children conflict between persons")


class FirstNameMissing(Exception):
    def __init__(self, iper):
        self.iper = iper
        super().__init__(f"First name missing for person {iper}")


def digest_children(base, ipl: List) -> str:
    result = ""
    for ip in ipl:
        p = driver.poi(base, ip)
        first_name = driver.sou(base, driver.get_first_name(p))
        surname = driver.sou(base, driver.get_surname(p))
        occ = driver.get_occ(p)
        result += first_name + "\n" + surname + "\n" + str(occ) + "\n"
    return mutil.digest(result)


def check_digest(conf, digest_val: str) -> None:
    ini_digest = conf.env.get("digest")
    if ini_digest is not None:
        if digest_val != ini_digest:
            _error_digest(conf)


def _error_digest(conf):
    raise ValueError("Digest mismatch")


def _only_printable(s: str) -> str:
    return ''.join(c for c in s if c.isprintable() or c in ('\n', '\r', '\t'))


def _rename_portrait_and_blason(conf, base, p, new_names):
    pass


def check_conflict(base, p, key: str, new_occ: int, ipl: List) -> None:
    name_lower = name.lower(key)
    iper_p = driver.get_iper(p)

    for ip in ipl:
        p1 = driver.poi(base, ip)
        iper_p1 = driver.get_iper(p1)

        if iper_p1 != iper_p:
            first_name = driver.p_first_name(base, p1)
            surname = driver.p_surname(base, p1)
            full_name = first_name + " " + surname
            name_lower_p1 = name.lower(full_name)
            occ_p1 = driver.get_occ(p1)

            if name_lower_p1 == name_lower and occ_p1 == new_occ:
                raise ChangeChildrenConflict(p, p1)


def change_child(conf, base, parent_surname: str, changed: List, ip) -> List:
    p = driver.poi(base, ip)
    iper = driver.get_iper(p)
    var = "c" + str(iper)

    new_first_name_env = conf.env.get(var + "_first_name")
    if new_first_name_env is not None:
        new_first_name = _only_printable(new_first_name_env)
    else:
        new_first_name = driver.p_first_name(base, p)

    new_surname_env = conf.env.get(var + "_surname")
    if new_surname_env is not None:
        new_surname = _only_printable(new_surname_env)
        if new_surname == "":
            new_surname = parent_surname
    else:
        new_surname = driver.p_surname(base, p)

    new_occ_env = conf.env.get(var + "_occ")
    if new_occ_env is not None:
        new_occ = int(new_occ_env)
    else:
        new_occ = 0

    if new_first_name == "":
        raise FirstNameMissing(ip)

    old_first_name = driver.p_first_name(base, p)
    old_surname = driver.p_surname(base, p)
    old_occ = driver.get_occ(p)

    if (new_first_name != old_first_name or
        new_surname != old_surname or
        new_occ != old_occ):

        key = new_first_name + " " + new_surname
        ipl = gutil.person_ht_find_all(base, key)
        check_conflict(base, p, key, new_occ, ipl)

        _rename_portrait_and_blason(conf, base, p,
                                    (new_first_name, new_surname, new_occ))

        changed_entry = (
            (old_first_name, old_surname, old_occ, ip),
            (new_first_name, new_surname, new_occ, ip)
        )
        changed = [changed_entry] + changed

        new_first_name_istr = driver.insert_string(base, new_first_name)
        new_surname_istr = driver.insert_string(base, new_surname)

        gen_p = driver.gen_person_of_person(p)
        gen_p.first_name = new_first_name_istr
        gen_p.surname = new_surname_istr
        gen_p.occ = new_occ

        driver.patch_person(base, ip, gen_p)

    return changed


def change_children(conf, base, parent_surname: str, ipl: List) -> List:
    changed = []
    for ip in ipl:
        changed = change_child(conf, base, parent_surname, changed, ip)
    return changed
