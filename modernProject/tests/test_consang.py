from lib import consang
from lib.consang import AncStat, Visit, Relationship, RelationshipInfo, TopologicalSortError
from lib.collection import Marker
from lib.gwdef import GenPerson, GenAscend, GenUnion, Sex, OwnAncestor, DontKnowIfDead, UnknownBurial
from lib import adef


class MockBase:
    def __init__(self, persons, families):
        self.persons = persons
        self.families = families
        self.nb_persons = len(persons)

    def get_person(self, i):
        return self.persons.get(i)

    def get_family(self, i):
        return self.families.get(i)


class MockDriver:
    @staticmethod
    def ipers(base):
        return list(base.persons.keys())

    @staticmethod
    def poi(base, i):
        return base.get_person(i)

    @staticmethod
    def foi(base, i):
        return base.get_family(i)

    @staticmethod
    def get_parents(person):
        return person.parents

    @staticmethod
    def get_father(family):
        return family.father

    @staticmethod
    def get_mother(family):
        return family.mother

    @staticmethod
    def get_consang(person):
        return person.consang

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


def test_anc_stat_enum():
    assert AncStat.MAYBE_ANC.value == 0
    assert AncStat.IS_ANC.value == 1


def test_visit_enum():
    assert Visit.NOT_VISITED.value == 0
    assert Visit.BEING_VISITED.value == 1
    assert Visit.VISITED.value == 2


def test_relationship_dataclass():
    rel = Relationship()
    assert rel.weight1 == 0.0
    assert rel.weight2 == 0.0
    assert rel.relationship == 0.0
    assert rel.lens1 == []
    assert rel.lens2 == []
    assert rel.inserted == 0
    assert rel.elim_ancestors is False
    assert rel.anc_stat1 == AncStat.MAYBE_ANC
    assert rel.anc_stat2 == AncStat.MAYBE_ANC

    rel2 = Relationship(weight1=0.5, weight2=0.25, relationship=0.125)
    assert rel2.weight1 == 0.5
    assert rel2.weight2 == 0.25
    assert rel2.relationship == 0.125


def test_relationship_info_dataclass():
    marker1 = Marker(get=lambda k: 0, set=lambda k, v: None)
    marker2 = Marker(get=lambda k: Relationship(), set=lambda k, v: None)
    ri = RelationshipInfo(tstab=marker1, reltab=marker2)
    assert ri.tstab == marker1
    assert ri.reltab == marker2
    assert ri.queue == []


def test_topological_sort_error():
    class MockPerson:
        def __init__(self):
            self.name = "John Doe"

    person = MockPerson()
    error = TopologicalSortError(person)
    assert error.person == person
    assert "Topological sort error" in str(error)


def test_half():
    assert consang.half(1.0) == 0.5
    assert consang.half(2.0) == 1.0
    assert consang.half(0.5) == 0.25
    assert consang.half(0.0) == 0.0


def test_new_mark():
    mark1 = consang.new_mark()
    mark2 = consang.new_mark()
    mark3 = consang.new_mark()
    assert mark2 == mark1 + 1
    assert mark3 == mark2 + 1


def test_noloop_aux_no_loop():
    from lib.database import Driver as RealDriver
    original_poi = RealDriver.poi
    original_foi = RealDriver.foi
    original_get_parents = RealDriver.get_parents
    original_get_father = RealDriver.get_father
    original_get_mother = RealDriver.get_mother

    try:
        RealDriver.poi = MockDriver.poi
        RealDriver.foi = MockDriver.foi
        RealDriver.get_parents = MockDriver.get_parents
        RealDriver.get_father = MockDriver.get_father
        RealDriver.get_mother = MockDriver.get_mother

        class MockFamily:
            def __init__(self, father, mother):
                self.father = father
                self.mother = mother

        class MockPerson:
            def __init__(self, parents=None):
                self.parents = parents

        p0 = MockPerson(parents=None)
        p1 = MockPerson(parents=None)
        f0 = MockFamily(0, 1)
        p2 = MockPerson(parents=0)

        base = MockBase(
            persons={0: p0, 1: p1, 2: p2},
            families={0: f0}
        )

        data = {}
        tab = Marker(
            get=lambda k: data.get(k, Visit.NOT_VISITED),
            set=lambda k, v: data.__setitem__(k, v)
        )
        errors = []

        def error_handler(err):
            errors.append(err)

        consang._noloop_aux(base, error_handler, tab, 2)

        assert len(errors) == 0
        assert tab.get(2) == Visit.VISITED
        assert tab.get(0) == Visit.VISITED
        assert tab.get(1) == Visit.VISITED

    finally:
        RealDriver.poi = original_poi
        RealDriver.foi = original_foi
        RealDriver.get_parents = original_get_parents
        RealDriver.get_father = original_get_father
        RealDriver.get_mother = original_get_mother


def test_noloop_aux_with_loop():
    from lib.database import Driver as RealDriver
    original_poi = RealDriver.poi
    original_foi = RealDriver.foi
    original_get_parents = RealDriver.get_parents
    original_get_father = RealDriver.get_father
    original_get_mother = RealDriver.get_mother

    try:
        RealDriver.poi = MockDriver.poi
        RealDriver.foi = MockDriver.foi
        RealDriver.get_parents = MockDriver.get_parents
        RealDriver.get_father = MockDriver.get_father
        RealDriver.get_mother = MockDriver.get_mother

        class MockFamily:
            def __init__(self, father, mother):
                self.father = father
                self.mother = mother

        class MockPerson:
            def __init__(self, parents=None):
                self.parents = parents

        p0 = MockPerson(parents=0)
        f0 = MockFamily(0, 0)

        base = MockBase(
            persons={0: p0},
            families={0: f0}
        )

        data = {}
        tab = Marker(
            get=lambda k: data.get(k, Visit.NOT_VISITED),
            set=lambda k, v: data.__setitem__(k, v)
        )
        errors = []

        def error_handler(err):
            errors.append(err)

        consang._noloop_aux(base, error_handler, tab, 0)

        assert len(errors) >= 1
        assert isinstance(errors[0], OwnAncestor)

    finally:
        RealDriver.poi = original_poi
        RealDriver.foi = original_foi
        RealDriver.get_parents = original_get_parents
        RealDriver.get_father = original_get_father
        RealDriver.get_mother = original_get_mother


def test_check_noloop():
    from lib.database import Driver as RealDriver
    original_ipers = RealDriver.ipers
    original_poi = RealDriver.poi
    original_foi = RealDriver.foi
    original_get_parents = RealDriver.get_parents
    original_get_father = RealDriver.get_father
    original_get_mother = RealDriver.get_mother
    original_iper_marker = RealDriver.iper_marker

    try:
        RealDriver.ipers = MockDriver.ipers
        RealDriver.poi = MockDriver.poi
        RealDriver.foi = MockDriver.foi
        RealDriver.get_parents = MockDriver.get_parents
        RealDriver.get_father = MockDriver.get_father
        RealDriver.get_mother = MockDriver.get_mother
        RealDriver.iper_marker = MockDriver.iper_marker

        class MockFamily:
            def __init__(self, father, mother):
                self.father = father
                self.mother = mother

        class MockPerson:
            def __init__(self, parents=None):
                self.parents = parents

        p0 = MockPerson(parents=None)
        p1 = MockPerson(parents=None)

        base = MockBase(
            persons={0: p0, 1: p1},
            families={}
        )

        errors = []

        def error_handler(err):
            errors.append(err)

        consang.check_noloop(base, error_handler)
        assert len(errors) == 0

    finally:
        RealDriver.ipers = original_ipers
        RealDriver.poi = original_poi
        RealDriver.foi = original_foi
        RealDriver.get_parents = original_get_parents
        RealDriver.get_father = original_get_father
        RealDriver.get_mother = original_get_mother
        RealDriver.iper_marker = original_iper_marker


def test_check_noloop_for_person_list():
    from lib.database import Driver as RealDriver
    original_ipers = RealDriver.ipers
    original_poi = RealDriver.poi
    original_foi = RealDriver.foi
    original_get_parents = RealDriver.get_parents
    original_get_father = RealDriver.get_father
    original_get_mother = RealDriver.get_mother
    original_iper_marker = RealDriver.iper_marker

    try:
        RealDriver.ipers = MockDriver.ipers
        RealDriver.poi = MockDriver.poi
        RealDriver.foi = MockDriver.foi
        RealDriver.get_parents = MockDriver.get_parents
        RealDriver.get_father = MockDriver.get_father
        RealDriver.get_mother = MockDriver.get_mother
        RealDriver.iper_marker = MockDriver.iper_marker

        class MockFamily:
            def __init__(self, father, mother):
                self.father = father
                self.mother = mother

        class MockPerson:
            def __init__(self, parents=None):
                self.parents = parents

        p0 = MockPerson(parents=None)
        p1 = MockPerson(parents=None)

        base = MockBase(
            persons={0: p0, 1: p1},
            families={}
        )

        errors = []

        def error_handler(err):
            errors.append(err)

        consang.check_noloop_for_person_list(base, error_handler, [0])
        assert len(errors) == 0

    finally:
        RealDriver.ipers = original_ipers
        RealDriver.poi = original_poi
        RealDriver.foi = original_foi
        RealDriver.get_parents = original_get_parents
        RealDriver.get_father = original_get_father
        RealDriver.get_mother = original_get_mother
        RealDriver.iper_marker = original_iper_marker


def test_topological_sort():
    from lib.database import Driver as RealDriver
    original_ipers = RealDriver.ipers
    original_foi = RealDriver.foi
    original_get_parents = RealDriver.get_parents
    original_get_father = RealDriver.get_father
    original_get_mother = RealDriver.get_mother
    original_iper_marker = RealDriver.iper_marker
    original_nb_of_persons = RealDriver.nb_of_persons

    try:
        RealDriver.ipers = MockDriver.ipers
        RealDriver.foi = MockDriver.foi
        RealDriver.get_parents = MockDriver.get_parents
        RealDriver.get_father = MockDriver.get_father
        RealDriver.get_mother = MockDriver.get_mother
        RealDriver.iper_marker = MockDriver.iper_marker
        RealDriver.nb_of_persons = MockDriver.nb_of_persons

        class MockFamily:
            def __init__(self, father, mother):
                self.father = father
                self.mother = mother

        class MockPerson:
            def __init__(self, parents=None):
                self.parents = parents

        p0 = MockPerson(parents=None)
        p1 = MockPerson(parents=None)
        f0 = MockFamily(0, 1)
        p2 = MockPerson(parents=0)

        base = MockBase(
            persons={0: p0, 1: p1, 2: p2},
            families={0: f0}
        )

        def poi(b, i):
            return b.get_person(i)

        tab = consang.topological_sort(base, poi)

        assert tab.get(2) == 0
        assert tab.get(0) == 1
        assert tab.get(1) == 1

    finally:
        RealDriver.ipers = original_ipers
        RealDriver.foi = original_foi
        RealDriver.get_parents = original_get_parents
        RealDriver.get_father = original_get_father
        RealDriver.get_mother = original_get_mother
        RealDriver.iper_marker = original_iper_marker
        RealDriver.nb_of_persons = original_nb_of_persons


def test_topological_sort_with_loop():
    from lib.database import Driver as RealDriver
    original_ipers = RealDriver.ipers
    original_poi = RealDriver.poi
    original_foi = RealDriver.foi
    original_get_parents = RealDriver.get_parents
    original_get_father = RealDriver.get_father
    original_get_mother = RealDriver.get_mother
    original_iper_marker = RealDriver.iper_marker
    original_nb_of_persons = RealDriver.nb_of_persons

    try:
        RealDriver.ipers = MockDriver.ipers
        RealDriver.poi = MockDriver.poi
        RealDriver.foi = MockDriver.foi
        RealDriver.get_parents = MockDriver.get_parents
        RealDriver.get_father = MockDriver.get_father
        RealDriver.get_mother = MockDriver.get_mother
        RealDriver.iper_marker = MockDriver.iper_marker
        RealDriver.nb_of_persons = MockDriver.nb_of_persons

        class MockFamily:
            def __init__(self, father, mother):
                self.father = father
                self.mother = mother

        class MockPerson:
            def __init__(self, parents=None):
                self.parents = parents

        p0 = MockPerson(parents=0)
        f0 = MockFamily(0, 0)

        base = MockBase(
            persons={0: p0},
            families={0: f0}
        )

        def poi(b, i):
            return b.get_person(i)

        try:
            tab = consang.topological_sort(base, poi)
            assert False, "Should have raised TopologicalSortError"
        except TopologicalSortError as e:
            assert e.person == p0

    finally:
        RealDriver.ipers = original_ipers
        RealDriver.poi = original_poi
        RealDriver.foi = original_foi
        RealDriver.get_parents = original_get_parents
        RealDriver.get_father = original_get_father
        RealDriver.get_mother = original_get_mother
        RealDriver.iper_marker = original_iper_marker
        RealDriver.nb_of_persons = original_nb_of_persons


def test_make_relationship_info():
    from lib.database import Driver as RealDriver
    original_ipers = RealDriver.ipers
    original_iper_marker = RealDriver.iper_marker

    try:
        RealDriver.ipers = MockDriver.ipers
        RealDriver.iper_marker = MockDriver.iper_marker

        class MockPerson:
            def __init__(self):
                self.parents = None

        base = MockBase(
            persons={0: MockPerson(), 1: MockPerson()},
            families={}
        )

        data = {}
        tstab = Marker(get=lambda k: data.get(k, 0), set=lambda k, v: data.__setitem__(k, v))
        ri = consang.make_relationship_info(base, tstab)

        assert ri.tstab == tstab
        assert isinstance(ri.reltab, Marker)
        assert ri.queue == []

    finally:
        RealDriver.ipers = original_ipers
        RealDriver.iper_marker = original_iper_marker


def test_insert_branch_len_rec():
    lens = [(1, 2, [10, 11]), (2, 3, [20, 21])]
    result = consang._insert_branch_len_rec((1, 1, 5), lens)

    assert len(result) == 2
    assert result[0] == (1, 3, [5, 10, 11])
    assert result[1] == (2, 3, [20, 21])

    result2 = consang._insert_branch_len_rec((3, 4, 30), lens)
    assert len(result2) == 3
    assert result2[2] == (3, 4, [30])

    result3 = consang._insert_branch_len_rec((1, -1, 5), [(1, 2, [10])])
    assert result3[0][1] == -1


def test_insert_branch_len_rec_empty():
    result = consang._insert_branch_len_rec((1, 2, 5), [])
    assert result == [(1, 2, [5])]


def test_insert_branch_len():
    lens = [(1, 2, [10, 11])]
    branch = (0, 1, [])
    result = consang.insert_branch_len(5, lens, branch)

    assert len(result) == 1
    assert result[0] == (1, 3, [5, 10, 11])


def test_consang_of():
    from lib.database import Driver as RealDriver
    original_get_consang = RealDriver.get_consang

    try:
        RealDriver.get_consang = MockDriver.get_consang

        class MockPerson:
            def __init__(self, consang):
                self.consang = consang

        p1 = MockPerson(adef.NO_CONSANG)
        assert consang.consang_of(p1) == 0.0

        p2 = MockPerson(adef.Fix.from_float(0.25))
        assert abs(consang.consang_of(p2) - 0.25) < 0.0001

    finally:
        RealDriver.get_consang = original_get_consang


def test_relationship_and_links_same_person():
    from lib.database import Driver as RealDriver
    original_ipers = RealDriver.ipers
    original_iper_marker = RealDriver.iper_marker

    try:
        RealDriver.ipers = MockDriver.ipers
        RealDriver.iper_marker = MockDriver.iper_marker

        class MockPerson:
            def __init__(self):
                self.parents = None

        base = MockBase(
            persons={0: MockPerson()},
            families={}
        )

        data = {}
        tstab = Marker(get=lambda k: data.get(k, 0), set=lambda k, v: data.__setitem__(k, v))
        ri = consang.make_relationship_info(base, tstab)

        rel, tops = consang.relationship_and_links(base, ri, False, 0, 0)
        assert rel == 1.0
        assert tops == []

    finally:
        RealDriver.ipers = original_ipers
        RealDriver.iper_marker = original_iper_marker


def test_relationship_and_links_siblings():
    from lib.database import Driver as RealDriver
    original_ipers = RealDriver.ipers
    original_poi = RealDriver.poi
    original_foi = RealDriver.foi
    original_get_parents = RealDriver.get_parents
    original_get_father = RealDriver.get_father
    original_get_mother = RealDriver.get_mother
    original_get_consang = RealDriver.get_consang
    original_iper_marker = RealDriver.iper_marker

    try:
        RealDriver.ipers = MockDriver.ipers
        RealDriver.poi = MockDriver.poi
        RealDriver.foi = MockDriver.foi
        RealDriver.get_parents = MockDriver.get_parents
        RealDriver.get_father = MockDriver.get_father
        RealDriver.get_mother = MockDriver.get_mother
        RealDriver.get_consang = MockDriver.get_consang
        RealDriver.iper_marker = MockDriver.iper_marker

        class MockFamily:
            def __init__(self, father, mother):
                self.father = father
                self.mother = mother

        class MockPerson:
            def __init__(self, parents=None, consang=None):
                self.parents = parents
                self.consang = consang if consang is not None else adef.NO_CONSANG

        p0 = MockPerson(parents=None)
        p1 = MockPerson(parents=None)
        f0 = MockFamily(0, 1)
        p2 = MockPerson(parents=0)
        p3 = MockPerson(parents=0)

        base = MockBase(
            persons={0: p0, 1: p1, 2: p2, 3: p3},
            families={0: f0}
        )

        def poi(b, i):
            return b.get_person(i)

        tstab = consang.topological_sort(base, poi)
        ri = consang.make_relationship_info(base, tstab)

        rel, tops = consang.relationship_and_links(base, ri, True, 2, 3)
        assert abs(rel - 0.25) < 0.001
        assert len(tops) == 2

    finally:
        RealDriver.ipers = original_ipers
        RealDriver.poi = original_poi
        RealDriver.foi = original_foi
        RealDriver.get_parents = original_get_parents
        RealDriver.get_father = original_get_father
        RealDriver.get_mother = original_get_mother
        RealDriver.get_consang = original_get_consang
        RealDriver.iper_marker = original_iper_marker


def test_relationship_and_links_unrelated():
    from lib.database import Driver as RealDriver
    original_ipers = RealDriver.ipers
    original_poi = RealDriver.poi
    original_foi = RealDriver.foi
    original_get_parents = RealDriver.get_parents
    original_get_father = RealDriver.get_father
    original_get_mother = RealDriver.get_mother
    original_get_consang = RealDriver.get_consang
    original_iper_marker = RealDriver.iper_marker

    try:
        RealDriver.ipers = MockDriver.ipers
        RealDriver.poi = MockDriver.poi
        RealDriver.foi = MockDriver.foi
        RealDriver.get_parents = MockDriver.get_parents
        RealDriver.get_father = MockDriver.get_father
        RealDriver.get_mother = MockDriver.get_mother
        RealDriver.get_consang = MockDriver.get_consang
        RealDriver.iper_marker = MockDriver.iper_marker

        class MockPerson:
            def __init__(self, parents=None, consang=None):
                self.parents = parents
                self.consang = consang if consang is not None else adef.NO_CONSANG

        p0 = MockPerson(parents=None)
        p1 = MockPerson(parents=None)

        base = MockBase(
            persons={0: p0, 1: p1},
            families={}
        )

        def poi(b, i):
            return b.get_person(i)

        tstab = consang.topological_sort(base, poi)
        ri = consang.make_relationship_info(base, tstab)

        rel, tops = consang.relationship_and_links(base, ri, False, 0, 1)
        assert rel == 0.0
        assert tops == []

    finally:
        RealDriver.ipers = original_ipers
        RealDriver.poi = original_poi
        RealDriver.foi = original_foi
        RealDriver.get_parents = original_get_parents
        RealDriver.get_father = original_get_father
        RealDriver.get_mother = original_get_mother
        RealDriver.get_consang = original_get_consang
        RealDriver.iper_marker = original_iper_marker


def test_phony_rel():
    assert consang.PHONY_REL.weight1 == 0.0
    assert consang.PHONY_REL.weight2 == 0.0
    assert consang.PHONY_REL.relationship == 0.0
    assert consang.PHONY_REL.lens1 == []
    assert consang.PHONY_REL.lens2 == []
    assert consang.PHONY_REL.inserted == 0
    assert consang.PHONY_REL.elim_ancestors is False
    assert consang.PHONY_REL.anc_stat1 == AncStat.MAYBE_ANC
    assert consang.PHONY_REL.anc_stat2 == AncStat.MAYBE_ANC
