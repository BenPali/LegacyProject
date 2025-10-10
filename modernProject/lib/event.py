from dataclasses import dataclass
from typing import Union, List, Tuple, Optional, Callable, TypeVar, Generic
from enum import Enum
from lib.gwdef import GenPersEventName, GenFamEventName, EpersName, EfamName, WitnessKind
from lib.adef import Cdate
from lib.date import cdate_to_dmy_opt, compare_dmy_opt


T = TypeVar('T')
U = TypeVar('U')


@dataclass
class Pevent(Generic[T]):
    name: Union[GenPersEventName, EpersName[T]]


@dataclass
class Fevent(Generic[T]):
    name: Union[GenFamEventName, EfamName[T]]


EventName = Union[Pevent[T], Fevent[T]]


@dataclass
class EventItem(Generic[T, U]):
    name: EventName[T]
    date: Cdate
    place: U
    note: U
    src: U
    witnesses: List[Tuple[U, WitnessKind]]
    spouse: Optional[U]


def compare_event_name(name1: EventName, name2: EventName) -> int:
    if isinstance(name1, Pevent) and isinstance(name1.name, GenPersEventName):
        n1 = name1.name
    else:
        n1 = None

    if isinstance(name2, Pevent) and isinstance(name2.name, GenPersEventName):
        n2 = name2.name
    else:
        n2 = None

    if n1 == GenPersEventName.EPERS_BIRTH:
        return -1
    if n2 == GenPersEventName.EPERS_BIRTH:
        return 1

    if n1 == GenPersEventName.EPERS_BAPTISM:
        if n2 in (GenPersEventName.EPERS_DEATH, GenPersEventName.EPERS_FUNERAL,
                  GenPersEventName.EPERS_BURIAL, GenPersEventName.EPERS_CREMATION):
            return -1

    if n2 == GenPersEventName.EPERS_BAPTISM:
        if n1 in (GenPersEventName.EPERS_DEATH, GenPersEventName.EPERS_FUNERAL,
                  GenPersEventName.EPERS_BURIAL, GenPersEventName.EPERS_CREMATION):
            return 1

    if n1 == GenPersEventName.EPERS_CREMATION and n2 == GenPersEventName.EPERS_BURIAL:
        return -1

    if n1 in (GenPersEventName.EPERS_BURIAL, GenPersEventName.EPERS_CREMATION):
        return 1
    if n2 in (GenPersEventName.EPERS_BURIAL, GenPersEventName.EPERS_CREMATION):
        return -1

    if n1 == GenPersEventName.EPERS_FUNERAL:
        return 1
    if n2 == GenPersEventName.EPERS_FUNERAL:
        return -1

    if n1 == GenPersEventName.EPERS_DEATH:
        return 1
    if n2 == GenPersEventName.EPERS_DEATH:
        return -1

    return 0


def _compare(get_name: Callable[[T], EventName],
            get_date: Callable[[T], Cdate],
            e1: T,
            e2: T) -> int:
    d1_opt = cdate_to_dmy_opt(get_date(e1))
    if d1_opt is None:
        return compare_event_name(get_name(e1), get_name(e2))

    d2_opt = cdate_to_dmy_opt(get_date(e2))
    if d2_opt is None:
        return compare_event_name(get_name(e1), get_name(e2))

    cmp = compare_dmy_opt(d1_opt, d2_opt, strict=False)
    if cmp is None or cmp == 0:
        return compare_event_name(get_name(e1), get_name(e2))
    return cmp


def sort_events(get_name: Callable[[T], EventName],
                get_date: Callable[[T], Cdate],
                events: List[T]) -> List[T]:
    from functools import cmp_to_key
    return sorted(events, key=cmp_to_key(lambda e1, e2: _compare(get_name, get_date, e1, e2)))
