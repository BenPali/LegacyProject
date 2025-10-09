import pytest
import json
from modernProject.lib import json_converter


def test_to_json_simple_dict():
    obj = {"name": "test", "value": 42}
    result = json_converter.to_json(obj)
    assert isinstance(result, str)
    parsed = json.loads(result)
    assert parsed == obj


def test_to_json_formatting():
    obj = {"a": 1, "b": 2}
    result = json_converter.to_json(obj)
    assert "\n" in result
    assert "  " in result


def test_to_json_unicode():
    obj = {"name": "François", "city": "Москва"}
    result = json_converter.to_json(obj)
    assert "François" in result
    assert "Москва" in result


def test_from_json_simple():
    json_str = '{"name": "test", "value": 42}'
    result = json_converter.from_json(json_str)
    assert result == {"name": "test", "value": 42}


def test_from_json_formatted():
    json_str = '''
    {
      "name": "test",
      "value": 42
    }
    '''
    result = json_converter.from_json(json_str)
    assert result == {"name": "test", "value": 42}


def test_from_json_unicode():
    json_str = '{"name": "François", "city": "Москва"}'
    result = json_converter.from_json(json_str)
    assert result["name"] == "François"
    assert result["city"] == "Москва"


def test_person_to_dict():
    class Person:
        def __init__(self, first_name, surname, occ):
            self.first_name = first_name
            self.surname = surname
            self.occ = occ

    person = Person("John", "Doe", 42)
    result = json_converter.person_to_dict(person)

    assert result == {
        "first_name": "John",
        "surname": "Doe",
        "occ": 42
    }


def test_person_to_dict_missing_attrs():
    class MinimalPerson:
        pass

    person = MinimalPerson()
    result = json_converter.person_to_dict(person)

    assert result == {
        "first_name": "",
        "surname": "",
        "occ": 0
    }


def test_person_to_dict_partial():
    class PartialPerson:
        def __init__(self):
            self.first_name = "Jane"

    person = PartialPerson()
    result = json_converter.person_to_dict(person)

    assert result == {
        "first_name": "Jane",
        "surname": "",
        "occ": 0
    }


def test_family_to_dict():
    class Family:
        def __init__(self, marriage, relation):
            self.marriage = marriage
            self.relation = relation

    family = Family("1990-01-01", "Married")
    result = json_converter.family_to_dict(family)

    assert result == {
        "marriage": "1990-01-01",
        "relation": "Married"
    }


def test_family_to_dict_missing_attrs():
    class MinimalFamily:
        pass

    family = MinimalFamily()
    result = json_converter.family_to_dict(family)

    assert result == {
        "marriage": None,
        "relation": None
    }


def test_family_to_dict_partial():
    class PartialFamily:
        def __init__(self):
            self.marriage = "2000-05-15"

    family = PartialFamily()
    result = json_converter.family_to_dict(family)

    assert result == {
        "marriage": "2000-05-15",
        "relation": None
    }


def test_round_trip():
    original = {"name": "Test", "values": [1, 2, 3]}
    json_str = json_converter.to_json(original)
    result = json_converter.from_json(json_str)
    assert result == original
