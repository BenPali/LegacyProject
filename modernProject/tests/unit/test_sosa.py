import pytest
from lib.sosa import Sosa, of_int, to_int


def test_sosa_creation():
    sosa = Sosa(42)
    assert sosa.value == 42


def test_sosa_creation_from_string():
    sosa = Sosa("123")
    assert sosa.value == 123


def test_sosa_str():
    sosa = Sosa(42)
    assert str(sosa) == "42"


def test_sosa_repr():
    sosa = Sosa(42)
    assert repr(sosa) == "Sosa(42)"


def test_sosa_equality():
    sosa1 = Sosa(42)
    sosa2 = Sosa(42)
    sosa3 = Sosa(43)
    assert sosa1 == sosa2
    assert sosa1 != sosa3


def test_sosa_equality_with_non_sosa():
    sosa = Sosa(42)
    assert sosa != 42
    assert sosa != "42"
    assert sosa != None


def test_sosa_hash():
    sosa1 = Sosa(42)
    sosa2 = Sosa(42)
    sosa3 = Sosa(43)
    assert hash(sosa1) == hash(sosa2)
    assert hash(sosa1) != hash(sosa3)


def test_sosa_in_set():
    sosa1 = Sosa(1)
    sosa2 = Sosa(2)
    sosa3 = Sosa(1)
    sosa_set = {sosa1, sosa2, sosa3}
    assert len(sosa_set) == 2


def test_sosa_in_dict():
    sosa1 = Sosa(1)
    sosa2 = Sosa(2)
    sosa_dict = {sosa1: "first", sosa2: "second"}
    assert sosa_dict[Sosa(1)] == "first"
    assert sosa_dict[Sosa(2)] == "second"


def test_of_int():
    sosa = of_int(100)
    assert isinstance(sosa, Sosa)
    assert sosa.value == 100


def test_to_int():
    sosa = Sosa(200)
    value = to_int(sosa)
    assert value == 200
    assert isinstance(value, int)


def test_round_trip():
    original = 42
    sosa = of_int(original)
    result = to_int(sosa)
    assert result == original
