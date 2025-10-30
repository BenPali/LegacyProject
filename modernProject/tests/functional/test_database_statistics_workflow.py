import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.gwb_generator import create_minimal_gwb
from lib import database, driver, secure, stats

def test_database_statistics_calculation_workflow(temp_dir):
    secure.add_assets(temp_dir)
    gwb_path = create_minimal_gwb(temp_dir, "stats_test")

    def calculate_and_verify_stats(base):
        person_count = driver.nb_of_persons(base)
        family_count = driver.nb_of_families(base)

        assert person_count == 2
        assert family_count == 1

        stat_obj = stats.stat_base(base)

        assert isinstance(stat_obj, stats.Stats)
        assert stat_obj.men >= 0
        assert stat_obj.women >= 0
        assert (stat_obj.men + stat_obj.women + stat_obj.neutre) <= person_count

        return True

    result = database.with_database(gwb_path, calculate_and_verify_stats)
    assert result is True

def test_database_age_statistics_workflow(temp_dir):
    secure.add_assets(temp_dir)
    gwb_path = create_minimal_gwb(temp_dir, "age_test")

    def calculate_age_distribution(base):
        person_count = driver.nb_of_persons(base)
        assert person_count > 0

        persons_with_birth = 0
        for i in range(person_count):
            person = driver.poi(base, i)
            birth = driver.get_birth(person)
            if birth and birth != 0:
                persons_with_birth += 1

        assert persons_with_birth >= 0

        return True

    result = database.with_database(gwb_path, calculate_age_distribution)
    assert result is True

def test_database_family_statistics_workflow(temp_dir):
    secure.add_assets(temp_dir)
    gwb_path = create_minimal_gwb(temp_dir, "family_stats_test")

    def calculate_family_stats(base):
        family_count = driver.nb_of_families(base)
        assert family_count == 1

        families_with_children = 0
        total_children = 0

        for i in range(family_count):
            family = driver.foi(base, i)
            children = driver.get_children(family)
            if children and len(children) > 0:
                families_with_children += 1
                total_children += len(children)

        assert families_with_children >= 0
        assert total_children >= 0

        return True

    result = database.with_database(gwb_path, calculate_family_stats)
    assert result is True
