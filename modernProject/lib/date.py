from typing import Optional, Union
from dataclasses import dataclass
from lib.adef import (
    Dmy, Dmy2, DateGreg, DateText, Calendar, Precision,
    CdateGregorian, CdateJulian, CdateFrench, CdateHebrew,
    CdateText, CdateDate, CdateNone, PrecisionOrYear, PrecisionYearInt
)

Cdate = Union[CdateGregorian, CdateJulian, CdateFrench, CdateHebrew, CdateText, CdateDate, CdateNone]
Date = Union[DateGreg, DateText]

class NotComparable(Exception):
    pass

def compress(d: Dmy) -> Optional[int]:
    simple = False
    if isinstance(d.prec, Precision):
        if d.prec in (Precision.SURE, Precision.ABOUT, Precision.MAYBE, Precision.BEFORE, Precision.AFTER):
            simple = d.day >= 0 and d.month >= 0 and d.year > 0 and d.year < 2500 and d.delta == 0

    if simple:
        p = 0
        if d.prec == Precision.ABOUT:
            p = 1
        elif d.prec == Precision.MAYBE:
            p = 2
        elif d.prec == Precision.BEFORE:
            p = 3
        elif d.prec == Precision.AFTER:
            p = 4
        return ((((((p * 32) + d.day) * 13) + d.month) * 2500) + d.year)
    return None

def uncompress(x: int) -> Dmy:
    year = x % 2500
    x = x // 2500
    month = x % 13
    x = x // 13
    day = x % 32
    x = x // 32

    prec_map = {1: Precision.ABOUT, 2: Precision.MAYBE, 3: Precision.BEFORE, 4: Precision.AFTER}
    prec = prec_map.get(x, Precision.SURE)

    return Dmy(day=day, month=month, year=year, prec=prec, delta=0)

def date_of_cdate(cd: Cdate) -> Date:
    if isinstance(cd, CdateGregorian):
        return DateGreg(dmy=uncompress(cd.value), calendar=Calendar.GREGORIAN)
    elif isinstance(cd, CdateJulian):
        return DateGreg(dmy=uncompress(cd.value), calendar=Calendar.JULIAN)
    elif isinstance(cd, CdateFrench):
        return DateGreg(dmy=uncompress(cd.value), calendar=Calendar.FRENCH)
    elif isinstance(cd, CdateHebrew):
        return DateGreg(dmy=uncompress(cd.value), calendar=Calendar.HEBREW)
    elif isinstance(cd, CdateDate):
        return cd.date
    elif isinstance(cd, CdateText):
        return DateText(text=cd.text)
    else:
        raise ValueError("date_of_cdate: Cnone")

def cdate_of_date(d: Date) -> Cdate:
    if isinstance(d, DateGreg):
        compressed = compress(d.dmy)
        if compressed is not None:
            if d.calendar == Calendar.GREGORIAN:
                return CdateGregorian(compressed)
            elif d.calendar == Calendar.JULIAN:
                return CdateJulian(compressed)
            elif d.calendar == Calendar.FRENCH:
                return CdateFrench(compressed)
            elif d.calendar == Calendar.HEBREW:
                return CdateHebrew(compressed)
        return CdateDate(d)
    elif isinstance(d, DateText):
        return CdateText(d.text)
    return CdateNone()

def cdate_of_od(od: Optional[Date]) -> Cdate:
    return cdate_of_date(od) if od is not None else CdateNone()

def od_of_cdate(cd: Cdate) -> Optional[Date]:
    return None if isinstance(cd, CdateNone) else date_of_cdate(cd)

cdate_None = cdate_of_od(None)

def dmy_of_dmy2(dmy2: Dmy2) -> Dmy:
    return Dmy(
        day=dmy2.day2,
        month=dmy2.month2,
        year=dmy2.year2,
        prec=Precision.SURE,
        delta=dmy2.delta2
    )

def leap_year(a: int) -> bool:
    if a % 100 == 0:
        return (a // 100) % 4 == 0
    return a % 4 == 0

def nb_days_in_month(m: int, a: int) -> int:
    if m == 2 and leap_year(a):
        return 29
    if 1 <= m <= 12:
        return [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
    return 0

def time_elapsed(d1: Dmy, d2: Dmy) -> Dmy:
    def compute_prec(p1: Union[Precision, PrecisionOrYear, PrecisionYearInt],
                     p2: Union[Precision, PrecisionOrYear, PrecisionYearInt]) -> Precision:
        if p1 == Precision.SURE and p2 == Precision.SURE:
            return Precision.SURE
        if p1 in (Precision.MAYBE, Precision.SURE, Precision.ABOUT) and p2 in (Precision.MAYBE, Precision.SURE, Precision.ABOUT):
            return Precision.MAYBE
        if p1 in (Precision.ABOUT, Precision.MAYBE, Precision.SURE, Precision.BEFORE) and \
           p2 in (Precision.AFTER, Precision.SURE, Precision.MAYBE, Precision.ABOUT):
            return Precision.AFTER
        if p1 in (Precision.ABOUT, Precision.MAYBE, Precision.SURE, Precision.AFTER) and \
           p2 in (Precision.BEFORE, Precision.SURE, Precision.MAYBE, Precision.ABOUT):
            return Precision.BEFORE
        return Precision.MAYBE

    prec = compute_prec(d1.prec, d2.prec)

    if d1.day == 0 and d1.month == 0:
        return Dmy(day=0, month=0, year=d2.year - d1.year, prec=prec, delta=0)

    if d1.day == 0:
        if d2.day == 0 and d2.month == 0:
            return Dmy(day=0, month=0, year=d2.year - d1.year, prec=prec, delta=0)

        if d2.day == 0:
            month = d2.month - d1.month
            r = 0
            if d1.month > d2.month:
                month += 12
                r = 1
            year = d2.year - d1.year - r
            return Dmy(day=0, month=month, year=year, prec=prec, delta=0)

        month = d2.month - d1.month
        r = 0
        if d1.month > d2.month:
            month += 12
            r = 1
        year = d2.year - d1.year - r
        return Dmy(day=0, month=month, year=year, prec=prec, delta=0)

    if d2.day == 0 and d2.month == 0:
        return Dmy(day=0, month=0, year=d2.year - d1.year, prec=prec, delta=0)

    if d2.day == 0:
        month = d2.month - d1.month
        r = 0
        if d1.month > d2.month:
            month += 12
            r = 1
        year = d2.year - d1.year - r
        return Dmy(day=0, month=month, year=year, prec=prec, delta=0)

    day = d2.day - d1.day
    r1 = 0
    if d1.day > d2.day:
        day += nb_days_in_month(d1.month, d1.year)
        r1 = 1

    month = d2.month - d1.month - r1
    r2 = 0
    if d1.month + r1 > d2.month:
        month += 12
        r2 = 1

    year = d2.year - d1.year - r2
    return Dmy(day=day, month=month, year=year, prec=prec, delta=0)

def time_elapsed_opt(d1: Dmy, d2: Dmy) -> Optional[Dmy]:
    if (d1.prec == Precision.AFTER and d2.prec == Precision.AFTER) or \
       (d1.prec == Precision.BEFORE and d2.prec == Precision.BEFORE):
        return None
    return time_elapsed(d1, d2)

def compare_dmy_opt(dmy1: Dmy, dmy2: Dmy, strict: bool = False) -> Optional[int]:
    year_cmp = (dmy1.year > dmy2.year) - (dmy1.year < dmy2.year)
    if year_cmp != 0:
        return _eval_strict(strict, dmy1, dmy2, year_cmp)
    return _compare_month_or_day(is_day=False, strict=strict, dmy1=dmy1, dmy2=dmy2)

def _compare_month_or_day(is_day: bool, strict: bool, dmy1: Dmy, dmy2: Dmy) -> Optional[int]:
    def compare_with_unknown(strict_mode, unknown, known):
        if isinstance(unknown.prec, Precision):
            if unknown.prec == Precision.AFTER:
                return 1
            elif unknown.prec == Precision.BEFORE:
                return -1
        if strict_mode:
            return None
        return _compare_prec(False, unknown, known)

    x = dmy1.day if is_day else dmy1.month
    y = dmy2.day if is_day else dmy2.month

    if x == 0 and y == 0:
        return _compare_prec(strict, dmy1, dmy2)
    elif x == 0:
        return compare_with_unknown(strict, dmy1, dmy2)
    elif y == 0:
        result = compare_with_unknown(strict, dmy2, dmy1)
        return -result if result is not None else None

    cmp = (x > y) - (x < y)
    if cmp == 0:
        next_fn = _compare_prec if is_day else lambda s, d1, d2: _compare_month_or_day(True, s, d1, d2)
        return next_fn(strict, dmy1, dmy2)
    return _eval_strict(strict, dmy1, dmy2, cmp)

def _compare_prec(strict: bool, dmy1: Dmy, dmy2: Dmy) -> Optional[int]:
    p1, p2 = dmy1.prec, dmy2.prec

    if isinstance(p1, Precision) and isinstance(p2, Precision):
        if p1 in (Precision.SURE, Precision.ABOUT, Precision.MAYBE) and \
           p2 in (Precision.SURE, Precision.ABOUT, Precision.MAYBE):
            return 0
        if (p1 == Precision.AFTER and p2 == Precision.AFTER) or \
           (p1 == Precision.BEFORE and p2 == Precision.BEFORE):
            return 0
        if p2 == Precision.AFTER or p1 == Precision.BEFORE:
            return -1
        if p1 == Precision.AFTER or p2 == Precision.BEFORE:
            return 1

    if isinstance(p1, PrecisionOrYear) and isinstance(p2, PrecisionOrYear):
        return compare_dmy_opt(dmy_of_dmy2(p1.dmy2), dmy_of_dmy2(p2.dmy2), strict)
    if isinstance(p1, PrecisionYearInt) and isinstance(p2, PrecisionYearInt):
        return compare_dmy_opt(dmy_of_dmy2(p1.dmy2), dmy_of_dmy2(p2.dmy2), strict)

    return 0

def _eval_strict(strict: bool, dmy1: Dmy, dmy2: Dmy, x: int) -> Optional[int]:
    if not strict:
        return x

    if x == -1:
        if isinstance(dmy1.prec, Precision) and dmy1.prec == Precision.AFTER:
            return None
        if isinstance(dmy2.prec, Precision) and dmy2.prec == Precision.BEFORE:
            return None
    elif x == 1:
        if isinstance(dmy1.prec, Precision) and dmy1.prec == Precision.BEFORE:
            return None
        if isinstance(dmy2.prec, Precision) and dmy2.prec == Precision.AFTER:
            return None
    return x

def compare_dmy(dmy1: Dmy, dmy2: Dmy, strict: bool = False) -> int:
    result = compare_dmy_opt(dmy1, dmy2, strict)
    if result is None:
        raise NotComparable()
    return result

def compare_date(d1: Date, d2: Date, strict: bool = False) -> int:
    if isinstance(d1, DateGreg) and isinstance(d2, DateGreg):
        return compare_dmy(d1.dmy, d2.dmy, strict)
    if isinstance(d1, DateGreg) and isinstance(d2, DateText):
        if strict:
            raise NotComparable()
        return 1
    if isinstance(d1, DateText) and isinstance(d2, DateGreg):
        if strict:
            raise NotComparable()
        return -1
    if strict:
        raise NotComparable()
    return 0

def cdate_to_dmy_opt(cdate: Cdate) -> Optional[Dmy]:
    od = od_of_cdate(cdate)
    if isinstance(od, DateGreg):
        return od.dmy
    return None
