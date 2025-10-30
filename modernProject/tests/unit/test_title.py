import pytest
from types import SimpleNamespace
from lib import title
from lib.adef import Precision, Dmy, CdateGregorian, DateGreg, Calendar
from lib.gwdef import NotDead, DeathWithReason, DeathReason


def test_date_search_enum():
    assert title.DateSearch.JUST_SELF is not None
    assert title.DateSearch.ADD_SPOUSE is not None
    assert title.DateSearch.ADD_CHILDREN is not None


def test_date_interval_no_dates(monkeypatch):
    def mock_poi(base, ip):
        return SimpleNamespace(iper=ip)

    def mock_get_iper(p):
        return p.iper

    def mock_get_birth(p):
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_baptism(p):
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_death(p):
        return SimpleNamespace()

    def mock_nobtitles(base, allowed, denied, p):
        return []

    def mock_cdate_to_dmy_opt(cd):
        return None

    def mock_dmy_of_death(death):
        return None

    monkeypatch.setattr("lib.title.driver.poi", mock_poi)
    monkeypatch.setattr("lib.title.driver.get_iper", mock_get_iper)
    monkeypatch.setattr("lib.title.driver.get_birth", mock_get_birth)
    monkeypatch.setattr("lib.title.driver.get_baptism", mock_get_baptism)
    monkeypatch.setattr("lib.title.driver.get_death", mock_get_death)
    monkeypatch.setattr("lib.title.driver.nobtitles", mock_nobtitles)
    monkeypatch.setattr("lib.title.date_mod.cdate_to_dmy_opt", mock_cdate_to_dmy_opt)
    monkeypatch.setattr("lib.title.date_mod.dmy_of_death", mock_dmy_of_death)

    conf = SimpleNamespace(allowed_titles=[], denied_titles=[], today=Dmy(1, 1, 2000, Precision.SURE, 0))
    base = SimpleNamespace()
    person = SimpleNamespace(iper=1)

    result = title.date_interval(conf, base, title.DateSearch.JUST_SELF, person)
    assert result is None


def test_date_interval_with_birth(monkeypatch):
    def mock_poi(base, ip):
        return SimpleNamespace(iper=ip)

    def mock_get_iper(p):
        return p.iper

    def mock_get_birth(p):
        return CdateGregorian(123456)

    def mock_get_baptism(p):
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_death(p):
        return SimpleNamespace()

    def mock_nobtitles(base, allowed, denied, p):
        return []

    def mock_cdate_to_dmy_opt(cd):
        if isinstance(cd, CdateGregorian):
            return Dmy(15, 6, 1990, Precision.SURE, 0)
        return None

    monkeypatch.setattr("lib.title.driver.poi", mock_poi)
    monkeypatch.setattr("lib.title.driver.get_iper", mock_get_iper)
    monkeypatch.setattr("lib.title.driver.get_birth", mock_get_birth)
    monkeypatch.setattr("lib.title.driver.get_baptism", mock_get_baptism)
    monkeypatch.setattr("lib.title.driver.get_death", mock_get_death)
    monkeypatch.setattr("lib.title.driver.nobtitles", mock_nobtitles)
    monkeypatch.setattr("lib.title.date_mod.cdate_to_dmy_opt", mock_cdate_to_dmy_opt)

    conf = SimpleNamespace(allowed_titles=[], denied_titles=[], today=Dmy(1, 1, 2000, Precision.SURE, 0))
    base = SimpleNamespace()
    person = SimpleNamespace(iper=1)

    result = title.date_interval(conf, base, title.DateSearch.JUST_SELF, person)
    assert result is not None
    d1, d2 = result
    assert d1.year == 1990
    assert d2.year == 1990


def test_compare_title_order_different_nth(monkeypatch):
    t1 = SimpleNamespace(t_nth=1, t_date_start=None, t_date_end=None)
    t2 = SimpleNamespace(t_nth=2, t_date_start=None, t_date_end=None)
    x1 = SimpleNamespace()
    x2 = SimpleNamespace()

    conf = SimpleNamespace()
    base = SimpleNamespace()

    result = title.compare_title_order(conf, base, (x1, t1), (x2, t2))
    assert result < 0


def test_compare_title_order_same_nth(monkeypatch):
    def mock_poi(base, ip):
        return SimpleNamespace(iper=0)

    def mock_get_iper(p):
        return 0

    def mock_get_birth(p):
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_baptism(p):
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_death(p):
        return SimpleNamespace()

    def mock_od_of_cdate(cd):
        return None

    def mock_cdate_to_dmy_opt(cd):
        return None

    def mock_dmy_of_death(death):
        return None

    def mock_nobtitles(base, allowed, denied, p):
        return []

    def mock_get_family(p):
        return []

    monkeypatch.setattr("lib.title.driver.poi", mock_poi)
    monkeypatch.setattr("lib.title.driver.get_iper", mock_get_iper)
    monkeypatch.setattr("lib.title.driver.get_birth", mock_get_birth)
    monkeypatch.setattr("lib.title.driver.get_baptism", mock_get_baptism)
    monkeypatch.setattr("lib.title.driver.get_death", mock_get_death)
    monkeypatch.setattr("lib.title.driver.get_family", mock_get_family)
    monkeypatch.setattr("lib.title.date_mod.od_of_cdate", mock_od_of_cdate)
    monkeypatch.setattr("lib.title.date_mod.cdate_to_dmy_opt", mock_cdate_to_dmy_opt)
    monkeypatch.setattr("lib.title.date_mod.dmy_of_death", mock_dmy_of_death)
    monkeypatch.setattr("lib.title.driver.nobtitles", mock_nobtitles)

    t1 = SimpleNamespace(t_nth=1, t_date_start=None, t_date_end=None)
    t2 = SimpleNamespace(t_nth=1, t_date_start=None, t_date_end=None)
    x1 = SimpleNamespace()
    x2 = SimpleNamespace()

    conf = SimpleNamespace(allowed_titles=[], denied_titles=[])
    base = SimpleNamespace()

    result = title.compare_title_order(conf, base, (x1, t1), (x2, t2))
    assert result == -1


def test_select_title_place_absolute(monkeypatch):
    def mock_ipers(base):
        return [0, 1]

    def mock_poi(base, ip):
        return SimpleNamespace(iper=ip)

    def mock_nobtitles(base, allowed, denied, p):
        if p.iper == 0:
            return [SimpleNamespace(t_ident=10, t_place=20)]
        return [SimpleNamespace(t_ident=11, t_place=21)]

    def mock_sou(base, istr):
        mapping = {10: "Duke", 11: "Count", 20: "London", 21: "Paris"}
        return mapping.get(istr, "")

    monkeypatch.setattr("lib.title.driver.ipers", mock_ipers)
    monkeypatch.setattr("lib.title.driver.poi", mock_poi)
    monkeypatch.setattr("lib.title.driver.nobtitles", mock_nobtitles)
    monkeypatch.setattr("lib.title.driver.sou", mock_sou)

    conf = SimpleNamespace(allowed_titles=[], denied_titles=[])
    base = SimpleNamespace()

    result_list, names_list = title.select_title_place(conf, base, True, "Duke", "London")
    assert len(result_list) == 1
    assert len(names_list) == 1
    assert "Duke" in names_list


def test_select_title_place_not_absolute(monkeypatch):
    def mock_ipers(base):
        return [0, 1]

    def mock_poi(base, ip):
        return SimpleNamespace(iper=ip)

    def mock_nobtitles(base, allowed, denied, p):
        if p.iper == 0:
            return [SimpleNamespace(t_ident=10, t_place=20)]
        return [SimpleNamespace(t_ident=11, t_place=21)]

    def mock_sou(base, istr):
        mapping = {10: "Duke", 11: "Count", 20: "London", 21: "Paris"}
        return mapping.get(istr, "")

    monkeypatch.setattr("lib.title.driver.ipers", mock_ipers)
    monkeypatch.setattr("lib.title.driver.poi", mock_poi)
    monkeypatch.setattr("lib.title.driver.nobtitles", mock_nobtitles)
    monkeypatch.setattr("lib.title.driver.sou", mock_sou)

    conf = SimpleNamespace(allowed_titles=[], denied_titles=[])
    base = SimpleNamespace()

    result_list, names_list = title.select_title_place(conf, base, False, "duke", "london")
    assert len(result_list) == 1
    assert len(names_list) == 1


def test_select_all_with_place(monkeypatch):
    def mock_ipers(base):
        return [0, 1]

    def mock_poi(base, ip):
        return SimpleNamespace(iper=ip)

    def mock_nobtitles(base, allowed, denied, p):
        if p.iper == 0:
            return [SimpleNamespace(t_ident=10, t_place=20)]
        return [SimpleNamespace(t_ident=11, t_place=20)]

    def mock_sou(base, istr):
        mapping = {10: "Duke", 11: "Count", 20: "London", 21: "Paris"}
        return mapping.get(istr, "")

    monkeypatch.setattr("lib.title.driver.ipers", mock_ipers)
    monkeypatch.setattr("lib.title.driver.poi", mock_poi)
    monkeypatch.setattr("lib.title.driver.nobtitles", mock_nobtitles)
    monkeypatch.setattr("lib.title.driver.sou", mock_sou)

    conf = SimpleNamespace(allowed_titles=[], denied_titles=[])
    base = SimpleNamespace()

    result = title.select_all_with_place(conf, base, "London")
    assert len(result) == 2


def test_select_title_absolute(monkeypatch):
    def mock_ipers(base):
        return [0, 1]

    def mock_poi(base, ip):
        return SimpleNamespace(iper=ip)

    def mock_nobtitles(base, allowed, denied, p):
        if p.iper == 0:
            return [SimpleNamespace(t_ident=10, t_place=20)]
        return [SimpleNamespace(t_ident=10, t_place=21)]

    def mock_sou(base, istr):
        mapping = {10: "Duke", 20: "London", 21: "Paris"}
        return mapping.get(istr, "")

    monkeypatch.setattr("lib.title.driver.ipers", mock_ipers)
    monkeypatch.setattr("lib.title.driver.poi", mock_poi)
    monkeypatch.setattr("lib.title.driver.nobtitles", mock_nobtitles)
    monkeypatch.setattr("lib.title.driver.sou", mock_sou)

    conf = SimpleNamespace(allowed_titles=[], denied_titles=[])
    base = SimpleNamespace()

    places, names = title.select_title(conf, base, True, "Duke")
    assert len(places) == 2
    assert len(names) == 1
    assert "Duke" in names


def test_select_title_not_absolute(monkeypatch):
    def mock_ipers(base):
        return [0]

    def mock_poi(base, ip):
        return SimpleNamespace(iper=ip)

    def mock_nobtitles(base, allowed, denied, p):
        return [SimpleNamespace(t_ident=10, t_place=20)]

    def mock_sou(base, istr):
        mapping = {10: "Duke", 20: "London"}
        return mapping.get(istr, "")

    monkeypatch.setattr("lib.title.driver.ipers", mock_ipers)
    monkeypatch.setattr("lib.title.driver.poi", mock_poi)
    monkeypatch.setattr("lib.title.driver.nobtitles", mock_nobtitles)
    monkeypatch.setattr("lib.title.driver.sou", mock_sou)

    conf = SimpleNamespace(allowed_titles=[], denied_titles=[])
    base = SimpleNamespace()

    places, names = title.select_title(conf, base, False, "duke")
    assert len(places) == 1
    assert len(names) == 1


def test_select_place(monkeypatch):
    def mock_ipers(base):
        return [0, 1]

    def mock_poi(base, ip):
        return SimpleNamespace(iper=ip)

    def mock_nobtitles(base, allowed, denied, p):
        if p.iper == 0:
            return [SimpleNamespace(t_ident=10, t_place=20)]
        return [SimpleNamespace(t_ident=11, t_place=20)]

    def mock_sou(base, istr):
        mapping = {10: "Duke", 11: "Count", 20: "London"}
        return mapping.get(istr, "")

    monkeypatch.setattr("lib.title.driver.ipers", mock_ipers)
    monkeypatch.setattr("lib.title.driver.poi", mock_poi)
    monkeypatch.setattr("lib.title.driver.nobtitles", mock_nobtitles)
    monkeypatch.setattr("lib.title.driver.sou", mock_sou)

    conf = SimpleNamespace(allowed_titles=[], denied_titles=[])
    base = SimpleNamespace()

    result = title.select_place(conf, base, "London")
    assert len(result) == 2
    assert "Duke" in result
    assert "Count" in result


def test_select_all(monkeypatch):
    def mock_ipers(base):
        return [0, 1]

    def mock_poi(base, ip):
        return SimpleNamespace(iper=ip)

    def mock_nobtitles(base, allowed, denied, p):
        if p.iper == 0:
            return [SimpleNamespace(t_place=20)]
        return [SimpleNamespace(t_place=21)]

    def mock_sou(base, istr):
        mapping = {20: "London", 21: "Paris"}
        return mapping.get(istr, "")

    monkeypatch.setattr("lib.title.driver.ipers", mock_ipers)
    monkeypatch.setattr("lib.title.driver.poi", mock_poi)
    monkeypatch.setattr("lib.title.driver.nobtitles", mock_nobtitles)
    monkeypatch.setattr("lib.title.driver.sou", mock_sou)

    conf = SimpleNamespace(allowed_titles=[], denied_titles=[])
    base = SimpleNamespace()

    result = title.select_all(lambda t: t.t_place, conf, base)
    assert len(result) == 2


def test_select_all_with_counter(monkeypatch):
    def mock_ipers(base):
        return [0, 1, 2]

    def mock_poi(base, ip):
        return SimpleNamespace(iper=ip)

    def mock_nobtitles(base, allowed, denied, p):
        return [SimpleNamespace(t_ident=10)]

    def mock_sou(base, istr):
        return "Duke"

    monkeypatch.setattr("lib.title.driver.ipers", mock_ipers)
    monkeypatch.setattr("lib.title.driver.poi", mock_poi)
    monkeypatch.setattr("lib.title.driver.nobtitles", mock_nobtitles)
    monkeypatch.setattr("lib.title.driver.sou", mock_sou)

    conf = SimpleNamespace(allowed_titles=[], denied_titles=[])
    base = SimpleNamespace()

    result = title.select_all_with_counter(lambda t: t.t_ident, conf, base)
    assert len(result) == 1
    assert result[0][0] == "Duke"
    assert result[0][1] == 3


def test_select_all_titles(monkeypatch):
    def mock_ipers(base):
        return [0, 1]

    def mock_poi(base, ip):
        return SimpleNamespace(iper=ip)

    def mock_nobtitles(base, allowed, denied, p):
        if p.iper == 0:
            return [SimpleNamespace(t_ident=10), SimpleNamespace(t_ident=11)]
        return [SimpleNamespace(t_ident=10)]

    def mock_sou(base, istr):
        mapping = {10: "Duke", 11: "Count"}
        return mapping.get(istr, "")

    monkeypatch.setattr("lib.title.driver.ipers", mock_ipers)
    monkeypatch.setattr("lib.title.driver.poi", mock_poi)
    monkeypatch.setattr("lib.title.driver.nobtitles", mock_nobtitles)
    monkeypatch.setattr("lib.title.driver.sou", mock_sou)

    conf = SimpleNamespace(allowed_titles=[], denied_titles=[])
    base = SimpleNamespace()

    result = title.select_all_titles(conf, base)
    assert len(result) == 2


def test_select_all_places(monkeypatch):
    def mock_ipers(base):
        return [0, 1]

    def mock_poi(base, ip):
        return SimpleNamespace(iper=ip)

    def mock_nobtitles(base, allowed, denied, p):
        if p.iper == 0:
            return [SimpleNamespace(t_place=20)]
        return [SimpleNamespace(t_place=21)]

    def mock_sou(base, istr):
        mapping = {20: "London", 21: "Paris"}
        return mapping.get(istr, "")

    monkeypatch.setattr("lib.title.driver.ipers", mock_ipers)
    monkeypatch.setattr("lib.title.driver.poi", mock_poi)
    monkeypatch.setattr("lib.title.driver.nobtitles", mock_nobtitles)
    monkeypatch.setattr("lib.title.driver.sou", mock_sou)

    conf = SimpleNamespace(allowed_titles=[], denied_titles=[])
    base = SimpleNamespace()

    result = title.select_all_places(conf, base)
    assert len(result) == 2
    assert "London" in result
    assert "Paris" in result


def test_date_interval_with_baptism(monkeypatch):
    def mock_poi(base, ip):
        return SimpleNamespace(iper=ip)

    def mock_get_iper(p):
        return p.iper

    def mock_get_birth(p):
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_baptism(p):
        return CdateGregorian(123456)

    def mock_get_death(p):
        return SimpleNamespace()

    def mock_nobtitles(base, allowed, denied, p):
        return []

    def mock_cdate_to_dmy_opt(cd):
        if isinstance(cd, CdateGregorian):
            return Dmy(10, 5, 1985, Precision.SURE, 0)
        return None

    monkeypatch.setattr("lib.title.driver.poi", mock_poi)
    monkeypatch.setattr("lib.title.driver.get_iper", mock_get_iper)
    monkeypatch.setattr("lib.title.driver.get_birth", mock_get_birth)
    monkeypatch.setattr("lib.title.driver.get_baptism", mock_get_baptism)
    monkeypatch.setattr("lib.title.driver.get_death", mock_get_death)
    monkeypatch.setattr("lib.title.driver.nobtitles", mock_nobtitles)
    monkeypatch.setattr("lib.title.date_mod.cdate_to_dmy_opt", mock_cdate_to_dmy_opt)

    conf = SimpleNamespace(allowed_titles=[], denied_titles=[], today=Dmy(1, 1, 2000, Precision.SURE, 0))
    base = SimpleNamespace()
    person = SimpleNamespace(iper=1)

    result = title.date_interval(conf, base, title.DateSearch.JUST_SELF, person)
    assert result is not None
    d1, d2 = result
    assert d1.year == 1985
    assert d2.year == 1985


def test_date_interval_with_not_dead(monkeypatch):
    def mock_poi(base, ip):
        return SimpleNamespace(iper=ip)

    def mock_get_iper(p):
        return p.iper

    def mock_get_birth(p):
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_baptism(p):
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_death(p):
        return NotDead()

    def mock_nobtitles(base, allowed, denied, p):
        return []

    def mock_cdate_to_dmy_opt(cd):
        return None

    def mock_dmy_of_death(death):
        return None

    monkeypatch.setattr("lib.title.driver.poi", mock_poi)
    monkeypatch.setattr("lib.title.driver.get_iper", mock_get_iper)
    monkeypatch.setattr("lib.title.driver.get_birth", mock_get_birth)
    monkeypatch.setattr("lib.title.driver.get_baptism", mock_get_baptism)
    monkeypatch.setattr("lib.title.driver.get_death", mock_get_death)
    monkeypatch.setattr("lib.title.driver.nobtitles", mock_nobtitles)
    monkeypatch.setattr("lib.title.date_mod.cdate_to_dmy_opt", mock_cdate_to_dmy_opt)
    monkeypatch.setattr("lib.title.date_mod.dmy_of_death", mock_dmy_of_death)

    conf = SimpleNamespace(allowed_titles=[], denied_titles=[], today=Dmy(1, 1, 2025, Precision.SURE, 0))
    base = SimpleNamespace()
    person = SimpleNamespace(iper=1)

    result = title.date_interval(conf, base, title.DateSearch.JUST_SELF, person)
    assert result is not None
    d1, d2 = result
    assert d2.year == 2025


def test_date_interval_with_titles(monkeypatch):
    def mock_poi(base, ip):
        return SimpleNamespace(iper=ip)

    def mock_get_iper(p):
        return p.iper

    def mock_get_birth(p):
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_baptism(p):
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_death(p):
        return SimpleNamespace()

    def mock_nobtitles(base, allowed, denied, p):
        return [
            SimpleNamespace(t_date_start=CdateGregorian(111), t_date_end=CdateGregorian(222))
        ]

    def mock_cdate_to_dmy_opt(cd):
        if isinstance(cd, CdateGregorian):
            if cd.value == 111:
                return Dmy(1, 1, 1900, Precision.SURE, 0)
            elif cd.value == 222:
                return Dmy(31, 12, 1920, Precision.SURE, 0)
        return None

    monkeypatch.setattr("lib.title.driver.poi", mock_poi)
    monkeypatch.setattr("lib.title.driver.get_iper", mock_get_iper)
    monkeypatch.setattr("lib.title.driver.get_birth", mock_get_birth)
    monkeypatch.setattr("lib.title.driver.get_baptism", mock_get_baptism)
    monkeypatch.setattr("lib.title.driver.get_death", mock_get_death)
    monkeypatch.setattr("lib.title.driver.nobtitles", mock_nobtitles)
    monkeypatch.setattr("lib.title.date_mod.cdate_to_dmy_opt", mock_cdate_to_dmy_opt)

    conf = SimpleNamespace(allowed_titles=[], denied_titles=[], today=Dmy(1, 1, 2000, Precision.SURE, 0))
    base = SimpleNamespace()
    person = SimpleNamespace(iper=1)

    result = title.date_interval(conf, base, title.DateSearch.JUST_SELF, person)
    assert result is not None
    d1, d2 = result
    assert d1.year == 1900
    assert d2.year == 1920


def test_date_interval_add_spouse(monkeypatch):
    def mock_poi(base, ip):
        return SimpleNamespace(iper=ip)

    def mock_get_iper(p):
        return p.iper

    def mock_get_birth(p):
        if p.iper == 1:
            return CdateGregorian(100)
        else:
            return CdateGregorian(101)

    def mock_get_baptism(p):
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_death(p):
        return SimpleNamespace()

    def mock_nobtitles(base, allowed, denied, p):
        return []

    def mock_cdate_to_dmy_opt(cd):
        if isinstance(cd, CdateGregorian):
            if cd.value == 100:
                return Dmy(1, 1, 1980, Precision.SURE, 0)
            elif cd.value == 101:
                return Dmy(1, 1, 1982, Precision.SURE, 0)
            elif cd.value == 200:
                return Dmy(15, 6, 2005, Precision.SURE, 0)
        return None

    def mock_dmy_of_death(death):
        return None

    def mock_get_family(p):
        return [10]

    def mock_foi(base, ifam):
        return SimpleNamespace(ifam=ifam)

    def mock_get_marriage(fam):
        return CdateGregorian(200)

    def mock_get_spouse(iper, fam):
        return 2

    monkeypatch.setattr("lib.title.driver.poi", mock_poi)
    monkeypatch.setattr("lib.title.driver.get_iper", mock_get_iper)
    monkeypatch.setattr("lib.title.driver.get_birth", mock_get_birth)
    monkeypatch.setattr("lib.title.driver.get_baptism", mock_get_baptism)
    monkeypatch.setattr("lib.title.driver.get_death", mock_get_death)
    monkeypatch.setattr("lib.title.driver.nobtitles", mock_nobtitles)
    monkeypatch.setattr("lib.title.date_mod.cdate_to_dmy_opt", mock_cdate_to_dmy_opt)
    monkeypatch.setattr("lib.title.date_mod.dmy_of_death", mock_dmy_of_death)
    monkeypatch.setattr("lib.title.driver.get_family", mock_get_family)
    monkeypatch.setattr("lib.title.driver.foi", mock_foi)
    monkeypatch.setattr("lib.title.driver.get_marriage", mock_get_marriage)
    monkeypatch.setattr("lib.title.gutil.spouse", mock_get_spouse)

    conf = SimpleNamespace(allowed_titles=[], denied_titles=[], today=Dmy(1, 1, 2000, Precision.SURE, 0))
    base = SimpleNamespace()
    person = SimpleNamespace(iper=1)

    result = title.date_interval(conf, base, title.DateSearch.ADD_SPOUSE, person)
    assert result is not None
    d1, d2 = result
    assert d1.year == 1980
    assert d2.year == 2005


def test_date_interval_add_children(monkeypatch):
    def mock_poi(base, ip):
        return SimpleNamespace(iper=ip)

    def mock_get_iper(p):
        return p.iper

    def mock_get_birth(p):
        if p.iper == 1:
            return CdateGregorian(100)
        elif p.iper == 3:
            return CdateGregorian(103)
        return CdateGregorian(101)

    def mock_get_baptism(p):
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_death(p):
        return SimpleNamespace()

    def mock_nobtitles(base, allowed, denied, p):
        return []

    def mock_cdate_to_dmy_opt(cd):
        if isinstance(cd, CdateGregorian):
            if cd.value == 100:
                return Dmy(1, 1, 1980, Precision.SURE, 0)
            elif cd.value == 101:
                return Dmy(1, 1, 1982, Precision.SURE, 0)
            elif cd.value == 103:
                return Dmy(1, 1, 2010, Precision.SURE, 0)
        return None

    def mock_dmy_of_death(death):
        return None

    def mock_get_family(p):
        return [10]

    def mock_foi(base, ifam):
        return SimpleNamespace(ifam=ifam)

    def mock_get_marriage(fam):
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_spouse(iper, fam):
        return 2

    def mock_get_children(fam):
        return [3]

    monkeypatch.setattr("lib.title.driver.poi", mock_poi)
    monkeypatch.setattr("lib.title.driver.get_iper", mock_get_iper)
    monkeypatch.setattr("lib.title.driver.get_birth", mock_get_birth)
    monkeypatch.setattr("lib.title.driver.get_baptism", mock_get_baptism)
    monkeypatch.setattr("lib.title.driver.get_death", mock_get_death)
    monkeypatch.setattr("lib.title.driver.nobtitles", mock_nobtitles)
    monkeypatch.setattr("lib.title.date_mod.cdate_to_dmy_opt", mock_cdate_to_dmy_opt)
    monkeypatch.setattr("lib.title.date_mod.dmy_of_death", mock_dmy_of_death)
    monkeypatch.setattr("lib.title.driver.get_family", mock_get_family)
    monkeypatch.setattr("lib.title.driver.foi", mock_foi)
    monkeypatch.setattr("lib.title.driver.get_marriage", mock_get_marriage)
    monkeypatch.setattr("lib.title.gutil.spouse", mock_get_spouse)
    monkeypatch.setattr("lib.title.driver.get_children", mock_get_children)

    conf = SimpleNamespace(allowed_titles=[], denied_titles=[], today=Dmy(1, 1, 2000, Precision.SURE, 0))
    base = SimpleNamespace()
    person = SimpleNamespace(iper=1)

    result = title.date_interval(conf, base, title.DateSearch.ADD_CHILDREN, person)
    assert result is not None
    d1, d2 = result
    assert d1.year == 1980
    assert d2.year == 2010


def test_compare_title_dates_with_start_dates(monkeypatch):
    def mock_get_birth(p):
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_death(p):
        return SimpleNamespace()

    def mock_od_of_cdate(cd):
        if isinstance(cd, CdateGregorian):
            if cd.value == 100:
                return DateGreg(Dmy(1, 1, 1900, Precision.SURE, 0), Calendar.GREGORIAN)
            elif cd.value == 101:
                return DateGreg(Dmy(1, 1, 1910, Precision.SURE, 0), Calendar.GREGORIAN)
        return None

    def mock_compare_dmy(d1, d2):
        if d1.year < d2.year:
            return -1
        elif d1.year > d2.year:
            return 1
        return 0

    monkeypatch.setattr("lib.title.driver.get_birth", mock_get_birth)
    monkeypatch.setattr("lib.title.driver.get_death", mock_get_death)
    monkeypatch.setattr("lib.title.date_mod.od_of_cdate", mock_od_of_cdate)
    monkeypatch.setattr("lib.title.date_mod.compare_dmy", mock_compare_dmy)

    conf = SimpleNamespace()
    base = SimpleNamespace()
    x1 = SimpleNamespace()
    x2 = SimpleNamespace()
    t1 = SimpleNamespace(t_date_start=CdateGregorian(100), t_date_end=None)
    t2 = SimpleNamespace(t_date_start=CdateGregorian(101), t_date_end=None)

    result = title.compare_title_dates(conf, base, (x1, t1), (x2, t2))
    assert result < 0


def test_compare_title_dates_with_equal_starts(monkeypatch):
    def mock_get_birth(p):
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_death(p):
        return SimpleNamespace()

    def mock_od_of_cdate(cd):
        if isinstance(cd, CdateGregorian):
            if cd.value == 100:
                return DateGreg(Dmy(1, 1, 1900, Precision.SURE, 0), Calendar.GREGORIAN)
            elif cd.value == 200:
                return DateGreg(Dmy(31, 12, 1920, Precision.SURE, 0), Calendar.GREGORIAN)
            elif cd.value == 201:
                return DateGreg(Dmy(31, 12, 1925, Precision.SURE, 0), Calendar.GREGORIAN)
        return None

    def mock_compare_dmy(d1, d2):
        if d1.year < d2.year:
            return -1
        elif d1.year > d2.year:
            return 1
        return 0

    def mock_compare_date(d1, d2):
        return mock_compare_dmy(d1.dmy, d2.dmy)

    monkeypatch.setattr("lib.title.driver.get_birth", mock_get_birth)
    monkeypatch.setattr("lib.title.driver.get_death", mock_get_death)
    monkeypatch.setattr("lib.title.date_mod.od_of_cdate", mock_od_of_cdate)
    monkeypatch.setattr("lib.title.date_mod.compare_dmy", mock_compare_dmy)
    monkeypatch.setattr("lib.title.date_mod.compare_date", mock_compare_date)

    conf = SimpleNamespace()
    base = SimpleNamespace()
    x1 = SimpleNamespace()
    x2 = SimpleNamespace()
    t1 = SimpleNamespace(t_date_start=CdateGregorian(100), t_date_end=CdateGregorian(200))
    t2 = SimpleNamespace(t_date_start=CdateGregorian(100), t_date_end=CdateGregorian(201))

    result = title.compare_title_dates(conf, base, (x1, t1), (x2, t2))
    assert result < 0


def test_compare_title_dates_with_end_dates(monkeypatch):
    def mock_get_birth(p):
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_death(p):
        return SimpleNamespace()

    def mock_od_of_cdate(cd):
        if isinstance(cd, CdateGregorian):
            if cd.value == 200:
                return DateGreg(Dmy(31, 12, 1920, Precision.SURE, 0), Calendar.GREGORIAN)
            elif cd.value == 201:
                return DateGreg(Dmy(31, 12, 1925, Precision.SURE, 0), Calendar.GREGORIAN)
        return None

    def mock_compare_date(d1, d2):
        if d1.dmy.year < d2.dmy.year:
            return -1
        elif d1.dmy.year > d2.dmy.year:
            return 1
        return 0

    monkeypatch.setattr("lib.title.driver.get_birth", mock_get_birth)
    monkeypatch.setattr("lib.title.driver.get_death", mock_get_death)
    monkeypatch.setattr("lib.title.date_mod.od_of_cdate", mock_od_of_cdate)
    monkeypatch.setattr("lib.title.date_mod.compare_date", mock_compare_date)

    conf = SimpleNamespace()
    base = SimpleNamespace()
    x1 = SimpleNamespace()
    x2 = SimpleNamespace()
    t1 = SimpleNamespace(t_date_start=None, t_date_end=CdateGregorian(200))
    t2 = SimpleNamespace(t_date_start=None, t_date_end=CdateGregorian(201))

    result = title.compare_title_dates(conf, base, (x1, t1), (x2, t2))
    assert result < 0


def test_compare_title_dates_death_before_start(monkeypatch):
    def mock_get_birth(p):
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_death(p):
        if p == x1:
            return DeathWithReason(DeathReason.KILLED, CdateGregorian(500))
        return SimpleNamespace()

    def mock_od_of_cdate(cd):
        if isinstance(cd, CdateGregorian):
            if cd.value == 500:
                return DateGreg(Dmy(1, 1, 1800, Precision.SURE, 0), Calendar.GREGORIAN)
            elif cd.value == 100:
                return DateGreg(Dmy(1, 1, 1900, Precision.SURE, 0), Calendar.GREGORIAN)
        return None

    def mock_date_of_cdate(cd):
        return mock_od_of_cdate(cd)

    def mock_compare_date(d1, d2):
        if d1.dmy.year < d2.dmy.year:
            return -1
        elif d1.dmy.year > d2.dmy.year:
            return 1
        return 0

    monkeypatch.setattr("lib.title.driver.get_birth", mock_get_birth)
    monkeypatch.setattr("lib.title.driver.get_death", mock_get_death)
    monkeypatch.setattr("lib.title.date_mod.od_of_cdate", mock_od_of_cdate)
    monkeypatch.setattr("lib.title.date_mod.date_of_cdate", mock_date_of_cdate)
    monkeypatch.setattr("lib.title.date_mod.compare_date", mock_compare_date)

    conf = SimpleNamespace()
    base = SimpleNamespace()
    x1 = SimpleNamespace()
    x2 = SimpleNamespace()
    t1 = SimpleNamespace(t_date_start=None, t_date_end=None)
    t2 = SimpleNamespace(t_date_start=CdateGregorian(100), t_date_end=None)

    result = title.compare_title_dates(conf, base, (x1, t1), (x2, t2))
    assert result < 0


def test_compare_title_dates_start_after_death(monkeypatch):
    def mock_get_birth(p):
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_death(p):
        if p == x2:
            return DeathWithReason(DeathReason.KILLED, CdateGregorian(500))
        return SimpleNamespace()

    def mock_od_of_cdate(cd):
        if isinstance(cd, CdateGregorian):
            if cd.value == 500:
                return DateGreg(Dmy(1, 1, 1800, Precision.SURE, 0), Calendar.GREGORIAN)
            elif cd.value == 100:
                return DateGreg(Dmy(1, 1, 1900, Precision.SURE, 0), Calendar.GREGORIAN)
        return None

    def mock_date_of_cdate(cd):
        return mock_od_of_cdate(cd)

    def mock_compare_date(d1, d2):
        if d1.dmy.year < d2.dmy.year:
            return -1
        elif d1.dmy.year > d2.dmy.year:
            return 1
        return 0

    monkeypatch.setattr("lib.title.driver.get_birth", mock_get_birth)
    monkeypatch.setattr("lib.title.driver.get_death", mock_get_death)
    monkeypatch.setattr("lib.title.date_mod.od_of_cdate", mock_od_of_cdate)
    monkeypatch.setattr("lib.title.date_mod.date_of_cdate", mock_date_of_cdate)
    monkeypatch.setattr("lib.title.date_mod.compare_date", mock_compare_date)

    conf = SimpleNamespace()
    base = SimpleNamespace()
    x1 = SimpleNamespace()
    x2 = SimpleNamespace()
    t1 = SimpleNamespace(t_date_start=CdateGregorian(100), t_date_end=None)
    t2 = SimpleNamespace(t_date_start=None, t_date_end=None)

    result = title.compare_title_dates(conf, base, (x1, t1), (x2, t2))
    assert result > 0


def test_compare_title_dates_intervals_no_overlap(monkeypatch):
    def mock_poi(base, ip):
        return SimpleNamespace(iper=ip)

    def mock_get_iper(p):
        return p.iper

    def mock_get_birth(p):
        if p.iper == 1:
            return CdateGregorian(100)
        elif p.iper == 2:
            return CdateGregorian(200)
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_baptism(p):
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_death(p):
        if p.iper == 1:
            return DeathWithReason(DeathReason.KILLED, CdateGregorian(150))
        elif p.iper == 2:
            return DeathWithReason(DeathReason.KILLED, CdateGregorian(250))
        return SimpleNamespace()

    def mock_nobtitles(base, allowed, denied, p):
        return []

    def mock_get_family(p):
        return []

    def mock_od_of_cdate(cd):
        return None

    def mock_cdate_to_dmy_opt(cd):
        if isinstance(cd, CdateGregorian):
            if cd.value == 100:
                return Dmy(1, 1, 1800, Precision.SURE, 0)
            elif cd.value == 150:
                return Dmy(1, 1, 1850, Precision.SURE, 0)
            elif cd.value == 200:
                return Dmy(1, 1, 1900, Precision.SURE, 0)
            elif cd.value == 250:
                return Dmy(1, 1, 1950, Precision.SURE, 0)
        return None

    def mock_dmy_of_death(death):
        if isinstance(death, DeathWithReason):
            return mock_cdate_to_dmy_opt(death.date)
        return None

    def mock_compare_dmy(d1, d2):
        if d1.year < d2.year:
            return -1
        elif d1.year > d2.year:
            return 1
        return 0

    monkeypatch.setattr("lib.title.driver.poi", mock_poi)
    monkeypatch.setattr("lib.title.driver.get_iper", mock_get_iper)
    monkeypatch.setattr("lib.title.driver.get_birth", mock_get_birth)
    monkeypatch.setattr("lib.title.driver.get_baptism", mock_get_baptism)
    monkeypatch.setattr("lib.title.driver.get_death", mock_get_death)
    monkeypatch.setattr("lib.title.driver.nobtitles", mock_nobtitles)
    monkeypatch.setattr("lib.title.driver.get_family", mock_get_family)
    monkeypatch.setattr("lib.title.date_mod.od_of_cdate", mock_od_of_cdate)
    monkeypatch.setattr("lib.title.date_mod.cdate_to_dmy_opt", mock_cdate_to_dmy_opt)
    monkeypatch.setattr("lib.title.date_mod.dmy_of_death", mock_dmy_of_death)
    monkeypatch.setattr("lib.title.date_mod.compare_dmy", mock_compare_dmy)

    conf = SimpleNamespace(allowed_titles=[], denied_titles=[], today=Dmy(1, 1, 2000, Precision.SURE, 0))
    base = SimpleNamespace()
    x1 = SimpleNamespace(iper=1)
    x2 = SimpleNamespace(iper=2)
    t1 = SimpleNamespace(t_date_start=None, t_date_end=None)
    t2 = SimpleNamespace(t_date_start=None, t_date_end=None)

    result = title.compare_title_dates(conf, base, (x1, t1), (x2, t2))
    assert result < 0


def test_compare_title_order_zero_nth(monkeypatch):
    def mock_poi(base, ip):
        return SimpleNamespace(iper=0)

    def mock_get_iper(p):
        return 0

    def mock_get_birth(p):
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_baptism(p):
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_death(p):
        return SimpleNamespace()

    def mock_od_of_cdate(cd):
        return None

    def mock_cdate_to_dmy_opt(cd):
        return None

    def mock_dmy_of_death(death):
        return None

    def mock_nobtitles(base, allowed, denied, p):
        return []

    def mock_get_family(p):
        return []

    monkeypatch.setattr("lib.title.driver.poi", mock_poi)
    monkeypatch.setattr("lib.title.driver.get_iper", mock_get_iper)
    monkeypatch.setattr("lib.title.driver.get_birth", mock_get_birth)
    monkeypatch.setattr("lib.title.driver.get_baptism", mock_get_baptism)
    monkeypatch.setattr("lib.title.driver.get_death", mock_get_death)
    monkeypatch.setattr("lib.title.driver.get_family", mock_get_family)
    monkeypatch.setattr("lib.title.date_mod.od_of_cdate", mock_od_of_cdate)
    monkeypatch.setattr("lib.title.date_mod.cdate_to_dmy_opt", mock_cdate_to_dmy_opt)
    monkeypatch.setattr("lib.title.date_mod.dmy_of_death", mock_dmy_of_death)
    monkeypatch.setattr("lib.title.driver.nobtitles", mock_nobtitles)

    t1 = SimpleNamespace(t_nth=0, t_date_start=None, t_date_end=None)
    t2 = SimpleNamespace(t_nth=5, t_date_start=None, t_date_end=None)
    x1 = SimpleNamespace()
    x2 = SimpleNamespace()

    conf = SimpleNamespace(allowed_titles=[], denied_titles=[])
    base = SimpleNamespace()

    result = title.compare_title_order(conf, base, (x1, t1), (x2, t2))
    assert result == -1


def test_compare_title_dates_equal_starts_no_end2(monkeypatch):
    def mock_get_birth(p):
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_death(p):
        return SimpleNamespace()

    def mock_od_of_cdate(cd):
        if isinstance(cd, CdateGregorian):
            if cd.value == 100:
                return DateGreg(Dmy(1, 1, 1900, Precision.SURE, 0), Calendar.GREGORIAN)
            elif cd.value == 200:
                return DateGreg(Dmy(31, 12, 1920, Precision.SURE, 0), Calendar.GREGORIAN)
        return None

    def mock_compare_dmy(d1, d2):
        if d1.year < d2.year:
            return -1
        elif d1.year > d2.year:
            return 1
        return 0

    monkeypatch.setattr("lib.title.driver.get_birth", mock_get_birth)
    monkeypatch.setattr("lib.title.driver.get_death", mock_get_death)
    monkeypatch.setattr("lib.title.date_mod.od_of_cdate", mock_od_of_cdate)
    monkeypatch.setattr("lib.title.date_mod.compare_dmy", mock_compare_dmy)

    conf = SimpleNamespace()
    base = SimpleNamespace()
    x1 = SimpleNamespace()
    x2 = SimpleNamespace()
    t1 = SimpleNamespace(t_date_start=CdateGregorian(100), t_date_end=CdateGregorian(200))
    t2 = SimpleNamespace(t_date_start=CdateGregorian(100), t_date_end=None)

    result = title.compare_title_dates(conf, base, (x1, t1), (x2, t2))
    assert result == -1


def test_compare_title_dates_intervals_spouse_overlap(monkeypatch):
    def mock_poi(base, ip):
        return SimpleNamespace(iper=ip)

    def mock_get_iper(p):
        return p.iper

    def mock_get_birth(p):
        if p.iper == 1:
            return CdateGregorian(100)
        elif p.iper == 2:
            return CdateGregorian(200)
        elif p.iper == 3:
            return CdateGregorian(110)
        elif p.iper == 4:
            return CdateGregorian(210)
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_baptism(p):
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_death(p):
        return SimpleNamespace()

    def mock_nobtitles(base, allowed, denied, p):
        return []

    def mock_get_family(p):
        if p.iper == 1:
            return [10]
        elif p.iper == 2:
            return [20]
        return []

    def mock_foi(base, ifam):
        return SimpleNamespace(ifam=ifam)

    def mock_get_marriage(fam):
        from lib.adef import CdateNone
        return CdateNone()

    def mock_spouse(iper, fam):
        if iper == 1:
            return 3
        elif iper == 2:
            return 4
        return 0

    def mock_od_of_cdate(cd):
        return None

    def mock_cdate_to_dmy_opt(cd):
        if isinstance(cd, CdateGregorian):
            if cd.value == 100:
                return Dmy(1, 1, 1900, Precision.SURE, 0)
            elif cd.value == 110:
                return Dmy(1, 1, 1910, Precision.SURE, 0)
            elif cd.value == 200:
                return Dmy(1, 1, 1905, Precision.SURE, 0)
            elif cd.value == 210:
                return Dmy(1, 1, 1915, Precision.SURE, 0)
        return None

    def mock_dmy_of_death(death):
        return None

    def mock_compare_dmy(d1, d2):
        if d1.year < d2.year:
            return -1
        elif d1.year > d2.year:
            return 1
        return 0

    monkeypatch.setattr("lib.title.driver.poi", mock_poi)
    monkeypatch.setattr("lib.title.driver.get_iper", mock_get_iper)
    monkeypatch.setattr("lib.title.driver.get_birth", mock_get_birth)
    monkeypatch.setattr("lib.title.driver.get_baptism", mock_get_baptism)
    monkeypatch.setattr("lib.title.driver.get_death", mock_get_death)
    monkeypatch.setattr("lib.title.driver.nobtitles", mock_nobtitles)
    monkeypatch.setattr("lib.title.driver.get_family", mock_get_family)
    monkeypatch.setattr("lib.title.driver.foi", mock_foi)
    monkeypatch.setattr("lib.title.driver.get_marriage", mock_get_marriage)
    monkeypatch.setattr("lib.title.gutil.spouse", mock_spouse)
    monkeypatch.setattr("lib.title.date_mod.od_of_cdate", mock_od_of_cdate)
    monkeypatch.setattr("lib.title.date_mod.cdate_to_dmy_opt", mock_cdate_to_dmy_opt)
    monkeypatch.setattr("lib.title.date_mod.dmy_of_death", mock_dmy_of_death)
    monkeypatch.setattr("lib.title.date_mod.compare_dmy", mock_compare_dmy)

    conf = SimpleNamespace(allowed_titles=[], denied_titles=[], today=Dmy(1, 1, 2000, Precision.SURE, 0))
    base = SimpleNamespace()
    x1 = SimpleNamespace(iper=1)
    x2 = SimpleNamespace(iper=2)
    t1 = SimpleNamespace(t_date_start=None, t_date_end=None)
    t2 = SimpleNamespace(t_date_start=None, t_date_end=None)

    result = title.compare_title_dates(conf, base, (x1, t1), (x2, t2))
    assert result == -1


def test_compare_title_dates_intervals_children_overlap(monkeypatch):
    def mock_poi(base, ip):
        return SimpleNamespace(iper=ip)

    def mock_get_iper(p):
        return p.iper

    def mock_get_birth(p):
        if p.iper in [1, 3, 5]:
            return CdateGregorian(100)
        elif p.iper in [2, 4, 6]:
            return CdateGregorian(200)
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_baptism(p):
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_death(p):
        return SimpleNamespace()

    def mock_nobtitles(base, allowed, denied, p):
        return []

    def mock_get_family(p):
        if p.iper in [1, 2]:
            return [10]
        return []

    def mock_foi(base, ifam):
        return SimpleNamespace(ifam=ifam)

    def mock_get_marriage(fam):
        from lib.adef import CdateNone
        return CdateNone()

    def mock_spouse(iper, fam):
        if iper == 1:
            return 3
        elif iper == 2:
            return 4
        return 0

    def mock_get_children(fam):
        if fam.ifam == 10:
            return [5, 6]
        return []

    def mock_od_of_cdate(cd):
        return None

    def mock_cdate_to_dmy_opt(cd):
        if isinstance(cd, CdateGregorian):
            if cd.value == 100:
                return Dmy(1, 1, 1900, Precision.SURE, 0)
            elif cd.value == 200:
                return Dmy(1, 1, 1910, Precision.SURE, 0)
        return None

    def mock_dmy_of_death(death):
        return None

    def mock_compare_dmy(d1, d2):
        if d1.year < d2.year:
            return -1
        elif d1.year > d2.year:
            return 1
        return 0

    monkeypatch.setattr("lib.title.driver.poi", mock_poi)
    monkeypatch.setattr("lib.title.driver.get_iper", mock_get_iper)
    monkeypatch.setattr("lib.title.driver.get_birth", mock_get_birth)
    monkeypatch.setattr("lib.title.driver.get_baptism", mock_get_baptism)
    monkeypatch.setattr("lib.title.driver.get_death", mock_get_death)
    monkeypatch.setattr("lib.title.driver.nobtitles", mock_nobtitles)
    monkeypatch.setattr("lib.title.driver.get_family", mock_get_family)
    monkeypatch.setattr("lib.title.driver.foi", mock_foi)
    monkeypatch.setattr("lib.title.driver.get_marriage", mock_get_marriage)
    monkeypatch.setattr("lib.title.gutil.spouse", mock_spouse)
    monkeypatch.setattr("lib.title.driver.get_children", mock_get_children)
    monkeypatch.setattr("lib.title.date_mod.od_of_cdate", mock_od_of_cdate)
    monkeypatch.setattr("lib.title.date_mod.cdate_to_dmy_opt", mock_cdate_to_dmy_opt)
    monkeypatch.setattr("lib.title.date_mod.dmy_of_death", mock_dmy_of_death)
    monkeypatch.setattr("lib.title.date_mod.compare_dmy", mock_compare_dmy)

    conf = SimpleNamespace(allowed_titles=[], denied_titles=[], today=Dmy(1, 1, 2000, Precision.SURE, 0))
    base = SimpleNamespace()
    x1 = SimpleNamespace(iper=1)
    x2 = SimpleNamespace(iper=2)
    t1 = SimpleNamespace(t_date_start=None, t_date_end=None)
    t2 = SimpleNamespace(t_date_start=None, t_date_end=None)

    result = title.compare_title_dates(conf, base, (x1, t1), (x2, t2))
    assert result == -1


def test_compare_title_dates_one_interval_children_none(monkeypatch):
    def mock_poi(base, ip):
        return SimpleNamespace(iper=ip)

    def mock_get_iper(p):
        return p.iper

    def mock_get_birth(p):
        if p.iper == 1:
            return CdateGregorian(100)
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_baptism(p):
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_death(p):
        return SimpleNamespace()

    def mock_nobtitles(base, allowed, denied, p):
        return []

    def mock_get_family(p):
        if p.iper == 1:
            return [10]
        return []

    def mock_foi(base, ifam):
        return SimpleNamespace(ifam=ifam)

    def mock_get_marriage(fam):
        from lib.adef import CdateNone
        return CdateNone()

    def mock_spouse(iper, fam):
        return 3

    def mock_get_children(fam):
        return [5]

    def mock_od_of_cdate(cd):
        return None

    def mock_cdate_to_dmy_opt(cd):
        if isinstance(cd, CdateGregorian):
            if cd.value == 100:
                return Dmy(1, 1, 1900, Precision.SURE, 0)
        return None

    def mock_dmy_of_death(death):
        return None

    def mock_compare_dmy(d1, d2):
        if d1.year < d2.year:
            return -1
        elif d1.year > d2.year:
            return 1
        return 0

    monkeypatch.setattr("lib.title.driver.poi", mock_poi)
    monkeypatch.setattr("lib.title.driver.get_iper", mock_get_iper)
    monkeypatch.setattr("lib.title.driver.get_birth", mock_get_birth)
    monkeypatch.setattr("lib.title.driver.get_baptism", mock_get_baptism)
    monkeypatch.setattr("lib.title.driver.get_death", mock_get_death)
    monkeypatch.setattr("lib.title.driver.nobtitles", mock_nobtitles)
    monkeypatch.setattr("lib.title.driver.get_family", mock_get_family)
    monkeypatch.setattr("lib.title.driver.foi", mock_foi)
    monkeypatch.setattr("lib.title.driver.get_marriage", mock_get_marriage)
    monkeypatch.setattr("lib.title.gutil.spouse", mock_spouse)
    monkeypatch.setattr("lib.title.driver.get_children", mock_get_children)
    monkeypatch.setattr("lib.title.date_mod.od_of_cdate", mock_od_of_cdate)
    monkeypatch.setattr("lib.title.date_mod.cdate_to_dmy_opt", mock_cdate_to_dmy_opt)
    monkeypatch.setattr("lib.title.date_mod.dmy_of_death", mock_dmy_of_death)
    monkeypatch.setattr("lib.title.date_mod.compare_dmy", mock_compare_dmy)

    conf = SimpleNamespace(allowed_titles=[], denied_titles=[], today=Dmy(1, 1, 2000, Precision.SURE, 0))
    base = SimpleNamespace()
    x1 = SimpleNamespace(iper=1)
    x2 = SimpleNamespace(iper=2)
    t1 = SimpleNamespace(t_date_start=None, t_date_end=None)
    t2 = SimpleNamespace(t_date_start=None, t_date_end=None)

    result = title.compare_title_dates(conf, base, (x1, t1), (x2, t2))
    assert result == -1


def test_compare_title_order_t2_greater(monkeypatch):
    t1 = SimpleNamespace(t_nth=1, t_date_start=None, t_date_end=None)
    t2 = SimpleNamespace(t_nth=2, t_date_start=None, t_date_end=None)
    x1 = SimpleNamespace()
    x2 = SimpleNamespace()

    conf = SimpleNamespace()
    base = SimpleNamespace()

    result = title.compare_title_order(conf, base, (x1, t1), (x2, t2))
    assert result == -1


def test_compare_title_order_t1_greater(monkeypatch):
    t1 = SimpleNamespace(t_nth=5, t_date_start=None, t_date_end=None)
    t2 = SimpleNamespace(t_nth=2, t_date_start=None, t_date_end=None)
    x1 = SimpleNamespace()
    x2 = SimpleNamespace()

    conf = SimpleNamespace()
    base = SimpleNamespace()

    result = title.compare_title_order(conf, base, (x1, t1), (x2, t2))
    assert result == 1


def test_compare_title_dates_interval_self_branches(monkeypatch):
    def mock_poi(base, ip):
        return SimpleNamespace(iper=ip)

    def mock_get_iper(p):
        return p.iper

    def mock_get_birth(p):
        if p.iper == 1:
            return CdateGregorian(100)
        elif p.iper == 2:
            return CdateGregorian(200)
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_baptism(p):
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_death(p):
        if p.iper == 1:
            return DeathWithReason(DeathReason.KILLED, CdateGregorian(120))
        elif p.iper == 2:
            return DeathWithReason(DeathReason.KILLED, CdateGregorian(220))
        return SimpleNamespace()

    def mock_nobtitles(base, allowed, denied, p):
        return []

    def mock_get_family(p):
        return []

    def mock_od_of_cdate(cd):
        return None

    def mock_cdate_to_dmy_opt(cd):
        if isinstance(cd, CdateGregorian):
            if cd.value == 100:
                return Dmy(1, 1, 1900, Precision.SURE, 0)
            elif cd.value == 120:
                return Dmy(1, 1, 1920, Precision.SURE, 0)
            elif cd.value == 200:
                return Dmy(1, 1, 1905, Precision.SURE, 0)
            elif cd.value == 220:
                return Dmy(1, 1, 1925, Precision.SURE, 0)
        return None

    def mock_dmy_of_death(death):
        if isinstance(death, DeathWithReason):
            return mock_cdate_to_dmy_opt(death.date)
        return None

    def mock_compare_dmy(d1, d2):
        if d1.year < d2.year:
            return -1
        elif d1.year > d2.year:
            return 1
        if d1.month < d2.month:
            return -1
        elif d1.month > d2.month:
            return 1
        return 0

    monkeypatch.setattr("lib.title.driver.poi", mock_poi)
    monkeypatch.setattr("lib.title.driver.get_iper", mock_get_iper)
    monkeypatch.setattr("lib.title.driver.get_birth", mock_get_birth)
    monkeypatch.setattr("lib.title.driver.get_baptism", mock_get_baptism)
    monkeypatch.setattr("lib.title.driver.get_death", mock_get_death)
    monkeypatch.setattr("lib.title.driver.nobtitles", mock_nobtitles)
    monkeypatch.setattr("lib.title.driver.get_family", mock_get_family)
    monkeypatch.setattr("lib.title.date_mod.od_of_cdate", mock_od_of_cdate)
    monkeypatch.setattr("lib.title.date_mod.cdate_to_dmy_opt", mock_cdate_to_dmy_opt)
    monkeypatch.setattr("lib.title.date_mod.dmy_of_death", mock_dmy_of_death)
    monkeypatch.setattr("lib.title.date_mod.compare_dmy", mock_compare_dmy)

    conf = SimpleNamespace(allowed_titles=[], denied_titles=[], today=Dmy(1, 1, 2000, Precision.SURE, 0))
    base = SimpleNamespace()
    x1 = SimpleNamespace(iper=1)
    x2 = SimpleNamespace(iper=2)
    t1 = SimpleNamespace(t_date_start=None, t_date_end=None)
    t2 = SimpleNamespace(t_date_start=None, t_date_end=None)

    result = title.compare_title_dates(conf, base, (x1, t1), (x2, t2))
    assert result in [-1, 1]


def test_compare_title_dates_interval_reverse(monkeypatch):
    def mock_poi(base, ip):
        return SimpleNamespace(iper=ip)

    def mock_get_iper(p):
        return p.iper

    def mock_get_birth(p):
        if p.iper == 1:
            return CdateGregorian(200)
        elif p.iper == 2:
            return CdateGregorian(100)
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_baptism(p):
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_death(p):
        if p.iper == 1:
            return DeathWithReason(DeathReason.KILLED, CdateGregorian(220))
        elif p.iper == 2:
            return DeathWithReason(DeathReason.KILLED, CdateGregorian(120))
        return SimpleNamespace()

    def mock_nobtitles(base, allowed, denied, p):
        return []

    def mock_get_family(p):
        return []

    def mock_od_of_cdate(cd):
        return None

    def mock_cdate_to_dmy_opt(cd):
        if isinstance(cd, CdateGregorian):
            if cd.value == 100:
                return Dmy(1, 1, 1900, Precision.SURE, 0)
            elif cd.value == 120:
                return Dmy(1, 1, 1920, Precision.SURE, 0)
            elif cd.value == 200:
                return Dmy(1, 1, 1905, Precision.SURE, 0)
            elif cd.value == 220:
                return Dmy(1, 1, 1925, Precision.SURE, 0)
        return None

    def mock_dmy_of_death(death):
        if isinstance(death, DeathWithReason):
            return mock_cdate_to_dmy_opt(death.date)
        return None

    def mock_compare_dmy(d1, d2):
        if d1.year < d2.year:
            return -1
        elif d1.year > d2.year:
            return 1
        return 0

    monkeypatch.setattr("lib.title.driver.poi", mock_poi)
    monkeypatch.setattr("lib.title.driver.get_iper", mock_get_iper)
    monkeypatch.setattr("lib.title.driver.get_birth", mock_get_birth)
    monkeypatch.setattr("lib.title.driver.get_baptism", mock_get_baptism)
    monkeypatch.setattr("lib.title.driver.get_death", mock_get_death)
    monkeypatch.setattr("lib.title.driver.nobtitles", mock_nobtitles)
    monkeypatch.setattr("lib.title.driver.get_family", mock_get_family)
    monkeypatch.setattr("lib.title.date_mod.od_of_cdate", mock_od_of_cdate)
    monkeypatch.setattr("lib.title.date_mod.cdate_to_dmy_opt", mock_cdate_to_dmy_opt)
    monkeypatch.setattr("lib.title.date_mod.dmy_of_death", mock_dmy_of_death)
    monkeypatch.setattr("lib.title.date_mod.compare_dmy", mock_compare_dmy)

    conf = SimpleNamespace(allowed_titles=[], denied_titles=[], today=Dmy(1, 1, 2000, Precision.SURE, 0))
    base = SimpleNamespace()
    x1 = SimpleNamespace(iper=1)
    x2 = SimpleNamespace(iper=2)
    t1 = SimpleNamespace(t_date_start=None, t_date_end=None)
    t2 = SimpleNamespace(t_date_start=None, t_date_end=None)

    result = title.compare_title_dates(conf, base, (x1, t1), (x2, t2))
    assert result in [-1, 1]


def test_compare_title_dates_second_child_has_none(monkeypatch):
    def mock_poi(base, ip):
        return SimpleNamespace(iper=ip)

    def mock_get_iper(p):
        return p.iper

    def mock_get_birth(p):
        if p.iper == 2:
            return CdateGregorian(100)
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_baptism(p):
        from lib.adef import CdateNone
        return CdateNone()

    def mock_get_death(p):
        return SimpleNamespace()

    def mock_nobtitles(base, allowed, denied, p):
        return []

    def mock_get_family(p):
        if p.iper == 2:
            return [10]
        return []

    def mock_foi(base, ifam):
        return SimpleNamespace(ifam=ifam)

    def mock_get_marriage(fam):
        from lib.adef import CdateNone
        return CdateNone()

    def mock_spouse(iper, fam):
        return 3

    def mock_get_children(fam):
        return [5]

    def mock_od_of_cdate(cd):
        return None

    def mock_cdate_to_dmy_opt(cd):
        if isinstance(cd, CdateGregorian):
            if cd.value == 100:
                return Dmy(1, 1, 1900, Precision.SURE, 0)
        return None

    def mock_dmy_of_death(death):
        return None

    def mock_compare_dmy(d1, d2):
        if d1.year < d2.year:
            return -1
        elif d1.year > d2.year:
            return 1
        return 0

    monkeypatch.setattr("lib.title.driver.poi", mock_poi)
    monkeypatch.setattr("lib.title.driver.get_iper", mock_get_iper)
    monkeypatch.setattr("lib.title.driver.get_birth", mock_get_birth)
    monkeypatch.setattr("lib.title.driver.get_baptism", mock_get_baptism)
    monkeypatch.setattr("lib.title.driver.get_death", mock_get_death)
    monkeypatch.setattr("lib.title.driver.nobtitles", mock_nobtitles)
    monkeypatch.setattr("lib.title.driver.get_family", mock_get_family)
    monkeypatch.setattr("lib.title.driver.foi", mock_foi)
    monkeypatch.setattr("lib.title.driver.get_marriage", mock_get_marriage)
    monkeypatch.setattr("lib.title.gutil.spouse", mock_spouse)
    monkeypatch.setattr("lib.title.driver.get_children", mock_get_children)
    monkeypatch.setattr("lib.title.date_mod.od_of_cdate", mock_od_of_cdate)
    monkeypatch.setattr("lib.title.date_mod.cdate_to_dmy_opt", mock_cdate_to_dmy_opt)
    monkeypatch.setattr("lib.title.date_mod.dmy_of_death", mock_dmy_of_death)
    monkeypatch.setattr("lib.title.date_mod.compare_dmy", mock_compare_dmy)

    conf = SimpleNamespace(allowed_titles=[], denied_titles=[], today=Dmy(1, 1, 2000, Precision.SURE, 0))
    base = SimpleNamespace()
    x1 = SimpleNamespace(iper=1)
    x2 = SimpleNamespace(iper=2)
    t1 = SimpleNamespace(t_date_start=None, t_date_end=None)
    t2 = SimpleNamespace(t_date_start=None, t_date_end=None)

    result = title.compare_title_dates(conf, base, (x1, t1), (x2, t2))
    assert result == 1
