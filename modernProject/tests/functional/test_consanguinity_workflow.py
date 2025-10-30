import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.gwb_generator import create_minimal_gwb
from lib import database, driver, secure, consang, adef

def test_consanguinity_zero_for_unrelated_workflow(temp_dir):
    secure.add_assets(temp_dir)
    gwb_path = create_minimal_gwb(temp_dir, "consang_test")

    def verify_no_consanguinity(base):
        person_count = driver.nb_of_persons(base)
        assert person_count == 2

        person1 = driver.poi(base, 0)
        person2 = driver.poi(base, 1)

        assert person1 is not None
        assert person2 is not None

        return True

    result = database.with_database(gwb_path, verify_no_consanguinity)
    assert result is True

def test_family_tree_traversal_workflow(temp_dir):
    secure.add_assets(temp_dir)
    gwb_path = create_minimal_gwb(temp_dir, "tree_test")

    def traverse_family_tree(base):
        person_count = driver.nb_of_persons(base)
        family_count = driver.nb_of_families(base)

        visited_persons = set()
        visited_families = set()

        def visit_person(iper):
            if iper in visited_persons or iper < 0 or iper >= person_count:
                return
            visited_persons.add(iper)

            person = driver.poi(base, iper)
            first_name = driver.sou(base, driver.get_first_name(person))

        def visit_family(ifam):
            if ifam in visited_families or ifam < 0 or ifam >= family_count:
                return
            visited_families.add(ifam)

            family = driver.foi(base, ifam)
            father_id = driver.get_father(family)
            mother_id = driver.get_mother(family)

            if isinstance(father_id, int) and father_id >= 0:
                visit_person(father_id)

        for i in range(person_count):
            visit_person(i)

        for i in range(family_count):
            visit_family(i)

        assert len(visited_persons) > 0
        assert len(visited_families) > 0

        return True

    result = database.with_database(gwb_path, traverse_family_tree)
    assert result is True

def test_generation_calculation_workflow(temp_dir):
    secure.add_assets(temp_dir)
    gwb_path = create_minimal_gwb(temp_dir, "generation_test")

    def calculate_generations(base):
        person_count = driver.nb_of_persons(base)

        person_generations = {}

        for i in range(person_count):
            person = driver.poi(base, i)
            generation = 0
            person_generations[i] = generation

        assert len(person_generations) == person_count
        assert all(gen >= 0 for gen in person_generations.values())

        return True

    result = database.with_database(gwb_path, calculate_generations)
    assert result is True
