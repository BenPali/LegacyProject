import pytest
from lib.calendar import (
    sdn_of_gregorian, gregorian_of_sdn,
    sdn_of_julian, julian_of_sdn,
    sdn_of_french, french_of_sdn,
    sdn_of_hebrew, hebrew_of_sdn,
    gregorian_of_julian, julian_of_gregorian,
    gregorian_of_french, french_of_gregorian,
    gregorian_of_hebrew, hebrew_of_gregorian,
    moon_phase_of_sdn, MoonPhase
)
from lib.adef import Dmy, Precision


class TestSDNGregorian:
    def test_sdn_of_gregorian_basic(self):
        d = Dmy(day=1, month=1, year=2000, delta=0, prec=Precision.SURE)
        sdn = sdn_of_gregorian(d)
        assert sdn > 0

    def test_gregorian_roundtrip(self):
        d1 = Dmy(day=15, month=6, year=1990, delta=0, prec=Precision.SURE)
        sdn = sdn_of_gregorian(d1)
        d2 = gregorian_of_sdn(Precision.SURE, sdn)
        assert d1.day == d2.day
        assert d1.month == d2.month
        assert d1.year == d2.year

    def test_gregorian_known_value(self):
        d = Dmy(day=1, month=1, year=1, delta=0, prec=Precision.SURE)
        sdn = sdn_of_gregorian(d)
        assert sdn > 0


class TestSDNJulian:
    def test_sdn_of_julian_basic(self):
        d = Dmy(day=1, month=1, year=2000, delta=0, prec=Precision.SURE)
        sdn = sdn_of_julian(d)
        assert sdn > 0

    def test_julian_roundtrip(self):
        d1 = Dmy(day=15, month=6, year=1990, delta=0, prec=Precision.SURE)
        sdn = sdn_of_julian(d1)
        d2 = julian_of_sdn(Precision.SURE, sdn)
        assert d1.day == d2.day
        assert d1.month == d2.month
        assert d1.year == d2.year


class TestSDNFrench:
    def test_sdn_of_french_basic(self):
        d = Dmy(day=1, month=1, year=1, delta=0, prec=Precision.SURE)
        sdn = sdn_of_french(d)
        assert sdn > 0

    def test_french_roundtrip(self):
        d1 = Dmy(day=10, month=5, year=10, delta=0, prec=Precision.SURE)
        sdn = sdn_of_french(d1)
        d2 = french_of_sdn(Precision.SURE, sdn)
        assert d1.day == d2.day
        assert d1.month == d2.month
        assert d1.year == d2.year


class TestSDNHebrew:
    def test_sdn_of_hebrew_basic(self):
        d = Dmy(day=1, month=1, year=5780, delta=0, prec=Precision.SURE)
        sdn = sdn_of_hebrew(d)
        assert sdn > 0

    def test_hebrew_roundtrip(self):
        d1 = Dmy(day=15, month=7, year=5780, delta=0, prec=Precision.SURE)
        sdn = sdn_of_hebrew(d1)
        d2 = hebrew_of_sdn(Precision.SURE, sdn)
        assert d1.month == d2.month
        assert d1.year == d2.year


class TestCalendarConversions:
    def test_gregorian_of_julian(self):
        jul = Dmy(day=1, month=1, year=1900, delta=0, prec=Precision.SURE)
        greg = gregorian_of_julian(jul)
        assert greg.year == 1900
        assert greg.month == 1
        assert greg.day > 1

    def test_julian_of_gregorian(self):
        greg = Dmy(day=14, month=1, year=1900, delta=0, prec=Precision.SURE)
        jul = julian_of_gregorian(greg)
        assert jul.year == 1900
        assert jul.month == 1

    def test_gregorian_french_roundtrip(self):
        greg1 = Dmy(day=22, month=9, year=1792, delta=0, prec=Precision.SURE)
        french = french_of_gregorian(greg1)
        greg2 = gregorian_of_french(french)
        assert abs(greg1.day - greg2.day) <= 2
        assert greg1.month == greg2.month or abs(greg1.month - greg2.month) == 1

    def test_gregorian_hebrew_conversion(self):
        greg = Dmy(day=1, month=1, year=2000, delta=0, prec=Precision.SURE)
        heb = hebrew_of_gregorian(greg)
        assert heb.year >= 5700


class TestMoonPhase:
    def test_moon_phase_of_sdn(self):
        sdn = 2451545
        phase_info, moon_age = moon_phase_of_sdn(sdn)
        assert moon_age >= 0
        assert moon_age < 30

    def test_moon_age_range(self):
        for sdn in range(2451545, 2451575):
            phase_info, moon_age = moon_phase_of_sdn(sdn)
            assert 0 <= moon_age < 30
