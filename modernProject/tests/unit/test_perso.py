import pytest
import math
from unittest.mock import Mock, MagicMock, patch

from lib import perso
from lib import config
from lib import driver
from lib import gwdef
from lib import util


class TestConstants:
    def test_max_im_wid(self):
        assert perso.MAX_IM_WID == 240

    def test_infinite(self):
        assert perso.INFINITE == 10000


class TestRound2Dec:
    def test_round_basic(self):
        assert perso.round_2_dec(1.234) == 1.23

    def test_round_up(self):
        assert perso.round_2_dec(1.235) == 1.24

    def test_round_down(self):
        assert perso.round_2_dec(1.234) == 1.23

    def test_round_integer(self):
        assert perso.round_2_dec(5.0) == 5.0

    def test_round_negative(self):
        assert perso.round_2_dec(-3.456) == -3.46


class TestGenerationPersonClasses:
    def test_gp_person(self):
        gp = perso.GP_person(1, 100, 50)
        assert gp.sosa == 1
        assert gp.iper == 100
        assert gp.ifam == 50

    def test_gp_same(self):
        gp = perso.GP_same(2, 3, 100)
        assert gp.sosa1 == 2
        assert gp.sosa2 == 3
        assert gp.iper == 100

    def test_gp_interv(self):
        gp = perso.GP_interv((1, 10))
        assert gp.interval == (1, 10)

    def test_gp_missing(self):
        gp = perso.GP_missing(5, 200)
        assert gp.sosa == 5
        assert gp.iper == 200


class TestHidePerson:
    def test_hide_person_not_authorized(self):
        conf = Mock()
        base = Mock()
        p = Mock()
        with patch('lib.util.authorized_age', return_value=False):
            with patch('lib.util.is_hide_names', return_value=False):
                assert perso.hide_person(conf, base, p) is True

    def test_hide_person_hidden_names(self):
        conf = Mock()
        base = Mock()
        p = Mock()
        with patch('lib.util.authorized_age', return_value=True):
            with patch('lib.util.is_hide_names', return_value=True):
                assert perso.hide_person(conf, base, p) is True

    def test_hide_person_visible(self):
        conf = Mock()
        base = Mock()
        p = Mock()
        with patch('lib.util.authorized_age', return_value=True):
            with patch('lib.util.is_hide_names', return_value=False):
                assert perso.hide_person(conf, base, p) is False


class TestGetDeathText:
    def test_death_text_not_authorized(self):
        conf = Mock()
        p = Mock()
        result = perso.get_death_text(conf, p, False)
        assert result == ""

    def test_death_text_unspecified(self):
        conf = Mock()
        p = Mock()
        death = gwdef.DeathWithReason(gwdef.DeathReason.UNSPECIFIED, None)
        with patch('lib.driver.get_sex', return_value=gwdef.Sex.MALE):
            with patch('lib.driver.get_death', return_value=death):
                with patch('lib.util.index_of_sex', return_value=0):
                    with patch('lib.util.transl_nth', return_value="died"):
                        result = perso.get_death_text(conf, p, True)
                        assert result == "died"

    def test_death_text_murdered(self):
        conf = Mock()
        p = Mock()
        death = gwdef.DeathWithReason(gwdef.DeathReason.MURDERED, None)
        with patch('lib.driver.get_sex', return_value=gwdef.Sex.MALE):
            with patch('lib.driver.get_death', return_value=death):
                with patch('lib.util.index_of_sex', return_value=0):
                    with patch('lib.util.transl_nth', return_value="murdered"):
                        result = perso.get_death_text(conf, p, True)
                        assert result == "murdered"

    def test_death_text_killed(self):
        conf = Mock()
        p = Mock()
        death = gwdef.DeathWithReason(gwdef.DeathReason.KILLED, None)
        with patch('lib.driver.get_sex', return_value=gwdef.Sex.MALE):
            with patch('lib.driver.get_death', return_value=death):
                with patch('lib.util.index_of_sex', return_value=0):
                    with patch('lib.util.transl_nth', return_value="killed (in action)"):
                        result = perso.get_death_text(conf, p, True)
                        assert result == "killed (in action)"

    def test_death_text_executed(self):
        conf = Mock()
        p = Mock()
        death = gwdef.DeathWithReason(gwdef.DeathReason.EXECUTED, None)
        with patch('lib.driver.get_sex', return_value=gwdef.Sex.MALE):
            with patch('lib.driver.get_death', return_value=death):
                with patch('lib.util.index_of_sex', return_value=0):
                    with patch('lib.util.transl_nth', return_value="executed (legally killed)"):
                        result = perso.get_death_text(conf, p, True)
                        assert result == "executed (legally killed)"

    def test_death_text_disappeared(self):
        conf = Mock()
        p = Mock()
        death = gwdef.DeathWithReason(gwdef.DeathReason.DISAPPEARED, None)
        with patch('lib.driver.get_sex', return_value=gwdef.Sex.MALE):
            with patch('lib.driver.get_death', return_value=death):
                with patch('lib.util.index_of_sex', return_value=0):
                    with patch('lib.util.transl_nth', return_value="disappeared"):
                        result = perso.get_death_text(conf, p, True)
                        assert result == "disappeared"

    def test_death_text_dead_young(self):
        conf = Mock()
        p = Mock()
        death = gwdef.DeadYoung()
        with patch('lib.driver.get_sex', return_value=gwdef.Sex.MALE):
            with patch('lib.driver.get_death', return_value=death):
                with patch('lib.util.index_of_sex', return_value=0):
                    with patch('lib.util.transl_nth', return_value="died young"):
                        result = perso.get_death_text(conf, p, True)
                        assert result == "died young"

    def test_death_text_dead_dont_know_when(self):
        conf = Mock()
        p = Mock()
        death = gwdef.DeadDontKnowWhen()
        with patch('lib.driver.get_sex', return_value=gwdef.Sex.MALE):
            with patch('lib.driver.get_death', return_value=death):
                with patch('lib.util.index_of_sex', return_value=0):
                    with patch('lib.util.transl_nth', return_value="died"):
                        result = perso.get_death_text(conf, p, True)
                        assert result == "died"


class TestGetBaptismText:
    def test_baptism_text_not_authorized(self):
        conf = Mock()
        p = Mock()
        result = perso.get_baptism_text(conf, p, False)
        assert result == ""

    def test_baptism_text_authorized(self):
        conf = Mock()
        p = Mock()
        with patch('lib.driver.get_sex', return_value=gwdef.Sex.MALE):
            with patch('lib.util.index_of_sex', return_value=0):
                with patch('lib.util.transl_nth', return_value="baptized"):
                    result = perso.get_baptism_text(conf, p, True)
                    assert result == "baptized"


class TestGetBirthText:
    def test_birth_text_not_authorized(self):
        conf = Mock()
        p = Mock()
        result = perso.get_birth_text(conf, p, False)
        assert result == ""

    def test_birth_text_authorized(self):
        conf = Mock()
        p = Mock()
        with patch('lib.driver.get_sex', return_value=gwdef.Sex.MALE):
            with patch('lib.util.index_of_sex', return_value=0):
                with patch('lib.util.transl_nth', return_value="born"):
                    result = perso.get_birth_text(conf, p, True)
                    assert result == "born"


class TestGetBurialText:
    def test_burial_text_not_authorized(self):
        conf = Mock()
        p = Mock()
        result = perso.get_burial_text(conf, p, False)
        assert result == ""

    def test_burial_text_authorized(self):
        conf = Mock()
        p = Mock()
        with patch('lib.driver.get_sex', return_value=gwdef.Sex.MALE):
            with patch('lib.util.index_of_sex', return_value=0):
                with patch('lib.util.transl_nth', return_value="buried"):
                    result = perso.get_burial_text(conf, p, True)
                    assert result == "buried"


class TestGetCremationText:
    def test_cremation_text_not_authorized(self):
        conf = Mock()
        p = Mock()
        result = perso.get_cremation_text(conf, p, False)
        assert result == ""

    def test_cremation_text_authorized(self):
        conf = Mock()
        p = Mock()
        with patch('lib.driver.get_sex', return_value=gwdef.Sex.MALE):
            with patch('lib.util.index_of_sex', return_value=0):
                with patch('lib.util.transl_nth', return_value="cremated"):
                    result = perso.get_cremation_text(conf, p, True)
                    assert result == "cremated"


class TestLimitDesc:
    def test_limit_desc_default(self):
        conf = Mock()
        conf.base_env = {}
        result = perso.limit_desc(conf)
        assert result == perso.INFINITE

    def test_limit_desc_custom(self):
        conf = Mock()
        conf.base_env = {"max_desc_level": "5"}
        result = perso.limit_desc(conf)
        assert result == 5

    def test_limit_desc_invalid(self):
        conf = Mock()
        conf.base_env = {"max_desc_level": "invalid"}
        result = perso.limit_desc(conf)
        assert result == perso.INFINITE


class TestWillPrint:
    def test_will_print_gp_person(self):
        gp = perso.GP_person(1, 100, 50)
        assert perso.will_print(gp) is True

    def test_will_print_gp_same(self):
        gp = perso.GP_same(2, 3, 100)
        assert perso.will_print(gp) is True

    def test_will_print_gp_missing(self):
        gp = perso.GP_missing(5, 200)
        assert perso.will_print(gp) is True

    def test_will_print_gp_interv(self):
        gp = perso.GP_interv((1, 10))
        assert perso.will_print(gp) is False


class TestStringOfMarriageText:
    def test_marriage_text_no_date_no_place(self):
        conf = Mock()
        base = Mock()
        fam = Mock()
        with patch('lib.driver.get_marriage', return_value=None):
            with patch('lib.driver.get_marriage_place', return_value=0):
                with patch('lib.driver.sou', return_value=""):
                    with patch('lib.date.od_of_cdate', return_value=None):
                        result = perso.string_of_marriage_text(conf, base, fam)
                        assert result == ""


class TestHelperFunctions:
    def test_bool_val(self):
        assert perso.bool_val(True) is True
        assert perso.bool_val(False) is False

    def test_str_val(self):
        assert perso.str_val("test") == "test"

    def test_null_val(self):
        assert perso.null_val() == ""

    def test_safe_val(self):
        assert perso.safe_val("test") == "test"


class TestImageSizeFunctions:
    def test_string_of_image_size(self):
        conf = Mock()
        base = Mock()
        p_auth_tuple = (Mock(), True)
        result = perso.string_of_image_size(conf, base, p_auth_tuple)
        assert result == ""

    def test_string_of_image_medium_size(self):
        conf = Mock()
        base = Mock()
        p_auth_tuple = (Mock(), True)
        result = perso.string_of_image_medium_size(conf, base, p_auth_tuple)
        assert result == ""

    def test_string_of_image_small_size(self):
        conf = Mock()
        base = Mock()
        p_auth_tuple = (Mock(), True)
        result = perso.string_of_image_small_size(conf, base, p_auth_tuple)
        assert result == ""


class TestDescendantFunctions:
    def test_get_descendants_at_level(self):
        base = Mock()
        p = Mock()
        result = perso.get_descendants_at_level(base, p, 2)
        assert result == []

    def test_make_desc_level_table(self):
        conf = Mock()
        base = Mock()
        p = Mock()
        desc_mark, fam_mark = perso.make_desc_level_table(conf, base, 5, p)
        assert desc_mark == {}
        assert fam_mark == {}

    def test_desc_level_max(self):
        base = Mock()
        desc_level_table_l = []
        result = perso.desc_level_max(base, desc_level_table_l)
        assert result == 0

    def test_max_descendant_level(self):
        base = Mock()
        desc_level_table_l = []
        result = perso.max_descendant_level(base, desc_level_table_l)
        assert result == 0


class TestGenerationFunctions:
    def test_next_generation(self):
        conf = Mock()
        base = Mock()
        mark = {}
        gpl = []
        result = perso.next_generation(conf, base, mark, gpl)
        assert result == []

    def test_next_generation2(self):
        conf = Mock()
        base = Mock()
        mark = {}
        gpl = []
        result = perso.next_generation2(conf, base, mark, gpl)
        assert result == []

    def test_get_all_generations(self):
        conf = Mock()
        base = Mock()
        p = Mock()
        result = perso.get_all_generations(conf, base, p)
        assert result == []


class TestDuplicationFunctions:
    def test_has_possible_duplications(self):
        conf = Mock()
        base = Mock()
        p = Mock()
        result = perso.has_possible_duplications(conf, base, p)
        assert result is False

    def test_first_possible_duplication(self):
        base = Mock()
        ip = 1
        excl_dup = ([], [])
        result = perso.first_possible_duplication(base, ip, excl_dup)
        assert result == perso.Dup.NO_DUP

    def test_excluded_possible_duplications(self):
        conf = Mock()
        result = perso.excluded_possible_duplications(conf)
        assert result == ([], [])


class TestListFunctions:
    def test_nobility_titles_list(self):
        conf = Mock()
        base = Mock()
        p = Mock()
        result = perso.nobility_titles_list(conf, base, p)
        assert result == []

    def test_build_surnames_list(self):
        conf = Mock()
        base = Mock()
        v = None
        p = Mock()
        result = perso.build_surnames_list(conf, base, v, p)
        assert result == []

    def test_build_list_eclair(self):
        conf = Mock()
        base = Mock()
        v = None
        p = Mock()
        result = perso.build_list_eclair(conf, base, v, p)
        assert result == []


class TestTreeFunctions:
    def test_enrich(self):
        lst1 = []
        lst2 = []
        result = perso.enrich(lst1, lst2)
        assert result == []

    def test_is_empty(self):
        lst = [perso.Cell.EMPTY, perso.Cell.EMPTY]
        assert perso.is_empty(lst) is True

    def test_is_empty_not_empty(self):
        lst = [perso.Cell.EMPTY, perso.Cell.FULL]
        assert perso.is_empty(lst) is False

    def test_enrich_tree(self):
        lst = []
        result = perso.enrich_tree(lst)
        assert result == []


class TestEnvironmentFunctions:
    def test_get_env(self):
        env = {"key": "value"}
        result = perso.get_env("key", env)
        assert result == "value"

    def test_get_env_missing(self):
        env = {}
        result = perso.get_env("key", env)
        assert result is None

    def test_mode_local_true(self):
        env = {"local": True}
        assert perso.mode_local(env) is True

    def test_mode_local_false(self):
        env = {}
        assert perso.mode_local(env) is False


class TestMiscFunctions:
    def test_has_history(self):
        conf = Mock()
        base = Mock()
        p = Mock()
        result = perso.has_history(conf, base, p, True)
        assert result is False

    def test_get_linked_page(self):
        conf = Mock()
        base = Mock()
        p = Mock()
        result = perso.get_linked_page(conf, base, p, "test")
        assert result == ""

    def test_compare_ls(self):
        result = perso.compare_ls([], [])
        assert result == 0

    def test_has_witness_for_event(self):
        conf = Mock()
        base = Mock()
        p = Mock()
        result = perso.has_witness_for_event(conf, base, p, "birth")
        assert result is False
