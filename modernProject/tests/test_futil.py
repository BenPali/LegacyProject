import pytest
from lib.futil import (
    map_title_strings, map_pers_event, map_fam_event, map_relation_ps,
    map_person_ps, map_ascend_f, map_union_f, map_family_ps,
    map_couple_p, map_descend_p, eq_lists, eq_titles, eq_title_names,
    gen_person_misc_names
)
from lib.gwdef import (
    GenTitle, Tmain, Tname, Tnone,
    GenPersEvent, GenPersEventName, EpersName,
    GenFamEvent, GenFamEventName, EfamName,
    GenRelation, RelationType, GenPerson, Sex, Access,
    GenAscend, GenUnion, GenDescend, GenFamily, RelationKind,
    NotDead, DeathWithReason, DeathReason, UnknownBurial, Buried, Cremated,
    NotDivorced, DivorceWithDate, WitnessKind
)
from lib.adef import CdateNone, CdateGregorian, Dmy, Precision, Fix, Couple
from lib.date import compress


def test_map_title_strings_basic():
    title = GenTitle[str](
        t_name=Tmain[str](),
        t_ident="id1",
        t_place="Paris",
        t_date_start=CdateNone(),
        t_date_end=CdateNone(),
        t_nth=1
    )

    mapped = map_title_strings(str.upper, title)

    assert isinstance(mapped.t_name, Tmain)
    assert mapped.t_ident == "ID1"
    assert mapped.t_place == "PARIS"
    assert mapped.t_nth == 1


def test_map_title_strings_with_tname():
    title = GenTitle[str](
        t_name=Tname[str](name="Duke"),
        t_ident="id1",
        t_place="London",
        t_date_start=CdateNone(),
        t_date_end=CdateNone(),
        t_nth=2
    )

    mapped = map_title_strings(str.upper, title)

    assert isinstance(mapped.t_name, Tname)
    assert mapped.t_name.name == "DUKE"
    assert mapped.t_place == "LONDON"


def test_map_title_strings_with_tnone():
    title = GenTitle[str](
        t_name=Tnone[str](),
        t_ident="id1",
        t_place="Berlin",
        t_date_start=CdateNone(),
        t_date_end=CdateNone(),
        t_nth=0
    )

    mapped = map_title_strings(str.upper, title)

    assert isinstance(mapped.t_name, Tnone)
    assert mapped.t_ident == "ID1"


def test_map_pers_event_with_enum_name():
    event = GenPersEvent[int, str](
        epers_name=GenPersEventName.EPERS_BIRTH,
        epers_date=CdateNone(),
        epers_place="Paris",
        epers_reason="",
        epers_note="note",
        epers_src="source",
        epers_witnesses=[(1, WitnessKind.WITNESS), (2, WitnessKind.WITNESS)]
    )

    mapped = map_pers_event(lambda x: x * 10, str.upper, event)

    assert mapped.epers_name == GenPersEventName.EPERS_BIRTH
    assert mapped.epers_place == "PARIS"
    assert mapped.epers_note == "NOTE"
    assert mapped.epers_witnesses == [(10, WitnessKind.WITNESS), (20, WitnessKind.WITNESS)]


def test_map_pers_event_with_custom_name():
    event = GenPersEvent[int, str](
        epers_name=EpersName[str](name="custom_event"),
        epers_date=CdateNone(),
        epers_place="London",
        epers_reason="",
        epers_note="",
        epers_src="",
        epers_witnesses=[]
    )

    mapped = map_pers_event(lambda x: x + 5, str.upper, event)

    assert isinstance(mapped.epers_name, EpersName)
    assert mapped.epers_name.name == "CUSTOM_EVENT"
    assert mapped.epers_place == "LONDON"


def test_map_fam_event_with_enum_name():
    event = GenFamEvent[int, str](
        efam_name=GenFamEventName.EFAM_MARRIAGE,
        efam_date=CdateNone(),
        efam_place="Rome",
        efam_reason="",
        efam_note="ceremony",
        efam_src="registry",
        efam_witnesses=[(1, WitnessKind.WITNESS)]
    )

    mapped = map_fam_event(lambda x: x * 2, str.upper, event)

    assert mapped.efam_name == GenFamEventName.EFAM_MARRIAGE
    assert mapped.efam_place == "ROME"
    assert mapped.efam_note == "CEREMONY"
    assert mapped.efam_witnesses == [(2, WitnessKind.WITNESS)]


def test_map_fam_event_with_custom_name():
    event = GenFamEvent[int, str](
        efam_name=EfamName[str](name="special_union"),
        efam_date=CdateNone(),
        efam_place="Vegas",
        efam_reason="",
        efam_note="",
        efam_src="",
        efam_witnesses=[]
    )

    mapped = map_fam_event(lambda x: x, str.upper, event)

    assert isinstance(mapped.efam_name, EfamName)
    assert mapped.efam_name.name == "SPECIAL_UNION"


def test_map_relation_ps():
    relation = GenRelation[int, str](
        r_type=RelationType.ADOPTION,
        r_fath=1,
        r_moth=2,
        r_sources="source1"
    )

    mapped = map_relation_ps(lambda x: x * 10, str.upper, relation)

    assert mapped.r_type == RelationType.ADOPTION
    assert mapped.r_fath == 10
    assert mapped.r_moth == 20
    assert mapped.r_sources == "SOURCE1"


def test_map_relation_ps_with_none_parents():
    relation = GenRelation[int, str](
        r_type=RelationType.RECOGNITION,
        r_fath=None,
        r_moth=None,
        r_sources="source2"
    )

    mapped = map_relation_ps(lambda x: x * 10, str.upper, relation)

    assert mapped.r_fath is None
    assert mapped.r_moth is None
    assert mapped.r_sources == "SOURCE2"


def test_map_person_ps_basic():
    person = GenPerson[int, int, str](
        first_name="John",
        surname="Doe",
        occ=0,
        image="",
        public_name="",
        qualifiers=[],
        aliases=[],
        first_names_aliases=[],
        surnames_aliases=[],
        titles=[],
        rparents=[],
        related=[],
        occupation="",
        sex=Sex.MALE,
        access=Access.PUBLIC,
        birth=CdateNone(),
        birth_place="NYC",
        birth_note="",
        birth_src="",
        baptism=CdateNone(),
        baptism_place="",
        baptism_note="",
        baptism_src="",
        death=NotDead(),
        death_place="",
        death_note="",
        death_src="",
        burial=UnknownBurial(),
        burial_place="",
        burial_note="",
        burial_src="",
        pevents=[],
        notes="",
        psources="",
        key_index=42
    )

    mapped = map_person_ps(lambda x: x * 2, str.upper, person)

    assert mapped.first_name == "JOHN"
    assert mapped.surname == "DOE"
    assert mapped.birth_place == "NYC"
    assert mapped.key_index == 42


def test_map_person_ps_with_titles():
    title = GenTitle[str](
        t_name=Tname[str](name="Sir"),
        t_ident="KBE",
        t_place="England",
        t_date_start=CdateNone(),
        t_date_end=CdateNone(),
        t_nth=1
    )

    person = GenPerson[int, int, str](
        first_name="Arthur",
        surname="Pendragon",
        occ=0,
        image="",
        public_name="King Arthur",
        qualifiers=[],
        aliases=["Rex"],
        first_names_aliases=[],
        surnames_aliases=[],
        titles=[title],
        rparents=[],
        related=[],
        occupation="King",
        sex=Sex.MALE,
        access=Access.PUBLIC,
        birth=CdateNone(),
        birth_place="",
        birth_note="",
        birth_src="",
        baptism=CdateNone(),
        baptism_place="",
        baptism_note="",
        baptism_src="",
        death=NotDead(),
        death_place="",
        death_note="",
        death_src="",
        burial=UnknownBurial(),
        burial_place="",
        burial_note="",
        burial_src="",
        pevents=[],
        notes="",
        psources="",
        key_index=1
    )

    mapped = map_person_ps(lambda x: x, str.upper, person)

    assert len(mapped.titles) == 1
    assert mapped.titles[0].t_name.name == "SIR"
    assert mapped.public_name == "KING ARTHUR"
    assert mapped.aliases == ["REX"]


def test_map_ascend_f_with_parents():
    ascend = GenAscend[int](parents=10, consang=Fix(0))

    mapped = map_ascend_f(lambda x: x * 2, ascend)

    assert mapped.parents == 20
    assert mapped.consang == Fix(0)


def test_map_ascend_f_without_parents():
    ascend = GenAscend[int](parents=None, consang=Fix(0))

    mapped = map_ascend_f(lambda x: x * 2, ascend)

    assert mapped.parents is None


def test_map_union_f():
    union = GenUnion[int](family=[1, 2, 3])

    mapped = map_union_f(lambda x: x * 10, union)

    assert mapped.family == [10, 20, 30]


def test_map_union_f_empty():
    union = GenUnion[int](family=[])

    mapped = map_union_f(lambda x: x * 10, union)

    assert mapped.family == []


def test_map_family_ps_basic():
    family = GenFamily[int, int, str](
        marriage=CdateNone(),
        marriage_place="Church",
        marriage_note="",
        marriage_src="",
        witnesses=[1, 2],
        relation=RelationKind.MARRIED,
        divorce=NotDivorced(),
        fevents=[],
        comment="Happy couple",
        origin_file="db.gw",
        fsources="",
        fam_index=100
    )

    mapped = map_family_ps(lambda x: x * 2, lambda x: x + 50, str.upper, family)

    assert mapped.witnesses == [2, 4]
    assert mapped.fam_index == 150
    assert mapped.marriage_place == "CHURCH"
    assert mapped.comment == "HAPPY COUPLE"


def test_map_family_ps_with_divorce():
    date = CdateGregorian(value=compress(Dmy(day=1, month=1, year=2000, prec=Precision.SURE, delta=0)))
    family = GenFamily[int, int, str](
        marriage=CdateNone(),
        marriage_place="",
        marriage_note="",
        marriage_src="",
        witnesses=[],
        relation=RelationKind.MARRIED,
        divorce=DivorceWithDate(date=date),
        fevents=[],
        comment="",
        origin_file="",
        fsources="",
        fam_index=200
    )

    mapped = map_family_ps(lambda x: x, lambda x: x, lambda x: x, family)

    assert isinstance(mapped.divorce, DivorceWithDate)


def test_map_couple_p():
    couple = Couple(father=10, mother=20)

    mapped = map_couple_p(False, lambda x: x * 3, couple)

    assert mapped.father == 30
    assert mapped.mother == 60


def test_map_descend_p():
    descend = GenDescend[int](children=[1, 2, 3, 4])

    mapped = map_descend_p(lambda x: x + 100, descend)

    assert mapped.children == [101, 102, 103, 104]


def test_eq_lists_equal():
    l1 = [1, 2, 3]
    l2 = ["1", "2", "3"]

    assert eq_lists(lambda a, b: str(a) == b, l1, l2)


def test_eq_lists_not_equal():
    l1 = [1, 2, 3]
    l2 = [1, 2, 4]

    assert not eq_lists(lambda a, b: a == b, l1, l2)


def test_eq_lists_different_lengths():
    l1 = [1, 2]
    l2 = [1, 2, 3]

    assert not eq_lists(lambda a, b: a == b, l1, l2)


def test_eq_title_names_tmain():
    tn1 = Tmain[str]()
    tn2 = Tmain[int]()

    assert eq_title_names(lambda a, b: True, tn1, tn2)


def test_eq_title_names_tnone():
    tn1 = Tnone[str]()
    tn2 = Tnone[int]()

    assert eq_title_names(lambda a, b: True, tn1, tn2)


def test_eq_title_names_tname_equal():
    tn1 = Tname[str](name="Duke")
    tn2 = Tname[str](name="Duke")

    assert eq_title_names(lambda a, b: a == b, tn1, tn2)


def test_eq_title_names_tname_not_equal():
    tn1 = Tname[str](name="Duke")
    tn2 = Tname[str](name="Earl")

    assert not eq_title_names(lambda a, b: a == b, tn1, tn2)


def test_eq_title_names_different_types():
    tn1 = Tmain[str]()
    tn2 = Tnone[str]()

    assert not eq_title_names(lambda a, b: True, tn1, tn2)


def test_eq_titles_equal():
    t1 = GenTitle[str](
        t_name=Tname[str](name="Duke"),
        t_ident="id1",
        t_place="London",
        t_date_start=CdateNone(),
        t_date_end=CdateNone(),
        t_nth=1
    )
    t2 = GenTitle[str](
        t_name=Tname[str](name="Duke"),
        t_ident="id1",
        t_place="London",
        t_date_start=CdateNone(),
        t_date_end=CdateNone(),
        t_nth=1
    )

    assert eq_titles(lambda a, b: a == b, t1, t2)


def test_eq_titles_not_equal_place():
    t1 = GenTitle[str](
        t_name=Tmain[str](),
        t_ident="id1",
        t_place="London",
        t_date_start=CdateNone(),
        t_date_end=CdateNone(),
        t_nth=1
    )
    t2 = GenTitle[str](
        t_name=Tmain[str](),
        t_ident="id1",
        t_place="Paris",
        t_date_start=CdateNone(),
        t_date_end=CdateNone(),
        t_nth=1
    )

    assert not eq_titles(lambda a, b: a == b, t1, t2)


def test_gen_person_misc_names_simple():
    def sou(x):
        return x

    names = gen_person_misc_names(
        sou=sou,
        empty_string="",
        quest_string="?",
        first_name="John",
        surname="Doe",
        public_name="",
        qualifiers=[],
        aliases=[],
        first_names_aliases=[],
        surnames_aliases=[],
        titles=[],
        husbands=[],
        father_titles_places=[]
    )

    assert "John Doe" in names
    assert len(names) > 0


def test_gen_person_misc_names_with_question():
    def sou(x):
        return x

    names = gen_person_misc_names(
        sou=sou,
        empty_string="",
        quest_string="?",
        first_name="?",
        surname="Doe",
        public_name="",
        qualifiers=[],
        aliases=[],
        first_names_aliases=[],
        surnames_aliases=[],
        titles=[],
        husbands=[],
        father_titles_places=[]
    )

    assert names == []


def test_gen_person_misc_names_with_aliases():
    def sou(x):
        return x

    names = gen_person_misc_names(
        sou=sou,
        empty_string="",
        quest_string="?",
        first_name="John",
        surname="Doe",
        public_name="",
        qualifiers=[],
        aliases=["Johnny", "JD"],
        first_names_aliases=["Jack"],
        surnames_aliases=["Dough"],
        titles=[],
        husbands=[],
        father_titles_places=[]
    )

    assert "Johnny" in names
    assert "JD" in names
    assert "Jack Doe" in names
    assert "John Dough" in names
