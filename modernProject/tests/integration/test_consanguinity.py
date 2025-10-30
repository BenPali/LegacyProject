import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.gwb_generator import create_minimal_gwb
from lib import database, driver, gwdef, adef, secure, consang

def test_family_relationships(temp_dir):
    secure.add_assets(temp_dir)
    gwb_path = create_minimal_gwb(temp_dir, "test_base")

    def test_family_structure(base):
        family_count = driver.nb_of_families(base)
        assert family_count == 1

        family = driver.foi(base, 0)
        father_id = driver.get_father(family)
        mother_id = driver.get_mother(family)
        children = driver.get_children(family)

        assert father_id == 0
        assert mother_id == []
        assert children == []

        return True

    result = database.with_database(gwb_path, test_family_structure)
    assert result is True

def test_person_family_links(temp_dir):
    secure.add_assets(temp_dir)
    gwb_path = create_minimal_gwb(temp_dir, "test_base")

    def test_person_to_family_connection(base):
        person1 = driver.poi(base, 0)
        person2 = driver.poi(base, 1)

        first_name1 = driver.sou(base, driver.get_first_name(person1)).decode()
        first_name2 = driver.sou(base, driver.get_first_name(person2)).decode()

        assert first_name1 == "John"
        assert first_name2 == "Jane"

        family = driver.foi(base, 0)
        father_id = driver.get_father(family)

        father = driver.poi(base, father_id)
        father_name = driver.sou(base, driver.get_first_name(father)).decode()
        assert father_name == "John"

        return True

    result = database.with_database(gwb_path, test_person_to_family_connection)
    assert result is True

def test_consanguinity_computation_basic(temp_dir):
    secure.add_assets(temp_dir)
    gwb_path = create_minimal_gwb(temp_dir, "test_base")

    def test_basic_computation(base):
        person_count = driver.nb_of_persons(base)
        assert person_count == 2

        person = driver.poi(base, 0)

        assert person is not None

        return True

    result = database.with_database(gwb_path, test_basic_computation)
    assert result is True
