from typing import List, Tuple, Optional, Callable, Any
from enum import Enum, auto
from types import SimpleNamespace
from lib import driver, name, date as date_mod, gutil
from lib.adef import Precision


class DateSearch(Enum):
    JUST_SELF = auto()
    ADD_SPOUSE = auto()
    ADD_CHILDREN = auto()


def _nobtit(conf, base, p):
    return driver.nobtitles(base, conf.allowed_titles, conf.denied_titles, p)


def _pget(conf, base, ip):
    return driver.poi(base, ip)


def date_interval(conf, base, t: DateSearch, x) -> Optional[Tuple[Any, Any]]:
    d1 = SimpleNamespace(day=0, month=0, year=2147483647, prec=Precision.SURE, delta=0)
    d2 = SimpleNamespace(day=0, month=0, year=0, prec=Precision.SURE, delta=0)
    found = False

    def set_date(d):
        nonlocal d1, d2, found
        if date_mod.compare_dmy(d, d1) < 0:
            d1 = d
        if date_mod.compare_dmy(d, d2) > 0:
            d2 = d
        found = True

    def loop_person(search_type, person):
        nonlocal found

        birth = driver.get_birth(person)
        birth_dmy = date_mod.cdate_to_dmy_opt(birth)
        if birth_dmy is not None:
            set_date(birth_dmy)

        baptism = driver.get_baptism(person)
        baptism_dmy = date_mod.cdate_to_dmy_opt(baptism)
        if baptism_dmy is not None:
            set_date(baptism_dmy)

        death = driver.get_death(person)
        death_dmy = date_mod.dmy_of_death(death)
        if death_dmy is not None:
            set_date(death_dmy)
        else:
            from lib.gwdef import NotDead
            if isinstance(death, NotDead):
                set_date(conf.today)

        titles = _nobtit(conf, base, person)
        for title in titles:
            start_dmy = date_mod.cdate_to_dmy_opt(title.t_date_start)
            if start_dmy is not None:
                set_date(start_dmy)
            end_dmy = date_mod.cdate_to_dmy_opt(title.t_date_end)
            if end_dmy is not None:
                set_date(end_dmy)

        if search_type == DateSearch.JUST_SELF:
            return

        u = _pget(conf, base, driver.get_iper(person))
        families = driver.get_family(u)
        for ifam in families:
            fam = driver.foi(base, ifam)
            marriage = driver.get_marriage(fam)
            marriage_dmy = date_mod.cdate_to_dmy_opt(marriage)
            if marriage_dmy is not None:
                set_date(marriage_dmy)

            spouse_ip = gutil.spouse(driver.get_iper(person), fam)
            spouse = _pget(conf, base, spouse_ip)
            loop_person(DateSearch.JUST_SELF, spouse)

            if search_type == DateSearch.ADD_CHILDREN:
                children = driver.get_children(fam)
                for child_ip in children:
                    child = _pget(conf, base, child_ip)
                    loop_person(DateSearch.JUST_SELF, child)

    loop_person(t, x)

    if found:
        return (d1, d2)
    return None


def compare_title_dates(conf, base, xt1: Tuple[Any, Any], xt2: Tuple[Any, Any]) -> int:
    x1, t1 = xt1
    x2, t2 = xt2

    birth1 = driver.get_birth(x1)
    start1 = date_mod.od_of_cdate(t1.t_date_start)
    end1 = date_mod.od_of_cdate(t1.t_date_end)
    death1 = driver.get_death(x1)

    birth2 = driver.get_birth(x2)
    start2 = date_mod.od_of_cdate(t2.t_date_start)
    end2 = date_mod.od_of_cdate(t2.t_date_end)
    death2 = driver.get_death(x2)

    from lib.adef import DateGreg
    from lib.gwdef import DeathWithReason

    if start1 is not None and isinstance(start1, DateGreg):
        if start2 is not None and isinstance(start2, DateGreg):
            cmp = date_mod.compare_dmy(start1.dmy, start2.dmy)
            if cmp == 0:
                if end1 is not None and end2 is not None:
                    return date_mod.compare_date(end1, end2)
                return -1
            return cmp

    if end1 is not None and isinstance(end1, DateGreg):
        if end2 is not None and isinstance(end2, DateGreg):
            return date_mod.compare_date(end1, end2)

    if isinstance(death1, DeathWithReason) and start2 is not None:
        d1_date = date_mod.date_of_cdate(death1.date)
        if d1_date is not None and date_mod.compare_date(d1_date, start2) <= 0:
            return -1

    if start1 is not None and isinstance(death2, DeathWithReason):
        d2_date = date_mod.date_of_cdate(death2.date)
        if d2_date is not None and isinstance(start1, DateGreg):
            if date_mod.compare_date(start1, d2_date) > 0:
                return 1

    interval1_self = date_interval(conf, base, DateSearch.JUST_SELF, x1)
    interval2_self = date_interval(conf, base, DateSearch.JUST_SELF, x2)

    if interval1_self is not None and interval2_self is not None:
        d11, d12 = interval1_self
        d21, d22 = interval2_self
        if date_mod.compare_dmy(d12, d21) <= 0:
            return -1
        elif date_mod.compare_dmy(d11, d22) >= 0:
            return 1
        elif date_mod.compare_dmy(d21, d11) > 0:
            return -1
        else:
            return 1

    interval1_spouse = date_interval(conf, base, DateSearch.ADD_SPOUSE, x1)
    interval2_spouse = date_interval(conf, base, DateSearch.ADD_SPOUSE, x2)

    if interval1_spouse is not None and interval2_spouse is not None:
        d11, d12 = interval1_spouse
        d21, d22 = interval2_spouse
        if date_mod.compare_dmy(d12, d21) <= 0:
            return -1
        elif date_mod.compare_dmy(d11, d22) >= 0:
            return 1
        elif date_mod.compare_dmy(d22, d12) >= 0:
            return -1
        else:
            return 1

    interval1_children = date_interval(conf, base, DateSearch.ADD_CHILDREN, x1)
    interval2_children = date_interval(conf, base, DateSearch.ADD_CHILDREN, x2)

    if interval1_children is not None and interval2_children is not None:
        d11, d12 = interval1_children
        d21, d22 = interval2_children
        if date_mod.compare_dmy(d21, d12) >= 0:
            return -1
        elif date_mod.compare_dmy(d11, d22) >= 0:
            return 1
        elif date_mod.compare_dmy(d22, d12) >= 0:
            return -1
        else:
            return 1

    if interval1_children is not None and interval2_children is None:
        return -1
    if interval1_children is None and interval2_children is not None:
        return 1

    return -1


def compare_title_order(conf, base, xt1: Tuple[Any, Any], xt2: Tuple[Any, Any]) -> int:
    _, t1 = xt1
    _, t2 = xt2

    if t1.t_nth == 0 or t2.t_nth == 0 or t1.t_nth == t2.t_nth:
        return compare_title_dates(conf, base, xt1, xt2)
    else:
        if t1.t_nth < t2.t_nth:
            return -1
        elif t1.t_nth > t2.t_nth:
            return 1
        return 0


def select_title_place(conf, base, absolute: bool, title: str, place: str) -> Tuple[List[Tuple[Any, Any]], List[str]]:
    names = {}
    result_list = []

    tl1 = name.lower(title)
    pl1 = name.lower(place)

    for i in driver.ipers(base):
        x = _pget(conf, base, i)
        titles = _nobtit(conf, base, x)

        for t in titles:
            tl2 = driver.sou(base, t.t_ident)
            pl2 = driver.sou(base, t.t_place)

            select = False
            if absolute:
                if title == tl2 and place == pl2:
                    select = True
            else:
                if tl1 == name.lower(tl2) and pl1 == name.lower(pl2):
                    select = True

            if select:
                names[t.t_ident] = True
                result_list.append((x, t))

    names_list = [driver.sou(base, istr) for istr in names.keys()]
    return (result_list, names_list)


def select_all_with_place(conf, base, place: str) -> List[Tuple[Any, Any]]:
    p = name.lower(place)
    result = []

    for i in driver.ipers(base):
        x = _pget(conf, base, i)
        titles = _nobtit(conf, base, x)

        for t in titles:
            pl = driver.sou(base, t.t_place)
            if name.lower(pl) == p:
                result.append((x, t))

    return result


def select_title(conf, base, absolute: bool, title: str) -> Tuple[List[str], List[str]]:
    places = {}
    names = {}

    tl = name.lower(title)

    for i in driver.ipers(base):
        x = _pget(conf, base, i)
        titles = _nobtit(conf, base, x)

        for t in titles:
            tn = driver.sou(base, t.t_ident)

            select = False
            if absolute:
                if tn == title:
                    select = True
            else:
                if name.lower(tn) == tl:
                    select = True

            if select:
                names[t.t_ident] = True
                places[t.t_place] = True

    places_list = [driver.sou(base, istr) for istr in places.keys()]
    names_list = [driver.sou(base, istr) for istr in names.keys()]
    return (places_list, names_list)


def select_place(conf, base, place: str) -> List[str]:
    names = {}
    p = name.lower(place)

    for i in driver.ipers(base):
        x = _pget(conf, base, i)
        titles = _nobtit(conf, base, x)

        for t in titles:
            pn = driver.sou(base, t.t_place)
            if name.lower(pn) == p:
                names[t.t_ident] = True

    return [driver.sou(base, istr) for istr in names.keys()]


def select_all(proj: Callable, conf, base) -> List[str]:
    ht = {}

    for i in driver.ipers(base):
        x = _pget(conf, base, i)
        titles = _nobtit(conf, base, x)

        for t in titles:
            y = proj(t)
            ht[y] = True

    return [driver.sou(base, istr) for istr in ht.keys()]


def select_all_with_counter(proj: Callable, conf, base) -> List[Tuple[str, int]]:
    ht = {}

    for i in driver.ipers(base):
        x = _pget(conf, base, i)
        titles = _nobtit(conf, base, x)

        for t in titles:
            y = proj(t)
            if y in ht:
                ht[y] += 1
            else:
                ht[y] = 1

    return [(driver.sou(base, istr), count) for istr, count in ht.items()]


def select_all_titles(conf, base) -> List[Tuple[str, int]]:
    return select_all_with_counter(lambda t: t.t_ident, conf, base)


def select_all_places(conf, base) -> List[str]:
    return select_all(lambda t: t.t_place, conf, base)
