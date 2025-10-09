import pytest
from lib.adef import (
    Fix, NO_CONSANG, Calendar, Precision, Dmy2, PrecisionOrYear, PrecisionYearInt,
    Dmy, DateGreg, DateText, CdateGregorian, CdateJulian, CdateFrench, CdateHebrew,
    CdateText, CdateDate, CdateNone, Couple, couple, parent, parent_array,
    multi_couple, multi_parent, safe, escaped, encoded, as_string
)


class TestFix:
    def test_fix_creation(self):
        f = Fix(100)
        assert f.value == 100

    def test_fix_from_float(self):
        f = Fix.from_float(0.5)
        assert f.value == 500000

    def test_fix_to_float(self):
        f = Fix(1000000)
        assert f.to_float() == 1.0

    def test_fix_roundtrip(self):
        original = 0.123456
        f = Fix.from_float(original)
        result = f.to_float()
        assert abs(result - original) < 1e-6

    def test_fix_equality(self):
        f1 = Fix(100)
        f2 = Fix(100)
        f3 = Fix(200)
        assert f1 == f2
        assert f1 != f3

    def test_no_consang(self):
        assert NO_CONSANG.value == -1


class TestCalendar:
    def test_calendar_values(self):
        assert Calendar.GREGORIAN
        assert Calendar.JULIAN
        assert Calendar.FRENCH
        assert Calendar.HEBREW


class TestPrecision:
    def test_precision_values(self):
        assert Precision.SURE
        assert Precision.ABOUT
        assert Precision.MAYBE
        assert Precision.BEFORE
        assert Precision.AFTER


class TestDmy2:
    def test_dmy2_creation(self):
        d = Dmy2(day2=15, month2=8, year2=1990, delta2=0)
        assert d.day2 == 15
        assert d.month2 == 8
        assert d.year2 == 1990
        assert d.delta2 == 0

    def test_dmy2_immutable(self):
        d = Dmy2(day2=15, month2=8, year2=1990, delta2=0)
        with pytest.raises(AttributeError):
            d.day2 = 20


class TestPrecisionTypes:
    def test_precision_or_year(self):
        d2 = Dmy2(day2=1, month2=1, year2=2000, delta2=0)
        p = PrecisionOrYear(dmy2=d2)
        assert p.dmy2 == d2

    def test_precision_year_int(self):
        d2 = Dmy2(day2=1, month2=1, year2=2000, delta2=0)
        p = PrecisionYearInt(dmy2=d2)
        assert p.dmy2 == d2


class TestDmy:
    def test_dmy_creation(self):
        d = Dmy(day=15, month=8, year=1990, prec=Precision.SURE, delta=0)
        assert d.day == 15
        assert d.month == 8
        assert d.year == 1990
        assert d.prec == Precision.SURE
        assert d.delta == 0

    def test_dmy_with_precision_or_year(self):
        d2 = Dmy2(day2=1, month2=1, year2=2000, delta2=0)
        prec = PrecisionOrYear(dmy2=d2)
        d = Dmy(day=15, month=8, year=1990, prec=prec, delta=0)
        assert d.prec == prec


class TestDate:
    def test_date_greg(self):
        dmy = Dmy(day=15, month=8, year=1990, prec=Precision.SURE, delta=0)
        d = DateGreg(dmy=dmy, calendar=Calendar.GREGORIAN)
        assert d.dmy == dmy
        assert d.calendar == Calendar.GREGORIAN

    def test_date_text(self):
        d = DateText(text="around 1990")
        assert d.text == "around 1990"


class TestCdate:
    def test_cdate_gregorian(self):
        c = CdateGregorian(value=12345)
        assert c.value == 12345

    def test_cdate_julian(self):
        c = CdateJulian(value=12345)
        assert c.value == 12345

    def test_cdate_french(self):
        c = CdateFrench(value=12345)
        assert c.value == 12345

    def test_cdate_hebrew(self):
        c = CdateHebrew(value=12345)
        assert c.value == 12345

    def test_cdate_text(self):
        c = CdateText(text="about 1990")
        assert c.text == "about 1990"

    def test_cdate_date(self):
        dt = DateText(text="1990")
        c = CdateDate(date=dt)
        assert c.date == dt

    def test_cdate_none_singleton(self):
        c1 = CdateNone()
        c2 = CdateNone()
        assert c1 is c2


class TestCouple:
    def test_couple_creation(self):
        c = Couple(father="John", mother="Jane")
        assert c.father == "John"
        assert c.mother == "Jane"

    def test_couple_function(self):
        c = couple("John", "Jane")
        assert c.father == "John"
        assert c.mother == "Jane"

    def test_parent_function(self):
        arr = ["John", "Jane"]
        c = parent(arr)
        assert c.father == "John"
        assert c.mother == "Jane"

    def test_parent_function_invalid_length(self):
        with pytest.raises(ValueError):
            parent(["John"])

    def test_parent_array_function(self):
        c = Couple(father="John", mother="Jane")
        arr = parent_array(c)
        assert arr == ["John", "Jane"]

    def test_multi_couple(self):
        c = multi_couple("John", "Jane")
        assert c.father == "John"
        assert c.mother == "Jane"

    def test_multi_parent(self):
        arr = ["John", "Jane"]
        c = multi_parent(arr)
        assert c.father == "John"
        assert c.mother == "Jane"

    def test_multi_parent_invalid_length(self):
        with pytest.raises(ValueError):
            multi_parent(["John", "Jane", "Extra"])


class TestStringTypes:
    def test_safe_string(self):
        s = safe("test")
        assert s == "test"
        assert isinstance(s, str)

    def test_escaped_string(self):
        s = escaped("test")
        assert s == "test"
        assert isinstance(s, str)

    def test_encoded_string(self):
        s = encoded("test")
        assert s == "test"
        assert isinstance(s, str)

    def test_as_string(self):
        s = safe("test")
        result = as_string(s)
        assert result == "test"
        assert isinstance(result, str)


class TestFixEdgeCases:
    def test_fix_zero(self):
        f = Fix.from_float(0.0)
        assert f.to_float() == 0.0

    def test_fix_negative(self):
        f = Fix.from_float(-0.5)
        assert abs(f.to_float() - (-0.5)) < 1e-6

    def test_fix_large_value(self):
        f = Fix.from_float(1000.0)
        assert abs(f.to_float() - 1000.0) < 1e-3

    def test_fix_small_value(self):
        f = Fix.from_float(0.000001)
        assert abs(f.to_float() - 0.000001) < 1e-6
