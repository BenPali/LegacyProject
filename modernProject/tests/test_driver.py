from lib.driver import istr, ifam, iper, Istr, Ifam, Iper


def test_type_aliases():
    i: istr = 5
    f: ifam = 10
    p: iper = 15
    assert isinstance(i, int)
    assert isinstance(f, int)
    assert isinstance(p, int)


def test_istr_constants():
    assert Istr.EMPTY == 0
    assert Istr.QUEST == 1


def test_istr_dummy():
    assert Istr.dummy() == -1


def test_istr_is_dummy():
    assert Istr.is_dummy(-1) is True
    assert Istr.is_dummy(0) is False
    assert Istr.is_dummy(1) is False
    assert Istr.is_dummy(100) is False


def test_istr_hash():
    assert Istr.hash_func(0) == 0
    assert Istr.hash_func(1) == 1
    assert Istr.hash_func(42) == 42
    assert Istr.hash_func(-1) == -1


def test_istr_equal():
    assert Istr.equal(0, 0) is True
    assert Istr.equal(1, 1) is True
    assert Istr.equal(42, 42) is True
    assert Istr.equal(0, 1) is False
    assert Istr.equal(42, 43) is False


def test_istr_compare():
    assert Istr.compare(0, 0) == 0
    assert Istr.compare(1, 0) == 1
    assert Istr.compare(0, 1) == -1
    assert Istr.compare(100, 50) == 1
    assert Istr.compare(50, 100) == -1


def test_istr_to_string():
    assert Istr.to_string(0) == "0"
    assert Istr.to_string(1) == "1"
    assert Istr.to_string(42) == "42"
    assert Istr.to_string(-1) == "-1"


def test_istr_of_string():
    assert Istr.of_string("0") == 0
    assert Istr.of_string("1") == 1
    assert Istr.of_string("42") == 42
    assert Istr.of_string("-1") == -1


def test_istr_is_empty():
    assert Istr.is_empty(0) is True
    assert Istr.is_empty(1) is False
    assert Istr.is_empty(42) is False
    assert Istr.is_empty(-1) is False


def test_istr_is_quest():
    assert Istr.is_quest(0) is False
    assert Istr.is_quest(1) is True
    assert Istr.is_quest(42) is False
    assert Istr.is_quest(-1) is False


def test_ifam_dummy():
    assert Ifam.dummy() == -1


def test_ifam_is_dummy():
    assert Ifam.is_dummy(-1) is True
    assert Ifam.is_dummy(0) is False
    assert Ifam.is_dummy(1) is False
    assert Ifam.is_dummy(100) is False


def test_ifam_hash():
    assert Ifam.hash_func(0) == 0
    assert Ifam.hash_func(42) == 42
    assert Ifam.hash_func(-1) == -1


def test_ifam_equal():
    assert Ifam.equal(0, 0) is True
    assert Ifam.equal(42, 42) is True
    assert Ifam.equal(0, 1) is False
    assert Ifam.equal(42, 43) is False


def test_ifam_compare():
    assert Ifam.compare(0, 0) == 0
    assert Ifam.compare(1, 0) == 1
    assert Ifam.compare(0, 1) == -1
    assert Ifam.compare(100, 50) == 1
    assert Ifam.compare(50, 100) == -1


def test_ifam_to_string():
    assert Ifam.to_string(0) == "0"
    assert Ifam.to_string(42) == "42"
    assert Ifam.to_string(-1) == "-1"


def test_ifam_of_string():
    assert Ifam.of_string("0") == 0
    assert Ifam.of_string("42") == 42
    assert Ifam.of_string("-1") == -1


def test_iper_dummy():
    assert Iper.dummy() == -1


def test_iper_is_dummy():
    assert Iper.is_dummy(-1) is True
    assert Iper.is_dummy(0) is False
    assert Iper.is_dummy(1) is False
    assert Iper.is_dummy(100) is False


def test_iper_hash():
    assert Iper.hash_func(0) == 0
    assert Iper.hash_func(42) == 42
    assert Iper.hash_func(-1) == -1


def test_iper_equal():
    assert Iper.equal(0, 0) is True
    assert Iper.equal(42, 42) is True
    assert Iper.equal(0, 1) is False
    assert Iper.equal(42, 43) is False


def test_iper_compare():
    assert Iper.compare(0, 0) == 0
    assert Iper.compare(1, 0) == 1
    assert Iper.compare(0, 1) == -1
    assert Iper.compare(100, 50) == 1
    assert Iper.compare(50, 100) == -1


def test_iper_to_string():
    assert Iper.to_string(0) == "0"
    assert Iper.to_string(42) == "42"
    assert Iper.to_string(-1) == "-1"


def test_iper_of_string():
    assert Iper.of_string("0") == 0
    assert Iper.of_string("42") == 42
    assert Iper.of_string("-1") == -1


def test_poi_and_foi():
    from lib.driver import poi, foi, Person, Family
    from types import SimpleNamespace

    mock_base = SimpleNamespace()
    person = poi(mock_base, 5)
    assert isinstance(person, Person)
    assert person.base == mock_base
    assert person.index == 5

    family = foi(mock_base, 10)
    assert isinstance(family, Family)
    assert family.base == mock_base
    assert family.index == 10


def test_sou():
    from lib.driver import sou
    from types import SimpleNamespace

    mock_strings = SimpleNamespace(get=lambda i: f"string_{i}")
    mock_data = SimpleNamespace(strings=mock_strings)
    mock_base = SimpleNamespace(data=mock_data)

    assert sou(mock_base, 5) == "string_5"
    assert sou(mock_base, 0) == "string_0"


def test_bname():
    from lib.driver import bname
    from types import SimpleNamespace

    mock_data = SimpleNamespace(bdir="/path/to/database.gwb")
    mock_base = SimpleNamespace(data=mock_data)
    assert bname(mock_base) == "database"

    mock_data2 = SimpleNamespace(bdir="/another/path/mybase.gwb")
    mock_base2 = SimpleNamespace(data=mock_data2)
    assert bname(mock_base2) == "mybase"


def test_nb_of_persons():
    from lib.driver import nb_of_persons
    from types import SimpleNamespace

    mock_persons = SimpleNamespace(arr=[None] * 100)
    mock_data = SimpleNamespace(persons=mock_persons)
    mock_base = SimpleNamespace(data=mock_data)
    assert nb_of_persons(mock_base) == 100


def test_nb_of_families():
    from lib.driver import nb_of_families
    from types import SimpleNamespace

    mock_families = SimpleNamespace(arr=[None] * 50)
    mock_data = SimpleNamespace(families=mock_families)
    mock_base = SimpleNamespace(data=mock_data)
    assert nb_of_families(mock_base) == 50


def test_iper_exists():
    from lib.driver import iper_exists
    from types import SimpleNamespace

    mock_persons = SimpleNamespace(arr=[None] * 100)
    mock_data = SimpleNamespace(persons=mock_persons)
    mock_base = SimpleNamespace(data=mock_data)

    assert iper_exists(mock_base, 0) is True
    assert iper_exists(mock_base, 50) is True
    assert iper_exists(mock_base, 99) is True
    assert iper_exists(mock_base, 100) is False
    assert iper_exists(mock_base, -1) is False


def test_ifam_exists():
    from lib.driver import ifam_exists
    from types import SimpleNamespace

    mock_families = SimpleNamespace(arr=[None] * 50)
    mock_data = SimpleNamespace(families=mock_families)
    mock_base = SimpleNamespace(data=mock_data)

    assert ifam_exists(mock_base, 0) is True
    assert ifam_exists(mock_base, 25) is True
    assert ifam_exists(mock_base, 49) is True
    assert ifam_exists(mock_base, 50) is False
    assert ifam_exists(mock_base, -1) is False


def test_person_getters():
    from lib.driver import (
        Person, get_iper, get_first_name, get_surname, get_occ,
        get_image, get_public_name, get_sex, get_access
    )
    from lib.gwdef import GenPerson, GenAscend, GenUnion, Sex, Access
    from lib.date import cdate_None
    from lib.adef import NO_CONSANG
    from types import SimpleNamespace

    gen_person = GenPerson(
        first_name=10,
        surname=20,
        occ=3,
        image=30,
        public_name=40,
        qualifiers=[],
        aliases=[],
        first_names_aliases=[],
        surnames_aliases=[],
        titles=[],
        rparents=[],
        related=[],
        occupation=50,
        sex=Sex.MALE,
        access=Access.PUBLIC,
        birth=cdate_None,
        birth_place=60,
        birth_note=61,
        birth_src=62,
        baptism=cdate_None,
        baptism_place=70,
        baptism_note=71,
        baptism_src=72,
        death=None,
        death_place=80,
        death_note=81,
        death_src=82,
        burial=None,
        burial_place=90,
        burial_note=91,
        burial_src=92,
        pevents=[],
        notes=100,
        psources=110,
        key_index=5
    )

    person = Person(base=None, index=5)
    person.gen_person = gen_person
    person.gen_ascend = GenAscend(parents=None, consang=NO_CONSANG)
    person.gen_union = GenUnion(family=[])

    assert get_iper(person) == 5
    assert get_first_name(person) == 10
    assert get_surname(person) == 20
    assert get_occ(person) == 3
    assert get_image(person) == 30
    assert get_public_name(person) == 40
    assert get_sex(person) == Sex.MALE
    assert get_access(person) == Access.PUBLIC


def test_family_getters():
    from lib.driver import (
        Family, get_ifam, get_father, get_mother, get_parent_array,
        get_children, get_marriage_place
    )
    from lib.gwdef import GenFamily, GenCouple, GenDescend
    from lib.date import cdate_None
    from types import SimpleNamespace

    gen_family = GenFamily(
        marriage=cdate_None,
        marriage_place=100,
        marriage_note=101,
        marriage_src=102,
        relation=None,
        divorce=None,
        fevents=[],
        witnesses=[],
        comment=110,
        origin_file=120,
        fsources=130,
        fam_index=15
    )
    gen_couple = GenCouple(father=10, mother=20)
    gen_descend = GenDescend(children=[30, 31, 32])

    family = Family(base=None, index=15)
    family.gen_family = gen_family
    family.gen_couple = gen_couple
    family.gen_descend = gen_descend

    assert get_ifam(family) == 15
    assert get_father(family) == 10
    assert get_mother(family) == 20
    assert get_parent_array(family) == (10, 20)
    assert get_children(family) == [30, 31, 32]
    assert get_marriage_place(family) == 100


def test_delete_operations():
    from lib.driver import delete_person, delete_ascend, delete_union
    from lib.driver import delete_family, delete_couple, delete_descend
    from types import SimpleNamespace

    patched_calls = []

    def mock_patch(name):
        def patch_func(*args):
            patched_calls.append((name, args))
        return patch_func

    mock_func = SimpleNamespace(
        patch_person=mock_patch('patch_person'),
        patch_ascend=mock_patch('patch_ascend'),
        patch_union=mock_patch('patch_union'),
        patch_family=mock_patch('patch_family'),
        patch_couple=mock_patch('patch_couple'),
        patch_descend=mock_patch('patch_descend')
    )
    mock_base = SimpleNamespace(func=mock_func)

    delete_person(mock_base, 5)
    assert patched_calls[0][0] == 'patch_person'
    assert patched_calls[0][1][0] == 5

    delete_ascend(mock_base, 6)
    assert patched_calls[1][0] == 'patch_ascend'
    assert patched_calls[1][1][0] == 6

    delete_union(mock_base, 7)
    assert patched_calls[2][0] == 'patch_union'
    assert patched_calls[2][1][0] == 7

    delete_family(mock_base, 8)
    assert patched_calls[3][0] == 'patch_family'
    assert patched_calls[3][1][0] == 8

    delete_couple(mock_base, 9)
    assert patched_calls[4][0] == 'patch_couple'
    assert patched_calls[4][1][0] == 9

    delete_descend(mock_base, 10)
    assert patched_calls[5][0] == 'patch_descend'
    assert patched_calls[5][1][0] == 10


def test_insert_string():
    from lib.driver import insert_string
    from types import SimpleNamespace

    mock_func = SimpleNamespace(insert_string=lambda s: 42)
    mock_base = SimpleNamespace(func=mock_func)

    result = insert_string(mock_base, "test")
    assert result == 42


def test_commit_patches():
    from lib.driver import commit_patches
    from types import SimpleNamespace

    committed = []
    mock_func = SimpleNamespace(commit_patches=lambda: committed.append(True))
    mock_base = SimpleNamespace(func=mock_func)

    commit_patches(mock_base)
    assert len(committed) == 1


def test_commit_notes():
    from lib.driver import commit_notes
    from types import SimpleNamespace

    committed = []
    mock_func = SimpleNamespace(commit_notes=lambda f, c: committed.append((f, c)))
    mock_base = SimpleNamespace(func=mock_func)

    commit_notes(mock_base, "test.txt", "content")
    assert len(committed) == 1
    assert committed[0] == ("test.txt", "content")


def test_commit_wiznotes():
    from lib.driver import commit_wiznotes
    from types import SimpleNamespace

    committed = []
    mock_func = SimpleNamespace(commit_wiznotes=lambda f, c: committed.append((f, c)))
    mock_base = SimpleNamespace(func=mock_func)

    commit_wiznotes(mock_base, "wizard.txt", "notes")
    assert len(committed) == 1
    assert committed[0] == ("wizard.txt", "notes")


def test_person_of_key():
    from lib.driver import person_of_key
    from types import SimpleNamespace

    mock_func = SimpleNamespace(person_of_key=lambda f, s, o: 123 if f == "John" else None)
    mock_base = SimpleNamespace(func=mock_func)

    result = person_of_key(mock_base, "John", "Doe", 0)
    assert result == 123

    result = person_of_key(mock_base, "Jane", "Doe", 0)
    assert result is None


def test_ipers():
    from lib.driver import ipers
    from types import SimpleNamespace

    mock_persons = SimpleNamespace(arr=[None] * 5)
    mock_data = SimpleNamespace(persons=mock_persons)
    mock_base = SimpleNamespace(data=mock_data)

    collection = ipers(mock_base)
    assert collection.length == 5
    assert collection.get(0) == 0
    assert collection.get(4) == 4
    assert collection.get(5) is None


def test_persons():
    from lib.driver import persons, Person
    from types import SimpleNamespace

    mock_persons = SimpleNamespace(arr=[None] * 3)
    mock_data = SimpleNamespace(persons=mock_persons)
    mock_base = SimpleNamespace(data=mock_data)

    collection = persons(mock_base)
    assert collection.length == 3
    person = collection.get(0)
    assert isinstance(person, Person)
    assert person.index == 0


def test_iper_marker():
    from lib.driver import iper_marker, ipers
    from types import SimpleNamespace

    mock_persons = SimpleNamespace(arr=[None] * 10)
    mock_data = SimpleNamespace(persons=mock_persons)
    mock_base = SimpleNamespace(data=mock_data)

    collection = ipers(mock_base)
    marker = iper_marker(collection, False)
    assert marker is not None


def test_ifam_marker():
    from lib.driver import ifam_marker, ifams
    from types import SimpleNamespace

    mock_families = SimpleNamespace(arr=[None] * 5)
    mock_data = SimpleNamespace(families=mock_families)
    mock_base = SimpleNamespace(data=mock_data)

    collection = ifams(mock_base)
    marker = ifam_marker(collection, False)
    assert marker is not None


def test_all_person_getters_coverage():
    from lib.driver import (
        Person, get_aliases, get_first_names_aliases, get_surnames_aliases,
        get_titles, get_related, get_rparents, get_birth_place, get_birth_note,
        get_birth_src, get_baptism, get_baptism_place, get_baptism_note,
        get_baptism_src, get_death, get_death_place, get_death_note, get_death_src,
        get_burial, get_burial_place, get_burial_note, get_burial_src,
        get_pevents, get_notes, get_psources, get_consang, get_parents, get_birth
    )
    from lib.gwdef import GenPerson, GenAscend, GenUnion, Sex, Access
    from lib.date import cdate_None
    from lib.adef import NO_CONSANG

    gen_person = GenPerson(
        first_name=10, surname=20, occ=3, image=30, public_name=40,
        qualifiers=[1, 2], aliases=[3, 4], first_names_aliases=[5, 6],
        surnames_aliases=[7, 8], titles=[9], rparents=[10], related=[11, 12],
        occupation=50, sex=Sex.MALE, access=Access.PUBLIC,
        birth=cdate_None, birth_place=60, birth_note=61, birth_src=62,
        baptism=cdate_None, baptism_place=70, baptism_note=71, baptism_src=72,
        death=None, death_place=80, death_note=81, death_src=82,
        burial=None, burial_place=90, burial_note=91, burial_src=92,
        pevents=[100], notes=110, psources=120, key_index=5
    )

    person = Person(base=None, index=5)
    person.gen_person = gen_person
    person.gen_ascend = GenAscend(parents=15, consang=NO_CONSANG)
    person.gen_union = GenUnion(family=[20, 21])

    assert get_aliases(person) == [3, 4]
    assert get_first_names_aliases(person) == [5, 6]
    assert get_surnames_aliases(person) == [7, 8]
    assert get_titles(person) == [9]
    assert get_related(person) == [11, 12]
    assert get_rparents(person) == [10]
    assert get_birth(person) == cdate_None
    assert get_birth_place(person) == 60
    assert get_birth_note(person) == 61
    assert get_birth_src(person) == 62
    assert get_baptism(person) == cdate_None
    assert get_baptism_place(person) == 70
    assert get_baptism_note(person) == 71
    assert get_baptism_src(person) == 72
    assert get_death(person) is None
    assert get_death_place(person) == 80
    assert get_death_note(person) == 81
    assert get_death_src(person) == 82
    assert get_burial(person) is None
    assert get_burial_place(person) == 90
    assert get_burial_note(person) == 91
    assert get_burial_src(person) == 92
    assert get_pevents(person) == [100]
    assert get_notes(person) == 110
    assert get_psources(person) == 120
    assert get_consang(person) == NO_CONSANG
    assert get_parents(person) == 15


def test_all_family_getters_coverage():
    from lib.driver import (
        Family, get_marriage_note, get_marriage_src, get_divorce,
        get_relation, get_fevents, get_fsources, get_origin_file
    )
    from lib.gwdef import GenFamily, GenCouple, GenDescend, RelationKind, NotDivorced
    from lib.date import cdate_None

    gen_family = GenFamily(
        marriage=cdate_None, marriage_place=100, marriage_note=101, marriage_src=102,
        relation=RelationKind.MARRIED, divorce=NotDivorced(), fevents=[200],
        witnesses=[10, 11], comment=110, origin_file=120, fsources=130, fam_index=15
    )
    gen_couple = GenCouple(father=10, mother=20)
    gen_descend = GenDescend(children=[30, 31, 32])

    family = Family(base=None, index=15)
    family.gen_family = gen_family
    family.gen_couple = gen_couple
    family.gen_descend = gen_descend

    assert get_marriage_note(family) == 101
    assert get_marriage_src(family) == 102
    assert isinstance(get_divorce(family), NotDivorced)
    assert get_relation(family) == RelationKind.MARRIED
    assert get_fevents(family) == [200]
    assert get_fsources(family) == 130
    assert get_origin_file(family) == 120


def test_base_operations_no_func():
    from lib.driver import insert_string, person_of_key, persons_of_name
    from lib.driver import persons_of_first_name, persons_of_surname
    from types import SimpleNamespace

    mock_base = SimpleNamespace()

    assert insert_string(mock_base, "test") == 0
    assert person_of_key(mock_base, "John", "Doe", 0) is None
    assert persons_of_name(mock_base, "John Doe") == []
    assert persons_of_first_name(mock_base) is None
    assert persons_of_surname(mock_base) is None


def test_base_operations_no_data():
    from lib.driver import sou, bname, nb_of_persons, nb_of_families
    from lib.driver import nb_of_real_persons, iper_exists, ifam_exists
    from types import SimpleNamespace

    mock_base = SimpleNamespace()

    assert sou(mock_base, 5) == ""
    assert bname(mock_base) == ""
    assert nb_of_persons(mock_base) == 0
    assert nb_of_families(mock_base) == 0
    assert nb_of_real_persons(mock_base) == 0
    assert iper_exists(mock_base, 0) is False
    assert ifam_exists(mock_base, 0) is False


def test_ifams_with_selection():
    from lib.driver import ifams, foi
    from types import SimpleNamespace

    mock_families = SimpleNamespace(arr=[None] * 5)
    mock_data = SimpleNamespace(families=mock_families)
    mock_base = SimpleNamespace(data=mock_data)

    select_even = lambda i: i % 2 == 0
    collection = ifams(mock_base, select=select_even)
    assert collection.length == 5


def test_families_with_selection():
    from lib.driver import families, Family
    from types import SimpleNamespace

    mock_families = SimpleNamespace(arr=[None] * 5)
    mock_data = SimpleNamespace(families=mock_families)
    mock_base = SimpleNamespace(data=mock_data)

    select_all = lambda f: True
    collection = families(mock_base, select=select_all)
    assert collection.length == 5
