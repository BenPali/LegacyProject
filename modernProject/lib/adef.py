from dataclasses import dataclass
from enum import Enum, auto
from typing import Union


class Fix:
    __slots__ = ('_value',)

    def __init__(self, value: int):
        self._value = value

    @classmethod
    def from_float(cls, x: float) -> 'Fix':
        return cls(int((x * 1000000.0) + 0.5))

    def to_float(self) -> float:
        return float(self._value) / 1000000.0

    @property
    def value(self) -> int:
        return self._value

    def __eq__(self, other):
        if isinstance(other, Fix):
            return self._value == other._value
        return False

    def __repr__(self):
        return f"Fix({self._value})"


NO_CONSANG = Fix(-1)


class Calendar(Enum):
    GREGORIAN = auto()
    JULIAN = auto()
    FRENCH = auto()
    HEBREW = auto()


class Precision(Enum):
    SURE = auto()
    ABOUT = auto()
    MAYBE = auto()
    BEFORE = auto()
    AFTER = auto()


@dataclass(frozen=True)
class Dmy2:
    day2: int
    month2: int
    year2: int
    delta2: int


@dataclass(frozen=True)
class PrecisionOrYear:
    dmy2: Dmy2


@dataclass(frozen=True)
class PrecisionYearInt:
    dmy2: Dmy2


PrecisionType = Union[Precision, PrecisionOrYear, PrecisionYearInt]


@dataclass(frozen=True)
class Dmy:
    day: int
    month: int
    year: int
    prec: PrecisionType
    delta: int


@dataclass(frozen=True)
class DateGreg:
    dmy: Dmy
    calendar: Calendar


@dataclass(frozen=True)
class DateText:
    text: str


Date = Union[DateGreg, DateText]


@dataclass(frozen=True)
class CdateGregorian:
    value: int


@dataclass(frozen=True)
class CdateJulian:
    value: int


@dataclass(frozen=True)
class CdateFrench:
    value: int


@dataclass(frozen=True)
class CdateHebrew:
    value: int


@dataclass(frozen=True)
class CdateText:
    text: str


@dataclass(frozen=True)
class CdateDate:
    date: Date


class CdateNone:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self):
        return "CdateNone()"


Cdate = Union[CdateGregorian, CdateJulian, CdateFrench, CdateHebrew, CdateText, CdateDate, CdateNone]


@dataclass(frozen=True)
class Couple:
    father: object
    mother: object


def couple(father, mother) -> Couple:
    return Couple(father=father, mother=mother)


def parent(parent_array) -> Couple:
    if len(parent_array) != 2:
        raise ValueError("parent_array must have exactly 2 elements")
    return Couple(father=parent_array[0], mother=parent_array[1])


def parent_array(cpl: Couple):
    return [cpl.father, cpl.mother]


def multi_couple(father, mother) -> Couple:
    return Couple(father=father, mother=mother)


def multi_parent(parent_arr) -> Couple:
    if len(parent_arr) != 2:
        raise ValueError("parent_arr must have exactly 2 elements")
    return Couple(father=parent_arr[0], mother=parent_arr[1])


class SafeString(str):
    pass


class EscapedString(str):
    pass


class EncodedString(str):
    pass


def safe(s: str) -> SafeString:
    return SafeString(s)


def escaped(s: str) -> EscapedString:
    return EscapedString(s)


def encoded(s: str) -> EncodedString:
    return EncodedString(s)


def as_string(astring) -> str:
    return str(astring)
