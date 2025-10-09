from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple
from lib.adef import Dmy, Dmy2, Precision, PrecisionOrYear, PrecisionYearInt


@dataclass
class CalendarDate:
    day: int
    month: int
    year: int
    delta: int


def to_calendar_date(dmy: Dmy) -> CalendarDate:
    return CalendarDate(day=dmy.day, month=dmy.month, year=dmy.year, delta=dmy.delta)


def of_calendar_date(cd: CalendarDate, prec: Precision = Precision.SURE) -> Dmy:
    return Dmy(day=cd.day, month=cd.month, year=cd.year, delta=cd.delta, prec=prec)


def sdn_of_gregorian(dmy: Dmy) -> int:
    year, month, day = dmy.year, dmy.month, dmy.day
    if month <= 2:
        year -= 1
        month += 12
    a = year // 100
    b = 2 - a + (a // 4)
    return int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524


def gregorian_of_sdn(prec: Precision, sdn: int) -> Dmy:
    temp = sdn + 68569
    n = 4 * temp // 146097
    temp = temp - (146097 * n + 3) // 4
    i = (4000 * (temp + 1)) // 1461001
    temp = temp - (1461 * i // 4) + 31
    j = (80 * temp) // 2447
    day = temp - (2447 * j // 80)
    temp = j // 11
    month = j + 2 - (12 * temp)
    year = 100 * (n - 49) + i + temp
    return Dmy(day=day, month=month, year=year, delta=0, prec=prec)


def sdn_of_julian(dmy: Dmy) -> int:
    year, month, day = dmy.year, dmy.month, dmy.day
    if month <= 2:
        year -= 1
        month += 12
    return int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day - 1524


def julian_of_sdn(prec: Precision, sdn: int) -> Dmy:
    b = 0
    c = sdn + 32082
    d = (4 * c + 3) // 1461
    e = c - (1461 * d // 4)
    m = (5 * e + 2) // 153
    day = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year = d - 4800 + m // 10
    return Dmy(day=day, month=month, year=year, delta=0, prec=prec)


def sdn_of_french(dmy: Dmy) -> int:
    year, month, day = dmy.year, dmy.month, dmy.day
    return (year - 1) * 365 + (year // 4) + (month - 1) * 30 + day + 2375474


def french_of_sdn(prec: Precision, sdn: int) -> Dmy:
    temp = sdn - 2375475
    year = (4 * temp + 3) // 1461 + 1
    day_of_year = temp - ((year - 1) * 365 + (year // 4))
    month = day_of_year // 30 + 1
    day = day_of_year % 30 + 1
    if day == 0:
        month -= 1
        day = 30
    return Dmy(day=day, month=month, year=year, delta=0, prec=prec)


def sdn_of_hebrew(dmy: Dmy) -> int:
    year, month, day = dmy.year, dmy.month, dmy.day
    months_in_year = 12
    if (year % 19 == 0 or year % 19 == 3 or year % 19 == 6 or
        year % 19 == 8 or year % 19 == 11 or year % 19 == 14 or year % 19 == 17):
        months_in_year = 13
    temp_month = month
    if months_in_year == 13 and month >= 6:
        temp_month += 1
    day_in_year = (temp_month - 1) * 30 + day
    return int((year - 1) * 365.25) + day_in_year + 347997


def hebrew_of_sdn(prec: Precision, sdn: int) -> Dmy:
    temp = sdn - 347998
    year = int(temp / 365.25) + 1
    day_of_year = temp - int((year - 1) * 365.25)
    month = day_of_year // 30 + 1
    day = day_of_year % 30 + 1
    if day == 0:
        month -= 1
        day = 30
    months_in_year = 12
    if (year % 19 == 0 or year % 19 == 3 or year % 19 == 6 or
        year % 19 == 8 or year % 19 == 11 or year % 19 == 14 or year % 19 == 17):
        months_in_year = 13
    if months_in_year == 13 and month >= 7:
        month -= 1
    return Dmy(day=day, month=month, year=year, delta=0, prec=prec)


def dmy_of_dmy2(dmy2: Dmy2) -> Dmy:
    return Dmy(day=dmy2.day2, month=dmy2.month2, year=dmy2.year2, delta=dmy2.delta2, prec=Precision.SURE)


def aux_convert(fn, dmy: Dmy) -> Dmy:
    def aux2(d2: Dmy2) -> Dmy2:
        d = of_calendar_date(fn(to_calendar_date(dmy_of_dmy2(d2))))
        return Dmy2(day2=d.day, month2=d.month, year2=d.year, delta2=d.delta)

    if isinstance(dmy.prec, PrecisionOrYear):
        new_prec = PrecisionOrYear(aux2(dmy.prec.dmy2))
    elif isinstance(dmy.prec, PrecisionYearInt):
        new_prec = PrecisionYearInt(aux2(dmy.prec.dmy2))
    else:
        new_prec = dmy.prec

    return of_calendar_date(fn(to_calendar_date(dmy)), new_prec)


def gregorian_of_julian_cd(cd: CalendarDate) -> CalendarDate:
    sdn = sdn_of_julian(Dmy(day=cd.day, month=cd.month, year=cd.year, delta=cd.delta, prec=Precision.SURE))
    result = gregorian_of_sdn(Precision.SURE, sdn)
    return CalendarDate(day=result.day, month=result.month, year=result.year, delta=result.delta)


def julian_of_gregorian_cd(cd: CalendarDate) -> CalendarDate:
    sdn = sdn_of_gregorian(Dmy(day=cd.day, month=cd.month, year=cd.year, delta=cd.delta, prec=Precision.SURE))
    result = julian_of_sdn(Precision.SURE, sdn)
    return CalendarDate(day=result.day, month=result.month, year=result.year, delta=result.delta)


def gregorian_of_french_cd(cd: CalendarDate) -> CalendarDate:
    sdn = sdn_of_french(Dmy(day=cd.day, month=cd.month, year=cd.year, delta=cd.delta, prec=Precision.SURE))
    result = gregorian_of_sdn(Precision.SURE, sdn)
    return CalendarDate(day=result.day, month=result.month, year=result.year, delta=result.delta)


def french_of_gregorian_cd(cd: CalendarDate) -> CalendarDate:
    sdn = sdn_of_gregorian(Dmy(day=cd.day, month=cd.month, year=cd.year, delta=cd.delta, prec=Precision.SURE))
    result = french_of_sdn(Precision.SURE, sdn)
    return CalendarDate(day=result.day, month=result.month, year=result.year, delta=result.delta)


def gregorian_of_hebrew_cd(cd: CalendarDate) -> CalendarDate:
    sdn = sdn_of_hebrew(Dmy(day=cd.day, month=cd.month, year=cd.year, delta=cd.delta, prec=Precision.SURE))
    result = gregorian_of_sdn(Precision.SURE, sdn)
    return CalendarDate(day=result.day, month=result.month, year=result.year, delta=result.delta)


def hebrew_of_gregorian_cd(cd: CalendarDate) -> CalendarDate:
    sdn = sdn_of_gregorian(Dmy(day=cd.day, month=cd.month, year=cd.year, delta=cd.delta, prec=Precision.SURE))
    result = hebrew_of_sdn(Precision.SURE, sdn)
    return CalendarDate(day=result.day, month=result.month, year=result.year, delta=result.delta)


def gregorian_of_julian(dmy: Dmy) -> Dmy:
    return aux_convert(gregorian_of_julian_cd, dmy)


def julian_of_gregorian(dmy: Dmy) -> Dmy:
    return aux_convert(julian_of_gregorian_cd, dmy)


def gregorian_of_french(dmy: Dmy) -> Dmy:
    return aux_convert(gregorian_of_french_cd, dmy)


def french_of_gregorian(dmy: Dmy) -> Dmy:
    return aux_convert(french_of_gregorian_cd, dmy)


def gregorian_of_hebrew(dmy: Dmy) -> Dmy:
    return aux_convert(gregorian_of_hebrew_cd, dmy)


def hebrew_of_gregorian(dmy: Dmy) -> Dmy:
    return aux_convert(hebrew_of_gregorian_cd, dmy)


class MoonPhase(Enum):
    NEW_MOON = "NewMoon"
    FIRST_QUARTER = "FirstQuarter"
    FULL_MOON = "FullMoon"
    LAST_QUARTER = "LastQuarter"


def moon_phase_of_sdn(sdn: int) -> Tuple[Optional[Tuple[MoonPhase, int, int]], int]:
    jd = sdn + 0.5
    k = int((jd - 2451550.1) / 29.530588853)
    t = k / 1236.85
    jde = 2451550.09766 + 29.530588861 * k
    phase_jd = jde

    moon_age = int((jd - 2451550.1) % 29.530588853)

    day_start = int(jd - 0.5)
    day_fraction = phase_jd - day_start
    hour = int(day_fraction * 24)
    minute = int((day_fraction * 24 - hour) * 60)

    phase_type = k % 4
    if day_start == int(phase_jd):
        if phase_type == 0:
            return (MoonPhase.NEW_MOON, hour, minute), moon_age
        elif phase_type == 1:
            return (MoonPhase.FIRST_QUARTER, hour, minute), moon_age
        elif phase_type == 2:
            return (MoonPhase.FULL_MOON, hour, minute), moon_age
        else:
            return (MoonPhase.LAST_QUARTER, hour, minute), moon_age

    return None, moon_age
