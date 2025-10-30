import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.gwb_generator import create_minimal_gwb
from lib import database, driver, secure, name, gutil

def test_name_search_workflow(temp_dir):
    secure.add_assets(temp_dir)
    gwb_path = create_minimal_gwb(temp_dir, "search_test")

    def search_by_name(base):
        target_name = "John"
        crushed_target = name.crush(target_name)

        found_persons = []
        person_count = driver.nb_of_persons(base)

        for i in range(person_count):
            person = driver.poi(base, i)
            first_name = driver.sou(base, driver.get_first_name(person))
            if isinstance(first_name, bytes):
                first_name = first_name.decode()

            crushed_first = name.crush(first_name)

            if crushed_first == crushed_target:
                found_persons.append((i, first_name))

        assert len(found_persons) >= 1
        assert found_persons[0][1] == "John"

        return True

    result = database.with_database(gwb_path, search_by_name)
    assert result is True

def test_surname_search_workflow(temp_dir):
    secure.add_assets(temp_dir)
    gwb_path = create_minimal_gwb(temp_dir, "surname_test")

    def search_by_surname(base):
        target_surname = "Doe"
        crushed_target = name.crush(target_surname)

        found_persons = []
        person_count = driver.nb_of_persons(base)

        for i in range(person_count):
            person = driver.poi(base, i)
            surname = driver.sou(base, driver.get_surname(person))
            if isinstance(surname, bytes):
                surname = surname.decode()

            crushed_surname = name.crush(surname)

            if crushed_surname == crushed_target:
                found_persons.append((i, surname))

        assert len(found_persons) >= 1
        assert found_persons[0][1] == "Doe"

        return True

    result = database.with_database(gwb_path, search_by_surname)
    assert result is True

def test_name_normalization_workflow(temp_dir):
    secure.add_assets(temp_dir)
    gwb_path = create_minimal_gwb(temp_dir, "normalize_test")

    def test_name_normalization(base):
        person = driver.poi(base, 0)
        first_name = driver.sou(base, driver.get_first_name(person))
        if isinstance(first_name, bytes):
            first_name = first_name.decode()

        assert first_name == "John"

        normalized = name.lower(first_name)
        assert normalized == "john"

        crushed = name.crush(first_name)
        crushed_upper = name.crush("JOHN")
        crushed_lower = name.crush("john")

        assert crushed == crushed_upper
        assert crushed == crushed_lower

        return True

    result = database.with_database(gwb_path, test_name_normalization)
    assert result is True
