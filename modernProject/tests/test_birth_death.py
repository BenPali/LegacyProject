import pytest
from types import SimpleNamespace
from modernProject.lib import birth_death, gwdef, date as date_mod, pqueue
from modernProject.lib.adef import Precision, Calendar, Dmy


def test_get_k_from_env():
    conf = SimpleNamespace(env={"k": "15"}, base_env={})
    assert birth_death.get_k(conf) == 15


def test_get_k_from_base_env():
    conf = SimpleNamespace(env={}, base_env={"latest_event": "25"})
    assert birth_death.get_k(conf) == 25


def test_get_k_default():
    conf = SimpleNamespace(env={}, base_env={})
    assert birth_death.get_k(conf) == 20


def test_get_k_invalid_base_env():
    conf = SimpleNamespace(env={}, base_env={"latest_event": "invalid"})
    assert birth_death.get_k(conf) == 20


def test_select_empty():
    class TestComparator(pqueue.OrderedType):
        def leq(self, a, b):
            return a[1].year <= b[1].year

    pq_class = lambda: pqueue.PQueue.create(TestComparator())
    nb_of = lambda base: 0
    iterator = lambda base: []
    get = lambda base, i: None
    get_date = lambda x: None
    conf = SimpleNamespace(env={}, base_env={})
    base = SimpleNamespace()

    result, length = birth_death.select(pq_class, nb_of, iterator, get, get_date, conf, base)
    assert result == []
    assert length == 0


def test_select_with_dates():
    class TestComparator(pqueue.OrderedType):
        def leq(self, a, b):
            return a[1].year <= b[1].year

    pq_class = lambda: pqueue.PQueue.create(TestComparator())
    nb_of = lambda base: 3
    iterator = lambda base: [0, 1, 2]

    persons = [
        SimpleNamespace(name="p0"),
        SimpleNamespace(name="p1"),
        SimpleNamespace(name="p2")
    ]

    get = lambda base, i: persons[i]

    dates = [
        SimpleNamespace(
            dmy=Dmy(day=1, month=1, year=1990, prec=Precision.SURE, delta=0),
            cal=Calendar.GREGORIAN
        ),
        SimpleNamespace(
            dmy=Dmy(day=1, month=1, year=1985, prec=Precision.SURE, delta=0),
            cal=Calendar.GREGORIAN
        ),
        SimpleNamespace(
            dmy=Dmy(day=1, month=1, year=1995, prec=Precision.SURE, delta=0),
            cal=Calendar.GREGORIAN
        )
    ]

    get_date = lambda x: dates[persons.index(x)]

    conf = SimpleNamespace(env={}, base_env={})
    base = SimpleNamespace()

    result, length = birth_death.select(pq_class, nb_of, iterator, get, get_date, conf, base)
    assert length == 3
    assert len(result) == 3


def test_select_with_limit():
    class TestComparator(pqueue.OrderedType):
        def leq(self, a, b):
            return a[1].year <= b[1].year

    pq_class = lambda: pqueue.PQueue.create(TestComparator())
    nb_of = lambda base: 5
    iterator = lambda base: [0, 1, 2, 3, 4]

    persons = [SimpleNamespace(name=f"p{i}") for i in range(5)]
    get = lambda base, i: persons[i]

    dates = [
        SimpleNamespace(
            dmy=Dmy(day=1, month=1, year=1990 + i, prec=Precision.SURE, delta=0),
            cal=Calendar.GREGORIAN
        ) for i in range(5)
    ]

    get_date = lambda x: dates[persons.index(x)]

    conf = SimpleNamespace(env={"k": "2"}, base_env={})
    base = SimpleNamespace()

    result, length = birth_death.select(pq_class, nb_of, iterator, get, get_date, conf, base)
    assert length == 2


def test_select_with_ref_date():
    class TestComparator(pqueue.OrderedType):
        def leq(self, a, b):
            return a[1].year <= b[1].year

    pq_class = lambda: pqueue.PQueue.create(TestComparator())
    nb_of = lambda base: 3
    iterator = lambda base: [0, 1, 2]

    persons = [SimpleNamespace(name=f"p{i}") for i in range(3)]
    get = lambda base, i: persons[i]

    dates = [
        SimpleNamespace(
            dmy=Dmy(day=1, month=1, year=1990, prec=Precision.SURE, delta=0),
            cal=Calendar.GREGORIAN
        ),
        SimpleNamespace(
            dmy=Dmy(day=1, month=1, year=1995, prec=Precision.SURE, delta=0),
            cal=Calendar.GREGORIAN
        ),
        SimpleNamespace(
            dmy=Dmy(day=1, month=1, year=2000, prec=Precision.SURE, delta=0),
            cal=Calendar.GREGORIAN
        )
    ]

    get_date = lambda x: dates[persons.index(x)]

    conf = SimpleNamespace(env={"by": "1996", "bm": 1, "bd": 1}, base_env={})
    base = SimpleNamespace()

    result, length = birth_death.select(pq_class, nb_of, iterator, get, get_date, conf, base)
    assert length == 2


def test_select_with_tuple_date():
    class TestComparator(pqueue.OrderedType):
        def leq(self, a, b):
            return a[1].year <= b[1].year

    pq_class = lambda: pqueue.PQueue.create(TestComparator())
    nb_of = lambda base: 1
    iterator = lambda base: [0]

    persons = [SimpleNamespace(name="p0")]
    get = lambda base, i: persons[i]

    dmy = Dmy(day=1, month=1, year=1990, prec=Precision.SURE, delta=0)
    get_date = lambda x: (dmy, Calendar.GREGORIAN)

    conf = SimpleNamespace(env={}, base_env={})
    base = SimpleNamespace()

    result, length = birth_death.select(pq_class, nb_of, iterator, get, get_date, conf, base)
    assert length == 1


def test_select_person_latest(monkeypatch):
    def mock_nb_of_persons(base):
        return 2

    def mock_ipers(base):
        return [0, 1]

    def mock_poi(base, i):
        return SimpleNamespace(name=f"p{i}", iper=i)

    monkeypatch.setattr("modernProject.lib.birth_death.driver.nb_of_persons", mock_nb_of_persons)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.ipers", mock_ipers)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.poi", mock_poi)

    def get_date(p):
        year = 1990 if p.iper == 0 else 1995
        return SimpleNamespace(
            dmy=Dmy(day=1, month=1, year=year, prec=Precision.SURE, delta=0),
            cal=Calendar.GREGORIAN
        )

    conf = SimpleNamespace(env={}, base_env={})
    base = SimpleNamespace()

    result, length = birth_death.select_person(conf, base, get_date, False)
    assert length == 2


def test_select_person_oldest(monkeypatch):
    def mock_nb_of_persons(base):
        return 2

    def mock_ipers(base):
        return [0, 1]

    def mock_poi(base, i):
        return SimpleNamespace(name=f"p{i}", iper=i)

    monkeypatch.setattr("modernProject.lib.birth_death.driver.nb_of_persons", mock_nb_of_persons)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.ipers", mock_ipers)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.poi", mock_poi)

    def get_date(p):
        year = 1990 if p.iper == 0 else 1995
        return SimpleNamespace(
            dmy=Dmy(day=1, month=1, year=year, prec=Precision.SURE, delta=0),
            cal=Calendar.GREGORIAN
        )

    conf = SimpleNamespace(env={}, base_env={})
    base = SimpleNamespace()

    result, length = birth_death.select_person(conf, base, get_date, True)
    assert length == 2


def test_select_family_latest(monkeypatch):
    def mock_nb_of_families(base):
        return 2

    def mock_ifams(base):
        return [0, 1]

    def mock_foi(base, i):
        return SimpleNamespace(name=f"f{i}", ifam=i)

    monkeypatch.setattr("modernProject.lib.birth_death.driver.nb_of_families", mock_nb_of_families)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.ifams", mock_ifams)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.foi", mock_foi)

    def get_date(f):
        year = 1990 if f.ifam == 0 else 1995
        return SimpleNamespace(
            dmy=Dmy(day=1, month=1, year=year, prec=Precision.SURE, delta=0),
            cal=Calendar.GREGORIAN
        )

    conf = SimpleNamespace(env={}, base_env={})
    base = SimpleNamespace()

    result, length = birth_death.select_family(conf, base, get_date, False)
    assert length == 2


def test_select_family_oldest(monkeypatch):
    def mock_nb_of_families(base):
        return 2

    def mock_ifams(base):
        return [0, 1]

    def mock_foi(base, i):
        return SimpleNamespace(name=f"f{i}", ifam=i)

    monkeypatch.setattr("modernProject.lib.birth_death.driver.nb_of_families", mock_nb_of_families)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.ifams", mock_ifams)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.foi", mock_foi)

    def get_date(f):
        year = 1990 if f.ifam == 0 else 1995
        return SimpleNamespace(
            dmy=Dmy(day=1, month=1, year=year, prec=Precision.SURE, delta=0),
            cal=Calendar.GREGORIAN
        )

    conf = SimpleNamespace(env={}, base_env={})
    base = SimpleNamespace()

    result, length = birth_death.select_family(conf, base, get_date, True)
    assert length == 2


def test_death_date(monkeypatch):
    def mock_get_death(p):
        from modernProject.lib.adef import CdateGregorian
        return gwdef.DeathWithReason(gwdef.DeathReason.KILLED, CdateGregorian(123456))

    def mock_date_of_death(death):
        if hasattr(death, 'date'):
            return SimpleNamespace(year=2000)
        return None

    monkeypatch.setattr("modernProject.lib.birth_death.driver.get_death", mock_get_death)
    monkeypatch.setattr("modernProject.lib.birth_death.date_mod.date_of_death", mock_date_of_death)

    p = SimpleNamespace()
    result = birth_death.death_date(p)
    assert result is not None


def test_death_date_none(monkeypatch):
    def mock_get_death(p):
        return gwdef.NotDead()

    def mock_date_of_death(death):
        return None

    monkeypatch.setattr("modernProject.lib.birth_death.driver.get_death", mock_get_death)
    monkeypatch.setattr("modernProject.lib.birth_death.date_mod.date_of_death", mock_date_of_death)

    p = SimpleNamespace()
    result = birth_death.death_date(p)
    assert result is None


def test_make_population_pyramid_basic(monkeypatch):
    def mock_ipers(base):
        return [0, 1, 2, 3]

    def mock_poi(base, i):
        return SimpleNamespace(iper=i)

    def mock_get_sex(p):
        return gwdef.Sex.MALE if p.iper % 2 == 0 else gwdef.Sex.FEMALE

    def mock_get_death(p):
        return gwdef.NotDead()

    def mock_get_birth(p):
        return SimpleNamespace()

    def mock_cdate_to_dmy_opt(cdate):
        return Dmy(day=1, month=1, year=1950, prec=Precision.SURE, delta=0)

    def mock_compare_dmy(d1, d2):
        return -1

    def mock_time_elapsed(d1, d2):
        return SimpleNamespace(year=30, month=0, day=0)

    monkeypatch.setattr("modernProject.lib.birth_death.driver.ipers", mock_ipers)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.poi", mock_poi)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.get_sex", mock_get_sex)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.get_death", mock_get_death)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.get_birth", mock_get_birth)
    monkeypatch.setattr("modernProject.lib.birth_death.date_mod.cdate_to_dmy_opt", mock_cdate_to_dmy_opt)
    monkeypatch.setattr("modernProject.lib.birth_death.date_mod.compare_dmy", mock_compare_dmy)
    monkeypatch.setattr("modernProject.lib.birth_death.date_mod.time_elapsed", mock_time_elapsed)

    conf = SimpleNamespace(env={}, base_env={})
    base = SimpleNamespace()
    at_date = Dmy(day=1, month=1, year=2000, prec=Precision.SURE, delta=0)

    men, wom = birth_death.make_population_pyramid(10, 10, 100, at_date, conf, base)
    assert len(men) == 11
    assert len(wom) == 11
    assert men[3] == 2
    assert wom[3] == 2


def test_make_population_pyramid_neuter(monkeypatch):
    def mock_ipers(base):
        return [0]

    def mock_poi(base, i):
        return SimpleNamespace(iper=i)

    def mock_get_sex(p):
        return gwdef.Sex.NEUTER

    def mock_get_death(p):
        return gwdef.NotDead()

    def mock_get_birth(p):
        return SimpleNamespace()

    monkeypatch.setattr("modernProject.lib.birth_death.driver.ipers", mock_ipers)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.poi", mock_poi)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.get_sex", mock_get_sex)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.get_death", mock_get_death)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.get_birth", mock_get_birth)

    conf = SimpleNamespace(env={}, base_env={})
    base = SimpleNamespace()
    at_date = Dmy(day=1, month=1, year=2000, prec=Precision.SURE, delta=0)

    men, wom = birth_death.make_population_pyramid(10, 10, 100, at_date, conf, base)
    assert sum(men) == 0
    assert sum(wom) == 0


def test_make_population_pyramid_no_birth(monkeypatch):
    def mock_ipers(base):
        return [0]

    def mock_poi(base, i):
        return SimpleNamespace(iper=i)

    def mock_get_sex(p):
        return gwdef.Sex.MALE

    def mock_get_death(p):
        return gwdef.NotDead()

    def mock_get_birth(p):
        return SimpleNamespace()

    def mock_cdate_to_dmy_opt(cdate):
        return None

    monkeypatch.setattr("modernProject.lib.birth_death.driver.ipers", mock_ipers)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.poi", mock_poi)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.get_sex", mock_get_sex)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.get_death", mock_get_death)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.get_birth", mock_get_birth)
    monkeypatch.setattr("modernProject.lib.birth_death.date_mod.cdate_to_dmy_opt", mock_cdate_to_dmy_opt)

    conf = SimpleNamespace(env={}, base_env={})
    base = SimpleNamespace()
    at_date = Dmy(day=1, month=1, year=2000, prec=Precision.SURE, delta=0)

    men, wom = birth_death.make_population_pyramid(10, 10, 100, at_date, conf, base)
    assert sum(men) == 0
    assert sum(wom) == 0


def test_make_population_pyramid_birth_after_at_date(monkeypatch):
    def mock_ipers(base):
        return [0]

    def mock_poi(base, i):
        return SimpleNamespace(iper=i)

    def mock_get_sex(p):
        return gwdef.Sex.MALE

    def mock_get_death(p):
        return gwdef.NotDead()

    def mock_get_birth(p):
        return SimpleNamespace()

    def mock_cdate_to_dmy_opt(cdate):
        return Dmy(day=1, month=1, year=2010, prec=Precision.SURE, delta=0)

    def mock_compare_dmy(d1, d2):
        return 1

    monkeypatch.setattr("modernProject.lib.birth_death.driver.ipers", mock_ipers)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.poi", mock_poi)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.get_sex", mock_get_sex)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.get_death", mock_get_death)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.get_birth", mock_get_birth)
    monkeypatch.setattr("modernProject.lib.birth_death.date_mod.cdate_to_dmy_opt", mock_cdate_to_dmy_opt)
    monkeypatch.setattr("modernProject.lib.birth_death.date_mod.compare_dmy", mock_compare_dmy)

    conf = SimpleNamespace(env={}, base_env={})
    base = SimpleNamespace()
    at_date = Dmy(day=1, month=1, year=2000, prec=Precision.SURE, delta=0)

    men, wom = birth_death.make_population_pyramid(10, 10, 100, at_date, conf, base)
    assert sum(men) == 0
    assert sum(wom) == 0


def test_make_population_pyramid_dont_know_if_dead_under_limit(monkeypatch):
    def mock_ipers(base):
        return [0]

    def mock_poi(base, i):
        return SimpleNamespace(iper=i)

    def mock_get_sex(p):
        return gwdef.Sex.FEMALE

    def mock_get_death(p):
        return gwdef.DontKnowIfDead()

    def mock_get_birth(p):
        return SimpleNamespace()

    def mock_cdate_to_dmy_opt(cdate):
        return Dmy(day=1, month=1, year=1970, prec=Precision.SURE, delta=0)

    def mock_compare_dmy(d1, d2):
        return -1

    def mock_time_elapsed(d1, d2):
        return SimpleNamespace(year=30, month=0, day=0)

    monkeypatch.setattr("modernProject.lib.birth_death.driver.ipers", mock_ipers)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.poi", mock_poi)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.get_sex", mock_get_sex)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.get_death", mock_get_death)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.get_birth", mock_get_birth)
    monkeypatch.setattr("modernProject.lib.birth_death.date_mod.cdate_to_dmy_opt", mock_cdate_to_dmy_opt)
    monkeypatch.setattr("modernProject.lib.birth_death.date_mod.compare_dmy", mock_compare_dmy)
    monkeypatch.setattr("modernProject.lib.birth_death.date_mod.time_elapsed", mock_time_elapsed)

    conf = SimpleNamespace(env={}, base_env={})
    base = SimpleNamespace()
    at_date = Dmy(day=1, month=1, year=2000, prec=Precision.SURE, delta=0)

    men, wom = birth_death.make_population_pyramid(10, 10, 100, at_date, conf, base)
    assert wom[3] == 1


def test_make_population_pyramid_dont_know_if_dead_over_limit(monkeypatch):
    def mock_ipers(base):
        return [0]

    def mock_poi(base, i):
        return SimpleNamespace(iper=i)

    def mock_get_sex(p):
        return gwdef.Sex.FEMALE

    def mock_get_death(p):
        return gwdef.DontKnowIfDead()

    def mock_get_birth(p):
        return SimpleNamespace()

    def mock_cdate_to_dmy_opt(cdate):
        return Dmy(day=1, month=1, year=1800, prec=Precision.SURE, delta=0)

    def mock_compare_dmy(d1, d2):
        return -1

    def mock_time_elapsed(d1, d2):
        return SimpleNamespace(year=200, month=0, day=0)

    monkeypatch.setattr("modernProject.lib.birth_death.driver.ipers", mock_ipers)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.poi", mock_poi)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.get_sex", mock_get_sex)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.get_death", mock_get_death)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.get_birth", mock_get_birth)
    monkeypatch.setattr("modernProject.lib.birth_death.date_mod.cdate_to_dmy_opt", mock_cdate_to_dmy_opt)
    monkeypatch.setattr("modernProject.lib.birth_death.date_mod.compare_dmy", mock_compare_dmy)
    monkeypatch.setattr("modernProject.lib.birth_death.date_mod.time_elapsed", mock_time_elapsed)

    conf = SimpleNamespace(env={}, base_env={})
    base = SimpleNamespace()
    at_date = Dmy(day=1, month=1, year=2000, prec=Precision.SURE, delta=0)

    men, wom = birth_death.make_population_pyramid(10, 10, 100, at_date, conf, base)
    assert sum(wom) == 0


def test_make_population_pyramid_died_before_at_date(monkeypatch):
    def mock_ipers(base):
        return [0]

    def mock_poi(base, i):
        return SimpleNamespace(iper=i)

    def mock_get_sex(p):
        return gwdef.Sex.MALE

    def mock_get_death(p):
        from modernProject.lib.adef import CdateGregorian
        return gwdef.DeathWithReason(gwdef.DeathReason.KILLED, CdateGregorian(123))

    def mock_get_birth(p):
        return SimpleNamespace()

    def mock_cdate_to_dmy_opt(cdate):
        return Dmy(day=1, month=1, year=1970, prec=Precision.SURE, delta=0)

    def mock_compare_dmy(d1, d2):
        if hasattr(d2, 'year'):
            return -1 if d1.year < d2.year else 1
        return -1

    def mock_time_elapsed(d1, d2):
        return SimpleNamespace(year=30, month=0, day=0)

    def mock_dmy_of_death(death):
        if hasattr(death, 'date'):
            return Dmy(day=1, month=1, year=1990, prec=Precision.SURE, delta=0)
        return None

    monkeypatch.setattr("modernProject.lib.birth_death.driver.ipers", mock_ipers)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.poi", mock_poi)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.get_sex", mock_get_sex)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.get_death", mock_get_death)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.get_birth", mock_get_birth)
    monkeypatch.setattr("modernProject.lib.birth_death.date_mod.cdate_to_dmy_opt", mock_cdate_to_dmy_opt)
    monkeypatch.setattr("modernProject.lib.birth_death.date_mod.compare_dmy", mock_compare_dmy)
    monkeypatch.setattr("modernProject.lib.birth_death.date_mod.time_elapsed", mock_time_elapsed)
    monkeypatch.setattr("modernProject.lib.birth_death.date_mod.dmy_of_death", mock_dmy_of_death)

    conf = SimpleNamespace(env={}, base_env={})
    base = SimpleNamespace()
    at_date = Dmy(day=1, month=1, year=2000, prec=Precision.SURE, delta=0)

    men, wom = birth_death.make_population_pyramid(10, 10, 100, at_date, conf, base)
    assert sum(men) == 0


def test_make_population_pyramid_died_after_at_date(monkeypatch):
    def mock_ipers(base):
        return [0]

    def mock_poi(base, i):
        return SimpleNamespace(iper=i)

    def mock_get_sex(p):
        return gwdef.Sex.MALE

    def mock_get_death(p):
        from modernProject.lib.adef import CdateGregorian
        return gwdef.DeathWithReason(gwdef.DeathReason.KILLED, CdateGregorian(456))

    def mock_get_birth(p):
        return SimpleNamespace()

    def mock_cdate_to_dmy_opt(cdate):
        return Dmy(day=1, month=1, year=1970, prec=Precision.SURE, delta=0)

    def mock_compare_dmy(d1, d2):
        if hasattr(d1, 'year') and hasattr(d2, 'year'):
            if d1.year < d2.year:
                return -1
            elif d1.year > d2.year:
                return 1
            return 0
        return -1

    def mock_time_elapsed(d1, d2):
        return SimpleNamespace(year=30, month=0, day=0)

    def mock_dmy_of_death(death):
        if hasattr(death, 'date'):
            return Dmy(day=1, month=1, year=2010, prec=Precision.SURE, delta=0)
        return None

    monkeypatch.setattr("modernProject.lib.birth_death.driver.ipers", mock_ipers)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.poi", mock_poi)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.get_sex", mock_get_sex)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.get_death", mock_get_death)
    monkeypatch.setattr("modernProject.lib.birth_death.driver.get_birth", mock_get_birth)
    monkeypatch.setattr("modernProject.lib.birth_death.date_mod.cdate_to_dmy_opt", mock_cdate_to_dmy_opt)
    monkeypatch.setattr("modernProject.lib.birth_death.date_mod.compare_dmy", mock_compare_dmy)
    monkeypatch.setattr("modernProject.lib.birth_death.date_mod.time_elapsed", mock_time_elapsed)
    monkeypatch.setattr("modernProject.lib.birth_death.date_mod.dmy_of_death", mock_dmy_of_death)

    conf = SimpleNamespace(env={}, base_env={})
    base = SimpleNamespace()
    at_date = Dmy(day=1, month=1, year=2000, prec=Precision.SURE, delta=0)

    men, wom = birth_death.make_population_pyramid(10, 10, 100, at_date, conf, base)
    assert men[3] == 1
