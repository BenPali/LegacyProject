import os
import sys
import tempfile
import shutil
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.gwb_generator import create_minimal_gwb
from lib import database, driver, gwdef, adef, secure

def test_database_create_and_open(temp_dir):
    secure.add_assets(temp_dir)
    gwb_path = create_minimal_gwb(temp_dir, "test_base")

    def check_base(base):
        assert driver.nb_of_persons(base) == 2
        assert driver.nb_of_families(base) == 1
        return True

    result = database.with_database(gwb_path, check_base)
    assert result is True

def test_database_person_lifecycle(temp_dir):
    secure.add_assets(temp_dir)
    gwb_path = create_minimal_gwb(temp_dir, "test_base")

    def check_persons(base):
        initial_count = driver.nb_of_persons(base)
        assert initial_count == 2

        person = driver.poi(base, 0)
        assert driver.sou(base, driver.get_first_name(person)).decode() == "John"
        assert driver.sou(base, driver.get_surname(person)).decode() == "Doe"
        sex = driver.get_sex(person)
        assert sex == 0

        person2 = driver.poi(base, 1)
        assert driver.sou(base, driver.get_first_name(person2)).decode() == "Jane"
        assert driver.sou(base, driver.get_surname(person2)).decode() == "Smith"
        sex2 = driver.get_sex(person2)
        assert sex2 == 1
        return True

    result = database.with_database(gwb_path, check_persons)
    assert result is True

def test_database_family_lifecycle(temp_dir):
    secure.add_assets(temp_dir)
    gwb_path = create_minimal_gwb(temp_dir, "test_base")

    def check_families(base):
        initial_count = driver.nb_of_families(base)
        assert initial_count == 1

        family = driver.foi(base, 0)
        assert family is not None
        relation = driver.get_relation(family)
        assert relation == 0
        divorce = driver.get_divorce(family)
        assert divorce == 0

        father_id = driver.get_father(family)
        assert father_id == 0
        mother_id = driver.get_mother(family)
        assert mother_id == []
        return True

    result = database.with_database(gwb_path, check_families)
    assert result is True
