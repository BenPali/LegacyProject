import pytest
from lib.gwdef import *
from lib.adef import Cdate, CdateGregorian, Dmy, Calendar, Precision, Fix

def test_http_status():
    assert HttpStatus.OK.value == 200
    assert HttpStatus.MOVED_TEMPORARILY.value == 302
    assert HttpStatus.BAD_REQUEST.value == 400
    assert HttpStatus.NOT_FOUND.value == 404

def test_http_exception():
    exc = HttpExn(HttpStatus.NOT_FOUND, "Page not found")
    assert exc.status == HttpStatus.NOT_FOUND
    assert exc.message == "Page not found"
    assert "NOT_FOUND" in str(exc)

def test_choice_left():
    choice = Choice.left(42)
    assert choice.is_left
    assert choice.value == 42

def test_choice_right():
    choice = Choice.right("test")
    assert not choice.is_left
    assert choice.value == "test"

def test_relation_kind():
    assert RelationKind.MARRIED
    assert RelationKind.NOT_MARRIED
    assert RelationKind.ENGAGED

def test_divorce_types():
    not_divorced = NotDivorced()
    assert isinstance(not_divorced, Divorce)

    dmy = Dmy(day=15, month=6, year=2000, prec=Precision.SURE, delta=0)
    divorced = DivorceWithDate(CdateGregorian(dmy))
    assert isinstance(divorced, Divorce)

def test_death_reason():
    assert DeathReason.KILLED
    assert DeathReason.MURDERED
    assert DeathReason.EXECUTED

def test_death_types():
    not_dead = NotDead()
    assert isinstance(not_dead, Death)

    dmy = Dmy(day=10, month=3, year=1950, prec=Precision.SURE, delta=0)
    death = DeathWithReason(DeathReason.UNSPECIFIED, CdateGregorian(dmy))
    assert isinstance(death, Death)
    assert death.reason == DeathReason.UNSPECIFIED

def test_burial_types():
    unknown = UnknownBurial()
    assert isinstance(unknown, Burial)

    dmy = Dmy(day=12, month=3, year=1950, prec=Precision.SURE, delta=0)
    buried = Buried(CdateGregorian(dmy))
    assert isinstance(buried, Burial)

    cremated = Cremated(CdateGregorian(dmy))
    assert isinstance(cremated, Burial)

def test_access():
    assert Access.PUBLIC
    assert Access.PRIVATE
    assert Access.SEMI_PUBLIC
    assert Access.IF_TITLES

def test_gen_title_name():
    tmain = Tmain()
    assert isinstance(tmain, GenTitleName)

    tname = Tname("Duke")
    assert isinstance(tname, GenTitleName)
    assert tname.name == "Duke"

    tnone = Tnone()
    assert isinstance(tnone, GenTitleName)

def test_gen_title():
    dmy = Dmy(day=1, month=1, year=1800, prec=Precision.SURE, delta=0)
    title = GenTitle(
        t_name=Tname("Baron"),
        t_ident="baron_id",
        t_place="London",
        t_date_start=CdateGregorian(dmy),
        t_date_end=CdateGregorian(dmy),
        t_nth=1
    )
    assert isinstance(title.t_name, Tname)
    assert title.t_ident == "baron_id"

def test_witness_kind():
    assert WitnessKind.WITNESS
    assert WitnessKind.WITNESS_GOD_PARENT
    assert WitnessKind.WITNESS_CIVIL_OFFICER

def test_gen_pers_event_name():
    assert GenPersEventName.EPERS_BIRTH
    assert GenPersEventName.EPERS_DEATH
    assert GenPersEventName.EPERS_BAPTISM
    assert GenPersEventName.EPERS_FUNERAL

def test_epers_name():
    custom_event = EpersName("Custom Event")
    assert custom_event.name == "Custom Event"

def test_gen_pers_event():
    dmy = Dmy(day=1, month=5, year=1900, prec=Precision.SURE, delta=0)
    event = GenPersEvent(
        epers_name=GenPersEventName.EPERS_BIRTH,
        epers_date=CdateGregorian(dmy),
        epers_place="Paris",
        epers_reason="",
        epers_note="",
        epers_src="",
        epers_witnesses=[]
    )
    assert event.epers_name == GenPersEventName.EPERS_BIRTH
    assert event.epers_place == "Paris"

def test_gen_fam_event_name():
    assert GenFamEventName.EFAM_MARRIAGE
    assert GenFamEventName.EFAM_DIVORCE
    assert GenFamEventName.EFAM_ENGAGE

def test_efam_name():
    custom_event = EfamName("Custom Family Event")
    assert custom_event.name == "Custom Family Event"

def test_gen_fam_event():
    dmy = Dmy(day=10, month=6, year=1920, prec=Precision.SURE, delta=0)
    event = GenFamEvent(
        efam_name=GenFamEventName.EFAM_MARRIAGE,
        efam_date=CdateGregorian(dmy),
        efam_place="London",
        efam_reason="",
        efam_note="",
        efam_src="",
        efam_witnesses=[]
    )
    assert event.efam_name == GenFamEventName.EFAM_MARRIAGE

def test_relation_type():
    assert RelationType.ADOPTION
    assert RelationType.RECOGNITION
    assert RelationType.GOD_PARENT

def test_gen_relation():
    relation = GenRelation(
        r_type=RelationType.ADOPTION,
        r_fath=None,
        r_moth="mother_id",
        r_sources="adoption_records"
    )
    assert relation.r_type == RelationType.ADOPTION
    assert relation.r_fath is None
    assert relation.r_moth == "mother_id"

def test_sex():
    assert Sex.MALE
    assert Sex.FEMALE
    assert Sex.NEUTER

def test_place():
    place = Place(
        other="",
        town="Paris",
        township="",
        canton="",
        district="",
        county="",
        region="Ile-de-France",
        country="France"
    )
    assert place.town == "Paris"
    assert place.country == "France"

def test_gen_person():
    dmy = Dmy(day=1, month=1, year=1900, prec=Precision.SURE, delta=0)
    person = GenPerson(
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
        birth=CdateGregorian(dmy),
        birth_place="London",
        birth_note="",
        birth_src="",
        baptism=CdateGregorian(dmy),
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
        key_index="person_1"
    )
    assert person.first_name == "John"
    assert person.surname == "Doe"
    assert person.sex == Sex.MALE

def test_gen_ascend():
    ascend = GenAscend(
        parents="family_1",
        consang=Fix(0)
    )
    assert ascend.parents == "family_1"

def test_gen_union():
    union = GenUnion(family=["fam_1", "fam_2"])
    assert len(union.family) == 2

def test_gen_descend():
    descend = GenDescend(children=["child_1", "child_2", "child_3"])
    assert len(descend.children) == 3

def test_gen_family():
    dmy = Dmy(day=1, month=6, year=1920, prec=Precision.SURE, delta=0)
    family = GenFamily(
        marriage=CdateGregorian(dmy),
        marriage_place="Paris",
        marriage_note="",
        marriage_src="",
        witnesses=[],
        relation=RelationKind.MARRIED,
        divorce=NotDivorced(),
        fevents=[],
        comment="",
        origin_file="data.gw",
        fsources="",
        fam_index="fam_1"
    )
    assert family.marriage_place == "Paris"
    assert family.relation == RelationKind.MARRIED

def test_person_error():
    error = AlreadyDefined("person_1")
    assert isinstance(error, PersonError)
    assert error.person == "person_1"

    error = OwnAncestor("person_2")
    assert isinstance(error, PersonError)

    error = BadSexOfMarriedPerson("person_3")
    assert isinstance(error, PersonError)

def test_rn_mode():
    assert RnMode.RN_ALL
    assert RnMode.RN_1LN
    assert RnMode.RN_DEG

def test_base_notes():
    def read_fn(page: str, mode: RnMode) -> str:
        return f"Content of {page}"

    def efiles_fn() -> List[str]:
        return ["page1.txt", "page2.txt"]

    notes = BaseNotes(
        nread=read_fn,
        norigin_file="notes.gw",
        efiles=efiles_fn
    )
    assert notes.nread("test", RnMode.RN_ALL) == "Content of test"
    assert len(notes.efiles()) == 2

def test_base_warning_big_age():
    dmy = Dmy(day=1, month=1, year=1950, prec=Precision.SURE, delta=0)
    warning = BigAgeBetweenSpouses("p1", "p2", dmy)
    assert isinstance(warning, BaseWarning)
    assert warning.person1 == "p1"

def test_base_warning_birth_after_death():
    warning = BirthAfterDeath("person_1")
    assert isinstance(warning, BaseWarning)

def test_base_warning_incoherent_sex():
    warning = IncoherentSex("person_1", 2, 3)
    assert isinstance(warning, BaseWarning)
    assert warning.count1 == 2

def test_missing_sources():
    ms = MissingSources()
    assert ms is not None

def test_base_changed_add_person():
    dmy = Dmy(day=1, month=1, year=1900, prec=Precision.SURE, delta=0)
    person = GenPerson(
        first_name="Jane",
        surname="Smith",
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
        sex=Sex.FEMALE,
        access=Access.PUBLIC,
        birth=CdateGregorian(dmy),
        birth_place="",
        birth_note="",
        birth_src="",
        baptism=CdateGregorian(dmy),
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
        key_index="p1"
    )
    change = UAddPerson(person)
    assert isinstance(change, BaseChanged)
    assert change.person.first_name == "Jane"

def test_base_changed_notes():
    change = UNotes(1, "Some notes")
    assert isinstance(change, BaseChanged)
    assert change.index == 1
    assert change.text == "Some notes"

def test_nldb_page():
    page = NLDB.PgInd("person_1")
    assert isinstance(page, NLDB.Page)
    assert page.person == "person_1"

    page = NLDB.PgFam("family_1")
    assert isinstance(page, NLDB.Page)

    page = NLDB.PgNotes()
    assert isinstance(page, NLDB.Page)

def test_nldb_key():
    key1 = ("John", "Doe", 0)
    key2 = ("John", "Doe", 0)
    key3 = ("Jane", "Doe", 0)

    assert NLDB.equal_key(key1, key2)
    assert not NLDB.equal_key(key1, key3)

def test_nldb_ind():
    ind = NLDB.Ind(ln_txt="Some text", ln_pos=42)
    assert ind.ln_txt == "Some text"
    assert ind.ln_pos == 42
