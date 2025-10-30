import sys
from io import StringIO
from lib import consang_all
from lib import consang
from lib import adef
from lib.gwdef import GenAscend
from lib.collection import Marker


class MockBase:
    def __init__(self, persons, families):
        self.persons = persons
        self.families = families
        self.nb_persons = len(persons)
        self.patches_committed = False

    def get_person(self, i):
        return self.persons.get(i)

    def get_family(self, i):
        return self.families.get(i)

    def p_first_name(self, p):
        return getattr(p, 'first_name', 'John')

    def p_surname(self, p):
        return getattr(p, 'surname', 'Doe')

    def get_occ(self, p):
        return 0


class MockPerson:
    def __init__(self, parents=None, consang=None):
        self.parents = parents
        self.consang = consang if consang is not None else adef.NO_CONSANG
        self.gen_ascend = GenAscend(parents=parents, consang=self.consang)


class MockFamily:
    def __init__(self, father, mother):
        self.father = father
        self.mother = mother


class MockDriver:
    @staticmethod
    def load_ascends_array(base):
        pass

    @staticmethod
    def load_couples_array(base):
        pass

    @staticmethod
    def ipers(base):
        from lib.collection import Collection
        keys = list(base.persons.keys())
        return Collection(length=len(keys), get=lambda i: keys[i] if 0 <= i < len(keys) else None)

    @staticmethod
    def ifams(base):
        from lib.collection import Collection
        keys = list(base.families.keys())
        return Collection(length=len(keys), get=lambda i: keys[i] if 0 <= i < len(keys) else None)

    @staticmethod
    def poi(base, i):
        return base.get_person(i)

    @staticmethod
    def foi(base, i):
        return base.get_family(i)

    @staticmethod
    def get_parents(person):
        return getattr(person, 'parents', None)

    @staticmethod
    def get_father(family):
        return family.father

    @staticmethod
    def get_mother(family):
        return family.mother

    @staticmethod
    def get_consang(person):
        return getattr(person, 'consang', adef.NO_CONSANG)

    @staticmethod
    def gen_ascend_of_person(person):
        return person.gen_ascend

    @staticmethod
    def patch_ascend(base, i, ascend):
        base.persons[i].consang = ascend.consang

    @staticmethod
    def commit_patches(base):
        base.patches_committed = True

    @staticmethod
    def nb_of_persons(base):
        return base.nb_persons

    @staticmethod
    def iper_marker(ipers, default_value):
        data = {}
        return Marker(
            get=lambda k: data.get(k, default_value),
            set=lambda k, v: data.__setitem__(k, v)
        )

    @staticmethod
    def ifam_marker(ifams, default_value):
        data = {}
        return Marker(
            get=lambda k: data.get(k, default_value),
            set=lambda k, v: data.__setitem__(k, v)
        )


def test_start_run_finish_progress():
    consang_all._start_progress()
    assert consang_all._progress_bar is not None

    consang_all._run_progress(50, 100)
    assert consang_all._progress_bar is not None

    consang_all._finish_progress()
    assert consang_all._progress_bar is None


def test_trace_verbosity_0():
    old_stderr = sys.stderr
    try:
        sys.stderr = StringIO()
        consang_all._trace(0, 10, 100)
        output = sys.stderr.getvalue()
        assert output == ""
    finally:
        sys.stderr = old_stderr


def test_trace_verbosity_1():
    old_stderr = sys.stderr
    try:
        sys.stderr = StringIO()
        consang_all._start_progress()
        consang_all._trace(1, 10, 100)
        consang_all._finish_progress()
    finally:
        sys.stderr = old_stderr


def test_trace_verbosity_2():
    old_stderr = sys.stderr
    try:
        sys.stderr = StringIO()
        consang_all._trace(2, 10, 100)
        output = sys.stderr.getvalue()
        assert "10" in output
    finally:
        sys.stderr = old_stderr


def test_consang_array():
    from lib import driver as RealDriver
    original_gen_ascend_of_person = RealDriver.gen_ascend_of_person
    original_load_ascends_array = RealDriver.load_ascends_array
    original_load_couples_array = RealDriver.load_couples_array
    original_poi = RealDriver.poi
    original_get_parents = RealDriver.get_parents
    original_get_consang = RealDriver.get_consang
    original_gen_ascend_of_person = RealDriver.gen_ascend_of_person
    original_patch_ascend = RealDriver.patch_ascend

    try:
        RealDriver.gen_ascend_of_person = MockDriver.gen_ascend_of_person
        RealDriver.load_ascends_array = MockDriver.load_ascends_array
        RealDriver.load_couples_array = MockDriver.load_couples_array
        RealDriver.poi = MockDriver.poi
        RealDriver.get_parents = MockDriver.get_parents
        RealDriver.get_consang = MockDriver.get_consang
        RealDriver.gen_ascend_of_person = MockDriver.gen_ascend_of_person
        RealDriver.patch_ascend = MockDriver.patch_ascend

        p0 = MockPerson(parents=None)
        base = MockBase(persons={0: p0}, families={})

        fget, cget, cset, patched = consang_all._consang_array(base)

        assert fget(0) is None
        assert cget(0) == adef.NO_CONSANG
        assert patched[0] is False

        cset(0, adef.Fix.from_float(0.25))
        assert patched[0] is True
        assert abs(cget(0).to_float() - 0.25) < 0.0001

    finally:
        RealDriver.gen_ascend_of_person = original_gen_ascend_of_person
        RealDriver.load_ascends_array = original_load_ascends_array
        RealDriver.load_couples_array = original_load_couples_array
        RealDriver.poi = original_poi
        RealDriver.get_parents = original_get_parents
        RealDriver.get_consang = original_get_consang
        RealDriver.gen_ascend_of_person = original_gen_ascend_of_person
        RealDriver.patch_ascend = original_patch_ascend


def test_compute_empty_base():
    from lib import driver as RealDriver
    from lib import consang as RealConsang
    original_ipers = RealDriver.ipers
    original_ifams = RealDriver.ifams
    original_ifam_marker = RealDriver.ifam_marker
    original_commit_patches = RealDriver.commit_patches
    original_topological_sort = RealConsang.topological_sort
    original_make_relationship_info = RealConsang.make_relationship_info

    try:
        RealDriver.ipers = MockDriver.ipers
        RealDriver.ifams = MockDriver.ifams
        RealDriver.ifam_marker = MockDriver.ifam_marker
        RealDriver.commit_patches = MockDriver.commit_patches

        def mock_topological_sort(base, poi):
            data = {}
            return Marker(get=lambda k: data.get(k, 0), set=lambda k, v: data.__setitem__(k, v))

        def mock_make_relationship_info(base, ts):
            data = {}
            return consang.RelationshipInfo(
                tstab=ts,
                reltab=Marker(get=lambda k: data.get(k, consang.PHONY_REL), set=lambda k, v: data.__setitem__(k, v))
            )

        RealConsang.topological_sort = mock_topological_sort
        RealConsang.make_relationship_info = mock_make_relationship_info

        base = MockBase(persons={}, families={})
        result = consang_all.compute(base, from_scratch=True, verbosity=0)

        assert result is False

    finally:
        RealDriver.ipers = original_ipers
        RealDriver.ifams = original_ifams
        RealDriver.ifam_marker = original_ifam_marker
        RealDriver.commit_patches = original_commit_patches
        RealConsang.topological_sort = original_topological_sort
        RealConsang.make_relationship_info = original_make_relationship_info


def test_compute_single_person_no_parents():
    from lib import driver as RealDriver
    from lib import consang as RealConsang
    from lib import gutil as RealGutil
    original_ipers = RealDriver.ipers
    original_ifams = RealDriver.ifams
    original_gen_ascend_of_person = RealDriver.gen_ascend_of_person
    original_load_ascends_array = RealDriver.load_ascends_array
    original_load_couples_array = RealDriver.load_couples_array
    original_poi = RealDriver.poi
    original_get_parents = RealDriver.get_parents
    original_get_consang = RealDriver.get_consang
    original_patch_ascend = RealDriver.patch_ascend
    original_ifam_marker = RealDriver.ifam_marker
    original_iper_marker = RealDriver.iper_marker
    original_commit_patches = RealDriver.commit_patches
    original_nb_of_persons = RealDriver.nb_of_persons
    original_topological_sort = RealConsang.topological_sort
    original_make_relationship_info = RealConsang.make_relationship_info
    original_designation = RealGutil.designation

    try:
        RealDriver.ipers = MockDriver.ipers
        RealDriver.ifams = MockDriver.ifams
        RealDriver.gen_ascend_of_person = MockDriver.gen_ascend_of_person
        RealDriver.load_ascends_array = MockDriver.load_ascends_array
        RealDriver.load_couples_array = MockDriver.load_couples_array
        RealDriver.poi = MockDriver.poi
        RealDriver.get_parents = MockDriver.get_parents
        RealDriver.get_consang = MockDriver.get_consang
        RealDriver.patch_ascend = MockDriver.patch_ascend
        RealDriver.ifam_marker = MockDriver.ifam_marker
        RealDriver.iper_marker = MockDriver.iper_marker
        RealDriver.commit_patches = MockDriver.commit_patches
        RealDriver.nb_of_persons = MockDriver.nb_of_persons

        def mock_topological_sort(base, poi):
            data = {}
            return Marker(get=lambda k: data.get(k, 0), set=lambda k, v: data.__setitem__(k, v))

        def mock_make_relationship_info(base, ts):
            data = {}
            return consang.RelationshipInfo(
                tstab=ts,
                reltab=Marker(get=lambda k: data.get(k, consang.PHONY_REL), set=lambda k, v: data.__setitem__(k, v))
            )

        def mock_designation(base, person):
            return "John.0 Doe"

        RealConsang.topological_sort = mock_topological_sort
        RealConsang.make_relationship_info = mock_make_relationship_info
        RealGutil.designation = mock_designation

        p0 = MockPerson(parents=None)
        base = MockBase(persons={0: p0}, families={})

        old_stderr = sys.stderr
        try:
            sys.stderr = StringIO()
            result = consang_all.compute(base, from_scratch=True, verbosity=0)
        finally:
            sys.stderr = old_stderr

        assert result is True
        assert abs(p0.consang.to_float() - 0.0) < 0.0001
        assert base.patches_committed is True

    finally:
        RealDriver.ipers = original_ipers
        RealDriver.ifams = original_ifams
        RealDriver.gen_ascend_of_person = original_gen_ascend_of_person
        RealDriver.load_ascends_array = original_load_ascends_array
        RealDriver.load_couples_array = original_load_couples_array
        RealDriver.poi = original_poi
        RealDriver.get_parents = original_get_parents
        RealDriver.get_consang = original_get_consang
        RealDriver.patch_ascend = original_patch_ascend
        RealDriver.ifam_marker = original_ifam_marker
        RealDriver.iper_marker = original_iper_marker
        RealDriver.commit_patches = original_commit_patches
        RealDriver.nb_of_persons = original_nb_of_persons
        RealConsang.topological_sort = original_topological_sort
        RealConsang.make_relationship_info = original_make_relationship_info
        RealGutil.designation = original_designation


def test_compute_with_parents():
    from lib import driver as RealDriver
    from lib import consang as RealConsang
    from lib import gutil as RealGutil
    original_ipers = RealDriver.ipers
    original_ifams = RealDriver.ifams
    original_gen_ascend_of_person = RealDriver.gen_ascend_of_person
    original_load_ascends_array = RealDriver.load_ascends_array
    original_load_couples_array = RealDriver.load_couples_array
    original_poi = RealDriver.poi
    original_foi = RealDriver.foi
    original_get_parents = RealDriver.get_parents
    original_get_father = RealDriver.get_father
    original_get_mother = RealDriver.get_mother
    original_get_consang = RealDriver.get_consang
    original_patch_ascend = RealDriver.patch_ascend
    original_ifam_marker = RealDriver.ifam_marker
    original_iper_marker = RealDriver.iper_marker
    original_commit_patches = RealDriver.commit_patches
    original_nb_of_persons = RealDriver.nb_of_persons
    original_topological_sort = RealConsang.topological_sort
    original_make_relationship_info = RealConsang.make_relationship_info
    original_relationship_and_links = RealConsang.relationship_and_links
    original_designation = RealGutil.designation

    try:
        RealDriver.ipers = MockDriver.ipers
        RealDriver.ifams = MockDriver.ifams
        RealDriver.gen_ascend_of_person = MockDriver.gen_ascend_of_person
        RealDriver.load_ascends_array = MockDriver.load_ascends_array
        RealDriver.load_couples_array = MockDriver.load_couples_array
        RealDriver.poi = MockDriver.poi
        RealDriver.foi = MockDriver.foi
        RealDriver.get_parents = MockDriver.get_parents
        RealDriver.get_father = MockDriver.get_father
        RealDriver.get_mother = MockDriver.get_mother
        RealDriver.get_consang = MockDriver.get_consang
        RealDriver.patch_ascend = MockDriver.patch_ascend
        RealDriver.ifam_marker = MockDriver.ifam_marker
        RealDriver.iper_marker = MockDriver.iper_marker
        RealDriver.commit_patches = MockDriver.commit_patches
        RealDriver.nb_of_persons = MockDriver.nb_of_persons

        def mock_topological_sort(base, poi):
            data = {0: 1, 1: 1, 2: 0}
            return Marker(get=lambda k: data.get(k, 0), set=lambda k, v: data.__setitem__(k, v))

        def mock_make_relationship_info(base, ts):
            data = {}
            return consang.RelationshipInfo(
                tstab=ts,
                reltab=Marker(get=lambda k: data.get(k, consang.PHONY_REL), set=lambda k, v: data.__setitem__(k, v))
            )

        def mock_relationship_and_links(base, tab, b, ip1, ip2):
            return (0.0, [])

        def mock_designation(base, person):
            return "John.0 Doe"

        RealConsang.topological_sort = mock_topological_sort
        RealConsang.make_relationship_info = mock_make_relationship_info
        RealConsang.relationship_and_links = mock_relationship_and_links
        RealGutil.designation = mock_designation

        p0 = MockPerson(parents=None)
        p1 = MockPerson(parents=None)
        f0 = MockFamily(0, 1)
        p2 = MockPerson(parents=0)

        base = MockBase(
            persons={0: p0, 1: p1, 2: p2},
            families={0: f0}
        )

        old_stderr = sys.stderr
        try:
            sys.stderr = StringIO()
            result = consang_all.compute(base, from_scratch=True, verbosity=0)
        finally:
            sys.stderr = old_stderr

        assert result is True
        assert abs(p0.consang.to_float() - 0.0) < 0.0001
        assert abs(p1.consang.to_float() - 0.0) < 0.0001
        assert abs(p2.consang.to_float() - 0.0) < 0.0001

    finally:
        RealDriver.ipers = original_ipers
        RealDriver.ifams = original_ifams
        RealDriver.gen_ascend_of_person = original_gen_ascend_of_person
        RealDriver.load_ascends_array = original_load_ascends_array
        RealDriver.load_couples_array = original_load_couples_array
        RealDriver.poi = original_poi
        RealDriver.foi = original_foi
        RealDriver.get_parents = original_get_parents
        RealDriver.get_father = original_get_father
        RealDriver.get_mother = original_get_mother
        RealDriver.get_consang = original_get_consang
        RealDriver.patch_ascend = original_patch_ascend
        RealDriver.ifam_marker = original_ifam_marker
        RealDriver.iper_marker = original_iper_marker
        RealDriver.commit_patches = original_commit_patches
        RealDriver.nb_of_persons = original_nb_of_persons
        RealConsang.topological_sort = original_topological_sort
        RealConsang.make_relationship_info = original_make_relationship_info
        RealConsang.relationship_and_links = original_relationship_and_links
        RealGutil.designation = original_designation


def test_compute_not_from_scratch():
    from lib import driver as RealDriver
    from lib import consang as RealConsang
    from lib import gutil as RealGutil
    original_ipers = RealDriver.ipers
    original_ifams = RealDriver.ifams
    original_gen_ascend_of_person = RealDriver.gen_ascend_of_person
    original_load_ascends_array = RealDriver.load_ascends_array
    original_load_couples_array = RealDriver.load_couples_array
    original_poi = RealDriver.poi
    original_get_parents = RealDriver.get_parents
    original_get_consang = RealDriver.get_consang
    original_patch_ascend = RealDriver.patch_ascend
    original_ifam_marker = RealDriver.ifam_marker
    original_iper_marker = RealDriver.iper_marker
    original_commit_patches = RealDriver.commit_patches
    original_nb_of_persons = RealDriver.nb_of_persons
    original_topological_sort = RealConsang.topological_sort
    original_make_relationship_info = RealConsang.make_relationship_info
    original_designation = RealGutil.designation

    try:
        RealDriver.ipers = MockDriver.ipers
        RealDriver.ifams = MockDriver.ifams
        RealDriver.gen_ascend_of_person = MockDriver.gen_ascend_of_person
        RealDriver.load_ascends_array = MockDriver.load_ascends_array
        RealDriver.load_couples_array = MockDriver.load_couples_array
        RealDriver.poi = MockDriver.poi
        RealDriver.get_parents = MockDriver.get_parents
        RealDriver.get_consang = MockDriver.get_consang
        RealDriver.patch_ascend = MockDriver.patch_ascend
        RealDriver.ifam_marker = MockDriver.ifam_marker
        RealDriver.iper_marker = MockDriver.iper_marker
        RealDriver.commit_patches = MockDriver.commit_patches
        RealDriver.nb_of_persons = MockDriver.nb_of_persons

        def mock_topological_sort(base, poi):
            data = {}
            return Marker(get=lambda k: data.get(k, 0), set=lambda k, v: data.__setitem__(k, v))

        def mock_make_relationship_info(base, ts):
            data = {}
            return consang.RelationshipInfo(
                tstab=ts,
                reltab=Marker(get=lambda k: data.get(k, consang.PHONY_REL), set=lambda k, v: data.__setitem__(k, v))
            )

        def mock_designation(base, person):
            return "John.0 Doe"

        RealConsang.topological_sort = mock_topological_sort
        RealConsang.make_relationship_info = mock_make_relationship_info
        RealGutil.designation = mock_designation

        p0 = MockPerson(parents=None, consang=adef.Fix.from_float(0.125))
        base = MockBase(persons={0: p0}, families={})

        old_stderr = sys.stderr
        try:
            sys.stderr = StringIO()
            result = consang_all.compute(base, from_scratch=False, verbosity=0)
        finally:
            sys.stderr = old_stderr

        assert result is False
        assert abs(p0.consang.to_float() - 0.125) < 0.0001

    finally:
        RealDriver.ipers = original_ipers
        RealDriver.ifams = original_ifams
        RealDriver.gen_ascend_of_person = original_gen_ascend_of_person
        RealDriver.load_ascends_array = original_load_ascends_array
        RealDriver.load_couples_array = original_load_couples_array
        RealDriver.poi = original_poi
        RealDriver.get_parents = original_get_parents
        RealDriver.get_consang = original_get_consang
        RealDriver.patch_ascend = original_patch_ascend
        RealDriver.ifam_marker = original_ifam_marker
        RealDriver.iper_marker = original_iper_marker
        RealDriver.commit_patches = original_commit_patches
        RealDriver.nb_of_persons = original_nb_of_persons
        RealConsang.topological_sort = original_topological_sort
        RealConsang.make_relationship_info = original_make_relationship_info
        RealGutil.designation = original_designation


def test_compute_with_verbosity_1():
    from lib import driver as RealDriver
    from lib import consang as RealConsang
    from lib import gutil as RealGutil
    original_ipers = RealDriver.ipers
    original_ifams = RealDriver.ifams
    original_gen_ascend_of_person = RealDriver.gen_ascend_of_person
    original_load_ascends_array = RealDriver.load_ascends_array
    original_load_couples_array = RealDriver.load_couples_array
    original_poi = RealDriver.poi
    original_get_parents = RealDriver.get_parents
    original_get_consang = RealDriver.get_consang
    original_patch_ascend = RealDriver.patch_ascend
    original_ifam_marker = RealDriver.ifam_marker
    original_iper_marker = RealDriver.iper_marker
    original_commit_patches = RealDriver.commit_patches
    original_nb_of_persons = RealDriver.nb_of_persons
    original_topological_sort = RealConsang.topological_sort
    original_make_relationship_info = RealConsang.make_relationship_info
    original_designation = RealGutil.designation

    try:
        RealDriver.ipers = MockDriver.ipers
        RealDriver.ifams = MockDriver.ifams
        RealDriver.gen_ascend_of_person = MockDriver.gen_ascend_of_person
        RealDriver.load_ascends_array = MockDriver.load_ascends_array
        RealDriver.load_couples_array = MockDriver.load_couples_array
        RealDriver.poi = MockDriver.poi
        RealDriver.get_parents = MockDriver.get_parents
        RealDriver.get_consang = MockDriver.get_consang
        RealDriver.patch_ascend = MockDriver.patch_ascend
        RealDriver.ifam_marker = MockDriver.ifam_marker
        RealDriver.iper_marker = MockDriver.iper_marker
        RealDriver.commit_patches = MockDriver.commit_patches
        RealDriver.nb_of_persons = MockDriver.nb_of_persons

        def mock_topological_sort(base, poi):
            data = {}
            return Marker(get=lambda k: data.get(k, 0), set=lambda k, v: data.__setitem__(k, v))

        def mock_make_relationship_info(base, ts):
            data = {}
            return consang.RelationshipInfo(
                tstab=ts,
                reltab=Marker(get=lambda k: data.get(k, consang.PHONY_REL), set=lambda k, v: data.__setitem__(k, v))
            )

        def mock_designation(base, person):
            return "John.0 Doe"

        RealConsang.topological_sort = mock_topological_sort
        RealConsang.make_relationship_info = mock_make_relationship_info
        RealGutil.designation = mock_designation

        p0 = MockPerson(parents=None)
        base = MockBase(persons={0: p0}, families={})

        old_stderr = sys.stderr
        try:
            sys.stderr = StringIO()
            result = consang_all.compute(base, from_scratch=True, verbosity=1)
            output = sys.stderr.getvalue()
            assert "To do: 1 persons" in output
        finally:
            sys.stderr = old_stderr

        assert result is True

    finally:
        RealDriver.ipers = original_ipers
        RealDriver.ifams = original_ifams
        RealDriver.gen_ascend_of_person = original_gen_ascend_of_person
        RealDriver.load_ascends_array = original_load_ascends_array
        RealDriver.load_couples_array = original_load_couples_array
        RealDriver.poi = original_poi
        RealDriver.get_parents = original_get_parents
        RealDriver.get_consang = original_get_consang
        RealDriver.patch_ascend = original_patch_ascend
        RealDriver.ifam_marker = original_ifam_marker
        RealDriver.iper_marker = original_iper_marker
        RealDriver.commit_patches = original_commit_patches
        RealDriver.nb_of_persons = original_nb_of_persons
        RealConsang.topological_sort = original_topological_sort
        RealConsang.make_relationship_info = original_make_relationship_info
        RealGutil.designation = original_designation


def test_compute_with_verbosity_2():
    from lib import driver as RealDriver
    from lib import consang as RealConsang
    from lib import gutil as RealGutil
    original_ipers = RealDriver.ipers
    original_ifams = RealDriver.ifams
    original_gen_ascend_of_person = RealDriver.gen_ascend_of_person
    original_load_ascends_array = RealDriver.load_ascends_array
    original_load_couples_array = RealDriver.load_couples_array
    original_poi = RealDriver.poi
    original_get_parents = RealDriver.get_parents
    original_get_consang = RealDriver.get_consang
    original_patch_ascend = RealDriver.patch_ascend
    original_ifam_marker = RealDriver.ifam_marker
    original_iper_marker = RealDriver.iper_marker
    original_commit_patches = RealDriver.commit_patches
    original_nb_of_persons = RealDriver.nb_of_persons
    original_topological_sort = RealConsang.topological_sort
    original_make_relationship_info = RealConsang.make_relationship_info
    original_designation = RealGutil.designation

    try:
        RealDriver.ipers = MockDriver.ipers
        RealDriver.ifams = MockDriver.ifams
        RealDriver.gen_ascend_of_person = MockDriver.gen_ascend_of_person
        RealDriver.load_ascends_array = MockDriver.load_ascends_array
        RealDriver.load_couples_array = MockDriver.load_couples_array
        RealDriver.poi = MockDriver.poi
        RealDriver.get_parents = MockDriver.get_parents
        RealDriver.get_consang = MockDriver.get_consang
        RealDriver.patch_ascend = MockDriver.patch_ascend
        RealDriver.ifam_marker = MockDriver.ifam_marker
        RealDriver.iper_marker = MockDriver.iper_marker
        RealDriver.commit_patches = MockDriver.commit_patches
        RealDriver.nb_of_persons = MockDriver.nb_of_persons

        def mock_topological_sort(base, poi):
            data = {}
            return Marker(get=lambda k: data.get(k, 0), set=lambda k, v: data.__setitem__(k, v))

        def mock_make_relationship_info(base, ts):
            data = {}
            return consang.RelationshipInfo(
                tstab=ts,
                reltab=Marker(get=lambda k: data.get(k, consang.PHONY_REL), set=lambda k, v: data.__setitem__(k, v))
            )

        def mock_designation(base, person):
            return "John.0 Doe"

        RealConsang.topological_sort = mock_topological_sort
        RealConsang.make_relationship_info = mock_make_relationship_info
        RealGutil.designation = mock_designation

        p0 = MockPerson(parents=None)
        base = MockBase(persons={0: p0}, families={})

        old_stderr = sys.stderr
        try:
            sys.stderr = StringIO()
            result = consang_all.compute(base, from_scratch=True, verbosity=2)
            output = sys.stderr.getvalue()
            assert "To do: 1 persons" in output
            assert "Computing consanguinity..." in output
            assert "done" in output
        finally:
            sys.stderr = old_stderr

        assert result is True

    finally:
        RealDriver.ipers = original_ipers
        RealDriver.ifams = original_ifams
        RealDriver.gen_ascend_of_person = original_gen_ascend_of_person
        RealDriver.load_ascends_array = original_load_ascends_array
        RealDriver.load_couples_array = original_load_couples_array
        RealDriver.poi = original_poi
        RealDriver.get_parents = original_get_parents
        RealDriver.get_consang = original_get_consang
        RealDriver.patch_ascend = original_patch_ascend
        RealDriver.ifam_marker = original_ifam_marker
        RealDriver.iper_marker = original_iper_marker
        RealDriver.commit_patches = original_commit_patches
        RealDriver.nb_of_persons = original_nb_of_persons
        RealConsang.topological_sort = original_topological_sort
        RealConsang.make_relationship_info = original_make_relationship_info
        RealGutil.designation = original_designation


def test_compute_with_keyboard_interrupt():
    from lib import driver as RealDriver
    from lib import consang as RealConsang
    from lib import gutil as RealGutil
    original_ipers = RealDriver.ipers
    original_ifams = RealDriver.ifams
    original_commit_patches = RealDriver.commit_patches
    original_topological_sort = RealConsang.topological_sort
    original_make_relationship_info = RealConsang.make_relationship_info
    original_designation = RealGutil.designation

    try:
        RealDriver.ipers = MockDriver.ipers
        RealDriver.ifams = MockDriver.ifams
        RealDriver.commit_patches = MockDriver.commit_patches

        def mock_topological_sort(base, poi):
            raise KeyboardInterrupt()

        def mock_make_relationship_info(base, ts):
            data = {}
            return consang.RelationshipInfo(
                tstab=ts,
                reltab=Marker(get=lambda k: data.get(k, consang.PHONY_REL), set=lambda k, v: data.__setitem__(k, v))
            )

        def mock_designation(base, person):
            return "John.0 Doe"

        RealConsang.topological_sort = mock_topological_sort
        RealConsang.make_relationship_info = mock_make_relationship_info
        RealGutil.designation = mock_designation

        base = MockBase(persons={}, families={})

        old_stderr = sys.stderr
        try:
            sys.stderr = StringIO()
            result = consang_all.compute(base, from_scratch=True, verbosity=1)
            output = sys.stderr.getvalue()
            assert "\n" in output
        finally:
            sys.stderr = old_stderr

        assert result is False

    finally:
        RealDriver.ipers = original_ipers
        RealDriver.ifams = original_ifams
        RealDriver.commit_patches = original_commit_patches
        RealConsang.topological_sort = original_topological_sort
        RealConsang.make_relationship_info = original_make_relationship_info
        RealGutil.designation = original_designation


def test_relationship_wrapper():
    from lib import driver as RealDriver
    from lib import consang as RealConsang
    original_ipers = RealDriver.ipers
    original_iper_marker = RealDriver.iper_marker
    original_relationship_and_links = RealConsang.relationship_and_links

    try:
        RealDriver.ipers = MockDriver.ipers
        RealDriver.iper_marker = MockDriver.iper_marker

        def mock_relationship_and_links(base, tab, b, ip1, ip2):
            return (0.125, [1, 2, 3])

        RealConsang.relationship_and_links = mock_relationship_and_links

        base = MockBase(persons={0: None, 1: None}, families={})
        data = {}
        ts = Marker(get=lambda k: data.get(k, 0), set=lambda k, v: data.__setitem__(k, v))
        tab = consang.make_relationship_info(base, ts)

        result = consang_all._relationship(base, tab, 0, 1)
        assert result == 0.125

    finally:
        RealDriver.ipers = original_ipers
        RealDriver.iper_marker = original_iper_marker
        RealConsang.relationship_and_links = original_relationship_and_links
