import pytest
from dataclasses import dataclass
from typing import Optional
from lib import stats
from lib.adef import Dmy, Precision, CdateDate, DateGreg, Calendar, CdateNone
from lib.gwdef import Sex, Death, NotDead, DeathWithReason, DeathReason


@dataclass
class MockPerson:
    iper: int
    first_name: str
    surname: str
    sex: any
    birth: any
    death: any
    parents: Optional[int] = None


@dataclass
class MockCouple:
    father: int
    mother: int


class MockBase:
    def __init__(self):
        self.persons_dict = {}
        self.families_dict = {}

    def add_person(self, p: MockPerson):
        self.persons_dict[p.iper] = p

    def add_family(self, ifam: int, cpl: MockCouple):
        self.families_dict[ifam] = cpl

    def poi(self, iper: int) -> Optional[MockPerson]:
        return self.persons_dict.get(iper)

    def foi(self, ifam: int) -> Optional[MockCouple]:
        return self.families_dict.get(ifam)

    def get_first_name(self, p: MockPerson) -> str:
        return p.first_name

    def get_surname(self, p: MockPerson) -> str:
        return p.surname

    def p_first_name(self, p: MockPerson) -> str:
        return p.first_name

    def p_surname(self, p: MockPerson) -> str:
        return p.surname

    def get_occ(self, p: MockPerson) -> int:
        return 0

    def persons(self):
        return list(self.persons_dict.values())


def test_stats_dataclass():
    s = stats.Stats()
    assert s.men == 0
    assert s.women == 0
    assert s.neutre == 0
    assert s.noname == 0
    assert s.oldest_father == (0, None)
    assert s.oldest_mother == (0, None)
    assert s.youngest_father == (1000, None)
    assert s.youngest_mother == (1000, None)
    assert s.oldest_dead == (0, None)
    assert s.oldest_still_alive == (0, None)


def test_birth_year_with_sure_precision():
    birth_date = DateGreg(
        dmy=Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=0),
        calendar=Calendar.GREGORIAN
    )
    p = MockPerson(
        iper=1, first_name="John", surname="Doe",
        sex=Sex.MALE, birth=CdateDate(date=birth_date), death=Death()
    )
    assert stats.birth_year(p) == 1990


def test_birth_year_with_about_precision():
    birth_date = DateGreg(
        dmy=Dmy(day=15, month=6, year=1990, prec=Precision.ABOUT, delta=0),
        calendar=Calendar.GREGORIAN
    )
    p = MockPerson(
        iper=1, first_name="John", surname="Doe",
        sex=Sex.MALE, birth=CdateDate(date=birth_date), death=Death()
    )
    assert stats.birth_year(p) is None


def test_birth_year_no_birth():
    p = MockPerson(
        iper=1, first_name="John", surname="Doe",
        sex=Sex.MALE, birth=CdateNone(), death=Death()
    )
    assert stats.birth_year(p) is None


def test_death_year_with_death():
    death_date = DateGreg(
        dmy=Dmy(day=20, month=12, year=2050, prec=Precision.SURE, delta=0),
        calendar=Calendar.GREGORIAN
    )
    p = MockPerson(
        iper=1, first_name="John", surname="Doe",
        sex=Sex.MALE, birth=CdateNone(),
        death=DeathWithReason(reason=DeathReason.UNSPECIFIED, date=CdateDate(date=death_date))
    )
    assert stats.death_year(2024, p) == 2050


def test_death_year_not_dead():
    p = MockPerson(
        iper=1, first_name="John", surname="Doe",
        sex=Sex.MALE, birth=CdateNone(), death=NotDead()
    )
    assert stats.death_year(2024, p) == 2024


def test_death_year_with_about_precision():
    death_date = DateGreg(
        dmy=Dmy(day=20, month=12, year=2050, prec=Precision.ABOUT, delta=0),
        calendar=Calendar.GREGORIAN
    )
    p = MockPerson(
        iper=1, first_name="John", surname="Doe",
        sex=Sex.MALE, birth=CdateNone(),
        death=DeathWithReason(reason=DeathReason.UNSPECIFIED, date=CdateDate(date=death_date))
    )
    assert stats.death_year(2024, p) is None


def test_death_year_no_death_info():
    p = MockPerson(
        iper=1, first_name="John", surname="Doe",
        sex=Sex.MALE, birth=CdateNone(), death=Death()
    )
    assert stats.death_year(2024, p) is None


def test_death_year_no_death_attribute():
    @dataclass
    class PersonWithoutDeath:
        iper: int
        first_name: str
    p = PersonWithoutDeath(iper=1, first_name="Test")
    assert stats.death_year(2024, p) is None


def test_update_stats_counts_men():
    base = MockBase()
    s = stats.Stats()
    p = MockPerson(
        iper=1, first_name="John", surname="Doe",
        sex=Sex.MALE, birth=CdateNone(), death=Death()
    )
    stats.update_stats(base, 2024, s, p)
    assert s.men == 1
    assert s.women == 0
    assert s.neutre == 0


def test_update_stats_counts_women():
    base = MockBase()
    s = stats.Stats()
    p = MockPerson(
        iper=1, first_name="Jane", surname="Doe",
        sex=Sex.FEMALE, birth=CdateNone(), death=Death()
    )
    stats.update_stats(base, 2024, s, p)
    assert s.men == 0
    assert s.women == 1
    assert s.neutre == 0


def test_update_stats_counts_neuter():
    base = MockBase()
    s = stats.Stats()
    p = MockPerson(
        iper=1, first_name="Pat", surname="Doe",
        sex=Sex.NEUTER, birth=CdateNone(), death=Death()
    )
    stats.update_stats(base, 2024, s, p)
    assert s.men == 0
    assert s.women == 0
    assert s.neutre == 1


def test_update_stats_counts_noname():
    base = MockBase()
    s = stats.Stats()
    p = MockPerson(
        iper=1, first_name="?", surname="?",
        sex=Sex.MALE, birth=CdateNone(), death=Death()
    )
    stats.update_stats(base, 2024, s, p)
    assert s.noname == 1


def test_update_stats_oldest_dead():
    base = MockBase()
    s = stats.Stats()
    birth_date = DateGreg(
        dmy=Dmy(day=1, month=1, year=1900, prec=Precision.SURE, delta=0),
        calendar=Calendar.GREGORIAN
    )
    death_date = DateGreg(
        dmy=Dmy(day=1, month=1, year=2000, prec=Precision.SURE, delta=0),
        calendar=Calendar.GREGORIAN
    )
    p = MockPerson(
        iper=1, first_name="Old", surname="Person",
        sex=Sex.MALE,
        birth=CdateDate(date=birth_date),
        death=DeathWithReason(reason=DeathReason.UNSPECIFIED, date=CdateDate(date=death_date))
    )
    stats.update_stats(base, 2024, s, p)
    assert s.oldest_dead[0] == 100
    assert s.oldest_dead[1] == p


def test_update_stats_oldest_still_alive():
    base = MockBase()
    s = stats.Stats()
    birth_date = DateGreg(
        dmy=Dmy(day=1, month=1, year=1940, prec=Precision.SURE, delta=0),
        calendar=Calendar.GREGORIAN
    )
    p = MockPerson(
        iper=1, first_name="Alive", surname="Person",
        sex=Sex.FEMALE,
        birth=CdateDate(date=birth_date),
        death=NotDead()
    )
    stats.update_stats(base, 2024, s, p)
    assert s.oldest_still_alive[0] == 84
    assert s.oldest_still_alive[1] == p


def test_update_stats_oldest_father():
    base = MockBase()
    birth_father = DateGreg(
        dmy=Dmy(day=1, month=1, year=1950, prec=Precision.SURE, delta=0),
        calendar=Calendar.GREGORIAN
    )
    birth_child = DateGreg(
        dmy=Dmy(day=1, month=1, year=2000, prec=Precision.SURE, delta=0),
        calendar=Calendar.GREGORIAN
    )
    father = MockPerson(
        iper=1, first_name="Father", surname="Doe",
        sex=Sex.MALE, birth=CdateDate(date=birth_father), death=Death()
    )
    mother = MockPerson(
        iper=2, first_name="Mother", surname="Doe",
        sex=Sex.FEMALE, birth=CdateNone(), death=Death()
    )
    child = MockPerson(
        iper=3, first_name="Child", surname="Doe",
        sex=Sex.MALE, birth=CdateDate(date=birth_child), death=Death(),
        parents=1
    )
    base.add_person(father)
    base.add_person(mother)
    base.add_person(child)
    base.add_family(1, MockCouple(father=1, mother=2))

    s = stats.Stats()
    stats.update_stats(base, 2024, s, child)
    assert s.oldest_father[0] == 50
    assert s.oldest_father[1] == father


def test_update_stats_youngest_father():
    base = MockBase()
    birth_father = DateGreg(
        dmy=Dmy(day=1, month=1, year=1998, prec=Precision.SURE, delta=0),
        calendar=Calendar.GREGORIAN
    )
    birth_child = DateGreg(
        dmy=Dmy(day=1, month=1, year=2015, prec=Precision.SURE, delta=0),
        calendar=Calendar.GREGORIAN
    )
    father = MockPerson(
        iper=1, first_name="Father", surname="Young",
        sex=Sex.MALE, birth=CdateDate(date=birth_father), death=Death()
    )
    mother = MockPerson(
        iper=2, first_name="Mother", surname="Young",
        sex=Sex.FEMALE, birth=CdateNone(), death=Death()
    )
    child = MockPerson(
        iper=3, first_name="Child", surname="Young",
        sex=Sex.MALE, birth=CdateDate(date=birth_child), death=Death(),
        parents=1
    )
    base.add_person(father)
    base.add_person(mother)
    base.add_person(child)
    base.add_family(1, MockCouple(father=1, mother=2))

    s = stats.Stats()
    stats.update_stats(base, 2024, s, child)
    assert s.youngest_father[0] == 17
    assert s.youngest_father[1] == father


def test_update_stats_oldest_mother():
    base = MockBase()
    birth_mother = DateGreg(
        dmy=Dmy(day=1, month=1, year=1960, prec=Precision.SURE, delta=0),
        calendar=Calendar.GREGORIAN
    )
    birth_child = DateGreg(
        dmy=Dmy(day=1, month=1, year=2005, prec=Precision.SURE, delta=0),
        calendar=Calendar.GREGORIAN
    )
    father = MockPerson(
        iper=1, first_name="Father", surname="Smith",
        sex=Sex.MALE, birth=CdateNone(), death=Death()
    )
    mother = MockPerson(
        iper=2, first_name="Mother", surname="Smith",
        sex=Sex.FEMALE, birth=CdateDate(date=birth_mother), death=Death()
    )
    child = MockPerson(
        iper=3, first_name="Child", surname="Smith",
        sex=Sex.FEMALE, birth=CdateDate(date=birth_child), death=Death(),
        parents=1
    )
    base.add_person(father)
    base.add_person(mother)
    base.add_person(child)
    base.add_family(1, MockCouple(father=1, mother=2))

    s = stats.Stats()
    stats.update_stats(base, 2024, s, child)
    assert s.oldest_mother[0] == 45
    assert s.oldest_mother[1] == mother


def test_update_stats_youngest_mother():
    base = MockBase()
    birth_mother = DateGreg(
        dmy=Dmy(day=1, month=1, year=1997, prec=Precision.SURE, delta=0),
        calendar=Calendar.GREGORIAN
    )
    birth_child = DateGreg(
        dmy=Dmy(day=1, month=1, year=2013, prec=Precision.SURE, delta=0),
        calendar=Calendar.GREGORIAN
    )
    father = MockPerson(
        iper=1, first_name="Father", surname="Jones",
        sex=Sex.MALE, birth=CdateNone(), death=Death()
    )
    mother = MockPerson(
        iper=2, first_name="Mother", surname="Jones",
        sex=Sex.FEMALE, birth=CdateDate(date=birth_mother), death=Death()
    )
    child = MockPerson(
        iper=3, first_name="Child", surname="Jones",
        sex=Sex.FEMALE, birth=CdateDate(date=birth_child), death=Death(),
        parents=1
    )
    base.add_person(father)
    base.add_person(mother)
    base.add_person(child)
    base.add_family(1, MockCouple(father=1, mother=2))

    s = stats.Stats()
    stats.update_stats(base, 2024, s, child)
    assert s.youngest_mother[0] == 16
    assert s.youngest_mother[1] == mother


def test_stat_base():
    base = MockBase()
    birth_date = DateGreg(
        dmy=Dmy(day=1, month=1, year=1990, prec=Precision.SURE, delta=0),
        calendar=Calendar.GREGORIAN
    )
    p1 = MockPerson(
        iper=1, first_name="John", surname="Doe",
        sex=Sex.MALE, birth=CdateDate(date=birth_date), death=Death()
    )
    p2 = MockPerson(
        iper=2, first_name="Jane", surname="Doe",
        sex=Sex.FEMALE, birth=CdateNone(), death=Death()
    )
    base.add_person(p1)
    base.add_person(p2)

    s = stats.stat_base(base)
    assert s.men == 1
    assert s.women == 1
    assert s.neutre == 0


def test_print_stats(capsys):
    base = MockBase()
    s = stats.Stats(men=10, women=15, neutre=2, noname=1)
    stats.print_stats(base, s)
    captured = capsys.readouterr()
    assert "10 men" in captured.out
    assert "15 women" in captured.out
    assert "2 unknown sex" in captured.out
    assert "1 unnamed" in captured.out


def test_print_stats_with_persons(capsys):
    base = MockBase()
    birth_date = DateGreg(
        dmy=Dmy(day=1, month=1, year=1900, prec=Precision.SURE, delta=0),
        calendar=Calendar.GREGORIAN
    )
    death_date = DateGreg(
        dmy=Dmy(day=1, month=1, year=2000, prec=Precision.SURE, delta=0),
        calendar=Calendar.GREGORIAN
    )
    p = MockPerson(
        iper=1, first_name="Test", surname="Person",
        sex=Sex.MALE,
        birth=CdateDate(date=birth_date),
        death=DeathWithReason(reason=DeathReason.UNSPECIFIED, date=CdateDate(date=death_date))
    )
    base.add_person(p)
    s = stats.Stats(
        men=1,
        oldest_dead=(100, p)
    )
    stats.print_stats(base, s)
    captured = capsys.readouterr()
    assert "1 men" in captured.out
    assert "Oldest:" in captured.out
    assert "100" in captured.out


def test_print_stats_with_none_persons(capsys):
    base = MockBase()
    s = stats.Stats(
        men=5,
        women=3,
        oldest_still_alive=(50, None),
        youngest_father=(25, None),
        youngest_mother=(22, None),
        oldest_father=(60, None),
        oldest_mother=(55, None)
    )
    stats.print_stats(base, s)
    captured = capsys.readouterr()
    assert "5 men" in captured.out
    assert "3 women" in captured.out
    assert "Oldest still alive: N/A, 50" in captured.out
    assert "Youngest father: N/A, 25" in captured.out
    assert "Youngest mother: N/A, 22" in captured.out
    assert "Oldest father: N/A, 60" in captured.out
    assert "Oldest mother: N/A, 55" in captured.out


def test_print_stats_all_categories(capsys):
    base = MockBase()
    birth_date = DateGreg(
        dmy=Dmy(day=1, month=1, year=1950, prec=Precision.SURE, delta=0),
        calendar=Calendar.GREGORIAN
    )
    p_alive = MockPerson(
        iper=1, first_name="Alive", surname="Person",
        sex=Sex.MALE, birth=CdateDate(date=birth_date), death=NotDead()
    )
    p_father_young = MockPerson(
        iper=2, first_name="Young", surname="Dad",
        sex=Sex.MALE, birth=CdateDate(date=birth_date), death=Death()
    )
    p_mother_young = MockPerson(
        iper=3, first_name="Young", surname="Mom",
        sex=Sex.FEMALE, birth=CdateDate(date=birth_date), death=Death()
    )
    p_father_old = MockPerson(
        iper=4, first_name="Old", surname="Dad",
        sex=Sex.MALE, birth=CdateDate(date=birth_date), death=Death()
    )
    p_mother_old = MockPerson(
        iper=5, first_name="Old", surname="Mom",
        sex=Sex.FEMALE, birth=CdateDate(date=birth_date), death=Death()
    )
    base.add_person(p_alive)
    base.add_person(p_father_young)
    base.add_person(p_mother_young)
    base.add_person(p_father_old)
    base.add_person(p_mother_old)
    s = stats.Stats(
        men=3,
        women=2,
        oldest_still_alive=(74, p_alive),
        youngest_father=(18, p_father_young),
        youngest_mother=(16, p_mother_young),
        oldest_father=(65, p_father_old),
        oldest_mother=(55, p_mother_old)
    )
    stats.print_stats(base, s)
    captured = capsys.readouterr()
    assert "3 men" in captured.out
    assert "2 women" in captured.out
    assert "Oldest still alive: Alive.0 Person, 74" in captured.out
    assert "Youngest father: Young.0 Dad, 18" in captured.out
    assert "Youngest mother: Young.0 Mom, 16" in captured.out
    assert "Oldest father: Old.0 Dad, 65" in captured.out
    assert "Oldest mother: Old.0 Mom, 55" in captured.out
