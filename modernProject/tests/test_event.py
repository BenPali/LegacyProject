import pytest
from lib.event import (
    Pevent, Fevent, EventName, EventItem,
    compare_event_name, sort_events
)
from lib.gwdef import GenPersEventName, GenFamEventName, WitnessKind
from lib.adef import (
    Dmy, Calendar, Precision, CdateGregorian, CdateNone
)
from lib.date import compress


def test_pevent_creation():
    event = Pevent(name=GenPersEventName.EPERS_BIRTH)
    assert isinstance(event, Pevent)
    assert event.name == GenPersEventName.EPERS_BIRTH


def test_fevent_creation():
    event = Fevent(name=GenFamEventName.EFAM_MARRIAGE)
    assert isinstance(event, Fevent)
    assert event.name == GenFamEventName.EFAM_MARRIAGE


def test_event_item_creation():
    name = Pevent(name=GenPersEventName.EPERS_BIRTH)
    date = CdateGregorian(value=compress(Dmy(day=1, month=1, year=1900, prec=Precision.SURE, delta=0)))
    item = EventItem(
        name=name,
        date=date,
        place="Paris",
        note="Birth note",
        src="Source",
        witnesses=[],
        spouse=None
    )
    assert item.name == name
    assert item.date == date
    assert item.place == "Paris"
    assert item.note == "Birth note"
    assert item.src == "Source"
    assert item.witnesses == []
    assert item.spouse is None


def test_compare_event_name_birth_first():
    birth = Pevent(name=GenPersEventName.EPERS_BIRTH)
    death = Pevent(name=GenPersEventName.EPERS_DEATH)
    baptism = Pevent(name=GenPersEventName.EPERS_BAPTISM)

    assert compare_event_name(birth, death) == -1
    assert compare_event_name(birth, baptism) == -1
    assert compare_event_name(death, birth) == 1
    assert compare_event_name(baptism, birth) == 1


def test_compare_event_name_baptism_before_death():
    baptism = Pevent(name=GenPersEventName.EPERS_BAPTISM)
    death = Pevent(name=GenPersEventName.EPERS_DEATH)
    funeral = Pevent(name=GenPersEventName.EPERS_FUNERAL)
    burial = Pevent(name=GenPersEventName.EPERS_BURIAL)
    cremation = Pevent(name=GenPersEventName.EPERS_CREMATION)

    assert compare_event_name(baptism, death) == -1
    assert compare_event_name(baptism, funeral) == -1
    assert compare_event_name(baptism, burial) == -1
    assert compare_event_name(baptism, cremation) == -1

    assert compare_event_name(death, baptism) == 1
    assert compare_event_name(funeral, baptism) == 1
    assert compare_event_name(burial, baptism) == 1
    assert compare_event_name(cremation, baptism) == 1


def test_compare_event_name_death_last():
    death = Pevent(name=GenPersEventName.EPERS_DEATH)
    occupation = Pevent(name=GenPersEventName.EPERS_OCCUPATION)

    assert compare_event_name(death, occupation) == 1
    assert compare_event_name(occupation, death) == -1


def test_compare_event_name_funeral_ordering():
    funeral = Pevent(name=GenPersEventName.EPERS_FUNERAL)
    occupation = Pevent(name=GenPersEventName.EPERS_OCCUPATION)

    assert compare_event_name(funeral, occupation) == 1
    assert compare_event_name(occupation, funeral) == -1


def test_compare_event_name_burial_cremation():
    burial = Pevent(name=GenPersEventName.EPERS_BURIAL)
    cremation = Pevent(name=GenPersEventName.EPERS_CREMATION)
    occupation = Pevent(name=GenPersEventName.EPERS_OCCUPATION)

    assert compare_event_name(cremation, burial) == -1
    assert compare_event_name(burial, occupation) == 1
    assert compare_event_name(cremation, occupation) == 1
    assert compare_event_name(occupation, burial) == -1
    assert compare_event_name(occupation, cremation) == -1


def test_compare_event_name_same_event():
    occupation1 = Pevent(name=GenPersEventName.EPERS_OCCUPATION)
    occupation2 = Pevent(name=GenPersEventName.EPERS_OCCUPATION)

    assert compare_event_name(occupation1, occupation2) == 0


def test_compare_event_name_family_events():
    marriage = Fevent(name=GenFamEventName.EFAM_MARRIAGE)
    divorce = Fevent(name=GenFamEventName.EFAM_DIVORCE)

    assert compare_event_name(marriage, divorce) == 0


def test_sort_events_by_name_only():
    birth = Pevent(name=GenPersEventName.EPERS_BIRTH)
    death = Pevent(name=GenPersEventName.EPERS_DEATH)
    baptism = Pevent(name=GenPersEventName.EPERS_BAPTISM)

    event1 = EventItem(birth, CdateNone(), "", "", "", [], None)
    event2 = EventItem(death, CdateNone(), "", "", "", [], None)
    event3 = EventItem(baptism, CdateNone(), "", "", "", [], None)

    events = [event2, event3, event1]
    sorted_events = sort_events(lambda e: e.name, lambda e: e.date, events)

    assert sorted_events[0].name == birth
    assert sorted_events[1].name == baptism
    assert sorted_events[2].name == death


def test_sort_events_by_date():
    birth = Pevent(name=GenPersEventName.EPERS_BIRTH)
    date1 = CdateGregorian(value=compress(Dmy(day=1, month=1, year=1900, prec=Precision.SURE, delta=0)))
    date2 = CdateGregorian(value=compress(Dmy(day=1, month=1, year=1950, prec=Precision.SURE, delta=0)))
    date3 = CdateGregorian(value=compress(Dmy(day=1, month=1, year=1925, prec=Precision.SURE, delta=0)))

    event1 = EventItem(birth, date1, "", "", "", [], None)
    event2 = EventItem(birth, date2, "", "", "", [], None)
    event3 = EventItem(birth, date3, "", "", "", [], None)

    events = [event2, event1, event3]
    sorted_events = sort_events(lambda e: e.name, lambda e: e.date, events)

    assert sorted_events[0].date == date1
    assert sorted_events[1].date == date3
    assert sorted_events[2].date == date2


def test_sort_events_mixed_dates_and_names():
    birth = Pevent(name=GenPersEventName.EPERS_BIRTH)
    death = Pevent(name=GenPersEventName.EPERS_DEATH)
    baptism = Pevent(name=GenPersEventName.EPERS_BAPTISM)

    date1 = CdateGregorian(value=compress(Dmy(day=1, month=1, year=1900, prec=Precision.SURE, delta=0)))
    date2 = CdateGregorian(value=compress(Dmy(day=1, month=1, year=1980, prec=Precision.SURE, delta=0)))

    event1 = EventItem(birth, date1, "", "", "", [], None)
    event2 = EventItem(death, date2, "", "", "", [], None)
    event3 = EventItem(baptism, CdateNone(), "", "", "", [], None)

    events = [event3, event2, event1]
    sorted_events = sort_events(lambda e: e.name, lambda e: e.date, events)

    assert sorted_events[0] == event1
    assert sorted_events[1] == event3
    assert sorted_events[2] == event2


def test_sort_events_same_date_different_names():
    birth = Pevent(name=GenPersEventName.EPERS_BIRTH)
    baptism = Pevent(name=GenPersEventName.EPERS_BAPTISM)

    date = CdateGregorian(value=compress(Dmy(day=1, month=1, year=1900, prec=Precision.SURE, delta=0)))

    event1 = EventItem(baptism, date, "", "", "", [], None)
    event2 = EventItem(birth, date, "", "", "", [], None)

    events = [event1, event2]
    sorted_events = sort_events(lambda e: e.name, lambda e: e.date, events)

    assert sorted_events[0].name == birth
    assert sorted_events[1].name == baptism


def test_sort_events_empty_list():
    events = []
    sorted_events = sort_events(lambda e: e.name, lambda e: e.date, events)
    assert sorted_events == []


def test_sort_events_single_event():
    birth = Pevent(name=GenPersEventName.EPERS_BIRTH)
    date = CdateGregorian(value=compress(Dmy(day=1, month=1, year=1900, prec=Precision.SURE, delta=0)))
    event = EventItem(birth, date, "", "", "", [], None)

    events = [event]
    sorted_events = sort_events(lambda e: e.name, lambda e: e.date, events)
    assert sorted_events == [event]


def test_event_item_with_witnesses():
    birth = Pevent(name=GenPersEventName.EPERS_BIRTH)
    date = CdateNone()
    witnesses = [(1, WitnessKind.WITNESS), (2, WitnessKind.WITNESS_GOD_PARENT)]

    event = EventItem(birth, date, "", "", "", witnesses, None)
    assert len(event.witnesses) == 2
    assert event.witnesses[0] == (1, WitnessKind.WITNESS)
    assert event.witnesses[1] == (2, WitnessKind.WITNESS_GOD_PARENT)


def test_event_item_with_spouse():
    marriage = Fevent(name=GenFamEventName.EFAM_MARRIAGE)
    date = CdateNone()

    event = EventItem(marriage, date, "", "", "", [], spouse=42)
    assert event.spouse == 42
