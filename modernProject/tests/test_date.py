import pytest
from lib.date import *
from lib.adef import *

def test_leap_year():
    assert leap_year(2000) == True
    assert leap_year(2004) == True
    assert leap_year(1900) == False
    assert leap_year(2001) == False
    assert leap_year(2024) == True

def test_nb_days_in_month():
    assert nb_days_in_month(1, 2020) == 31
    assert nb_days_in_month(2, 2020) == 29
    assert nb_days_in_month(2, 2019) == 28
    assert nb_days_in_month(4, 2020) == 30
    assert nb_days_in_month(12, 2020) == 31
    assert nb_days_in_month(0, 2020) == 0
    assert nb_days_in_month(13, 2020) == 0

def test_compress_uncompress():
    d = Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=0)
    compressed = compress(d)
    assert compressed is not None
    uncompressed = uncompress(compressed)
    assert uncompressed.day == d.day
    assert uncompressed.month == d.month
    assert uncompressed.year == d.year
    assert uncompressed.prec == d.prec

def test_compress_precision():
    d_about = Dmy(day=10, month=5, year=1985, prec=Precision.ABOUT, delta=0)
    c = compress(d_about)
    u = uncompress(c)
    assert u.prec == Precision.ABOUT

    d_before = Dmy(day=20, month=12, year=2000, prec=Precision.BEFORE, delta=0)
    c = compress(d_before)
    u = uncompress(c)
    assert u.prec == Precision.BEFORE

    d_maybe = Dmy(day=10, month=5, year=1985, prec=Precision.MAYBE, delta=0)
    c = compress(d_maybe)
    u = uncompress(c)
    assert u.prec == Precision.MAYBE

    d_after = Dmy(day=10, month=5, year=1985, prec=Precision.AFTER, delta=0)
    c = compress(d_after)
    u = uncompress(c)
    assert u.prec == Precision.AFTER

def test_compress_returns_none_for_invalid():
    d = Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=5)
    assert compress(d) is None

    d = Dmy(day=15, month=6, year=3000, prec=Precision.SURE, delta=0)
    assert compress(d) is None

def test_cdate_conversions():
    d = DateGreg(dmy=Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=0), calendar=Calendar.GREGORIAN)
    cd = cdate_of_date(d)
    assert isinstance(cd, CdateGregorian)

    d2 = date_of_cdate(cd)
    assert isinstance(d2, DateGreg)
    assert d2.dmy.day == 15
    assert d2.dmy.month == 6
    assert d2.dmy.year == 1990

def test_date_of_cdate_all_calendars():
    for calendar in Calendar:
        d = DateGreg(dmy=Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=0), calendar=calendar)
        cd = cdate_of_date(d)
        assert isinstance(cd, Cdate)

        d2 = date_of_cdate(cd)
        assert isinstance(d2, Date)
        assert d2.dmy.day == 15
        assert d2.dmy.month == 6
        assert d2.dmy.year == 1990
    
def test_date_of_cdate_date():
    d = DateGreg(dmy=Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=0), calendar=Calendar.GREGORIAN)
    cd = CdateDate(date=d)
    result = date_of_cdate(cd)
    
    assert result == d
    assert result is cd.date

def test_cdate_of_date_text():
    text_date = DateText(text="TextDate")
    cd = cdate_of_date(text_date)
    
    assert isinstance(cd, CdateText)
    assert cd.text == "TextDate"
    
    result = date_of_cdate(cd)
    assert isinstance(result, DateText)
    assert result.text == "TextDate"

def test_cdate_of_date_compressed_none():
    d = DateGreg(dmy=Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=5), calendar=Calendar.GREGORIAN)
    cd = cdate_of_date(d)
    
    assert isinstance(cd, CdateDate)
    assert cd.date == d
    
    result = date_of_cdate(cd)
    assert result == d

def test_cdate_none():
    cd = cdate_of_od(None)
    assert isinstance(cd, CdateNone)

    od = od_of_cdate(cd)
    assert od is None

def test_time_elapsed_compute_prec():
    d1 = Dmy(day=1, month=1, year=2000, prec=Precision.SURE, delta=0)
    d2 = Dmy(day=1, month=1, year=2010, prec=Precision.SURE, delta=0)
    result = time_elapsed(d1, d2)
    assert result.prec == Precision.SURE

    d1 = Dmy(day=1, month=1, year=2000, prec=Precision.MAYBE, delta=0)
    d2 = Dmy(day=1, month=1, year=2010, prec=Precision.ABOUT, delta=0)
    result = time_elapsed(d1, d2)
    assert result.prec == Precision.MAYBE    

    d1 = Dmy(day=1, month=1, year=2000, prec=Precision.ABOUT, delta=0)
    d2 = Dmy(day=1, month=1, year=2010, prec=Precision.MAYBE, delta=0)
    result = time_elapsed(d1, d2)
    assert result.prec == Precision.MAYBE

    d1 = Dmy(day=1, month=1, year=2000, prec=Precision.BEFORE, delta=0)
    d2 = Dmy(day=1, month=1, year=2010, prec=Precision.AFTER, delta=0)
    result = time_elapsed(d1, d2)
    assert result.prec == Precision.AFTER

    d1 = Dmy(day=1, month=1, year=2000, prec=Precision.AFTER, delta=0)
    d2 = Dmy(day=1, month=1, year=2010, prec=Precision.BEFORE, delta=0)
    result = time_elapsed(d1, d2)
    assert result.prec == Precision.BEFORE    

    d1 = Dmy(day=1, month=1, year=2000, prec=Precision.BEFORE, delta=0)
    d2 = Dmy(day=1, month=1, year=2010, prec=Precision.BEFORE, delta=0)
    result = time_elapsed(d1, d2)
    assert result.prec == Precision.MAYBE

def test_time_elapsed_special_cases():
    d1 = Dmy(day=0, month=0, year=2000, prec=Precision.SURE, delta=0)
    d2 = Dmy(day=15, month=6, year=2010, prec=Precision.SURE, delta=0)
    result = time_elapsed(d1, d2)
    assert result.day == 0
    assert result.month == 0
    assert result.year == 10
    
    d1 = Dmy(day=0, month=5, year=2000, prec=Precision.SURE, delta=0)
    d2 = Dmy(day=0, month=0, year=2010, prec=Precision.SURE, delta=0)
    result = time_elapsed(d1, d2)
    assert result.day == 0
    assert result.month == 0
    assert result.year == 10
    
    d1 = Dmy(day=0, month=5, year=2000, prec=Precision.SURE, delta=0)
    d2 = Dmy(day=0, month=3, year=2001, prec=Precision.SURE, delta=0)
    result = time_elapsed(d1, d2)
    assert result.day == 0
    assert result.month == 10
    assert result.year == 0
    
    d1 = Dmy(day=0, month=5, year=2000, prec=Precision.SURE, delta=0)
    d2 = Dmy(day=15, month=3, year=2001, prec=Precision.SURE, delta=0)
    result = time_elapsed(d1, d2)
    assert result.day == 0
    assert result.month == 10
    assert result.year == 0
    
    d1 = Dmy(day=15, month=6, year=2000, prec=Precision.SURE, delta=0)
    d2 = Dmy(day=0, month=0, year=2010, prec=Precision.SURE, delta=0)
    result = time_elapsed(d1, d2)
    assert result.day == 0
    assert result.month == 0
    assert result.year == 10
    
    d1 = Dmy(day=15, month=6, year=2000, prec=Precision.SURE, delta=0)
    d2 = Dmy(day=0, month=3, year=2001, prec=Precision.SURE, delta=0)
    result = time_elapsed(d1, d2)
    assert result.day == 0
    assert result.month == 9
    assert result.year == 0
    
    d1 = Dmy(day=20, month=6, year=2000, prec=Precision.SURE, delta=0)
    d2 = Dmy(day=10, month=7, year=2000, prec=Precision.SURE, delta=0)
    result = time_elapsed(d1, d2)
    assert result.day == 20
    assert result.month == 0
    assert result.year == 0
    
    d1 = Dmy(day=20, month=7, year=2000, prec=Precision.SURE, delta=0)
    d2 = Dmy(day=10, month=6, year=2001, prec=Precision.SURE, delta=0)
    result = time_elapsed(d1, d2)
    assert result.day == 21
    assert result.month == 10
    assert result.year == 0

def test_dmy_of_dmy2():
    dmy2 = Dmy2(day2=10, month2=3, year2=1985, delta2=0)
    dmy = dmy_of_dmy2(dmy2)
    assert dmy.day == 10
    assert dmy.month == 3
    assert dmy.year == 1985
    assert dmy.prec == Precision.SURE

def test_time_elapsed_simple():
    d1 = Dmy(day=1, month=1, year=2000, prec=Precision.SURE, delta=0)
    d2 = Dmy(day=1, month=1, year=2010, prec=Precision.SURE, delta=0)
    elapsed = time_elapsed(d1, d2)
    assert elapsed.year == 10
    assert elapsed.month == 0
    assert elapsed.day == 0

def test_time_elapsed_with_months():
    d1 = Dmy(day=0, month=6, year=2000, prec=Precision.SURE, delta=0)
    d2 = Dmy(day=0, month=9, year=2001, prec=Precision.SURE, delta=0)
    elapsed = time_elapsed(d1, d2)
    assert elapsed.year == 1
    assert elapsed.month == 3

def test_time_elapsed_complex():
    d1 = Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=0)
    d2 = Dmy(day=20, month=8, year=1995, prec=Precision.SURE, delta=0)
    elapsed = time_elapsed(d1, d2)
    assert elapsed.year == 5
    assert elapsed.month == 2
    assert elapsed.day == 5

def test_time_elapsed_opt():
    d1 = Dmy(day=1, month=1, year=2000, prec=Precision.AFTER, delta=0)
    d2 = Dmy(day=1, month=1, year=2010, prec=Precision.AFTER, delta=0)
    assert time_elapsed_opt(d1, d2) is None
    
    d1 = Dmy(day=1, month=1, year=2000, prec=Precision.BEFORE, delta=0)
    d2 = Dmy(day=1, month=1, year=2010, prec=Precision.BEFORE, delta=0)
    assert time_elapsed_opt(d1, d2) is None

    d1 = Dmy(day=1, month=1, year=2000, prec=Precision.AFTER, delta=0)
    d2 = Dmy(day=1, month=1, year=2010, prec=Precision.SURE, delta=0)
    elapsed = time_elapsed_opt(d1, d2)
    assert elapsed is not None
    assert elapsed.year == 10
    assert elapsed.prec == Precision.BEFORE
    
    d1 = Dmy(day=1, month=1, year=2000, prec=Precision.BEFORE, delta=0)
    d2 = Dmy(day=1, month=1, year=2010, prec=Precision.SURE, delta=0)
    elapsed = time_elapsed_opt(d1, d2)
    assert elapsed is not None
    assert elapsed.year == 10
    assert elapsed.prec == Precision.AFTER
    
    d1 = Dmy(day=1, month=1, year=2000, prec=Precision.SURE, delta=0)
    d2 = Dmy(day=1, month=1, year=2010, prec=Precision.SURE, delta=0)
    elapsed = time_elapsed_opt(d1, d2)
    assert elapsed is not None
    assert elapsed.year == 10

def test_compare_dmy_equal():
    d1 = Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=0)
    d2 = Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=0)
    assert compare_dmy(d1, d2) == 0

def test_compare_dmy_different_years():
    d1 = Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=0)
    d2 = Dmy(day=15, month=6, year=2000, prec=Precision.SURE, delta=0)
    assert compare_dmy(d1, d2) < 0
    assert compare_dmy(d2, d1) > 0

def test_compare_dmy_different_months():
    d1 = Dmy(day=15, month=3, year=1990, prec=Precision.SURE, delta=0)
    d2 = Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=0)
    assert compare_dmy(d1, d2) < 0

def test_compare_dmy_different_days():
    d1 = Dmy(day=10, month=6, year=1990, prec=Precision.SURE, delta=0)
    d2 = Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=0)
    assert compare_dmy(d1, d2) < 0

def test_compare_dmy_with_precision():
    d1 = Dmy(day=0, month=0, year=1990, prec=Precision.SURE, delta=0)
    d2 = Dmy(day=0, month=0, year=1990, prec=Precision.ABOUT, delta=0)
    assert compare_dmy_opt(d1, d2, False) == 0
    
    d1 = Dmy(day=0, month=0, year=1990, prec=Precision.AFTER, delta=0)
    d2 = Dmy(day=0, month=0, year=1990, prec=Precision.AFTER, delta=0)
    assert compare_dmy_opt(d1, d2, False) == 0
    
    d1 = Dmy(day=0, month=0, year=1990, prec=Precision.BEFORE, delta=0)
    d2 = Dmy(day=0, month=0, year=1990, prec=Precision.BEFORE, delta=0)
    assert compare_dmy_opt(d1, d2, False) == 0
    
    d1 = Dmy(day=0, month=0, year=1990, prec=Precision.BEFORE, delta=0)
    d2 = Dmy(day=0, month=0, year=1990, prec=Precision.SURE, delta=0)
    assert compare_dmy_opt(d1, d2, False) == -1
    
    d1 = Dmy(day=0, month=0, year=1990, prec=Precision.SURE, delta=0)
    d2 = Dmy(day=0, month=0, year=1990, prec=Precision.AFTER, delta=0)
    assert compare_dmy_opt(d1, d2, False) == -1
    
    d1 = Dmy(day=0, month=0, year=1990, prec=Precision.AFTER, delta=0)
    d2 = Dmy(day=0, month=0, year=1990, prec=Precision.SURE, delta=0)
    assert compare_dmy_opt(d1, d2, False) == 1
    
    d1 = Dmy(day=0, month=0, year=1990, prec=Precision.SURE, delta=0)
    d2 = Dmy(day=0, month=0, year=1990, prec=Precision.BEFORE, delta=0)
    assert compare_dmy_opt(d1, d2, False) == 1
    
    d1 = Dmy(day=15, month=6, year=1990, prec=Precision.BEFORE, delta=0)
    d2 = Dmy(day=15, month=6, year=1990, prec=Precision.AFTER, delta=0)
    assert compare_dmy(d1, d2) < 0

def test_compare_dmy_strict_not_comparable():
    d1 = Dmy(day=15, month=6, year=1990, prec=Precision.AFTER, delta=0)
    d2 = Dmy(day=20, month=6, year=1990, prec=Precision.BEFORE, delta=0)
    with pytest.raises(NotComparable):
        compare_dmy(d1, d2, strict=True)

def test_compare_date_greg():
    d1 = DateGreg(dmy=Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=0), calendar=Calendar.GREGORIAN)
    d2 = DateGreg(dmy=Dmy(day=20, month=6, year=1990, prec=Precision.SURE, delta=0), calendar=Calendar.GREGORIAN)
    assert compare_date(d1, d2) < 0

def test_compare_date_text():
    t1 = DateText(text="some date")
    t2 = DateText(text="other date")
    assert compare_date(t1, t2) == 0

def test_compare_date_greg_vs_text():
    d = DateGreg(dmy=Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=0), calendar=Calendar.GREGORIAN)
    t = DateText(text="some date")
    assert compare_date(d, t) > 0
    assert compare_date(t, d) < 0

def test_cdate_to_dmy_opt():
    cd = CdateGregorian(value=compress(Dmy(day=15, month=6, year=1990, prec=Precision.SURE, delta=0)))
    dmy = cdate_to_dmy_opt(cd)
    assert dmy is not None
    assert dmy.day == 15
    assert dmy.month == 6
    assert dmy.year == 1990

    cd_text = CdateText(text="some date")
    assert cdate_to_dmy_opt(cd_text) is None
