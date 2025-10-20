from dataclasses import dataclass
from typing import Optional, Any
import time


@dataclass
class Stats:
    men: int = 0
    women: int = 0
    neutre: int = 0
    noname: int = 0
    oldest_father: tuple[int, Any] = (0, None)
    oldest_mother: tuple[int, Any] = (0, None)
    youngest_father: tuple[int, Any] = (1000, None)
    youngest_mother: tuple[int, Any] = (1000, None)
    oldest_dead: tuple[int, Any] = (0, None)
    oldest_still_alive: tuple[int, Any] = (0, None)


def birth_year(p) -> Optional[int]:
    from lib import date
    birth_dmy = date.cdate_to_dmy_opt(p.birth if hasattr(p, 'birth') else None)
    if birth_dmy:
        from lib.adef import Precision
        if birth_dmy.prec == Precision.SURE:
            return birth_dmy.year
    return None


def death_year(current_year: int, p) -> Optional[int]:
    from lib import date
    from lib.gwdef import Death, NotDead
    death_obj = p.death if hasattr(p, 'death') else None
    if death_obj is None:
        return None
    if isinstance(death_obj, NotDead):
        return current_year
    if hasattr(death_obj, 'date'):
        death_dmy = date.cdate_to_dmy_opt(death_obj.date)
        if death_dmy:
            from lib.adef import Precision
            if death_dmy.prec == Precision.SURE:
                return death_dmy.year
    return None


def update_stats(base, current_year: int, s: Stats, p) -> None:
    from lib.gwdef import Sex, NotDead
    sex = p.sex if hasattr(p, 'sex') else None
    if sex == Sex.MALE:
        s.men += 1
    elif sex == Sex.FEMALE:
        s.women += 1
    elif sex == Sex.NEUTER:
        s.neutre += 1

    first_name = base.get_first_name(p) if hasattr(base, 'get_first_name') else (p.first_name if hasattr(p, 'first_name') else "")
    surname = base.get_surname(p) if hasattr(base, 'get_surname') else (p.surname if hasattr(p, 'surname') else "")
    if first_name == "?" and surname == "?":
        s.noname += 1

    birth_y = birth_year(p)
    death_y = death_year(current_year, p)
    death_obj = p.death if hasattr(p, 'death') else None

    if birth_y is not None and death_y is not None:
        age = death_y - birth_y
        if age > s.oldest_dead[0] and not isinstance(death_obj, NotDead):
            s.oldest_dead = (age, p)
        if age > s.oldest_still_alive[0] and isinstance(death_obj, NotDead):
            s.oldest_still_alive = (age, p)

    parents_ifam = p.parents if hasattr(p, 'parents') else None
    if birth_y is not None and parents_ifam is not None:
        cpl = base.foi(parents_ifam) if hasattr(base, 'foi') else None
        if cpl is not None:
            father_iper = cpl.father if hasattr(cpl, 'father') else None
            if father_iper is not None:
                father = base.poi(father_iper) if hasattr(base, 'poi') else None
                if father is not None:
                    father_birth_y = birth_year(father)
                    if father_birth_y is not None:
                        age = birth_y - father_birth_y
                        if age > s.oldest_father[0]:
                            s.oldest_father = (age, father)
                        if age < s.youngest_father[0]:
                            s.youngest_father = (age, father)

            mother_iper = cpl.mother if hasattr(cpl, 'mother') else None
            if mother_iper is not None:
                mother = base.poi(mother_iper) if hasattr(base, 'poi') else None
                if mother is not None:
                    mother_birth_y = birth_year(mother)
                    if mother_birth_y is not None:
                        age = birth_y - mother_birth_y
                        if age > s.oldest_mother[0]:
                            s.oldest_mother = (age, mother)
                        if age < s.youngest_mother[0]:
                            s.youngest_mother = (age, mother)


def stat_base(base) -> Stats:
    dummy_person = None
    s = Stats(
        men=0,
        women=0,
        neutre=0,
        noname=0,
        oldest_father=(0, dummy_person),
        oldest_mother=(0, dummy_person),
        youngest_father=(1000, dummy_person),
        youngest_mother=(1000, dummy_person),
        oldest_dead=(0, dummy_person),
        oldest_still_alive=(0, dummy_person)
    )
    current_year = time.localtime().tm_year
    persons = base.persons() if hasattr(base, 'persons') else []
    for p in persons:
        update_stats(base, current_year, s, p)
    return s


def print_stats(base, s: Stats) -> None:
    from lib import gutil
    print()
    print(f"{s.men} men")
    print(f"{s.women} women")
    print(f"{s.neutre} unknown sex")
    print(f"{s.noname} unnamed")

    if s.oldest_dead[1] is not None:
        print(f"Oldest: {gutil.designation(base, s.oldest_dead[1])}, {s.oldest_dead[0]}")
    else:
        print(f"Oldest: N/A, {s.oldest_dead[0]}")

    if s.oldest_still_alive[1] is not None:
        print(f"Oldest still alive: {gutil.designation(base, s.oldest_still_alive[1])}, {s.oldest_still_alive[0]}")
    else:
        print(f"Oldest still alive: N/A, {s.oldest_still_alive[0]}")

    if s.youngest_father[1] is not None:
        print(f"Youngest father: {gutil.designation(base, s.youngest_father[1])}, {s.youngest_father[0]}")
    else:
        print(f"Youngest father: N/A, {s.youngest_father[0]}")

    if s.youngest_mother[1] is not None:
        print(f"Youngest mother: {gutil.designation(base, s.youngest_mother[1])}, {s.youngest_mother[0]}")
    else:
        print(f"Youngest mother: N/A, {s.youngest_mother[0]}")

    if s.oldest_father[1] is not None:
        print(f"Oldest father: {gutil.designation(base, s.oldest_father[1])}, {s.oldest_father[0]}")
    else:
        print(f"Oldest father: N/A, {s.oldest_father[0]}")

    if s.oldest_mother[1] is not None:
        print(f"Oldest mother: {gutil.designation(base, s.oldest_mother[1])}, {s.oldest_mother[0]}")
    else:
        print(f"Oldest mother: N/A, {s.oldest_mother[0]}")

    print()
