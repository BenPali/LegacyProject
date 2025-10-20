import pytest
from dataclasses import dataclass
from typing import Optional, List, Any
from lib import gutil
from lib import adef
from lib.gwdef import Death, DeathWithReason, DeathReason, Buried, Cremated, UnknownBurial


@dataclass
class MockPerson:
    iper: int
    first_name: str
    surname: str
    occ: int
    birth: Any
    baptism: Any
    death: Any
    burial: Any
    titles: List = None

    def __post_init__(self):
        if self.titles is None:
            self.titles = []


@dataclass
class MockCouple:
    father: int
    mother: int


class MockBase:
    def __init__(self):
        self.persons = {}
        self.persons_by_name = {}

    def add_person(self, p: MockPerson):
        self.persons[p.iper] = p
        full_name = f"{p.first_name} {p.surname}"
        if full_name not in self.persons_by_name:
            self.persons_by_name[full_name] = []
        self.persons_by_name[full_name].append(p.iper)

    def poi(self, iper: int) -> MockPerson:
        return self.persons.get(iper)

    def p_first_name(self, p: MockPerson) -> str:
        return p.first_name

    def p_surname(self, p: MockPerson) -> str:
        return p.surname

    def get_occ(self, p: MockPerson) -> int:
        return p.occ

    def get_iper(self, p: MockPerson) -> int:
        return p.iper

    def get_birth(self, p: MockPerson):
        return p.birth

    def get_baptism(self, p: MockPerson):
        return p.baptism

    def get_death(self, p: MockPerson):
        return p.death

    def get_burial(self, p: MockPerson):
        return p.burial

    def get_titles(self, p: MockPerson):
        return p.titles

    def person_of_key(self, first_name: str, surname: str, occ: int) -> Optional[int]:
        for iper, p in self.persons.items():
            if p.first_name == first_name and p.surname == surname and p.occ == occ:
                return iper
        return None

    def persons_of_name(self, full_name: str) -> List[int]:
        return self.persons_by_name.get(full_name, [])

    def person_misc_names(self, p: MockPerson, title_fn) -> List[str]:
        misc = []
        if p.first_name and p.surname:
            misc.append(f"{p.first_name} {p.surname}")
        return misc


def test_father():
    cpl = MockCouple(father=1, mother=2)
    assert gutil.father(cpl) == 1


def test_mother():
    cpl = MockCouple(father=1, mother=2)
    assert gutil.mother(cpl) == 2


def test_couple_simple():
    cpl = gutil.couple(False, 5, 6)
    assert cpl.father == 5
    assert cpl.mother == 6


def test_couple_multi():
    cpl = gutil.couple(True, 7, 8)
    assert cpl.father == 7
    assert cpl.mother == 8


def test_parent_array():
    cpl = adef.couple(10, 20)
    arr = gutil.parent_array(cpl)
    assert arr == [10, 20]


def test_spouse():
    cpl = MockCouple(father=100, mother=200)
    assert gutil.spouse(100, cpl) == 200
    assert gutil.spouse(200, cpl) == 100
    assert gutil.spouse(999, cpl) == 100


def test_designation():
    base = MockBase()
    p = MockPerson(iper=1, first_name="John", surname="Doe", occ=2,
                   birth=None, baptism=None, death=None, burial=None)
    assert gutil.designation(base, p) == "John.2 Doe"


def test_person_is_key_direct_match():
    base = MockBase()
    p = MockPerson(iper=1, first_name="Alice", surname="Smith", occ=0,
                   birth=None, baptism=None, death=None, burial=None)
    base.add_person(p)
    assert gutil.person_is_key(base, p, "Alice Smith")
    assert gutil.person_is_key(base, p, "alice smith")
    assert not gutil.person_is_key(base, p, "Bob Jones")


def test_find_num():
    assert gutil.find_num("abc123def", 3) == (123, 6)
    assert gutil.find_num("abc 456def", 3) == (456, 7)
    assert gutil.find_num("abc", 0) is None
    assert gutil.find_num("123", 0) == (123, 3)


def test_split_key():
    result = gutil.split_key("John.5 Doe", 0)
    assert result is not None
    pos, first_name, occ, surname = result
    assert first_name == "John"
    assert occ == 5
    assert surname == " Doe"

    result = gutil.split_key("Mary.Jane.10 Smith", 0)
    assert result is not None
    pos, first_name, occ, surname = result
    assert first_name == "Mary.Jane"
    assert occ == 10
    assert surname == " Smith"

    result = gutil.split_key("NoOcc Here", 0)
    assert result is None


def test_person_of_string_key():
    base = MockBase()
    p = MockPerson(iper=42, first_name="Bob", surname="Johnson", occ=1,
                   birth=None, baptism=None, death=None, burial=None)
    base.add_person(p)
    assert gutil.person_of_string_key(base, "Bob.1 Johnson") == 42
    assert gutil.person_of_string_key(base, "Bob.2 Johnson") is None
    assert gutil.person_of_string_key(base, "NoMatch") is None


def test_rsplit_key():
    result = gutil.rsplit_key("John.5 Doe")
    assert result == ("John", 5, " Doe")

    result = gutil.rsplit_key("prefix.John.5 Doe")
    assert result == ("prefix.John", 5, " Doe")

    result = gutil.rsplit_key("NoOcc Here")
    assert result is None


def test_person_of_string_dot_key():
    base = MockBase()
    p = MockPerson(iper=99, first_name="Charlie", surname="Brown", occ=3,
                   birth=None, baptism=None, death=None, burial=None)
    base.add_person(p)
    assert gutil.person_of_string_dot_key(base, "Charlie.3 Brown") == 99
    assert gutil.person_of_string_dot_key(base, "Charlie.0 Brown") is None


def test_person_not_a_key_find_all():
    base = MockBase()
    p1 = MockPerson(iper=1, first_name="Emma", surname="Davis", occ=0,
                    birth=None, baptism=None, death=None, burial=None)
    p2 = MockPerson(iper=2, first_name="Emma", surname="Davis", occ=1,
                    birth=None, baptism=None, death=None, burial=None)
    base.add_person(p1)
    base.add_person(p2)
    result = gutil.person_not_a_key_find_all(base, "Emma Davis")
    assert len(result) == 2
    assert 1 in result
    assert 2 in result


def test_person_ht_find_all_with_key():
    base = MockBase()
    p = MockPerson(iper=10, first_name="Frank", surname="Miller", occ=0,
                   birth=None, baptism=None, death=None, burial=None)
    base.add_person(p)
    result = gutil.person_ht_find_all(base, "Frank.0 Miller")
    assert result == [10]


def test_person_ht_find_all_without_key():
    base = MockBase()
    p1 = MockPerson(iper=1, first_name="Grace", surname="Lee", occ=0,
                    birth=None, baptism=None, death=None, burial=None)
    p2 = MockPerson(iper=2, first_name="Grace", surname="Lee", occ=1,
                    birth=None, baptism=None, death=None, burial=None)
    base.add_person(p1)
    base.add_person(p2)
    result = gutil.person_ht_find_all(base, "Grace Lee")
    assert len(result) == 2


def test_find_same_name():
    base = MockBase()
    p1 = MockPerson(iper=1, first_name="Henry", surname="Wilson", occ=0,
                    birth=None, baptism=None, death=None, burial=None)
    p2 = MockPerson(iper=2, first_name="Henry", surname="Wilson", occ=1,
                    birth=None, baptism=None, death=None, burial=None)
    p3 = MockPerson(iper=3, first_name="Henry", surname="Wilson", occ=2,
                    birth=None, baptism=None, death=None, burial=None)
    base.add_person(p1)
    base.add_person(p2)
    base.add_person(p3)
    result = gutil.find_same_name(base, p2)
    assert len(result) == 3
    assert result[0].occ == 0
    assert result[1].occ == 1
    assert result[2].occ == 2


def test_trim_trailing_spaces():
    assert gutil.trim_trailing_spaces("hello") == "hello"
    assert gutil.trim_trailing_spaces("hello   ") == "hello"
    assert gutil.trim_trailing_spaces("hello\t\n\r ") == "hello"
    assert gutil.trim_trailing_spaces("   ") == ""
    assert gutil.trim_trailing_spaces("") == ""
    assert gutil.trim_trailing_spaces("no trailing") == "no trailing"


def test_alphabetic_utf_8():
    assert gutil.alphabetic_utf_8("abc", "abc") == 0
    assert gutil.alphabetic_utf_8("abc", "abd") < 0
    assert gutil.alphabetic_utf_8("abd", "abc") > 0
    assert gutil.alphabetic_utf_8("", "") == 0
    assert gutil.alphabetic_utf_8("", "a") < 0
    assert gutil.alphabetic_utf_8("a", "") > 0


def test_alphabetic_value():
    assert gutil.alphabetic_value('a') == 10 * ord('a')
    assert gutil.alphabetic_value('A') == 10 * ord('A')
    assert gutil.alphabetic_value('?') == 3000


def test_alphabetic_iso_8859_1():
    assert gutil.alphabetic_iso_8859_1("abc", "abc") == 0
    assert gutil.alphabetic_iso_8859_1("abc", "abd") < 0
    assert gutil.alphabetic_iso_8859_1("abd", "abc") > 0


def test_alphabetic():
    assert gutil.alphabetic("test", "test") == 0
    assert gutil.alphabetic("apple", "banana") < 0
    assert gutil.alphabetic("banana", "apple") > 0


def test_alphabetic_order():
    assert gutil.alphabetic_order("alpha", "alpha") == 0
    assert gutil.alphabetic_order("alpha", "beta") < 0
    assert gutil.alphabetic_order("beta", "alpha") > 0


def test_arg_list_of_string():
    assert gutil.arg_list_of_string("one two three") == ["one", "two", "three"]
    assert gutil.arg_list_of_string("one  two   three") == ["one", "two", "three"]
    assert gutil.arg_list_of_string('one "two three" four') == ["one", "two three", "four"]
    assert gutil.arg_list_of_string("one 'two three' four") == ["one", "two three", "four"]
    assert gutil.arg_list_of_string("") == []
    assert gutil.arg_list_of_string("  ") == []
    assert gutil.arg_list_of_string("single") == ["single"]


def test_sort_person_list():
    base = MockBase()
    p1 = MockPerson(iper=1, first_name="Alice", surname="Smith", occ=0,
                    birth=adef.CdateNone(), baptism=adef.CdateNone(),
                    death=Death(), burial=UnknownBurial())
    p2 = MockPerson(iper=2, first_name="Bob", surname="Smith", occ=0,
                    birth=adef.CdateNone(), baptism=adef.CdateNone(),
                    death=Death(), burial=UnknownBurial())
    p3 = MockPerson(iper=3, first_name="Alice", surname="Jones", occ=0,
                    birth=adef.CdateNone(), baptism=adef.CdateNone(),
                    death=Death(), burial=UnknownBurial())
    base.add_person(p1)
    base.add_person(p2)
    base.add_person(p3)
    sort_fn = gutil.sort_person_list(base)
    result = sort_fn([p2, p1, p3])
    assert result[0].iper == 3
    assert result[1].iper == 1
    assert result[2].iper == 2


def test_sort_uniq_person_list():
    base = MockBase()
    p1 = MockPerson(iper=1, first_name="Unique", surname="Person", occ=0,
                    birth=adef.CdateNone(), baptism=adef.CdateNone(),
                    death=Death(), burial=UnknownBurial())
    p2 = MockPerson(iper=2, first_name="Another", surname="Person", occ=0,
                    birth=adef.CdateNone(), baptism=adef.CdateNone(),
                    death=Death(), burial=UnknownBurial())
    base.add_person(p1)
    base.add_person(p2)
    sort_fn = gutil.sort_uniq_person_list(base)
    result = sort_fn([p1, p2, p1, p2])
    assert len(result) == 2


def test_find_free_occ():
    base = MockBase()
    p1 = MockPerson(iper=1, first_name="Test", surname="User", occ=0,
                    birth=None, baptism=None, death=None, burial=None)
    p2 = MockPerson(iper=2, first_name="Test", surname="User", occ=1,
                    birth=None, baptism=None, death=None, burial=None)
    p3 = MockPerson(iper=3, first_name="Test", surname="User", occ=3,
                    birth=None, baptism=None, death=None, burial=None)
    base.add_person(p1)
    base.add_person(p2)
    base.add_person(p3)
    assert gutil.find_free_occ(base, "Test", "User") == 2


def test_find_free_occ_empty():
    base = MockBase()
    assert gutil.find_free_occ(base, "New", "Person") == 0


def test_get_birth_death_date_with_birth_and_death():
    base = MockBase()
    from lib.adef import DateGreg, Dmy, Calendar, Precision
    birth_date = DateGreg(dmy=Dmy(day=1, month=1, year=1990, prec=Precision.SURE, delta=0),
                          calendar=Calendar.GREGORIAN)
    death_date = DateGreg(dmy=Dmy(day=1, month=1, year=2050, prec=Precision.SURE, delta=0),
                          calendar=Calendar.GREGORIAN)
    p = MockPerson(iper=1, first_name="Test", surname="Person", occ=0,
                   birth=adef.CdateDate(date=birth_date),
                   baptism=adef.CdateNone(),
                   death=DeathWithReason(reason=DeathReason.KILLED, date=adef.CdateDate(date=death_date)),
                   burial=UnknownBurial())
    base.add_person(p)
    birth, death, approx = gutil.get_birth_death_date(base, p)
    assert birth is not None
    assert death is not None
    assert approx is False


def test_get_birth_death_date_with_baptism():
    base = MockBase()
    from lib.adef import DateGreg, Dmy, Calendar, Precision
    baptism_date = DateGreg(dmy=Dmy(day=1, month=2, year=1990, prec=Precision.SURE, delta=0),
                            calendar=Calendar.GREGORIAN)
    p = MockPerson(iper=1, first_name="Test", surname="Person", occ=0,
                   birth=adef.CdateNone(),
                   baptism=adef.CdateDate(date=baptism_date),
                   death=Death(),
                   burial=UnknownBurial())
    base.add_person(p)
    birth, death, approx = gutil.get_birth_death_date(base, p)
    assert birth is not None
    assert approx is True


def test_get_birth_death_date_with_burial():
    base = MockBase()
    from lib.adef import DateGreg, Dmy, Calendar, Precision
    burial_date = DateGreg(dmy=Dmy(day=1, month=3, year=2050, prec=Precision.SURE, delta=0),
                           calendar=Calendar.GREGORIAN)
    p = MockPerson(iper=1, first_name="Test", surname="Person", occ=0,
                   birth=adef.CdateNone(),
                   baptism=adef.CdateNone(),
                   death=Death(),
                   burial=Buried(date=adef.CdateDate(date=burial_date)))
    base.add_person(p)
    birth, death, approx = gutil.get_birth_death_date(base, p)
    assert death is not None
    assert approx is True


def test_get_birth_death_date_no_dates():
    base = MockBase()
    p = MockPerson(iper=1, first_name="Test", surname="Person", occ=0,
                   birth=adef.CdateNone(),
                   baptism=adef.CdateNone(),
                   death=Death(),
                   burial=UnknownBurial())
    base.add_person(p)
    birth, death, approx = gutil.get_birth_death_date(base, p)
    assert birth is None
    assert death is None


def test_rsplit_key_with_dot_no_number():
    result = gutil.rsplit_key("John.Smith")
    assert result is None


def test_alphabetic_value_empty_string():
    result = gutil.alphabetic_value("")
    assert result == 0


def test_alphabetic_utf_8_with_accents():
    result = gutil.alphabetic_utf_8("café", "cafe")
    assert result != 0


def test_sort_person_list_with_dates():
    base = MockBase()
    from lib.adef import DateGreg, Dmy, Calendar, Precision
    birth1 = DateGreg(dmy=Dmy(day=1, month=1, year=1990, prec=Precision.SURE, delta=0),
                      calendar=Calendar.GREGORIAN)
    birth2 = DateGreg(dmy=Dmy(day=1, month=1, year=1980, prec=Precision.SURE, delta=0),
                      calendar=Calendar.GREGORIAN)
    death_date = DateGreg(dmy=Dmy(day=1, month=1, year=2050, prec=Precision.SURE, delta=0),
                          calendar=Calendar.GREGORIAN)

    p1 = MockPerson(iper=1, first_name="Alice", surname="Smith", occ=0,
                    birth=adef.CdateDate(date=birth1),
                    baptism=adef.CdateNone(),
                    death=Death(), burial=UnknownBurial())
    p2 = MockPerson(iper=2, first_name="Bob", surname="Smith", occ=0,
                    birth=adef.CdateDate(date=birth2),
                    baptism=adef.CdateNone(),
                    death=Death(), burial=UnknownBurial())
    p3 = MockPerson(iper=3, first_name="Charlie", surname="Smith", occ=0,
                    birth=adef.CdateNone(),
                    baptism=adef.CdateNone(),
                    death=DeathWithReason(reason=DeathReason.KILLED, date=adef.CdateDate(date=death_date)),
                    burial=UnknownBurial())
    base.add_person(p1)
    base.add_person(p2)
    base.add_person(p3)
    sort_fn = gutil.sort_person_list(base)
    result = sort_fn([p1, p2, p3])
    assert result[0].iper == 2
    assert result[1].iper == 1


def test_sort_person_list_birth_vs_death():
    base = MockBase()
    from lib.adef import DateGreg, Dmy, Calendar, Precision
    birth_date = DateGreg(dmy=Dmy(day=1, month=1, year=1990, prec=Precision.SURE, delta=0),
                          calendar=Calendar.GREGORIAN)
    death_date = DateGreg(dmy=Dmy(day=1, month=1, year=1980, prec=Precision.SURE, delta=0),
                          calendar=Calendar.GREGORIAN)

    p1 = MockPerson(iper=1, first_name="Alice", surname="Smith", occ=0,
                    birth=adef.CdateDate(date=birth_date),
                    baptism=adef.CdateNone(),
                    death=Death(), burial=UnknownBurial())
    p2 = MockPerson(iper=2, first_name="Bob", surname="Smith", occ=0,
                    birth=adef.CdateNone(),
                    baptism=adef.CdateNone(),
                    death=DeathWithReason(reason=DeathReason.KILLED, date=adef.CdateDate(date=death_date)),
                    burial=UnknownBurial())
    base.add_person(p1)
    base.add_person(p2)
    sort_fn = gutil.sort_person_list(base)
    result = sort_fn([p1, p2])
    assert result[0].iper == 2


def test_sort_person_list_death_vs_death():
    base = MockBase()
    from lib.adef import DateGreg, Dmy, Calendar, Precision
    death1 = DateGreg(dmy=Dmy(day=1, month=1, year=1980, prec=Precision.SURE, delta=0),
                      calendar=Calendar.GREGORIAN)
    death2 = DateGreg(dmy=Dmy(day=1, month=1, year=1990, prec=Precision.SURE, delta=0),
                      calendar=Calendar.GREGORIAN)

    p1 = MockPerson(iper=1, first_name="Alice", surname="Smith", occ=0,
                    birth=adef.CdateNone(),
                    baptism=adef.CdateNone(),
                    death=DeathWithReason(reason=DeathReason.KILLED, date=adef.CdateDate(date=death1)),
                    burial=UnknownBurial())
    p2 = MockPerson(iper=2, first_name="Bob", surname="Smith", occ=0,
                    birth=adef.CdateNone(),
                    baptism=adef.CdateNone(),
                    death=DeathWithReason(reason=DeathReason.KILLED, date=adef.CdateDate(date=death2)),
                    burial=UnknownBurial())
    base.add_person(p1)
    base.add_person(p2)
    sort_fn = gutil.sort_person_list(base)
    result = sort_fn([p2, p1])
    assert result[0].iper == 1
    assert result[1].iper == 2


def test_sort_person_list_no_dates_vs_with_birth():
    base = MockBase()
    from lib.adef import DateGreg, Dmy, Calendar, Precision
    birth_date = DateGreg(dmy=Dmy(day=1, month=1, year=1990, prec=Precision.SURE, delta=0),
                          calendar=Calendar.GREGORIAN)

    p1 = MockPerson(iper=1, first_name="Test", surname="Person", occ=0,
                    birth=adef.CdateNone(),
                    baptism=adef.CdateNone(),
                    death=Death(), burial=UnknownBurial())
    p2 = MockPerson(iper=2, first_name="Test", surname="Person", occ=1,
                    birth=adef.CdateDate(date=birth_date),
                    baptism=adef.CdateNone(),
                    death=Death(), burial=UnknownBurial())
    base.add_person(p1)
    base.add_person(p2)
    sort_fn = gutil.sort_person_list(base)
    result = sort_fn([p2, p1])
    assert result[0].iper == 1
    assert result[1].iper == 2


def test_sort_person_list_no_dates_vs_with_death():
    base = MockBase()
    from lib.adef import DateGreg, Dmy, Calendar, Precision
    death_date = DateGreg(dmy=Dmy(day=1, month=1, year=1990, prec=Precision.SURE, delta=0),
                          calendar=Calendar.GREGORIAN)

    p1 = MockPerson(iper=1, first_name="Test", surname="Person", occ=0,
                    birth=adef.CdateNone(),
                    baptism=adef.CdateNone(),
                    death=Death(), burial=UnknownBurial())
    p2 = MockPerson(iper=2, first_name="Test", surname="Person", occ=1,
                    birth=adef.CdateNone(),
                    baptism=adef.CdateNone(),
                    death=DeathWithReason(reason=DeathReason.KILLED, date=adef.CdateDate(date=death_date)),
                    burial=UnknownBurial())
    base.add_person(p1)
    base.add_person(p2)
    sort_fn = gutil.sort_person_list(base)
    result = sort_fn([p2, p1])
    assert result[0].iper == 1
    assert result[1].iper == 2


def test_sort_person_list_same_name_different_occ():
    base = MockBase()
    p1 = MockPerson(iper=1, first_name="Test", surname="Person", occ=0,
                    birth=adef.CdateNone(), baptism=adef.CdateNone(),
                    death=Death(), burial=UnknownBurial())
    p2 = MockPerson(iper=2, first_name="Test", surname="Person", occ=1,
                    birth=adef.CdateNone(), baptism=adef.CdateNone(),
                    death=Death(), burial=UnknownBurial())
    base.add_person(p1)
    base.add_person(p2)
    sort_fn = gutil.sort_person_list(base)
    result = sort_fn([p2, p1])
    assert result[0].iper == 1
    assert result[1].iper == 2


def test_person_of_string_dot_key_no_match():
    base = MockBase()
    result = gutil.person_of_string_dot_key(base, "NoMatch")
    assert result is None


def test_sort_uniq_person_list_empty():
    base = MockBase()
    sort_fn = gutil.sort_uniq_person_list(base)
    result = sort_fn([])
    assert result == []
