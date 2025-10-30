import os
import sys
from pathlib import Path
import tempfile

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.gwb_generator import create_minimal_gwb
from lib import database, driver, gwdef, adef, secure, name, mutil

def test_database_string_operations(temp_dir):
    secure.add_assets(temp_dir)
    gwb_path = create_minimal_gwb(temp_dir, "test_base")

    def test_string_insertion_and_retrieval(base):
        new_string_content = "TestString"
        new_string_index = driver.insert_string(base, new_string_content)

        assert new_string_index > 0

        retrieved = driver.sou(base, new_string_index)
        assert retrieved == new_string_content

        return True

    result = database.with_database(gwb_path, test_string_insertion_and_retrieval, read_only=False)
    assert result is True

def test_database_name_processing_integration(temp_dir):
    secure.add_assets(temp_dir)
    gwb_path = create_minimal_gwb(temp_dir, "test_base")

    def test_name_operations(base):
        person = driver.poi(base, 0)
        first_name = driver.sou(base, driver.get_first_name(person)).decode()
        surname = driver.sou(base, driver.get_surname(person)).decode()

        assert first_name == "John"
        assert surname == "Doe"

        crushed_first = name.crush(first_name)
        crushed_surname = name.crush(surname)

        assert crushed_first == name.crush("JOHN")
        assert crushed_surname == name.crush("DOE")

        lower_first = name.lower(first_name)
        assert lower_first == "john"

        return True

    result = database.with_database(gwb_path, test_name_operations)
    assert result is True

def test_database_multiple_persons_access(temp_dir):
    secure.add_assets(temp_dir)
    gwb_path = create_minimal_gwb(temp_dir, "test_base")

    def test_person_iteration(base):
        person_count = driver.nb_of_persons(base)
        assert person_count == 2

        persons_data = []
        for i in range(person_count):
            person = driver.poi(base, i)
            first_name = driver.sou(base, driver.get_first_name(person)).decode()
            surname = driver.sou(base, driver.get_surname(person)).decode()
            persons_data.append((first_name, surname))

        assert len(persons_data) == 2
        assert persons_data[0] == ("John", "Doe")
        assert persons_data[1] == ("Jane", "Smith")

        return True

    result = database.with_database(gwb_path, test_person_iteration)
    assert result is True
